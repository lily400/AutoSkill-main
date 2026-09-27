"""Reference-only offline validation and explicit future executor interface."""
import argparse
from pathlib import Path
import sys
from uuid import uuid4
from data_contracts import select, validate_object, sealed_run, require, utc, VERSION, safe
from evidence import read, save, sha, freeze, check_frozen
import reference_csv
import judge_csv

LAB=Path(__file__).resolve().parents[1]

def execute_reference(root,case_key):
    root=Path(root); ds,c,v=select(root,case_key)
    require(c['source_id']=='src-authored-order-csv','This reference implements case001 only')
    rows=[]
    for task_file in c['task_files']:
        task=read(root/task_file); eid='reference-'+uuid4().hex; folder=root/'executions'/eid
        workspace=folder/'workspace'; workspace.mkdir(parents=True,exist_ok=False)
        for name,content in task['inputs'].items(): (workspace/name).write_bytes(content.encode('utf-8'))
        before={name:sha(workspace/name) for name in task['inputs']}
        judge=ds['judges'][task['judge_id']]
        result={'schema_version':VERSION,'execution_id':eid,**{k:task[k] for k in ('case_id','source_id','family_id','task_id','contract_id','judge_id')},
            'run_id':None,'mode':'reference','execution_repeat':1,'status':'running','failure_category':'none',
            'reason':'Actual local reference implementation; not generated skill or model performance',
            'executor':{'id':'case001-reference','version':reference_csv.VERSION,'model':None},
            'input_before':before,'input_after':{},'actual_outputs':{},'error':None,'exit_code':None,
            'started_at_utc':utc(),'finished_at_utc':None,'dataset_freeze_sha256':sha(root/'catalog/freeze.json'),
            'run_checksums_sha256':None,'standard_hashes':{task_file:sha(root/task_file),c['contract_file']:sha(root/c['contract_file']),
                judge['implementation_file']:judge['implementation_sha256'],judge['reference_file']:judge['reference_sha256']}}
        save(folder/'execution.json',result)
        try:
            reference_csv.execute(workspace/'orders.csv',workspace/'outputs'); result['exit_code']=0
        except reference_csv.InputError as e:
            result.update(exit_code=1,error={'record':e.record,'field':e.field,'message':str(e)})
        except Exception as e:
            result.update(status='failed',failure_category='infrastructure',exit_code=2,
                error={'record':None,'field':None,'message':type(e).__name__+': '+str(e)})
        if result['status']=='running': result['status']='completed'
        result['input_after']={name:sha(workspace/name) for name in task['inputs'] if (workspace/name).is_file()}
        result['actual_outputs']={p.relative_to(workspace/'outputs').as_posix():p.read_bytes().decode('utf-8')
            for p in (workspace/'outputs').rglob('*') if p.is_file()}
        result['finished_at_utc']=utc(); validate_object('execution',result)
        save(folder/'execution.json',result)
        save(folder/'evidence/process.json',{'python':sys.executable,'version':sys.version,'kind':'local_reference_function','reference_sha256':judge['reference_sha256']})
        freeze(folder)
        verdict=judge_csv.judge(task,result); jid='judge-'+uuid4().hex
        judgment={'schema_version':VERSION,'judgment_id':jid,'execution_id':eid,'case_id':c['case_id'],
            'task_id':task['task_id'],'judge_id':task['judge_id'],**verdict,'execution_checksums_sha256':sha(folder/'checksums.json'),
            'judge_sha256':judge['implementation_sha256'],'created_at_utc':utc()}
        validate_object('judgment',judgment); jdir=root/'judgments'/jid
        save(jdir/'judgment.json',judgment); freeze(jdir)
        rows.append({'task_id':task['task_id'],'execution_id':eid,'judgment_id':jid,'passed':verdict['passed']})
    report={'schema_version':VERSION,'kind':'reference_development_validation','rows':rows,
        'passed':sum(r['passed'] is True for r in rows),'total':len(rows),
        'generated_skill_executions':0,'scientific_claim':'Only reference/judge engineering verification'}
    out=root/'reports'/('reference-'+uuid4().hex+'.json'); save(out,report); return out,report

def plan_execution(root,run_id,task_id):
    root=Path(root); rp,r,_=sealed_run(root,run_id)
    ds,c,_=select(root,read(rp/'config/config.json')['case_key'],r['variant_id'])
    require(task_id in ds['tasks'],'Unknown task'); t=ds['tasks'][task_id]
    require(t['case_id']==r['case_id'],'Cross-case execution')
    eid='planned-'+uuid4().hex
    result={'schema_version':VERSION,'execution_id':eid,**{k:t[k] for k in ('case_id','source_id','family_id','task_id','contract_id','judge_id')},
        'run_id':run_id,'mode':'generated_skill','execution_repeat':1,'status':'not_run','failure_category':'none',
        'reason':'Generated-skill executor adapter is not implemented; no task was executed',
        'executor':{'id':'pending-executor','version':'not-implemented','model':None},
        'input_before':{},'input_after':{},'actual_outputs':{},'error':None,'exit_code':None,
        'started_at_utc':utc(),'finished_at_utc':None,'dataset_freeze_sha256':sha(root/'catalog/freeze.json'),
        'run_checksums_sha256':sha(rp/'checksums.json'),'standard_hashes':{p:sha(root/p) for p in c['task_files'] if read(root/p)['task_id']==task_id}}
    validate_object('execution',result); out=root/'executions'/eid; save(out/'execution.json',result); freeze(out)
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='action',required=True)
    r=sub.add_parser('reference'); r.add_argument('--case',required=True)
    e=sub.add_parser('plan'); e.add_argument('--run',required=True); e.add_argument('--task',required=True)
    a=p.parse_args()
    if a.action=='reference':
        out,result=execute_reference(LAB,a.case); print(out); print(f"REFERENCE_ONLY {result['passed']}/{result['total']}; generated_skill_executions=0")
        return 0 if result['passed']==result['total'] else 4
    print(plan_execution(LAB,a.run,a.task)); return 0
if __name__=='__main__': raise SystemExit(main())
