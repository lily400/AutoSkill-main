"""Pinned SkillGenBench import and static audit. Never imports or executes a task."""
import ast
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


from .io import inside, inventory, read, sha256, utc, write
from .schema import check

REVISION = '5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d'
TYPES = ('code_repo', 'code_doc', 'domain_knowledge_doc')
REPOSITORY = 'https://github.com/QuantaAlpha/SkillGenBench'
REGISTRY = 'data/manifests/sgb/tasks.jsonl'
CONFIG = 'configs/datasets/sgb.json'


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def descriptor(path):
    """Accept only the release's trailing commas; never rewrite quoted strings."""
    text = Path(path).read_text(encoding='utf-8-sig')
    output = []; quoted = escaped = False; removed = 0
    for i, char in enumerate(text):
        if quoted:
            output.append(char)
            if escaped: escaped = False
            elif char == '\\': escaped = True
            elif char == '"': quoted = False
        elif char == '"':
            quoted = True; output.append(char)
        elif char == ',' and text[i+1:].lstrip().startswith(('}', ']')):
            removed += 1
        else:
            output.append(char)
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value: raise ValueError('Duplicate descriptor key: ' + key)
            value[key] = item
        return value
    return json.loads(''.join(output), object_pairs_hook=pairs), removed


def freeze_snapshot(snapshot, destination):
    snapshot, destination = Path(snapshot).resolve(), Path(destination)
    def git(*args):
        return subprocess.run(['git', '-C', str(snapshot), *args], capture_output=True, check=True).stdout
    if git('rev-parse', 'HEAD').decode().strip() != REVISION:
        raise ValueError('Unexpected SGB revision')
    git('diff', '--quiet', 'HEAD', '--')
    names = git('ls-files', '-z').decode('utf-8').split('\0')
    files = {}
    for name in filter(None, names):
        source = inside(snapshot, name)
        if (snapshot/name).is_symlink() or not source.is_file():
            raise ValueError('Snapshot must contain regular tracked files: ' + name)
        files[name] = sha256(source)
    manifest = destination/'snapshot_manifest.json'
    if destination.exists():
        saved = read(manifest)
        if saved['revision'] != REVISION or saved['files'] != files:
            raise ValueError('Existing SGB snapshot differs; refusing overwrite')
        if inventory(destination) != {**files, 'snapshot_manifest.json':sha256(manifest)}:
            raise ValueError('Frozen SGB snapshot drift')
        return saved
    destination.mkdir(parents=True)
    for name, digest in files.items():
        target = inside(destination, name); target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(snapshot/name, target)
        if sha256(target) != digest: raise ValueError('Snapshot changed during copy: ' + name)
    value = {'revision':REVISION, 'repository':REPOSITORY, 'files':files}
    write(manifest, value)
    return value


def _source(root, snapshot, file):
    origin = file.relative_to(snapshot).as_posix()
    digest = sha256(file); sid = 'sgb-' + identity(origin)[:16]
    local = f'data/raw_sources/sgb/{REVISION[:8]}/{digest[:16]}/{file.name}'
    target = inside(root, local)
    if target.exists():
        if sha256(target) != digest: raise ValueError('Source cache drift: ' + local)
    else:
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(file, target)
    manifest = {'source_id':sid, 'source_url':REPOSITORY.replace('github.com', 'raw.githubusercontent.com')+'/'+REVISION+'/'+origin,
        'source_repository':REPOSITORY, 'source_commit':REVISION, 'source_path':origin,
        'license':'SGB README License TBD; original material license unverified', 'downloaded_at':utc(),
        'sha256':digest, 'bytes':file.stat().st_size, 'document_type':'task_curated_release_text',
        'classification':'PUBLISHED_DATASET_SNAPSHOT', 'paper_snapshot_verified':False, 'local_path':local,
        'variant':'clean', 'transform':None}
    check('source', manifest)
    name = f'data/manifests/sgb/sources/{sid}.json'
    write(inside(root, name), manifest)
    return {'source_id':sid, 'manifest':name, 'manifest_sha256':sha256(root/name),
            'path':local, 'sha256':digest, 'origin':origin}


