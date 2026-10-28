"""Resume an interrupted Plan in a new run, reusing the upstream checkpoints."""
import hashlib
import json
import re
import shutil
from pathlib import Path

from .artifacts import resolve_run, run_refs
from .relocations import archived_path
from .io import check_windows_run_path, inside, inventory, read, resolve_upstream, sha256, upstream_inventory, utc, write


def window_key(payload):
    value = {'excerpt': payload.get('excerpt'), 'span': payload.get('section', {}).get('span')}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()


def _multi_document_checkpoint(parent, checkpoint, ingest, previous):
    """Recover extraction before any paid compile/register work has succeeded."""
    windows = ingest['windows']
    records, keys = {}, {}
    for w in windows:
        wid = w['window_id']
        key = (w['doc_id'], window_key({'excerpt':w['text'], 'section':{'span':w['span']}}))
        if key in keys or wid in records:
            raise ValueError('Ambiguous checkpoint window identity')
        keys[key] = wid
        path = checkpoint/'extract/windows'/w['doc_id']/(wid+'.json')
        records[wid] = read(path) if path.is_file() else {}
    completed = [w['window_id'] for w in windows
                 if records[w['window_id']].get('complete') and not records[w['window_id']].get('failed')]
    inherited = set(previous.get('completed_window_ids', []))
    if not completed or not inherited.issubset(completed):
        raise ValueError('Missing or changed completed extraction checkpoints')
    for doc in ingest['documents']:
        path = checkpoint/'extract/documents'/(doc['doc_id']+'.json')
        if path.is_file() and set(read(path).get('unresolved_window_ids', [])) & set(completed):
            raise ValueError('Completed window is also marked unresolved')
    plans, expands = {}, {}
    for call in read(parent/'model_calls.json'):
        functions = {f['function'] for f in call.get('stack', [])}
        if '_outline_matches_from_llm' in functions:
            continue
        if not functions & {'_plan_unit_skills', '_expand_planned_skill'}:
            raise ValueError('Multi-document recovery supports pre-compilation checkpoints only')
        request = read(parent/'http'/f"{call['number']:03d}"/'request.json')
        user = json.loads(next(m['content'] for m in request['messages'] if m['role']=='user'))
        wid = keys.get((user['document']['doc_id'], window_key(user)))
        if wid is None or wid in inherited:
            raise ValueError('Request does not match a new checkpoint window')
        if wid not in completed:
            if call.get('success') or '_expand_planned_skill' in functions:
                raise ValueError('Pending window has uncheckpointed calls; automatic recovery refused')
            continue
        if not call.get('success'):
            raise ValueError('Ambiguous failed call for completed window')
        bucket = plans if '_plan_unit_skills' in functions else expands
        bucket[wid] = bucket.get(wid, 0) + 1
    for wid in set(completed)-inherited:
        if plans.get(wid, 0)!=1 or expands.get(wid, 0)!=len(records[wid]['skill_drafts']):
            raise ValueError('Completed window calls do not match checkpoint drafts')
    # The official streaming compiler caches error-only documents as processed.
    # Exclude these empty downstream caches ONLY from the new run's copy.
    excluded = {}
    for stage in ('compile', 'register', 'final'):
        for path in (checkpoint/stage).rglob('*'):
            if path.is_file():
                if path.suffix=='.json':
                    data = read(path)
                    if any(data.get(k) for k in ('skill_specs','upserted_store_skills','lifecycles',
                                                 'change_logs','version_history','staging_runs')):
                        raise ValueError('Successful downstream artifacts require a different recovery path')
                excluded[path.relative_to(parent/'SkillBank').as_posix()] = sha256(path)
    return completed, excluded


