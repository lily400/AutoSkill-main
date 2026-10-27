"""Explicit ten-task result index and hash-checked historical evidence. Zero model calls."""
from pathlib import Path

from degradation_lab.io import inside, read, sha256, write
from .attribution import audit_pair
from .protocol import CONFIG
from downstream_eval.scoring.results import summarize, trial_record


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
                            accepted.append(trial_record(value, row['task_id'], pair['run_path']))
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
