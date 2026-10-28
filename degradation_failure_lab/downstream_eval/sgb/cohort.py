"""Explicit ten-task result index and hash-checked historical evidence. Zero model calls."""
from pathlib import Path

from degradation_lab.io import inside, read, sha256, write
from .attribution import audit_pair
from .protocol import CONFIG
from downstream_eval.scoring.results import summarize, trial_record, completion_state


def load(root, config):
    data = read(inside(root, config))
    if data.get('schema_version') != 1 or data.get('protocol_id') != read(inside(root, CONFIG))['protocol_id']:
        raise ValueError('Unknown formal cohort protocol')
    tasks = data['tasks']
    ids = [r['task_id'] for r in tasks]
    if len(tasks) != 10 or len(set(ids)) != 10:
        raise ValueError('Formal cohort requires ten distinct task IDs')
    refs = []
    for row in tasks:
        if row['status'] not in ('READY', 'NEEDS_WORK', 'REJECTED'):
            raise ValueError('Unknown admission status')
        pair = row.get('pair')
        if pair:
            if row['status'] != 'READY' or set(pair) != {'run_path', 'reference_label', 'target_label'}:
                raise ValueError('Only READY tasks may bind an explicit formal pair')
            path = inside(root, pair['run_path'])
            if not path.is_relative_to(Path(root).resolve() / 'runs/eval/sgb' / row['task_id']):
                raise ValueError('Formal pair points to another task')
            refs += [(str(path), pair['reference_label']), (str(path), pair['target_label'])]
    if len(set(refs)) != len(refs):
        raise ValueError('Formal trial is indexed twice')
    return data


def trace(root, manifest, index):
    aliases = read(inside(root, index))['files']
    recovered, missing = [], []
    for name, expected in manifest.items():
        path = inside(root, name)
        if path.is_file() and sha256(path) == expected:
            continue
        candidates = aliases.get(expected, [])
        match = next((p for p in candidates if inside(root, p).is_file()
                      and sha256(inside(root, p)) == expected), None)
        if match is None:
            missing.append(name)
        else:
            recovered.append({'original_path':name, 'sha256':expected, 'archive_path':match})
    return {'status':'VERIFIED' if not missing else 'INCOMPLETE',
            'recovered':recovered, 'missing':missing, 'files':len(manifest)}


def protocol_evidence(root, run, protocol, history_index):
    profile = read(run / 'profile.json')
    for key in ('model', 'budget', 'conditions', 'repeats_per_arm'):
        if profile.get(key) != protocol[key]:
            return {'status':'INELIGIBLE', 'reason':'Different ' + key}
    manifest = read(run / 'execution_manifest.json')
    history = trace(root, manifest, history_index)
    required = inside(root, protocol['skill_read_instruction']).read_text(encoding='utf-8').strip()
    for label in protocol['conditions']:
        config = read(run / 'configs' / (label + '.json'))
        text = []
        for stored in config.get('extra_instruction_paths', []):
            from .attribution import _stored_relative
            name = _stored_relative(Path(root), stored)
            digest = manifest.get(name)
            path = inside(root, name)
            if digest is None:
                return {'status':'INELIGIBLE', 'reason':'Instruction is not frozen'}
            if not path.is_file() or sha256(path) != digest:
                aliases = read(inside(root, history_index))['files'].get(digest, [])
                path = next((inside(root, p) for p in aliases if inside(root, p).is_file()
                             and sha256(inside(root, p)) == digest), None)
            if path is None:
                return {'status':'INELIGIBLE', 'reason':'Historical instruction bytes missing'}
            text.append(path.read_text(encoding='utf-8'))
        if required not in '\n'.join(text):
            return {'status':'INELIGIBLE', 'reason':'Required-reading protocol differs'}
    return {'status':'VERIFIED' if history['status'] == 'VERIFIED' else 'INCOMPLETE',
            'history':history, 'historical_adoption':profile.get('protocol_id') != protocol['protocol_id']}


def revised_values(root, run, row, values):
    """Apply an explicitly approved, hash-bound scoring correction to the same Agent outputs."""
    reference = row['score_revision']; path = inside(root, reference['path'])
    if not path.is_relative_to(Path(root) / 'results/sgb/rescores') or sha256(path) != reference['sha256']:
        raise ValueError('Scoring revision manifest hash/path mismatch')
    manifest = read(path)
    if (manifest.get('schema_version') != 1 or manifest.get('user_approved') is not True
            or manifest.get('model_calls') != 0 or manifest['run_path'] != row['pair']['run_path']
            or manifest['source_batch_results_sha256'] != sha256(run / 'batch_results.json')):
        raise ValueError('Scoring revision approval/source binding mismatch')
    if not manifest['files'] or any(sha256(inside(path.parent, name)) != digest
                                    for name, digest in manifest['files'].items()):
        raise ValueError('Scoring revision artifact hash mismatch')
    if len(values) != 2 or set(manifest['results']) != {v['label'] for v in values}:
        raise ValueError('Scoring revision must bind both original arms')
    revised = []
    for value in values:
        record = read(inside(path.parent, manifest['results'][value['label']]))
        grade = record['oracle']; original = value['oracle']; counts = grade['task_result']
        if (record['label'] != value['label'] or record['scoring_revision'] != manifest['protocol_id']
                or record['source_result_sha256'] != sha256(run / 'outcomes' / value['label'] / 'result.json')
                or grade.get('candidate_sha256') != original['candidate_sha256']
                or grade.get('oracle_sha256') != original['oracle_sha256']
                or grade.get('candidate_binding_verified') is not True or grade.get('infra_ok') is not True
                or grade.get('model_calls') != 0 or type(grade.get('task_success')) is not bool
                or value.get('infra_ok') is not True or value.get('native_exception')
                or value.get('failure_kind') not in ('none','task_failure')
                or counts['tests'] != original['task_result']['tests'] or counts['errors'] or counts['skipped']
                or counts['passed'] + counts['failed'] != counts['tests']
                or grade['task_success'] != (counts['passed'] == counts['tests'])):
            raise ValueError('Scoring revision candidate/Oracle/outcome binding mismatch')
        revision = {'protocol_id':manifest['protocol_id'], **reference,
                    'original_task_success':value['task_success'], 'original_task_result':original['task_result'],
                    'post_run_measurement_correction':True}
        revised.append(dict(value, oracle=grade, task_success=grade['task_success'],
                            failure_category=grade['failure_category'],
                            failure_kind='none' if grade['task_success'] else 'task_failure', scoring_revision=revision))
    return revised


