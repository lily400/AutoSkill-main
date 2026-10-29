"""Versioned source-based Family classification; no generation or SkillBank operations."""
import argparse
import copy
from datetime import datetime, timezone
import inspect
import json
from pathlib import Path
import re
import sys

from .catalog import SourceManager
from .io import inside, read, resolve_upstream, sha256
from .runner import ExperimentRunner, validate_config
from .schema import check
from .sgb import load_registry

CATALOG = 'configs/sgb/b1/family_catalog.v1.json'
POLICY = 'configs/sgb/b1/family_profile_policy.v1.json'
SOURCES = 'data/manifests/sgb/b1/source_family_map.v1.jsonl'
TASKS = 'data/manifests/sgb/b1/task_family_map.v1.jsonl'
READY = {'READY', 'READY_PRIMARY_BATCH'}
STATUSES = {'APPROVED', 'CLASSIFICATION_REQUIRED', 'ROUTING_REQUIRED'}
SCOPES = {'family_batch', 'primary_batch', 'unresolved'}


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def create(path, value, *, lines=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        if lines:
            for item in value:
                stream.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + '\n')
        else:
            stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    return path


def key(value):
    return re.sub(r'[\s_-]+', '', value.strip().casefold())


def validate_catalog(catalog):
    if catalog.get('schema_version') != 1:
        raise ValueError('Unsupported catalog schema')
    version = catalog.get('classification_version', '')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', version):
        raise ValueError('Invalid classification_version')
    domains, families, labels = {}, {}, {}
    for domain in catalog['domains']:
        did = domain['domain_id']
        if not re.fullmatch(r'[a-z][a-z0-9-]*', did) or did in domains or not domain['domain_name'].strip():
            raise ValueError('Invalid/duplicate Domain: ' + did)
        domains[did] = domain
    for family in catalog['families']:
        fid = family['family_id']
        if not re.fullmatch(r'[a-z][a-z0-9-]*', fid) or fid in families:
            raise ValueError('Invalid/duplicate Family ID: ' + fid)
        if family['domain_id'] not in domains:
            raise ValueError('Unknown Domain: ' + family['domain_id'])
        for field in ('family_name', 'knowledge_scope', 'applicability_boundary'):
            if not isinstance(family[field], str) or not family[field].strip():
                raise ValueError('Missing Family ' + field)
        if not isinstance(family['aliases'], list) or any(not isinstance(x, str) or not x.strip() for x in family['aliases']):
            raise ValueError('Invalid aliases: ' + fid)
        for label in [fid, family['family_name'], *family['aliases']]:
            normalized = key(label)
            if normalized in labels and labels[normalized] != fid:
                raise ValueError('Ambiguous Family label: ' + label)
            labels[normalized] = fid
        families[fid] = family
    if not domains or not families:
        raise ValueError('Catalog must contain Domains and Families')
    return families