def _registration_checkpoint(parent, checkpoint, ingest):
    """Resume documents interrupted during classify, before registry application."""
    compiled, registered_docs, registered_ids, pending_docs = {}, [], set(), []
    for doc in ingest['documents']:
        did = doc['doc_id']
        extracted = read(checkpoint/'extract/documents'/(did+'.json'))
        compiled_doc = read(checkpoint/'compile/documents'/(did+'.json'))
        if not extracted.get('complete') or extracted.get('failed') or compiled_doc.get('errors') or compiled_doc.get('skipped'):
            raise ValueError('Registration recovery requires complete extraction and compilation')
        compiled[did] = {x['skill_id'] for x in compiled_doc['skill_specs']}
        path = checkpoint/'register/documents'/(did+'.json')
        registered = read(path) if path.is_file() else {}
        if registered and not registered.get('skipped') and not registered.get('errors'):
            registered_docs.append(did)
            registered_ids.update(compiled[did])
        else:
            if any(registered.get(k) for k in ('skill_specs','upserted_store_skills','lifecycles','change_logs')):
                raise ValueError('Partial registration application is not safe to replay')
            pending_docs.append(did)
    decisions = {}
    for path in (checkpoint/'register/decisions').glob('*.json'):
        data = read(path)
        sid = data['skill_id']
        if sid != data.get('skill',{}).get('skill_id'):
            raise ValueError('Registration decision identity mismatch')
        decisions[sid] = data
    all_ids = set().union(*compiled.values())
    if not pending_docs or not set(decisions).issubset(all_ids):
        raise ValueError('No pending registration or unknown decision checkpoint')
    for did in pending_docs:
        # With every classification complete, registry application may have begun.
        if compiled[did].issubset(decisions):
            raise ValueError('Registration may have applied changes; automatic replay refused')
    for call in read(parent/'model_calls.json'):
        functions = {f['function'] for f in call.get('stack', [])}
        if 'register_versions' not in functions:
            continue
        request = read(parent/'http'/f"{call['number']:03d}"/'request.json')
        user = json.loads(next(m['content'] for m in request['messages'] if m['role']=='user'))
        if 'classify_change' in functions:
            sid = user.get('candidate_skill',{}).get('skill_id')
            if sid not in all_ids or (call.get('success') and sid not in decisions):
                raise ValueError('Uncheckpointed registration decision; automatic replay refused')
        elif 'classify_parent_link' in functions:
            if user.get('child_skill',{}).get('skill_id') not in registered_ids:
                raise ValueError('Pending document has uncheckpointed hierarchy work')
        else:
            raise ValueError('Registration recovery supports interrupted classification only')
    return {'completed_registration_doc_ids':registered_docs,
            'cached_registration_decision_ids':sorted(decisions)}


def _budget_extraction_calls(parent, checkpoint, windows, completed, inherited):
    """Account for known work replayed in the sole incomplete window after a budget stop."""
    errors = read(parent/'official_result.json').get('errors', [])
    if not errors or any(e.get('error') != 'P0 external observation budget exhausted' for e in errors):
        raise ValueError('Only a recorded observation-budget stop permits window replay')
    eligible = windows[len(inherited):len(completed)+1]
    keys = {window_key({'excerpt':w['text'], 'section':{'span':w['span']}}): w['window_id'] for w in eligible}
    groups = {}
    for call in read(parent/'model_calls.json'):
        groups.setdefault(call.get('logical_call_id', call['number']), []).append(call)
    work = {w['window_id']: {'plans': [], 'expands': []} for w in eligible}
    replayed = []
    for logical, calls in groups.items():
        last = calls[-1]
        if (not last.get('success') or any(c.get('success') or not c.get('transport_retry_eligible')
                                         or calls[i+1].get('retry_of') != logical for i,c in enumerate(calls[:-1]))):
            raise ValueError('Unresolved HTTP delivery cannot be replayed as a budget stop')
        for call in calls:
            if call.get('success') and sha256(parent/'http'/f"{call['number']:03d}"/'response.json') != call['response_sha256']:
                raise ValueError('Saved response hash mismatch')
        functions = {f['function'] for f in last.get('stack', [])}
        if '_outline_matches_from_llm' in functions:
            continue
        kind = 'plans' if '_plan_unit_skills' in functions else 'expands' if '_expand_planned_skill' in functions else None
        if kind is None:
            raise ValueError('Budget recovery supports extraction-only HTTP work')
        payloads = [read(parent/'http'/f"{c['number']:03d}"/'request.json') for c in calls]
        if any(p != payloads[0] for p in payloads):
            raise ValueError('Transport retry payload changed')
        user = json.loads(next(m['content'] for m in payloads[0]['messages'] if m['role']=='user'))
        wid = keys.get(window_key(user))
        if wid is None:
            raise ValueError('Request does not match a checkpoint window')
        work[wid][kind].append(last)
        if wid == windows[len(completed)]['window_id']:
            replayed.extend(c['number'] for c in calls)
    for w in eligible:
        values = work[w['window_id']]
        if w['window_id'] in completed:
            record = read(checkpoint/'extract/windows'/w['doc_id']/(w['window_id']+'.json'))
            if len(values['plans']) != 1 or len(values['expands']) != len(record['skill_drafts']):
                raise ValueError('Completed window calls disagree with checkpoint drafts')
        elif len(values['plans']) > 1 or (values['expands'] and not values['plans']):
            raise ValueError('Ambiguous incomplete-window work')
    excluded = {}
    for stage in ('compile', 'register', 'final'):
        for p in (checkpoint/stage).rglob('*'):
            if not p.is_file():
                continue
            if p.suffix == '.json' and any(read(p).get(k) for k in (
                    'skill_specs', 'upserted_store_skills', 'lifecycles', 'change_logs', 'version_history', 'staging_runs')):
                raise ValueError('Successful downstream artifacts cannot be discarded')
            excluded[p.relative_to(parent/'SkillBank').as_posix()] = sha256(p)
    return sorted(replayed), excluded


