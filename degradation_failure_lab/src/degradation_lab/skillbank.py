"""Source-scoped build identities and immutable references; never invokes a model."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

from .artifacts import load_run, resolve_run, run_refs
from .family import FamilyRegistry, READY, create, jsonl
from .io import inside, inventory, read, resolve_upstream, sha256, upstream_inventory, utc, write
from .layout import generation_path
from .runner import ExperimentRunner, validate_config

BASE = 'data/manifests/sgb/b1'
POLICY = 'configs/sgb/b1/skillbank_policy.v1.json'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def identity(kind, payload):
    return kind + '-' + hashlib.sha256(canonical(payload)).hexdigest()


def checked_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value):
        raise ValueError('Unsafe identity: ' + str(value))
    return value


def full_inventory(root):
    root = Path(root)
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError('Snapshot symlink rejected: ' + str(p))
        if p.is_file():
            result[p.relative_to(root).as_posix()] = sha256(p)
    return result


def code_inventory(root):
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(Path(root).rglob('*.py'))
            if '__pycache__' not in p.parts}


def make_recipe(**conditions):
    if conditions.get('prompt_metadata_policy') != 'legacy':
        raise ValueError('Only recorded legacy prompt metadata is implemented')
    payload = dict(schema_version=1, **copy.deepcopy(conditions))
    return {'recipe_id': identity('recipe', payload), 'conditions': payload}


def check_recipe(recipe):
    if recipe['recipe_id'] != identity('recipe', recipe['conditions']):
        raise ValueError('BuildRecipe hash mismatch')


def build_run(recipe, run_id, *, parent_run_id=None):
    """A plan is not an executed repetition. Legacy contexts are bound again at prepare."""
    check_recipe(recipe)
    return {'run_id': checked_id(run_id), 'recipe_id': recipe['recipe_id'], 'state': 'PLANNED',
            'parent_run_id': parent_run_id, 'independent_generation': parent_run_id is None,
            'legacy_context_rebind_required': recipe['conditions']['model_visible_metadata']['lab_run_id'] != run_id}


def _append(path, row, key, *, merge_aliases=False):
    """Serialize append-only index updates; no log replacement or budget access."""
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + '.lock')
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        rows = jsonl(path) if path.exists() else []
        previous = next((r for r in reversed(rows) if r[key] == row[key]), None)
        if previous:
            if merge_aliases:
                if previous['content_sha256'] != row['content_sha256']:
                    raise ValueError('SourceSet identity collision')
                aliases = {canonical(x): x for x in previous['aliases'] + row['aliases']}
                row = dict(row, aliases=[aliases[k] for k in sorted(aliases)])
            elif previous != row:
                raise ValueError('Immutable registry identity already exists: ' + row[key])
            if previous == row:
                return
        data = canonical(row) + b'\n'
        with path.open('ab') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
    finally:
        os.close(fd); lock.unlink()


class SkillBank:
    def __init__(self, root, *, index_dir=None, families=None):
        self.root = Path(root).resolve()
        self.index = Path(index_dir).resolve() if index_dir else self.root/BASE
        self.families = families or FamilyRegistry(self.root)
        self.policy = read(self.root/POLICY)
        if self.policy.get('schema_version') != 1 or self.policy.get('prompt_metadata_policy') != 'legacy':
            raise ValueError('Unsupported SkillBank policy')

    def path(self, value):
        value = Path(value)
        p = value.resolve() if value.is_absolute() else inside(self.root, value)
        if not p.is_relative_to(self.root) and not p.is_relative_to(self.index):
            raise ValueError('SkillBank reference escapes lab/index')
        return p

    def rows(self, filename):
        p = self.index/filename
        return jsonl(p) if p.exists() else []

    def source_set(self, references):
        if not references:
            raise ValueError('SOURCE_PENDING: nonempty sources required')
        aliases = []
        for ref in references:
            self.families.admitted(ref)
            aliases.append({'source_id': ref['source_id'], 'sha256': ref['sha256'],
                            'manifest': (self.families.path(ref['manifest']).relative_to(self.root).as_posix()
                                         if self.families.path(ref['manifest']).is_relative_to(self.root) else str(self.families.path(ref['manifest']))),
                            'manifest_sha256': sha256(self.families.path(ref['manifest']))})
        contents = sorted({r['sha256'] for r in references})
        for row in self.families.rows:
            if row['source_sha256'] in contents:
                aliases.append({'source_id': row['source_id'], 'sha256': row['source_sha256'],
                                'manifest': row['source_manifest'], 'manifest_sha256': row['source_manifest_sha256']})
        unique = {canonical(x): x for x in aliases}
        return {'source_set_id': identity('sources', {'schema_version': 1, 'content_sha256': contents}),
                'schema_version': 1, 'content_sha256': contents,
                'identity_scope': 'registered_parent_document_content',
                'aliases': [unique[k] for k in sorted(unique)]}

    def remember_sources(self, value):
        expected = identity('sources', {'schema_version': 1, 'content_sha256': value['content_sha256']})
        if (not value['content_sha256'] or value['content_sha256'] != sorted(set(value['content_sha256']))
                or any(not re.fullmatch(r'[0-9a-f]{64}',x) for x in value['content_sha256'])
                or value['source_set_id'] != expected):
            raise ValueError('Invalid SourceSet')
        _append(self.index/'source_sets.v1.jsonl', value, 'source_set_id', merge_aliases=True)

    def _taxonomy(self, config, *, historical_hashes=None):
        loader = self.families.upstream()
        pipe = config['pipeline']
        domain = pipe.get('domain_type') or pipe.get('domain') or ''
        path = pipe.get('skill_taxonomy_path', '')
        resolved = self.families.path(path) if path else None
        if historical_hashes is not None:
            upstream = resolve_upstream(self.root)
            names = ['AutoSkill4Doc/skill_taxonomies/default.yaml']
            candidate = 'AutoSkill4Doc/skill_taxonomies/' + domain + '.yaml'
            if (upstream/candidate).is_file():
                names.append(candidate)
            if resolved:
                raise ValueError('Historical external taxonomy needs its original byte snapshot')
            if any(historical_hashes.get(n) != sha256(upstream/n) for n in names):
                raise ValueError('Historical taxonomy bytes cannot be reconstructed safely')
        taxonomy = loader(domain_type=domain, taxonomy_path=str(resolved) if resolved else '')
        return taxonomy, {'effective': taxonomy.to_dict(),
                          'effective_sha256': hashlib.sha256(canonical(taxonomy.to_dict())).hexdigest(),
                          'external_file_sha256': sha256(resolved) if resolved else None}

    def _recipe(self, source_set, resolution, inputs, config, condition, metadata, code, *,
                mode, initial_store, lineage=None, historical=False):
        validate_config(config)
        taxonomy, taxonomy_record = self._taxonomy(config, historical_hashes=code['upstream'] if historical else None)
        if mode == 'classified':
            runtime = self.families.check_runtime(config, resolution)
            runtime_family = {k: runtime[k] for k in ('family_id','family_name','profile_id')}
        elif mode == 'default-control':
            if taxonomy.family_candidates or config['pipeline'].get('family_name') or config['pipeline'].get('profile_id'):
                raise ValueError('Explicit legacy default control required')
            runtime_family = {'family_id': '', 'family_name': taxonomy.default_family_name,
                              'profile_id': taxonomy.derive_profile_id(family_name=taxonomy.default_family_name)}
            if runtime_family['family_name'] != '未分类技能':
                raise ValueError('Unknown default Family')
        else:
            raise ValueError('Unknown Family mode')
        normalized_config = copy.deepcopy(config)
        normalized_config.pop('credential_env', None)
        normalized_config.pop('configuration_note', None)
        if normalized_config['pipeline'].get('skill_taxonomy_path'):
            normalized_config['pipeline']['skill_taxonomy_path'] = {'sha256': taxonomy_record['external_file_sha256']}
        family = {'classification_version': 'legacy-unrecorded' if historical else resolution['classification_version'],
                  'catalog_sha256': None if historical else resolution['catalog_sha256'],
                  'source_family_id': resolution['primary_family_id'],
                  'assignment_scope': resolution['assignment_scope'],
                  'secondary_family_ids':sorted(f for f in resolution['involved_families'] if f!=resolution['primary_family_id']),
                  'mixed':resolution['mixed'], 'runtime_family': runtime_family, 'mode': mode}
        return make_recipe(source_set_id=source_set['source_set_id'],
            ordered_inputs=[{k:i[k] for k in ('input_id','source_id','source_sha256','path','sha256')} for i in inputs],
            loader_input_order=sorted(i['path'] for i in inputs), taxonomy=taxonomy_record,
            classification=family, generator_code=code, generation_config=normalized_config,
            prompt_metadata_policy='legacy', model_visible_metadata=metadata,
            condition=condition, initial_store=initial_store, lineage=lineage or [],
            generation_mode='joint_set', skillbank_policy_sha256=sha256(self.root/POLICY))

    def _current_code(self):
        upstream = {k:v for k,v in upstream_inventory(resolve_upstream(self.root)).items()
                    if not k.endswith('.bak') and '.bak.' not in k}
        return {'upstream': upstream, 'wrapper': code_inventory(self.root/'src/degradation_lab'),
                'python': sys.version}

    def plan(self, task, case_id, condition_id, run_id, *, family_mode, force_generation=False):
        checked_id(run_id)
        resolution = self.families.resolve(task['sources'], task_key=task['task_key'],
                                          rule_conflicts=task.get('rule_conflicts', []))
        if resolution['routing_status'] not in READY:
            return {'decision': 'BLOCKED', 'reason': resolution['routing_status'], 'family': resolution}
        sources = self.source_set(task['sources'])
        bundle, condition, manifest, config = ExperimentRunner(self.root).resolve(case_id, condition_id)
        if set(i['source_sha256'] for i in manifest['inputs']) != set(sources['content_sha256']):
            return {'decision': 'BLOCKED', 'reason': 'GENERATION_CASE_SOURCE_MISMATCH'}
        if any(r['run_id'] == run_id for r in run_refs(self.root)):
            raise ValueError('BuildRun ID already exists; independent repetitions need a new run ID')
        target = generation_path(self.root, case_id, condition_id, run_id)
        normalized = []
        for item in manifest['inputs']:
            src = inside(self.root, item['path'])
            dst = target/'inputs'/item['input_id']/src.name
            normalized.append(dict(item, original_path=item['path'], path=dst.relative_to(target).as_posix(),
                                   execution_path=str(dst)))
        snapshot = dict(manifest, inputs=normalized)
        metadata = {'case_id': case_id, 'condition_id': condition_id, 'lab_run_id': run_id, 'input_manifest': snapshot}
        recipe = self._recipe(sources, resolution, normalized, config, condition, metadata, self._current_code(),
                              mode=family_mode, initial_store={'kind':'empty'})
        result = {'schema_version': 1, 'decision':'NEED_GENERATION', 'task_key':task['task_key'],
                  'sources': task['sources'], 'source_set':sources, 'family':resolution, 'recipe':recipe,
                  'build_run':build_run(recipe, run_id), 'case_id':case_id, 'condition_id':condition_id,
                  'family_mode':family_mode, 'generation_path':str(target),
                  'force_generation':force_generation, 'model_calls':0}
        result['plan_id'] = identity('plan', result)
        return result

    def attach_prepared(self, run, plan):
        plan = read(Path(plan)) if not isinstance(plan, dict) else copy.deepcopy(plan)
        plan_id = plan.pop('plan_id')
        if plan_id != identity('plan', plan) or plan['decision'] != 'NEED_GENERATION':
            raise ValueError('Invalid generation plan')
        run = Path(run); invocation = read(run/'invocation.json')
        if ((invocation['case_id'],invocation['condition_id'],invocation['run_id']) !=
                (plan['case_id'],plan['condition_id'],plan['build_run']['run_id'])
                or Path(plan['generation_path']).resolve() != run.resolve()):
            raise ValueError('Prepared run differs from the bank plan')
        config = read(run/'config.json')
        old = config['pipeline'].get('skill_taxonomy_path')
        if old:
            local = run/'taxonomy.yaml'
            shutil.copyfile(self.families.path(old), local)
            config['pipeline']['skill_taxonomy_path'] = str(local); write(run/'config.json',config)
        input_manifest = read(run/'input_manifest.json')
        metadata = {'case_id':invocation['case_id'], 'condition_id':invocation['condition_id'],
                    'lab_run_id':run.name, 'input_manifest':input_manifest}
        code = {'upstream': {k:v for k,v in read(run/'upstream_before.json').items()
                             if not k.endswith('.bak') and '.bak.' not in k},
                'wrapper':code_inventory(run/'wrapper_snapshot/degradation_lab'), 'python':sys.version}
        actual = self._recipe(plan['source_set'],plan['family'],input_manifest['inputs'],config,
                              read(run/'condition.json'),metadata,code,mode=plan['family_mode'],initial_store={'kind':'empty'})
        if actual != plan['recipe'] or invocation['initial_store_entries'] != []:
            raise ValueError('Prepared inputs/config/code/prompt differ from the exact recipe')
        build = dict(plan['build_run'],state='PREPARED',execution_kind=invocation['execution_kind'],
                     generation_path=run.relative_to(self.root).as_posix())
        create(run/'bank_build.json',{'schema_version':1,'recipe':actual,'build_run':build,
                                     'source_set':plan['source_set'],'sources':plan['sources'],'family':plan['family']})
        self.remember_sources(plan['source_set'])


    def capture_continuation(self, run):
        run=Path(run);resume=read(run/'resume.json')
        _,parent=resolve_run(self.root,resume['parent_run_id'])
        if not (parent/'bank_build.json').exists():
            return
        inherited=read(parent/'bank_build.json')
        source_set=self.source_set(inherited['sources'])
        resolution=self.families.resolve(inherited['sources'])
        if resolution['routing_status'] not in READY:
            raise ValueError('Continuation source routing unresolved')
        config=read(run/'config.json')
        old=config['pipeline'].get('skill_taxonomy_path')
        if old:
            local=run/'taxonomy.yaml';shutil.copyfile(self.families.path(old),local)
            config['pipeline']['skill_taxonomy_path']=str(local);write(run/'config.json',config)
        lineage=[];current=parent;seen=set()
        while True:
            if current.name in seen:raise ValueError('Cyclic continuation')
            seen.add(current.name)
            lineage.append({'run_id':current.name,'manifest_sha256':sha256(current/'artifact_manifest.json'),
                            'execution':read(current/'execution.json')})
            if not (current/'resume.json').exists():break
            _,current=resolve_run(self.root,read(current/'resume.json')['parent_run_id'])
        invocation=read(run/'invocation.json');inputs=read(run/'input_manifest.json')
        metadata={'case_id':invocation['case_id'],'condition_id':invocation['condition_id'],
                  'lab_run_id':resume['pipeline_run_id'],'input_manifest':inputs}
        code={'upstream':{k:v for k,v in read(run/'upstream_before.json').items() if not k.endswith('.bak') and '.bak.' not in k},
              'wrapper':code_inventory(run/'wrapper_snapshot/degradation_lab'),'python':sys.version}
        mode=inherited['recipe']['conditions']['classification']['mode']
        recipe=self._recipe(source_set,resolution,inputs['inputs'],config,read(run/'condition.json'),metadata,code,
            mode=mode,initial_store={'kind':'resume_checkpoint','parent_run_id':resume['parent_run_id'],
                'parent_manifest_sha256':resume['parent_manifest_sha256']},lineage=lineage)
        create(run/'bank_build.json',{'schema_version':1,'recipe':recipe,
            'build_run':dict(build_run(recipe,run.name,parent_run_id=resume['parent_run_id']),state='PREPARED'),
            'source_set':source_set,'sources':inherited['sources'],'family':resolution})

    def _run_recipe(self, generator, *, allow_legacy=False):
        from downstream_eval.integration.skill_freeze import verify_generation
        verified = verify_generation(self.root,generator)
        identity_record, run, result, stages, lineage, active, registry = verified
        status, execution = read(run/'status.json'),read(run/'execution.json')
        if (status.get('state') != 'COMPLETED' or not status.get('real_generation')
                or execution.get('exit_code') != 0 or not execution.get('upstream_unchanged')):
            raise ValueError('Only completed verified real generation can be frozen')
        for parent in lineage:
            _, path = resolve_run(self.root,parent['run_id'])
            invocation = read(path/'invocation.json')
            if not (path/'resume.json').exists() and invocation.get('initial_store_entries') != []:
                raise ValueError('Independent generation did not start from an empty SkillBank')
            parent_sources = {i['source_sha256'] for i in read(path/'input_manifest.json')['inputs']}
            if parent_sources != {i['source_sha256'] for i in read(run/'input_manifest.json')['inputs']}:
                raise ValueError('Lineage source exposure differs from declared SourceSet')
            calls = read(path/'model_calls.json')
            if not calls or not any(c.get('success') and c.get('response_id') for c in calls):
                raise ValueError('Real observed model calls required; fixtures are never formal snapshots')
        inputs = read(run/'input_manifest.json')
        refs = []
        sources_saved = {s['source_id']:s for s in read(run/'sources.json')}
        for item in inputs['inputs']:
            source = sources_saved[item['source_id']]
            known = self.families.by_id.get(item['source_id'])
            if known is None or source['sha256'] != item['source_sha256']:
                raise ValueError('Unregistered/changed generation source')
            refs.append({'source_id':item['source_id'],'sha256':item['source_sha256'],
                         'manifest':known['source_manifest'],'manifest_sha256':known['source_manifest_sha256']})
            if sha256(inside(run,item['path'])) != item['sha256']:
                raise ValueError('Run input changed')
        resolution = self.families.resolve(refs)
        if resolution['routing_status'] not in READY:
            raise ValueError('Unresolved source routing')
        source_set = self.source_set(refs)
        resume = read(run/'resume.json') if (run/'resume.json').exists() else None
        metadata = {'case_id':identity_record['case_id'],'condition_id':identity_record['condition_id'],
                    'lab_run_id':resume['pipeline_run_id'] if resume else run.name,'input_manifest':inputs}
        code = {'upstream':{k:v for k,v in read(run/'upstream_before.json').items()
                            if not k.endswith('.bak') and '.bak.' not in k},
                'wrapper':code_inventory(run/'wrapper_snapshot/degradation_lab'),
                'python':read(run/'invocation.json').get('python','historical-unrecorded')}
        legacy = not (run/'bank_build.json').exists()
        if legacy and not allow_legacy:
            raise ValueError('Historical build needs explicit allow_legacy; never relabel it B1')
        config = read(run/'config.json')
        mode = 'default-control' if legacy else read(run/'bank_build.json')['recipe']['conditions']['classification']['mode']
        if not legacy:
            captured = read(run/'bank_build.json')
            if captured['recipe']['conditions']['generator_code']['python'] != sys.version:
                code['python'] = captured['recipe']['conditions']['generator_code']['python']
        initial = {'kind':'resume_checkpoint','parent_run_id':resume['parent_run_id'],
                   'parent_manifest_sha256':resume['parent_manifest_sha256']} if resume else {'kind':'empty'}
        recipe = self._recipe(source_set,resolution,inputs['inputs'],config,read(run/'condition.json'),metadata,code,
                              mode=mode,initial_store=initial,lineage=lineage[1:],historical=legacy)
        if not legacy and recipe != captured['recipe']:
            raise ValueError('Completed build differs from its captured recipe')
        for skill in active.values():
            if not legacy:
                expected = recipe['conditions']['classification']['runtime_family']
                if any(str(skill.get('metadata',{}).get(k) or '') != v for k,v in expected.items()):
                    raise ValueError('Registered Skill Family metadata differs from recipe')
        return verified, source_set, recipe

    def _freeze_files(self, frozen, *, owned=False):
        frozen = self.path(frozen)
        required = ('skills_manifest.json','skill_freeze.json')
        files = {name:sha256(frozen/name) for name in required}
        if (frozen/'canonical_files.json').exists():
            files['canonical_files.json'] = sha256(frozen/'canonical_files.json')
        files.update({'skills/'+n:h for n,h in full_inventory(frozen/'skills').items()})
        if not (frozen/'skills').is_dir() or not any(n.endswith('/SKILL.md') for n in files):
            raise ValueError('Complete canonical packages required')
        if owned:
            observed=full_inventory(frozen)
            observed.pop('snapshot.json',None)
            if observed!=files:
                raise ValueError('Unlisted file in owned snapshot directory')
        return files

    def seal(self, generator, frozen, *, allow_legacy=False, manifest_output=None):
        verified,sources,recipe = self._run_recipe(generator,allow_legacy=allow_legacy)
        ident,run,_,stages,lineage,active,registry = verified
        frozen = self.path(frozen)
        packages = self._verify_packages(frozen,generator,active=active)
        support_registry = {x['support_id']:x for p in (registry/'supports').glob('*.json') if (x:=read(p))}
        allowed_files = {str(i['execution_path']).replace('\\','/').casefold() for i in read(run/'input_manifest.json')['inputs']}
        documents = {d['doc_id'] for d in stages['ingest']['documents']}
        for p in packages.values():
            for evidence in p['evidence']:
                if (support_registry.get(evidence['support_id']) != evidence or evidence['doc_id'] not in documents
                        or str(evidence['source_file']).replace('\\','/').casefold() not in allowed_files):
                    raise ValueError('Missing/foreign frozen source evidence')
        manifest = read(frozen/'skills_manifest.json')
        if manifest['source_artifact_manifest_sha256'] != sha256(run/'artifact_manifest.json'):
            raise ValueError('Freeze came from a different generation history')
        dependencies = {}
        for sid,item in active.items():
            links = ([item['parent_skill_id']] if item.get('parent_skill_id') else []) + item.get('child_skill_ids',[])
            links += item.get('metadata',{}).get('depends_on',[])
            if any(not isinstance(x,str) or x not in active for x in links):
                raise ValueError('Unclosed Skill dependencies')
            dependencies[sid] = sorted(set(links))
        payload = {'schema_version':1,'state':'FROZEN','evidence_kind':'real_verified_generation',
                   'source_set':sources,'recipe':recipe,
                   'build_run':{'run_id':generator,'generator_case_id':ident['case_id'],
                                'condition_id':ident['condition_id'],'generation_path':run.relative_to(self.root).as_posix(),
                                'lineage':lineage,'state':'VERIFIED','independent_generation':len(lineage)==1},
                   'frozen_root':frozen.relative_to(self.root).as_posix(),
                   'storage_scope':'owned_directory' if manifest_output is None else 'referenced_freeze_unit',
                   'files':self._freeze_files(frozen,owned=manifest_output is None),
                   'packages':{sid:{'version':p['version'],'files':p['files'],'support_ids':p['support_ids'],
                                    'evidence':p['evidence'],'provenance':p['provenance']} for sid,p in packages.items()},
                   'dependencies':dependencies}
        payload['package_set_digest'] = identity('packages',{sid:p['files'] for sid,p in packages.items()})
        snapshot = {'snapshot_id':identity('snapshot',payload),'payload':payload}
        location = self.path(manifest_output) if manifest_output else frozen/'snapshot.json'
        create(location,snapshot)
        self.remember_sources(sources)
        row = {'record_type':'snapshot','snapshot_id':snapshot['snapshot_id'],'recipe_id':recipe['recipe_id'],
               'source_set_id':sources['source_set_id'],'manifest_path':location.relative_to(self.root).as_posix() if location.is_relative_to(self.root) else str(location),
               'generator_run_id':generator,'state':'FROZEN','manifest_sha256':sha256(location)}
        _append(self.index/'bank_registry.v1.jsonl',row,'snapshot_id')
        return snapshot

    def freeze(self, generator, *, allow_legacy=False):
        from downstream_eval.integration.skill_freeze import freeze_generation
        verified,_,_ = self._run_recipe(generator,allow_legacy=allow_legacy)
        ident,run,*_ = verified
        destination = run.parent/'_snapshots'/generator
        freeze_generation(self.root,generator,destination,case_id=ident['case_id'],condition=ident['condition_id'])
        return self.seal(generator,destination,allow_legacy=allow_legacy)

    def _verify_packages(self, frozen, generator, *, active=None):
        manifest,freeze = read(frozen/'skills_manifest.json'),read(frozen/'skill_freeze.json')
        if (manifest['generator_run_id'] != generator or freeze['generator_run_id'] != generator
                or freeze['manifest_sha256'] != sha256(frozen/'skills_manifest.json')
                or freeze['files'] != full_inventory(frozen/'skills')):
            raise ValueError('Frozen package files/manifest/identity changed')
        packages = manifest['packages']
        if not packages or freeze['skill_count'] != len(packages) or (active is not None and set(packages) != set(active)):
            raise ValueError('Frozen package set differs from final registry')
        for sid,p in packages.items():
            checked_id(sid)
            folder = inside(frozen/'skills',sid)
            body = (folder/'SKILL.md').read_text(encoding='utf-8')
            if (full_inventory(folder) != p['files'] or sha256(folder/'SKILL.md') != p['sha256']
                    or not re.search(r'^id: "'+re.escape(sid)+r'"$',body,re.M)
                    or not re.search(r'^version: "'+re.escape(p['version'])+r'"$',body,re.M)):
                raise ValueError('Canonical Skill ID/version/bytes changed: '+sid)
            if not p['evidence'] or {e['support_id'] for e in p['evidence']} != set(p['support_ids']):
                raise ValueError('Missing support provenance')
            if active is not None:
                if (p['version'] != active[sid]['version']
                        or set(p['support_ids']) != set(active[sid]['support_ids'])):
                    raise ValueError('Frozen version/support differs from live registry')
        return packages

    def snapshot(self, snapshot_id):
        candidates = [r for r in self.rows('bank_registry.v1.jsonl') if r['snapshot_id']==snapshot_id]
        if not candidates or any(r != candidates[0] for r in candidates):
            raise ValueError('Snapshot missing or ambiguous')
        row = candidates[0]
        if sha256(self.path(row['manifest_path']))!=row['manifest_sha256']:
            raise ValueError('Snapshot manifest bytes changed')
        snapshot = read(self.path(row['manifest_path'])); payload = snapshot['payload']
        if (snapshot['snapshot_id'] != snapshot_id or identity('snapshot',payload) != snapshot_id
                or payload['state']!='FROZEN' or payload['evidence_kind']!='real_verified_generation'):
            raise ValueError('Snapshot identity/state changed')
        check_recipe(payload['recipe'])
        if (row['recipe_id'] != payload['recipe']['recipe_id']
                or row['source_set_id'] != payload['source_set']['source_set_id']
                or row['generator_run_id'] != payload['build_run']['run_id']):
            raise ValueError('Registry/snapshot identity mismatch')
        for proof in payload['build_run']['lineage']:
            _, origin = resolve_run(self.root,proof['run_id'])
            invocation = read(origin/'invocation.json')
            saved = read(origin/'artifact_manifest.json')
            if (sha256(origin/'artifact_manifest.json') != proof['manifest_sha256']
                    or any(sha256(inside(origin,n))!=h for n,h in saved.items())
                    or invocation.get('execution_kind') != 'official' or not invocation.get('real_generation')):
                raise ValueError('Snapshot real generation provenance changed')
        _, origin = resolve_run(self.root,payload['build_run']['run_id'])
        if (read(origin/'status.json').get('state') != 'COMPLETED'
                or read(origin/'execution.json').get('exit_code') != 0):
            raise ValueError('Snapshot origin is no longer a completed real generation')
        frozen=self.path(payload['frozen_root'])
        if payload['storage_scope'] not in ('owned_directory','referenced_freeze_unit'):
            raise ValueError('Unknown snapshot storage scope')
        if self._freeze_files(frozen,owned=payload['storage_scope']=='owned_directory') != payload['files']:
            raise ValueError('Snapshot file set/hash changed')
        self._verify_packages(frozen,payload['build_run']['run_id'])
        return snapshot

    def find(self, task):
        if (self.root/'configs/datasets/sgb.json').is_file():
            from .sgb import load_registry
            _, registered = load_registry(self.root)
            known = [t for t in registered if t['task_key']==task['task_key']]
            if known and {s['sha256'] for s in known[0]['sources']} != {s['sha256'] for s in task['sources']}:
                return {'decision':'BLOCKED','reason':'REGISTERED_TASK_SOURCE_MISMATCH'}
        resolution=self.families.resolve(task['sources'],task_key=task['task_key'],rule_conflicts=task.get('rule_conflicts',[]))
        if resolution['routing_status'] not in READY:
            return {'decision':'BLOCKED','reason':resolution['routing_status']}
        source_set=self.source_set(task['sources'])
        candidates=[]
        for row in self.rows('bank_registry.v1.jsonl'):
            if row['source_set_id']==source_set['source_set_id']:
                self.snapshot(row['snapshot_id'])
                candidates.append({k:row[k] for k in ('snapshot_id','recipe_id','generator_run_id')})
        return {'decision':'SELECT_RECIPE_AND_SNAPSHOT' if candidates else 'NEED_GENERATION',
                'source_set_id':source_set['source_set_id'],'candidates':candidates,
                'generation_plan':{'backend':'ExperimentRunner','required':['case_id','condition_id','new_run_id','family_mode'],
                                   'initial_store':'empty','partial_overlap_reuse':False},'model_calls':0}

    def lookup(self, task, recipe_id, snapshot_id=None, *, force_generation=False):
        found=self.find(task)
        if found['decision']=='BLOCKED':return found
        if force_generation:
            return {'decision':'NEED_GENERATION','reason':'INDEPENDENT_REPEAT_REQUIRED','recipe_id':recipe_id,'model_calls':0}
        candidates=[r for r in found['candidates'] if r['recipe_id']==recipe_id]
        if snapshot_id:
            candidate=self.snapshot(snapshot_id)
            payload=candidate['payload']
            source_set=self.source_set(task['sources'])
            if payload['source_set']['source_set_id']!=source_set['source_set_id']:
                return {'decision':'BLOCKED','reason':'SOURCE_SET_MISMATCH'}
            if payload['recipe']['recipe_id']!=recipe_id:
                return {'decision':'BLOCKED','reason':'RECIPE_MISMATCH'}
            self._compatible_classification(task,payload)
            return {'decision':'REUSE_FROZEN','snapshot_id':snapshot_id,'recipe_id':recipe_id,
                    'generator_run_id':payload['build_run']['run_id'],'model_calls':0}
        return dict(found,decision='SELECT_SNAPSHOT' if candidates else 'NEED_GENERATION',candidates=candidates,recipe_id=recipe_id)

    def _compatible_classification(self, task, payload):
        current=self.families.resolve(task['sources'],task_key=task['task_key'],rule_conflicts=task.get('rule_conflicts',[]))
        old=payload['recipe']['conditions']['classification']
        if (current['routing_status'] not in READY or old['source_family_id']!=current['primary_family_id']
                or old['assignment_scope']!=current['assignment_scope']
                or old['secondary_family_ids']!=sorted(f for f in current['involved_families'] if f!=current['primary_family_id'])):
            raise ValueError('Family routing/primary mismatch')
        if old['classification_version']!='legacy-unrecorded' and (
                old['classification_version']!=current['classification_version'] or old['catalog_sha256']!=current['catalog_sha256']):
            raise ValueError('Classification version/catalog mismatch')

    def bind(self, task, snapshot_id, *, recipe_id, condition_id, accept_legacy=False, required_scope=None):
        decision=self.lookup(task,recipe_id,snapshot_id)
        if decision['decision']!='REUSE_FROZEN':
            raise ValueError(decision['reason'])
        payload=self.snapshot(snapshot_id)['payload']
        classification=payload['recipe']['conditions']['classification']
        if classification['classification_version']=='legacy-unrecorded' and not accept_legacy:
            raise ValueError('Explicit accept_legacy required; historical snapshots are not B1 Family treatment')
        if payload['build_run']['condition_id']!=condition_id:
            raise ValueError('Condition mismatch')
        if required_scope and classification['assignment_scope']!=required_scope:
            raise ValueError('Assignment scope mismatch')
        data={'schema_version':1,'task_key':task['task_key'],'sources':task['sources'],
              'rule_conflicts':task.get('rule_conflicts',[]),'source_set_id':payload['source_set']['source_set_id'],
              'snapshot_id':snapshot_id,'recipe_id':recipe_id,'condition_id':condition_id,
              'classification_version':classification['classification_version'],
              'accept_legacy':accept_legacy,'assignment_scope':classification['assignment_scope'],
              'generator_run_id':payload['build_run']['run_id'],'generator_case_id':payload['build_run']['generator_case_id'],
              'prompt_context_policy':'consume_recorded_generation_context'}
        binding=dict(data,binding_id=identity('binding',data))
        _append(self.index/'task_bindings.v1.jsonl',binding,'binding_id')
        return binding

    def binding(self, binding_id, *, task_key=None):
        rows=[r for r in self.rows('task_bindings.v1.jsonl') if r['binding_id']==binding_id]
        if not rows or any(r!=rows[0] for r in rows):
            raise ValueError('Binding missing or ambiguous')
        binding=rows[0];body={k:v for k,v in binding.items() if k!='binding_id'}
        if identity('binding',body)!=binding_id or (task_key and binding['task_key']!=task_key):
            raise ValueError('TaskBinding identity mismatch')
        task={'task_key':binding['task_key'],'sources':binding['sources'],'rule_conflicts':binding['rule_conflicts']}
        # For existing SGB consumers, re-read authoritative allowed sources, never trust only a copied binding.
        if (self.root/'configs/datasets/sgb.json').is_file():
            from .sgb import load_registry
            _,tasks=load_registry(self.root)
            selected=[t for t in tasks if t['task_key']==binding['task_key']]
            if selected:task=selected[0]
        choice=self.lookup(task,binding['recipe_id'],binding['snapshot_id'])
        if choice['decision']!='REUSE_FROZEN':
            raise ValueError('Task allowed sources no longer match snapshot')
        payload=self.snapshot(binding['snapshot_id'])['payload']
        if (binding['source_set_id']!=payload['source_set']['source_set_id']
                or binding['generator_run_id']!=payload['build_run']['run_id']
                or binding['generator_case_id']!=payload['build_run']['generator_case_id']
                or binding['condition_id']!=payload['build_run']['condition_id']
                or binding['classification_version']!=payload['recipe']['conditions']['classification']['classification_version']
                or binding['assignment_scope']!=payload['recipe']['conditions']['classification']['assignment_scope']
                or (binding['classification_version']=='legacy-unrecorded' and not binding['accept_legacy'])):
            raise ValueError('Binding condition/classification/provenance mismatch')
        return binding

    def packages(self, binding_id, *, task_key):
        binding=self.binding(binding_id,task_key=task_key)
        payload=self.snapshot(binding['snapshot_id'])['payload']
        frozen=self.path(payload['frozen_root'])
        entries=read(frozen/'skills_manifest.json')['packages']
        return {sid:{'path':frozen/'skills'/sid/'SKILL.md','metadata':p['metadata'],'files':p['files']}
                for sid,p in entries.items()}

    def materialize(self, binding_id, task_key, destination):
        from downstream_eval.integration.skill_install import copy_packages
        binding=self.binding(binding_id,task_key=task_key)
        payload=self.snapshot(binding['snapshot_id'])['payload']
        destination=Path(destination)
        if not destination.resolve().is_relative_to(self.root) and not destination.resolve().is_relative_to(self.index):
            raise ValueError('Consumer output must be inside lab')
        if (destination/'skills').exists() or (destination/'skillbank_reference.json').exists():
            raise FileExistsError('Consumer skills/reference must be new')
        destination.mkdir(parents=True,exist_ok=True)
        copy_packages(self.packages(binding_id,task_key=task_key),destination/'skills')
        frozen=self.path(payload['frozen_root'])
        for name in ('skills_manifest.json','skill_freeze.json'):
            shutil.copyfile(frozen/name,destination/name)
        create(destination/'skillbank_reference.json',binding)
        return read(destination/'skills_manifest.json')['packages']


def verify_consumption(root, output, *, task_key=None):
    output=Path(output)
    ref=read(output/'skillbank_reference.json')
    manager=SkillBank(root)
    binding=manager.binding(ref['binding_id'],task_key=task_key)
    if binding!=ref:
        raise ValueError('Frozen consumer binding differs from registry')
    snapshot=manager.snapshot(binding['snapshot_id'])['payload']
    if any(sha256(output/name)!=snapshot['files'][name] for name in ('skills_manifest.json','skill_freeze.json')):
        raise ValueError('Consumer frozen manifest bytes changed')
    if full_inventory(output/'skills')!=read(manager.path(snapshot['frozen_root'])/'skill_freeze.json')['files']:
        raise ValueError('Consumer installed package bytes changed')
    return binding


def main(root=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',default=str(root or Path(__file__).resolve().parents[2]))
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('validate')
    for name in ('find','plan','lookup','bind'):
        command=sub.add_parser(name)
        task=command.add_mutually_exclusive_group(required=True)
        task.add_argument('--task');task.add_argument('--task-json')
        if name=='plan':
            command.add_argument('--case',required=True);command.add_argument('--condition',default='clean')
            command.add_argument('--run-id',required=True)
            command.add_argument('--family-mode',choices=('classified','default-control'),required=True)
            command.add_argument('--output')
            command.add_argument('--force-generation',action='store_true')
        if name in ('lookup','bind'):
            command.add_argument('--recipe-id',required=True)
            command.add_argument('--snapshot-id',required=name=='bind')
        if name=='bind':
            command.add_argument('--condition',required=True)
            command.add_argument('--accept-legacy',action='store_true')
            command.add_argument('--required-scope',choices=('family_batch','primary_batch'))
    freeze=sub.add_parser('freeze');freeze.add_argument('--generator-run',required=True)
    freeze.add_argument('--allow-legacy',action='store_true')
    adopt=sub.add_parser('adopt-legacy')
    adopt.add_argument('--generator-run',required=True);adopt.add_argument('--frozen',required=True)
    adopt.add_argument('--output',required=True)
    verify=sub.add_parser('verify');verify.add_argument('--snapshot-id',required=True)
    args=parser.parse_args()
    try:
        bank=SkillBank(args.root)
        if args.command=='validate':
            for row in bank.rows('source_sets.v1.jsonl'):
                hashes=row['content_sha256']
                if (not hashes or hashes!=sorted(set(hashes)) or any(not re.fullmatch(r'[0-9a-f]{64}',h) for h in hashes)
                        or row['source_set_id']!=identity('sources',{'schema_version':1,'content_sha256':hashes})):
                    raise ValueError('SourceSet index drift')
                for ref in row['aliases']:
                    if ref['sha256'] not in hashes:raise ValueError('Foreign SourceSet alias')
                    bank.families.admitted(ref)
            snapshots={r['snapshot_id'] for r in bank.rows('bank_registry.v1.jsonl')}
            bindings={r['binding_id'] for r in bank.rows('task_bindings.v1.jsonl')}
            for sid in snapshots:bank.snapshot(sid)
            for bid in bindings:bank.binding(bid)
            result={'status':'PASS','source_sets':len({r['source_set_id'] for r in bank.rows('source_sets.v1.jsonl')}),
                    'snapshots':len(snapshots),'bindings':len(bindings),'model_calls':0}
        elif args.command=='freeze':
            snap=bank.freeze(args.generator_run,allow_legacy=args.allow_legacy)
            result={'status':'FROZEN','snapshot_id':snap['snapshot_id'],'recipe_id':snap['payload']['recipe']['recipe_id']}
        elif args.command=='adopt-legacy':
            snap=bank.seal(args.generator_run,bank.path(args.frozen),allow_legacy=True,manifest_output=args.output)
            result={'status':'FROZEN_REFERENCE','snapshot_id':snap['snapshot_id'],
                    'recipe_id':snap['payload']['recipe']['recipe_id']}
        elif args.command=='verify':
            snap=bank.snapshot(args.snapshot_id)
            result={'status':'PASS','snapshot_id':snap['snapshot_id'],'recipe_id':snap['payload']['recipe']['recipe_id'],
                    'generator_run_id':snap['payload']['build_run']['run_id'],'model_calls':0}
        else:
            task=bank.families.registered_task(args.task) if args.task else read(Path(args.task_json))
            if args.command=='find':result=bank.find(task)
            elif args.command=='plan':
                result=bank.plan(task,args.case,args.condition,args.run_id,family_mode=args.family_mode,
                                 force_generation=args.force_generation)
                if args.output:create(Path(args.output),result)
            elif args.command=='lookup':result=bank.lookup(task,args.recipe_id,args.snapshot_id)
            else:result=bank.bind(task,args.snapshot_id,recipe_id=args.recipe_id,condition_id=args.condition,
                                  accept_legacy=args.accept_legacy,required_scope=args.required_scope)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 2 if result.get('decision')=='BLOCKED' else 0
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(json.dumps({'decision':'BLOCKED','reason':str(error)},ensure_ascii=False),file=sys.stderr)
        return 2