def report(root, config):
    root = Path(root).resolve(); cohort = load(root, config)
    protocol = read(inside(root, CONFIG)); tasks = []; records = []; observed = []
    for row in cohort['tasks']:
        item = {'task_id':row['task_id'], 'admission':row['status'], 'execution':'NOT_STARTED'}
        pair = row.get('pair')
        if pair:
            run = inside(root, pair['run_path'])
            if (run / 'batch_results.json').exists():
                checks = protocol_evidence(root, run, protocol, cohort['history_index'])
                spec = {'schema_version':1, 'analysis_id':cohort['cohort_id'], 'pair_id':row['task_id'],
                    'task_id':row['task_id'], 'comparison_kind':'no_skill_clean',
                    'reference':{'run_path':pair['run_path'], 'label':pair['reference_label']},
                    'target':{'run_path':pair['run_path'], 'label':pair['target_label']},
                    'evidence':[], 'rules':[], 'claims':[], 'interventions':[]}
                audit = audit_pair(root, spec)
                item.update(protocol=checks, comparability=audit['comparability'])
                values = read(run / 'batch_results.json')['results']
                limit = read(run / 'profile.json')['budget']['max_requests']
                for i, value in enumerate(values):
                    native_path = run / 'outcomes' / value['label'] / 'native.json'
                    if not native_path.is_file():continue
                    termination = completion_state(read(native_path),limit)
                    if (termination['status'] == 'turn_limit_unconfirmed' and value.get('infra_ok') is True
                            and not value.get('native_exception')
                            and value.get('failure_kind') in (None,'none','task_failure')):
                        correction = {'protocol_id':'terminus2-turn-limit-v2', **termination,
                                      'original_failure_kind':value.get('failure_kind'),
                                      'native_result':native_path.relative_to(root).as_posix(),
                                      'native_result_sha256':sha256(native_path)}
                        values[i] = dict(value,failure_kind='budget_exhausted',task_success=False,
                                         classification_revision=correction)
                if row.get('score_revision'):
                    values = revised_values(root, run, row, values)
                    item['score_revision'] = row['score_revision']
                labels = (pair['reference_label'], pair['target_label'])
                if len(values) > 2 or len({v['label'] for v in values}) != len(values) or any(v['label'] not in labels for v in values):
                    raise ValueError('Formal pair must contain at most one result per arm')
                identities_match = all(t is None or
                    (t['generator_run_id'] == row.get('generator_run_id') and t['case_id'] == row.get('case_id'))
                    for t in audit['trials'].values())
                item['generation_identity_matches'] = identities_match
                accepted = []
                if checks['status'] == 'VERIFIED' and identities_match:
                    for value in values:
                        side = 'reference' if value['label'] == pair['reference_label'] else 'target'
                        trial = audit['trials'][side]
                        if (trial and not trial['integrity_issues'] and value.get('model_api_results') is True
                                and (trial['scorable'] or value.get('infra_ok') is False)):
                            record = trial_record(value, row['task_id'], pair['run_path'])
                            if value.get('scoring_revision'):record['scoring_revision'] = value['scoring_revision']
                            if value.get('classification_revision'):record['classification_revision'] = value['classification_revision']
                            accepted.append(record)
                    observed += accepted
                item['observed_outcomes'] = accepted
                if (checks['status'] == 'VERIFIED' and identities_match
                        and audit['comparability'] == 'eligible' and len(accepted) == 2):
                    records += accepted
                    item.update(execution='COMPLETED', task_success={v['condition']:v['task_success'] for v in values})
                else:
                    item['execution'] = 'PARTIAL' if len(accepted) == 1 else 'INELIGIBLE_OR_INCOMPLETE'
            elif (run / 'batch.started').exists():
                item['execution'] = 'INCOMPLETE'
        tasks.append(item)
    return {'cohort_id':cohort['cohort_id'], 'protocol_id':cohort['protocol_id'],
            'planned_tasks':10, 'planned_trials':20, 'completed_pairs':sum(t['execution']=='COMPLETED' for t in tasks),
            'ready_tasks':sum(t['admission']=='READY' for t in tasks), 'tasks':tasks,
            'records':records, **summarize(records), 'observed_records':observed,
            'observed_summary':summarize(observed), 'model_calls':0,
            'metric':'One task = one paired binary outcome; testcase counts are never pooled.'}


def export(root, config, output):
    target = inside(root, output)
    if target.exists():
        raise FileExistsError(target)
    result = report(root, config)
    write(target / 'summary.json', result)
    return result