def prepare_resume(root, run_id, new_run_id, budget_overrides=None):
    identity, parent = resolve_run(root, run_id)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', new_run_id):
        raise ValueError('Unsafe run_id')
    relative = identity.get('path', f"runs/{identity['case_id']}/{identity['condition_id']}/{run_id}")
    target = inside(root, Path(relative).parent/new_run_id)
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
    stages = state['completed_stages']
    registration_resume = all(stage in stages for stage in ('ingest','extract','compile')) and 'register' not in stages
    if 'ingest' not in stages or ('extract' in stages and not registration_resume):
        raise ValueError('Recovery supports interrupted extraction or registration after complete compilation')
    ingest = read(checkpoint/'ingest/result.json')
    windows = ingest['windows']
    excluded = {}
    budget_replayed = []
    registration = {}
    if registration_resume:
        registration = _registration_checkpoint(parent, checkpoint, ingest)
        completed = [w['window_id'] for w in windows]
    elif len(ingest['documents']) > 1:
        completed, excluded = _multi_document_checkpoint(parent, checkpoint, ingest, previous)
    else:
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
        budget_errors = result.get('errors', [])
        if budget_errors and all(e.get('error') == 'P0 external observation budget exhausted' for e in budget_errors):
            budget_replayed, excluded = _budget_extraction_calls(parent, checkpoint, windows, completed,
                                                                 previous.get('completed_window_ids', []))
        else:
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
    logical_inputs = Path(invocation.get('store_path', str(parent/'SkillBank'))).parent/'inputs'
    source = Path(previous.get('source_path', str(logical_inputs)))
    input_manifest = read(parent/'input_manifest.json')
    for item in input_manifest['inputs']:
        if sha256(archived_path(item['execution_path'])) != item['sha256']:
            raise ValueError('Frozen source input changed')
    execution = read(parent/'execution.json')
    resume = {
        'parent_run_id':run_id, 'parent_path':str(parent),
        'parent_manifest_sha256':sha256(parent/'artifact_manifest.json'),
        'checkpoint_id':checkpoint_id, 'resume_key':state['metadata']['resume_key'],
        'source_path':str(source), 'pipeline_run_id':previous.get('pipeline_run_id', run_id),
        'completed_window_ids':completed, 'pending_window_ids':[w['window_id'] for w in windows if w['window_id'] not in completed],
        'completed_window_keys':[window_key({'excerpt':w['text'], 'section':{'span':w['span']}}) for w in windows if w['window_id'] in completed],
        'prior_http_attempts':execution.get('cumulative_http_attempts', execution['http_attempts']),
        'prior_usage_totals':execution.get('cumulative_usage_totals', execution['usage_totals']),
        'note':'Failed POST delivery/billing is unknown; recovering the failed Plan can repeat remote work.'
    }
    resume.update(registration)
    resume['budget_replayed_call_numbers'] = budget_replayed
    config = read(parent/'config.json')
    budget_before = {k:config[k] for k in ('max_http_calls','max_observed_total_tokens')}
    for key,value in (budget_overrides or {}).items():
        if key not in budget_before or type(value) is not int or value < config[key]:
            raise ValueError('Resume budget must be an explicit nondecreasing integer limit')
        config[key] = value
    resume['budget_before'] = budget_before
    resume['budget_after'] = {k:config[k] for k in budget_before}
    resume['excluded_checkpoint_artifacts'] = excluded
    if (resume['prior_http_attempts'] >= config['max_http_calls'] or
            resume['prior_usage_totals'].get('total_tokens',0) >= config['max_observed_total_tokens']):
        raise ValueError('Resume budget exhausted; explicitly authorize a higher cumulative '
                         '--max-observed-total-tokens or --max-http-calls limit')
    target.mkdir(parents=True, exist_ok=False)
    for name in ('case.json','rules.json','conditions.json','condition.json','config.json','sources.json','input_manifest.json'):
        shutil.copyfile(parent/name, target/name)
    shutil.copytree(parent/'inputs', target/'inputs', copy_function=shutil.copy2)
    write(target/'config.json', config)
    def ignore_failed_caches(directory, names):
        return [name for name in names
                if (Path(directory)/name).relative_to(parent/'SkillBank').as_posix() in excluded]
    shutil.copytree(parent/'SkillBank', target/'SkillBank', copy_function=shutil.copy2,
                    ignore=ignore_failed_caches)
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
    if 'cached_registration_decision_ids' in resume:
        if functions & {'compile_skills','_plan_unit_skills','_expand_planned_skill'}:
            raise RuntimeError('Registration resume refused extraction/compilation request')
        if 'classify_change' in functions:
            user = json.loads(next(m['content'] for m in payload['messages'] if m['role']=='user'))
            if user.get('candidate_skill',{}).get('skill_id') in resume['cached_registration_decision_ids']:
                raise RuntimeError('Resume refused to resend a cached registration decision')
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