def _legacy(root, matrix, mapping, audit):
    rows = {}; links = {}
    for source, name, target in ((matrix, 'admission.csv', rows), (mapping, 'rule_map.csv', links)):
        if source is None: continue
        destination = audit/'legacy'/name; destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        with destination.open(encoding='utf-8-sig', newline='') as stream:
            for row in csv.DictReader(stream):
                target[row['task_id']] = {'row':row, 'evidence':destination.relative_to(root).as_posix(),
                                          'sha256':sha256(destination)}
    return rows, links


def import_snapshot(root, snapshot, audit_id, matrix=None, mapping=None):
    root = Path(root).resolve()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',audit_id):raise ValueError('Unsafe audit ID')
    audit = inside(root, 'results/sgb/audits/'+audit_id)
    if (root/CONFIG).exists() or audit.exists():
        raise FileExistsError('SGB already imported or audit ID exists; use sgb audit to verify')
    frozen = inside(root, '.external/skillgenbench/'+REVISION[:8])
    freeze_snapshot(snapshot, frozen)
    audit.mkdir(parents=True)
    prior, links = _legacy(root, matrix, mapping, audit)
    rows = []; source_names = set()
    for task_file in sorted(frozen.glob('skill_evaluation/*/*/*/task.toml')):
        kind, collection, task_id = task_file.relative_to(frozen/'skill_evaluation').parts[:3]
        if kind not in TYPES: raise ValueError('Unknown source type')
        task = tomllib.loads(task_file.read_text(encoding='utf-8'))
        key = 't-' + identity([kind, collection, task_id])[:12]
        source_dir = frozen/'data_source'/kind/collection/'tasks'/task_id
        parsed, removed = descriptor(source_dir/'task.json')
        conflicts = []
        comparisons = {'task_id':task_id, 'source':kind, 'collection_slug':collection,
            'submission_kind':task['submission']['kind'], 'submission_target_file':task['submission'].get('target_file',''),
            'expected_output_file':task.get('expected',{}).get('output_file','')}
        for field, expected in comparisons.items():
            if parsed.get(field) != expected:
                conflicts.append({'field':field, 'descriptor':parsed.get(field), 'task_toml':expected})
        inputs = []; excluded = []
        for file in sorted((source_dir/'materials/docs').rglob('*')):
            if not file.is_file(): continue
            reason = None
            if file.suffix.lower() not in ('.md', '.rst', '.txt', '.html'):
                reason = 'not_approved_narrative_text'
            else:
                try:
                    if not file.read_text(encoding='utf-8').strip(): reason = 'empty_text'
                except UnicodeDecodeError: reason = 'not_utf8'
            if reason:
                excluded.append({'path':file.relative_to(frozen).as_posix(), 'reason':reason})
            else:
                item = _source(root, frozen, file); inputs.append(item); source_names.add(item['manifest'])
        test_files = sorted((task_file.parent/'tests').rglob('*'))
        syntax_errors = []
        for file in test_files:
            if file.is_file() and file.suffix == '.py':
                try: ast.parse(file.read_text(encoding='utf-8-sig'), filename=file.name)
                except (SyntaxError, UnicodeDecodeError) as error:
                    syntax_errors.append({'path':file.relative_to(frozen).as_posix(), 'error':str(error)})
        previous = prior.get(task_id); rule = links.get(task_id)
        research = previous['row']['current_admission_status'] if previous else 'PENDING_RULE_TASK_ORACLE_REVIEW'
        prior_hashes = json.loads(previous['row']['document_sha256']) if previous else {}
        evidence_matches = all((frozen/name).is_file() and sha256(frozen/name)==h for name,h in prior_hashes.items())
        if previous and not evidence_matches: research = 'STALE_PRIOR_EVIDENCE'
        files = [source_dir/'task.json', source_dir/'instruction.md', source_dir/'source.toml', task_file]
        files += [p for p in task_file.parent.rglob('*') if p.is_file() and p != task_file]
        assets = {p.relative_to(frozen).as_posix():sha256(p) for p in files if p.is_file()}
        bundle = 'b-' + identity([(i['origin'].split('/materials/docs/',1)[-1], i['sha256']) for i in inputs])[:16] if inputs else None
        row = {'schema_version':1, 'dataset_id':'skillgenbench', 'dataset_revision':REVISION,
            'source_type':kind, 'collection':collection, 'original_task_id':task_id, 'task_key':key,
            'source_bundle_id':bundle, 'sources':inputs, 'excluded_source_files':excluded,
            'generation_scope':'source_only_task_curated', 'generator_input_kind':'documents' if inputs else 'unresolved',
            'source_status':'FILES_VERIFIED' if inputs else 'NO_TASK_LOCAL_DOCUMENTS',
            'research_fit':research, 'prior_evidence':previous, 'rule_evidence':rule,
            'metadata':{'trailing_commas_removed_in_memory':removed, 'conflicts':conflicts},
            'official_task':task, 'official_assets':assets,
            'oracle_status':'SYNTAX_ERROR' if syntax_errors else ('REVISION_REQUIRED' if 'ORACLE_REVISION' in research else 'STATIC_ONLY'),
            'oracle_syntax_errors':syntax_errors, 'runtime_status':'NOT_RUN', 'calibration_status':'NOT_RUN',
            'generation_case_id':None, 'legacy_runs':[], 'execution_status':'BLOCKED',
            'blockers':['runtime_not_verified', 'oracle_positive_negative_not_verified', 'experiment_not_frozen'],
            'downstream_task_path':f'downstream_eval/tasks/sgb/{kind}/{task_id}'}
        if conflicts: row['blockers'].append('metadata_contract_conflict')
        if not inputs: row['blockers'].append('generator_corpus_unresolved')
        if research not in ('STATIC_BASIC_ENGINEERING','STATIC_BASIC_ORACLE_REVISION'):
            row['blockers'].append('research_rule_link_unresolved')
        if syntax_errors: row['blockers'].append('oracle_syntax_error')
        adapter = {
            'schema_version':1, 'task_key':key, 'registry':REGISTRY,
            'official_task':task_file.relative_to(root).as_posix(),
            'submission_kind':task['submission']['kind'], 'status':'METADATA_ONLY',
            'note':'No Agent-facing tests, answers, docs or executable task are materialized by import.'}
        if task_id=='scrapy-task-024' and (root/row['downstream_task_path']/'task.toml').is_file():
            adapter.update(status='HISTORICAL_CALIBRATION_ADAPTER',
                runner='downstream_eval.sgb.scrapy024',agent='downstream_eval.sgb.scrapy_agent:ScrapyTerminus2',
                launcher='scripts/sgb/Invoke-Scrapy024Calibration.ps1',
                note='Existing Task-024 calibration assets; new experiments still require preparation and a frozen budget.')
        write(root/row['downstream_task_path']/'adapter.json', adapter)
        rows.append(row)
    if len(rows) != 187 or len({r['task_key'] for r in rows}) != 187:
        raise ValueError('Pinned snapshot must contain exactly 187 distinct tasks')
    for row in rows:
        if row['original_task_id']=='scrapy-task-024': _bind_scrapy(root, row)
    catalog_path = root/'data/catalog.json'
    catalog = read(catalog_path)
    if any(d['dataset_id']=='skillgenbench' for d in catalog['datasets']):
        raise ValueError('Dataset already registered')
    catalog['datasets'].append({'dataset_id':'skillgenbench',
        'description':'All 187 pinned SGB tasks inventoried; source registration is not research/runtime admission',
        'source_manifests':sorted(source_names)})
    write(catalog_path, catalog)
    registry = root/REGISTRY; registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    config = {'schema_version':1, 'revision':REVISION, 'snapshot':frozen.relative_to(root).as_posix(),
        'snapshot_manifest_sha256':sha256(frozen/'snapshot_manifest.json'), 'registry':REGISTRY,
        'registry_sha256':sha256(registry), 'import_audit':audit.relative_to(root).as_posix()}
    write(root/CONFIG, config)
    write(root/'configs/experiments/sgb/template.json', {
        'schema_version':1, 'status':'DRAFT', 'dataset_revision':REVISION, 'task_keys':[],
        'conditions':['NoSkill','CleanSkill','RelevantDegradation','IrrelevantDegradation'],
        'generation_repeats':1, 'agent_repeats':3, 'model':None, 'budget':None,
        'note':'A template is not an authorization or runnable experiment.'})
    for name in ('data/condition_inputs/sgb','tests/fixtures/sgb','docs/sgb','results/sgb/analyses'):
        (root/name).mkdir(parents=True,exist_ok=True)
    report = audit_registry(root)
    write(audit/'import_result.json', report)
    fields=['task_key','source_type','original_task_id','source_status','research_fit','oracle_status',
            'runtime_status','calibration_status','metadata_conflicts','blockers']
    with (audit/'review_queue.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in rows:
            value={k:row[k] for k in fields if k not in ('metadata_conflicts','blockers')}
            value.update(metadata_conflicts=json.dumps(row['metadata']['conflicts'],ensure_ascii=False),
                         blockers=';'.join(row['blockers']))
            writer.writerow(value)
    return report


def _bind_scrapy(root, row):
    legacy = root/'runs/eval/sgb/scrapy-task-024/s24d001/batch_results.json'
    case = root/'cases/sgb/case024_scrapy'
    if not legacy.is_file() or not case.is_dir(): return
    batch = read(legacy)
    if len(batch['results']) != 6: raise ValueError('Unexpected historical calibration')
    original_inputs=read(case/'inputs/clean.json')['inputs']
    if sorted(i['sha256'] for i in original_inputs)!=sorted(i['sha256'] for i in row['sources']):
        raise ValueError('Historical source bytes differ from imported corpus')
    oracle_hash=row['official_assets']['skill_evaluation/code_doc/scrapy/scrapy-task-024/tests/eval.py']
    if any(r['oracle']['oracle_original_sha256']!=oracle_hash for r in batch['results']):
        raise ValueError('Historical Oracle differs from imported task')
    row['legacy_runs'] = [{'path':legacy.relative_to(root).as_posix(), 'sha256':sha256(legacy),
        'kind':'historical_calibration', 'task_successes':sum(r['task_success'] for r in batch['results'])}]
    row['calibration_status'] = 'HISTORICAL_SIX_TRIALS_COMPLETED'
    row['existing_generation_case_id'] = 'case024_scrapy'
    row['existing_task_adapter'] = row['downstream_task_path']
    # New case references imported source bytes; historical run contents stay intact under SGB.
    cid='case024_sgb'; base=root/'cases/sgb'/cid
    if base.exists(): raise FileExistsError(base)
    original=read(case/'case.json'); original.update(case_id=cid,dataset_id='skillgenbench',
        source_ids=[i['source_id'] for i in row['sources']], execution_gate=f'data/manifests/sgb/gates/{row["task_key"]}.json')
    write(base/'case.json',original)
    rules=read(case/'rules.json');rules['case_id']=cid
    old_ids=read(case/'case.json')['source_ids']
    mapping=dict(zip(old_ids,original['source_ids']))
    if len(old_ids)!=len(row['sources']):raise ValueError('Scrapy source mapping changed')
    for rule in rules['rules']:
        for anchor in rule['source_evidence']:anchor['source_id']=mapping[anchor['source_id']]
    write(base/'rules.json',rules)
    name=f'cases/sgb/{cid}/inputs/clean.json'
    write(root/name,{'schema_version':1,'case_id':cid,'condition_id':'clean','inputs':[
        {'input_id':f'input{n:03d}','source_id':i['source_id'],'source_sha256':i['sha256'],
         'path':i['path'],'sha256':i['sha256']} for n,i in enumerate(row['sources'],1)]})
    write(base/'conditions.json',{'schema_version':1,'case_id':cid,'conditions':[
        {'condition_id':'clean','kind':'clean','input_manifest':name,'operator':None,'parameters':{}}]})
    write(root/original['execution_gate'],{'status':'BLOCKED',
        'reason':'New namespaced case: experiment, runtime and scoring binding must be frozen before model execution.',
        'historical_case_id':'case024_scrapy'})
    row['generation_case_id']=cid


def load_registry(root):
    root=Path(root).resolve();config=read(root/CONFIG)
    if config['revision'] != REVISION:raise ValueError('Unexpected registry revision')
    registry=inside(root,config['registry'])
    if sha256(registry)!=config['registry_sha256']:raise ValueError('Registry changed outside the import/audit protocol')
    rows=[json.loads(s) for s in registry.read_text(encoding='utf-8').splitlines() if s.strip()]
    if len(rows)!=187 or len({r['task_key'] for r in rows})!=187:raise ValueError('Registry count/identity drift')
    return config,rows


def audit_registry(root):
    root=Path(root).resolve();config,rows=load_registry(root)
    if config.get('relocations') and sha256(inside(root,config['relocations']))!=config['relocations_sha256']:
        raise ValueError('SGB archive relocation manifest changed')
    snapshot=inside(root,config['snapshot']);manifest=snapshot/'snapshot_manifest.json'
    if sha256(manifest)!=config['snapshot_manifest_sha256']:raise ValueError('Snapshot manifest changed')
    frozen=read(manifest);actual=inventory(snapshot)
    if actual!={**frozen['files'],'snapshot_manifest.json':sha256(manifest)}:raise ValueError('Snapshot file drift')
    for row in rows:
        if row.get('existing_task_adapter'):
            if row['existing_task_adapter']!=row['downstream_task_path']:
                raise ValueError('Task adapter is outside its SGB task directory')
            task=inside(root,row['downstream_task_path'])
            if read(task/'adapter.json')['task_key']!=row['task_key']:
                raise ValueError('Task adapter identity drift')
            for name in ['instruction.md','task.toml','scorer/source_manifest.json']:
                if not (task/name).is_file():raise ValueError('Missing SGB calibration asset: '+name)
        for item in row['sources']:
            if sha256(inside(root,item['manifest']))!=item['manifest_sha256']:
                raise ValueError('Source manifest drift')
            value=check('source',read(inside(root,item['manifest'])))
            if value['sha256']!=item['sha256'] or sha256(inside(root,value['local_path']))!=item['sha256']:
                raise ValueError('Registered source drift')
        for name,digest in row['official_assets'].items():
            if frozen['files'].get(name)!=digest:raise ValueError('Task asset identity differs from snapshot')
        for prior in (row['prior_evidence'],row['rule_evidence']):
            if prior and sha256(inside(root,prior['evidence']))!=prior['sha256']:raise ValueError('Prior audit changed')
        for legacy in row['legacy_runs']:
            if sha256(inside(root,legacy['path']))!=legacy['sha256']:raise ValueError('Historical run changed')
    return {'status':'PASS','scope':'STATIC_IMPORT_AND_INTEGRITY_ONLY','revision':REVISION,'tasks':len(rows),
        'counts':{field:dict(Counter(r[field] for r in rows)) for field in
                  ('source_type','source_status','research_fit','oracle_status','runtime_status','calibration_status')},
        'descriptor_normalized':sum(bool(r['metadata']['trailing_commas_removed_in_memory']) for r in rows),
        'metadata_conflicts':sum(bool(r['metadata']['conflicts']) for r in rows),
        'oracle_syntax_error_tasks':sum(bool(r['oracle_syntax_errors']) for r in rows),
        'source_manifests':len({i['manifest'] for r in rows for i in r['sources']}),
        'unique_source_contents':len({i['sha256'] for r in rows for i in r['sources']}),
        'executable_tasks':sum(r['execution_status']=='READY' for r in rows),
        'model_calls':0,'agent_runs':0,'snapshot_files':len(frozen['files']),
        'oracle_syntax_check':'ast.parse only; no task code executed',
        'audit_python':sys.version.split()[0]}


def selected_tasks(root, tasks=None):
    config,rows=load_registry(root)
    if tasks:
        selected=[r for r in rows if r['task_key'] in tasks or r['original_task_id'] in tasks]
        if any(not any(k in (r['task_key'],r['original_task_id']) for r in selected) for k in tasks):
            raise ValueError('Unknown SGB task selector')
        rows=selected
    return config,rows