class FamilyRegistry:
    def __init__(self, root, *, catalog=CATALOG, source_map=SOURCES, policy=POLICY):
        self.root = Path(root).resolve()
        self.catalog_path, self.source_map_path = self.path(catalog), self.path(source_map)
        self.catalog, self.policy = read(self.catalog_path), read(self.path(policy))
        self.families = validate_catalog(self.catalog)
        self.catalog_hash = sha256(self.catalog_path)
        if (self.policy.get('schema_version') != 1
                or self.policy.get('profile_rule') != 'taxonomy.derive_profile_id'
                or self.policy.get('max_runtime_candidates') != 1):
            raise ValueError('Unsupported Family profile policy')
        self.version = self.catalog['classification_version']
        self.rows = jsonl(self.source_map_path)
        self.by_id, self.by_hash = {}, {}
        for row in self.rows:
            self.validate_assignment(row)
            sid, digest = row['source_id'], row['source_sha256']
            if sid in self.by_id:
                raise ValueError('Duplicate source_id: ' + sid)
            prior = self.by_hash.get(digest)
            if prior and self.assignment(prior) != self.assignment(row):
                raise ValueError('Same content has inconsistent Family assignment: ' + digest)
            self.by_id[sid] = row
            self.by_hash[digest] = row
        self._manager = None

    def path(self, value):
        value = Path(value)
        return value.resolve() if value.is_absolute() else inside(self.root, value)

    @staticmethod
    def assignment(row):
        return {field: row[field] for field in ('primary_family_id', 'secondary_family_ids',
                                                'assignment_scope', 'mixed', 'status')}

    def validate_assignment(self, row):
        if row['classification_version'] != self.version or row['catalog_sha256'] != self.catalog_hash:
            raise ValueError('Source mapping classification_version mismatch')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', row['source_id']):
            raise ValueError('Invalid source_id')
        if not re.fullmatch(r'[0-9a-f]{64}', row['source_sha256']):
            raise ValueError('Invalid source_sha256')
        primary, secondary = row['primary_family_id'], row['secondary_family_ids']
        if primary is not None and primary not in self.families:
            raise ValueError('Unknown primary Family: ' + str(primary))
        if (not isinstance(secondary, list) or len(set(secondary)) != len(secondary)
                or primary in secondary or any(f not in self.families for f in secondary)):
            raise ValueError('Invalid secondary Families')
        if type(row['mixed']) is not bool or row['mixed'] != bool(secondary):
            raise ValueError('mixed must agree with secondary Families')
        if row['status'] not in STATUSES or row['assignment_scope'] not in SCOPES:
            raise ValueError('Invalid assignment status/scope')
        if row['status'] == 'APPROVED':
            expected = 'primary_batch' if secondary else 'family_batch'
            if primary is None or row['assignment_scope'] != expected:
                raise ValueError('Approved assignment needs a valid primary and batch scope')
        elif row['assignment_scope'] != 'unresolved':
            raise ValueError('Pending assignments require unresolved scope')
        if not row['evidence_reference'] or not row['source_manifest']:
            raise ValueError('Source registration and classification evidence required')

    def admitted(self, reference):
        """Reuse source admission checks independently of the pinned SGB task count."""
        if self._manager is None:
            self._manager = SourceManager(self.root)
        manifest = self.path(reference['manifest'])
        source = check('source', read(manifest))
        if reference.get('manifest_sha256') and sha256(manifest) != reference['manifest_sha256']:
            raise ValueError('Source manifest drift')
        self._manager.verify(source)
        if source['source_id'] != reference['source_id'] or source['sha256'] != reference['sha256']:
            raise ValueError('Source reference identity/hash mismatch')
        return source

    def validate(self):
        evidence_hashes = {}
        for row in self.rows:
            self.admitted({'source_id': row['source_id'], 'sha256': row['source_sha256'],
                           'manifest': row['source_manifest'],
                           'manifest_sha256': row['source_manifest_sha256']})
            for evidence in row['evidence_reference']:
                path = self.path(evidence['path'])
                digest = evidence_hashes.setdefault(str(path), sha256(path))
                if digest != evidence['sha256']:
                    raise ValueError('Classification evidence drift: ' + str(path))
        return {'status': 'PASS', 'classification_version': self.version,
                'domains': len(self.catalog['domains']), 'families': len(self.families),
                'source_aliases': len(self.rows), 'unique_source_contents': len(self.by_hash),
                'pending_sources': sum(r['status'] != 'APPROVED' for r in self.by_hash.values())}

    def resolve(self, sources, *, task_key=None, rule_conflicts=()):
        result = {'classification_version': self.version, 'catalog_sha256': self.catalog_hash, 'task_key': task_key,
                  'source_set': sorted({s['sha256'] for s in sources}),
                  'source_ids': [s['source_id'] for s in sources],
                  'involved_families': [], 'primary_family_id': None,
                  'assignment_scope': 'unresolved', 'mixed': False}
        if not sources:
            return dict(result, routing_status='SOURCE_PENDING', reasons=['No admitted source documents'])
        if len(result['source_ids']) != len(set(result['source_ids'])):
            raise ValueError('Duplicate source_id in task inputs')
        assignments, unknown = [], []
        for source in sources:
            self.admitted(source)
            if source['source_id'] in self.by_id and self.by_id[source['source_id']]['source_sha256'] != source['sha256']:
                raise ValueError('Registered source_id changed content')
            assignment = self.by_hash.get(source['sha256'])
            if assignment is None or assignment['status'] == 'CLASSIFICATION_REQUIRED':
                unknown.append(source['sha256'])
            elif assignment['status'] == 'ROUTING_REQUIRED':
                return dict(result, routing_status='ROUTING_REQUIRED', reasons=['Source review requires routing'])
            else:
                assignments.append(assignment)
        involved = {f for a in assignments for f in [a['primary_family_id'], *a['secondary_family_ids']]}
        result['involved_families'] = sorted(involved)
        if unknown:
            return dict(result, routing_status='CLASSIFICATION_REQUIRED', reasons=['Unreviewed source content'],
                        unclassified_source_sha256=sorted(set(unknown)))
        primary = {a['primary_family_id'] for a in assignments}
        if len(primary) != 1 or rule_conflicts:
            return dict(result, routing_status='ROUTING_REQUIRED',
                        reasons=['Multiple primary Families or declared rule conflicts'], rule_conflicts=list(rule_conflicts))
        mixed = any(a['mixed'] for a in assignments)
        return dict(result, primary_family_id=next(iter(primary)), mixed=mixed,
                    assignment_scope='primary_batch' if mixed else 'family_batch',
                    routing_status='READY_PRIMARY_BATCH' if mixed else 'READY', reasons=[])

    def registered_task(self, task):
        _, rows = load_registry(self.root)
        matches = [r for r in rows if task in (r['task_key'], r['original_task_id'])]
        if len(matches) != 1:
            raise ValueError('Unknown/ambiguous registered task; use --task-json for new tasks')
        return matches[0]

    def task_map(self):
        _, tasks = load_registry(self.root)
        return [self.resolve(t['sources'], task_key=t['task_key']) for t in tasks]

    def register_source(self, manifest, *, family_id=None, secondary=(), evidence, reviewer, note):
        path = self.path(manifest)
        source = check('source', read(path))
        self.admitted({'source_id': source['source_id'], 'sha256': source['sha256'], 'manifest': str(path)})
        prior = self.by_hash.get(source['sha256'])
        if family_id is None and prior:
            assignment = self.assignment(prior)
        elif family_id is None:
            return {'routing_status': 'CLASSIFICATION_REQUIRED', 'source_sha256': source['sha256'],
                    'reason': 'Review a known Family or extend the catalog in a new version; nothing written'}
        else:
            assignment = {'primary_family_id': family_id, 'secondary_family_ids': sorted(secondary),
                          'assignment_scope': 'primary_batch' if secondary else 'family_batch',
                          'mixed': bool(secondary), 'status': 'APPROVED'}
        evidence_path = self.path(evidence)
        if not reviewer.strip() or not note.strip():
            raise ValueError('Explicit reviewer and source-based review note required')
        row = dict(assignment, classification_version=self.version, catalog_sha256=self.catalog_hash, source_id=source['source_id'],
                   source_sha256=source['sha256'], source_manifest=str(path),
                   source_manifest_sha256=sha256(path),
                   evidence_reference=[{'path': str(evidence_path), 'sha256': sha256(evidence_path)}],
                   review={'reviewer': reviewer, 'note': note, 'at': datetime.now(timezone.utc).isoformat()})
        self.validate_assignment(row)
        if source['source_id'] in self.by_id and self.by_id[source['source_id']]['source_sha256'] != source['sha256']:
            raise ValueError('Registered source_id changed content')
        if prior and self.assignment(prior) != assignment:
            raise ValueError('Content already classified differently; requires a new reviewed classification version')
        if source['source_id'] in self.by_id:
            return {'status': 'ALREADY_REGISTERED', 'source_id': source['source_id']}
        # Append only; never rewrite an existing classification decision.
        with self.source_map_path.open('a', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
        self.rows.append(row); self.by_id[row['source_id']] = row; self.by_hash[row['source_sha256']] = row
        return {'status': 'REGISTERED', 'source_id': source['source_id'], 'classification_version': self.version}

    def extend(self, proposal, catalog_output, source_output):
        proposal = read(self.path(proposal))
        updated = copy.deepcopy(self.catalog)
        version = proposal['classification_version']
        if version == self.version:
            raise ValueError('A new classification_version is required')
        updated.update(classification_version=version, parent_classification_version=self.version)
        updated['domains'].extend(proposal.get('domains', []))
        updated['families'].extend(proposal['families'])
        validate_catalog(updated)
        outputs = [self.path(catalog_output), self.path(source_output)]
        if any(p.exists() for p in outputs) or outputs[0] == outputs[1]:
            raise FileExistsError('New version outputs must be distinct and must not exist')
        create(outputs[0], updated)
        inherited = [dict(row, classification_version=version, catalog_sha256=sha256(outputs[0])) for row in self.rows]
        create(outputs[1], inherited, lines=True)
        return {'status': 'EXTENDED', 'classification_version': version,
                'catalog': str(outputs[0]), 'source_map': str(outputs[1])}

    def upstream(self):
        source = resolve_upstream(self.root)
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
        from AutoSkill4Doc.taxonomy import load_skill_taxonomy
        return load_skill_taxonomy

    def runtime(self, config, resolution, output, *, mode='classified'):
        if (resolution['classification_version'] != self.version or resolution.get('catalog_sha256') != self.catalog_hash
                or resolution['routing_status'] not in READY):
            raise ValueError('Family not ready: ' + resolution['routing_status'])
        validate_config(config)
        load_taxonomy = self.upstream()
        pipeline = config['pipeline']
        domain = str(pipeline.get('domain_type') or pipeline.get('domain') or '')
        original = pipeline.get('skill_taxonomy_path', '')
        base = load_taxonomy(domain_type=domain, taxonomy_path=str(self.path(original)) if original else '')
        payload = base.to_dict()
        family = self.families[resolution['primary_family_id']]
        if mode == 'classified':
            payload['family_candidates'] = [{'id': family['family_id'], 'name': family['family_name'],
                                             'visible_name': family['family_name'], 'aliases': family['aliases'],
                                             'keywords': []}]
            payload['default_family_name'] = family['family_name']
            profile = base.derive_profile_id(family_name=family['family_name'])
        elif mode == 'default-control':
            if (base.family_candidates or base.default_family_name != self.policy['default_control']['family_name']
                    or pipeline.get('family_name') or pipeline.get('profile_id')):
                raise ValueError('Default control requires the unchanged legacy empty-candidate baseline')
            profile = base.derive_profile_id(family_name=base.default_family_name)
        else:
            raise ValueError('Unknown runtime mode')
        output = self.path(output)
        if output.exists():
            raise FileExistsError('Runtime output must be a new directory')
        output.mkdir(parents=True)
        taxonomy_path = create(output/'taxonomy.yaml', payload)
        runtime = copy.deepcopy(config)
        runtime['pipeline']['skill_taxonomy_path'] = str(taxonomy_path)
        if mode == 'classified':
            runtime['pipeline'].update(family_name=family['family_name'], profile_id=profile)
        try:
            checked = self.check_runtime(runtime, resolution, mode=mode, base=base)
        except Exception:
            taxonomy_path.unlink()
            output.rmdir()
            raise
        config_path = create(output/'generation_config.json', runtime)
        return dict(checked, taxonomy_path=str(taxonomy_path), generation_config=str(config_path))

    def check_runtime(self, config, resolution, *, mode='classified', base=None):
        if (resolution['classification_version'] != self.version or resolution.get('catalog_sha256') != self.catalog_hash
                or resolution['routing_status'] not in READY):
            raise ValueError('Cannot configure an unresolved Family')
        validate_config(config)
        load_taxonomy = self.upstream()
        from AutoSkill4Doc.extract import extract_from_doc, _resolve_taxonomy_context
        from AutoSkill4Doc.family_resolver import DocumentFamilyResolver
        from AutoSkill4Doc.pipeline import DocumentBuildPipeline
        pipeline = config['pipeline']
        if set(pipeline) - set(inspect.signature(extract_from_doc).parameters):
            raise ValueError('Unsupported public extract_from_doc option')
        path = pipeline.get('skill_taxonomy_path')
        if not path or not self.path(path).is_file():
            raise ValueError('Missing runtime taxonomy; no default fallback allowed')
        taxonomy, name, _, profile = _resolve_taxonomy_context(
            domain=pipeline.get('domain', ''), domain_type=pipeline.get('domain_type', ''),
            skill_taxonomy_path=str(self.path(path)), family_name=pipeline.get('family_name', ''),
            profile_id=pipeline.get('profile_id', ''))
        fid = resolution['primary_family_id']
        family = self.families[fid]
        if mode == 'classified':
            candidate = taxonomy.resolve_family_candidate(requested=name)
            expected_profile = taxonomy.derive_profile_id(family_name=family['family_name'])
            if (len(taxonomy.family_candidates) != 1 or not candidate or candidate['id'] != fid
                    or name != family['family_name'] or profile != expected_profile
                    or taxonomy.default_family_name != family['family_name']
                    or candidate.get('aliases') != family['aliases'] or candidate.get('keywords')):
                raise ValueError('family_id/name/profile_id inconsistent with selected taxonomy')
            expected = {'family_id': fid, 'family_name': name, 'profile_id': profile}
        elif mode == 'default-control':
            if (taxonomy.family_candidates or pipeline.get('family_name') or pipeline.get('profile_id')
                    or taxonomy.default_family_name != self.policy['default_control']['family_name']):
                raise ValueError('Not an explicit legacy default control')
            expected = {'family_id': '', 'family_name': taxonomy.default_family_name,
                        'profile_id': taxonomy.derive_profile_id(family_name=taxonomy.default_family_name)}
        else:
            raise ValueError('Unknown runtime mode')
        # Replace all generation stages with inert objects. Only the actual metadata resolver runs.
        resolver = DocumentFamilyResolver(taxonomy=taxonomy, llm=None)
        plan = DocumentBuildPipeline(registry=None, taxonomy=taxonomy, family_resolver=resolver,
            document_ingestor=object(), document_skill_extractor=object(), skill_compiler=object())
        metadata = {'domain_type': taxonomy.domain_type}
        if name: metadata['family_name'] = name
        if profile: metadata['profile_id'] = profile
        resolved = plan.resolve_run_metadata(documents=[], metadata=metadata)
        if any(str(resolved.get(k) or '') != v for k, v in expected.items()):
            raise ValueError('Batch resolution changed Family metadata')
        if base:
            for field, value in base.to_dict().items():
                if field not in ('family_candidates', 'default_family_name') and taxonomy.to_dict()[field] != value:
                    raise ValueError('Family config changed independent taxonomy field: ' + field)
        return {'status': 'VALID', 'mode': mode, 'classification_version': self.version, 'catalog_sha256': self.catalog_hash,
                **expected, 'assignment_scope': resolution['assignment_scope'],
                'taxonomy_id': taxonomy.taxonomy_id, 'domain_type': taxonomy.domain_type,
                'model_calls': 0}


def main(root=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(root or Path(__file__).resolve().parents[2]))
    parser.add_argument('--catalog', default=CATALOG)
    parser.add_argument('--source-map', default=SOURCES)
    parser.add_argument('--policy', default=POLICY)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    derive = sub.add_parser('derive-tasks'); derive.add_argument('--output', required=True)
    for name in ('resolve', 'register-task', 'materialize', 'check-runtime'):
        command = sub.add_parser(name)
        target = command.add_mutually_exclusive_group(required=True)
        target.add_argument('--task'); target.add_argument('--task-json')
        if name in ('materialize', 'check-runtime'):
            source = command.add_mutually_exclusive_group(required=True)
            source.add_argument('--case'); source.add_argument('--generation-config')
            command.add_argument('--condition', default='clean')
            command.add_argument('--mode', choices=('classified', 'default-control'), default='classified')
        if name in ('materialize', 'register-task'): command.add_argument('--output', required=True)
    register = sub.add_parser('register-source')
    register.add_argument('--source-manifest', required=True); register.add_argument('--family')
    register.add_argument('--secondary', action='append', default=[])
    register.add_argument('--evidence', required=True); register.add_argument('--reviewer', required=True)
    register.add_argument('--note', required=True)
    extend = sub.add_parser('extend-catalog')
    extend.add_argument('--proposal', required=True); extend.add_argument('--output-catalog', required=True)
    extend.add_argument('--output-sources', required=True)
    args = parser.parse_args()
    try:
        registry = FamilyRegistry(args.root, catalog=args.catalog, source_map=args.source_map, policy=args.policy)
        if args.command == 'validate':
            result = registry.validate()
            actual = registry.task_map() if (registry.root/'configs/datasets/sgb.json').is_file() else []
            if actual and registry.catalog_path == registry.path(CATALOG) and registry.source_map_path == registry.path(SOURCES):
                if read(registry.path(POLICY))['initial_registry_sha256'] != sha256(registry.root/'data/manifests/sgb/tasks.jsonl'):
                    raise ValueError('Initial SGB registry drift')
                if jsonl(registry.path(TASKS)) != actual:
                    raise ValueError('Derived task mapping drift')
            result['task_routing'] = {status: sum(r['routing_status'] == status for r in actual)
                                      for status in sorted({r['routing_status'] for r in actual})}
        elif args.command == 'derive-tasks':
            rows = registry.task_map(); create(registry.path(args.output), rows, lines=True)
            result = {'status': 'CREATED', 'tasks': len(rows), 'output': args.output}
        elif args.command == 'register-source':
            result = registry.register_source(args.source_manifest, family_id=args.family, secondary=args.secondary,
                evidence=args.evidence, reviewer=args.reviewer, note=args.note)
        elif args.command == 'extend-catalog':
            result = registry.extend(args.proposal, args.output_catalog, args.output_sources)
        else:
            task = registry.registered_task(args.task) if args.task else read(registry.path(args.task_json))
            result = registry.resolve(task['sources'], task_key=task['task_key'], rule_conflicts=task.get('rule_conflicts', []))
            if args.command == 'register-task':
                create(registry.path(args.output), result)
            elif args.command != 'resolve':
                if result['routing_status'] not in READY:
                    print(json.dumps(result, ensure_ascii=False, indent=2)); return 2
                if args.case:
                    _, _, manifest, config = ExperimentRunner(registry.root).resolve(args.case, args.condition)
                    if {i['source_sha256'] for i in manifest['inputs']} != set(result['source_set']):
                        raise ValueError('Case allowed source contents differ from requested task')
                else:
                    config = read(registry.path(args.generation_config))
                result = (registry.runtime(config, result, args.output, mode=args.mode)
                          if args.command == 'materialize'
                          else registry.check_runtime(config, result, mode=args.mode))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('routing_status', 'READY') in READY else 2
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({'status': 'ERROR', 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
