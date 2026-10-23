"""Resume an interrupted Plan in a new run, reusing the upstream checkpoints."""
import hashlib
import json
import re
import shutil
from pathlib import Path

from .artifacts import resolve_run, run_refs
from .io import check_windows_run_path, inside, inventory, read, resolve_upstream, sha256, upstream_inventory, utc, write


def window_key(payload):
    value = {'excerpt': payload.get('excerpt'), 'span': payload.get('section', {}).get('span')}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def prepare_resume(root, run_id, new_run_id):
    identity, parent = resolve_run(root, run_id)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', new_run_id):
        raise ValueError('Unsafe run_id')
    target = inside(root, f"runs/{identity['case_id']}/{identity['condition_id']}/{new_run_id}")
    check_windows_run_path(target)
    if target.exists() or any(r['run_id'] == new_run_id for r in run_refs(root)):
        raise FileExistsError('Globally unique run_id already exists: ' + new_run_id)
    artifacts = read(parent/'artifact_manifest.json')
    if not artifacts or any(sha256(inside(parent, p)) != h for p,h in artifacts.items()):
        raise ValueError('Parent run artifact hash mismatch')
    upstream = resolve_upstream(root)
    if read(parent/'upstream_before.json') != read(parent/'upstream_after.json') or upstream_inventory(upstream) != read(parent/'upstream_after.json'):
        raise ValueError('Upstream source changed; cannot resume')
    previous = read(parent/'resume.json') if (parent/'resume.json').is_file() else {}
    invocation = read(parent/'invocation.json')
    result = read(parent/'official_result.json')
    checkpoint_id = result['intermediate']['run_id']
    checkpoint = inside(parent, 'SkillBank/.runtime/intermediate_runs/' + checkpoint_id)
    state = read(checkpoint/'status.json')
    if invocation.get('execution_kind') != 'official' or state.get('status') not in ('failed', 'partial'):
        raise ValueError('Only interrupted official runs can resume')
    if 'ingest' not in state['completed_stages'] or 'extract' in state['completed_stages']:
        raise ValueError('This recovery entry supports interrupted extraction only')
    ingest = read(checkpoint/'ingest/result.json')
    if len(ingest['documents']) != 1:
        raise ValueError('This recovery entry supports one document only')
    windows = ingest['windows']
    doc_id = ingest['documents'][0]['doc_id']
    completed = []
    for w in windows:
        path = checkpoint/'extract/windows'/doc_id/(w['window_id']+'.json')
        record = read(path) if path.is_file() else {}
        if record.get('complete') and not record.get('failed'):
            completed.append(w['window_id'])
    n = len(completed)
    if not n or n == len(windows) or completed != [w['window_id'] for w in windows[:n]]:
        raise ValueError('Recovery requires a completed window prefix and pending windows')
    k = len(previous.get('completed_window_ids', []))
    if completed[:k] != previous.get('completed_window_ids', []) or k > n:
        raise ValueError('Inherited completed windows changed')
    calls = read(parent/'model_calls.json')
    plans = [c for c in calls if any(f['function'] == '_plan_unit_skills' for f in c.get('stack', []))]
    expands = [c for c in calls if any(f['function'] == '_expand_planned_skill' for f in c.get('stack', []))]
    # A successful but uncheckpointed Plan/Expand must never be silently resent.
    if len(plans) != n-k+1 or not all(c.get('success') for c in plans[:-1]) or plans[-1].get('success') or calls[-1] != plans[-1]:
        raise ValueError('Pending window has uncheckpointed calls; automatic recovery refused')
    for call,w in zip(plans, windows[k:]):
        payload = read(parent/'http'/f"{call['number']:03d}"/'request.json')
        user = json.loads(next(m['content'] for m in payload['messages'] if m['role'] == 'user'))
        if window_key(user) != window_key({'excerpt':w['text'], 'section':{'span':w['span']}}):
            raise ValueError('Plan request does not match checkpoint window')
    drafts = [d for w in windows[k:n] for d in read(checkpoint/'extract/windows'/doc_id/(w['window_id']+'.json'))['skill_drafts']]
    if len(expands) != len(drafts) or not all(c.get('success') for c in expands):
        raise ValueError('Uncheckpointed Expand calls; automatic recovery refused')
    source = Path(previous.get('source_path', str(parent/'inputs')))
    input_manifest = read(parent/'input_manifest.json')
    for item in input_manifest['inputs']:
        if sha256(Path(item['execution_path'])) != item['sha256']:
            raise ValueError('Frozen source input changed')
    execution = read(parent/'execution.json')
    resume = {
        'parent_run_id':run_id, 'parent_path':str(parent),
        'parent_manifest_sha256':sha256(parent/'artifact_manifest.json'),
        'checkpoint_id':checkpoint_id, 'resume_key':state['metadata']['resume_key'],
        'source_path':str(source), 'pipeline_run_id':previous.get('pipeline_run_id', run_id),
        'completed_window_ids':completed, 'pending_window_ids':[w['window_id'] for w in windows[n:]],
        'completed_window_keys':[window_key({'excerpt':w['text'], 'section':{'span':w['span']}}) for w in windows[:n]],
        'prior_http_attempts':execution.get('cumulative_http_attempts', execution['http_attempts']),
        'prior_usage_totals':execution.get('cumulative_usage_totals', execution['usage_totals']),
        'note':'Failed POST delivery/billing is unknown; recovering the failed Plan can repeat remote work.'
    }
    target.mkdir(parents=True, exist_ok=False)
    for name in ('case.json','rules.json','conditions.json','condition.json','config.json','sources.json','input_manifest.json'):
        shutil.copyfile(parent/name, target/name)
    shutil.copytree(parent/'inputs', target/'inputs', copy_function=shutil.copy2)
    shutil.copytree(parent/'SkillBank', target/'SkillBank', copy_function=shutil.copy2)
    resume['seed_skillbank'] = inventory(target/'SkillBank')
    write(target/'resume.json', resume)
    write(target/'environment.json', {'upstream_path':str(upstream)})
    write(target/'upstream_before.json', upstream_inventory(upstream))
    shutil.copytree(Path(__file__).parent, target/'wrapper_snapshot/degradation_lab',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    write(target/'wrapper_manifest.json', inventory(target/'wrapper_snapshot'))
    write(target/'invocation.json', dict(identity, run_id=new_run_id, started_at=utc(),
          store_path=str(target/'SkillBank'), initial_store_entries=sorted(resume['seed_skillbank']),
          real_generation=False, execution_kind='official', resume_from=run_id))
    write(target/'status.json', {'state':'PREPARED', 'real_generation':False, 'updated_at':utc()})
    return target


def guard_request(resume, payload, stack):
    functions = {f['function'] for f in stack}
    if '_outline_matches_from_llm' in functions:
        raise RuntimeError('Resume refused an Outline request')
    if functions & {'_plan_unit_skills', '_expand_planned_skill'}:
        user = json.loads(next(m['content'] for m in payload['messages'] if m['role'] == 'user'))
        if window_key(user) in resume['completed_window_keys']:
            raise RuntimeError('Resume refused to resend a completed window')


def checked_finder(original, resume):
    def find(*, base_store_root, resume_key):
        found = original(base_store_root=base_store_root, resume_key=resume_key)
        if resume_key != resume['resume_key'] or not found or found['run_id'] != resume['checkpoint_id']:
            raise RuntimeError('Checkpoint identity mismatch; refusing a full rerun')
        return found
    return find
