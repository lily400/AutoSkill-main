"""SGB preparation and observed-result reporting, with no model or Agent imports."""
import re
from pathlib import Path

from degradation_lab.io import inside, read, sha256, write
from degradation_lab.sgb import audit_registry, selected_tasks
from .scoring.results import summarize, trial_record


def plan(root, tasks=None):
    _, rows = selected_tasks(root, tasks)
    return {'model_calls':0, 'agent_runs':0, 'tasks':[
        {'task_key':r['task_key'],'original_task_id':r['original_task_id'],
         'source_type':r['source_type'],'generation_case_id':r['generation_case_id'],
         'source_bundle_id':r['source_bundle_id'],'submission_kind':r['official_task']['submission']['kind'],
         'environment_label':r['official_task']['runtime']['docker_image'],
         'oracle_status':r['oracle_status'],'runtime_status':r['runtime_status'],
         'execution_status':r['execution_status'],'blockers':r['blockers'],
         'historical_calibration':r['legacy_runs']} for r in rows]}


def prepare(root, tasks, preparation_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',preparation_id):raise ValueError('Unsafe preparation ID')
    report=audit_registry(root)
    target=inside(root,'results/sgb/audits/'+preparation_id)
    if target.exists():raise FileExistsError(target)
    value=plan(root,tasks)
    # A manifest is useful even for blocked tasks, but never masquerades as a native Trial.
    value.update(status='PREPARATION_COMPLETE',scope='METADATA_AND_INTEGRITY_ONLY',
                 runnable=sum(r['execution_status']=='READY' for r in value['tasks']),
                 registry_audit=report)
    write(target/'preparation.json',value)
    return {'path':str(target/'preparation.json'),'tasks':len(value['tasks']),
            'runnable':value['runnable'],'model_calls':0,'agent_runs':0}


def aggregate(root, tasks, analysis_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',analysis_id):raise ValueError('Unsafe analysis ID')
    root=Path(root).resolve();_,rows=selected_tasks(root,tasks);observed=[];seen=set()
    for row in rows:
        for link in row['legacy_runs']:
            path=inside(root,link['path'])
            if sha256(path)!=link['sha256']:raise ValueError('Historical results changed')
            for value in read(path)['results']:
                key=(link['path'],value['label'])
                if key in seen:raise ValueError('Duplicate observed trial')
                seen.add(key);observed.append(trial_record(value,row['task_key'],link['path']))
    target=inside(root,'results/sgb/analyses/'+analysis_id)
    if target.exists():raise FileExistsError(target)
    write(target/'trials.json',observed)
    result={'status':'PASS','selected_tasks':len(rows),'observed_trials':len(observed),
            'tasks_without_observed_trials':[r['task_key'] for r in rows if not r['legacy_runs']],
            **summarize(observed),'model_calls':0,'agent_runs':0}
    write(target/'summary.json',result)
    return {k:v for k,v in result.items() if k!='tasks_without_observed_trials'} | {
        'tasks_without_observed_trials_count':len(result['tasks_without_observed_trials']),
        'summary_path':str(target/'summary.json')}
