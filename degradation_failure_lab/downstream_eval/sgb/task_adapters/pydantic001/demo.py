"""Pydantic001 source/case/Oracle engineering demonstration; never runs an LLM."""
import argparse
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree

from degradation_lab.catalog import CaseManager
from degradation_lab.io import inside, inventory, read, sha256, write
from degradation_lab.runner import ExperimentRunner
from degradation_lab.sgb import selected_tasks

LAB=Path(__file__).resolve().parents[4]
TASK_PATH='downstream_eval/tasks/sgb/code_doc/pydantic-task-001'
CASE_ID='case001_pyd'


def verify_assets(root):
    task=inside(root,TASK_PATH);manifest=read(task/'asset_manifest.json')
    for name,digest in manifest['files'].items():
        if sha256(inside(task,name))!=digest:raise ValueError('Task asset drift: '+name)
    _,rows=selected_tasks(root,['pydantic-task-001']);row=rows[0]
    # The pinned engineering demo survives registration of a separate formal adapter.
    if row['generation_case_id']!=CASE_ID:
        raise ValueError('Task/case binding drift')
    official=inside(root,read(inside(root,'configs/datasets/sgb.json'))['snapshot'])
    prefix='skill_evaluation/code_doc/pydantic/pydantic-task-001/'
    for local,original in [('instruction.md','instruction.md'),('task.original.toml','task.toml'),
                           ('scorer/oracle/eval.py','tests/eval.py'),('scorer/oracle/test.original.sh','tests/test.sh')]:
        if sha256(task/local)!=sha256(official/(prefix+original)):
            raise ValueError('Official task bytes changed: '+local)
    bundle=CaseManager(root).load(CASE_ID)
    if bundle['case']['source_ids']!=[s['source_id'] for s in row['sources']]:
        raise ValueError('Generation source binding drift')
    return task,row


def score(root,submission,output):
    """Run the unmodified release Oracle inside the pinned offline container."""
    task,row=verify_assets(root);lock=read(task/'runtime.lock.json')
    image=subprocess.run(['docker','image','inspect',lock['image'],'--format','{{.Id}}'],
                         check=True,capture_output=True,text=True).stdout.strip()
    if image!=lock['image_id']:raise ValueError('Runtime image drift')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    candidate=output/'candidate';candidate.mkdir()
    submitted=candidate/'agent_output.py';submitted.write_bytes(Path(submission).read_bytes())
    results=output/'verdict';results.mkdir();results.chmod(0o777)
    # Source documents, Skills, answers, Docker socket and credentials are not mounted.
    command=['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL',
        '--security-opt','no-new-privileges','--user','65532:65532','--pids-limit','64',
        '--memory','256m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=16m',
        '--env','TEST_ROOT_DIR=/submission','--env','PYTHONDONTWRITEBYTECODE=1',
        '--env','PYTEST_DISABLE_PLUGIN_AUTOLOAD=1',
        '--mount',f'type=bind,source={candidate.resolve()},target=/submission,readonly',
        '--mount',f'type=bind,source={(task/"scorer/oracle").resolve()},target=/oracle,readonly',
        '--mount',f'type=bind,source={results.resolve()},target=/results',lock['image'],
        'python','-B','-m','pytest','-p','no:cacheprovider','/oracle/eval.py','-q',
        '--junitxml=/results/junit.xml']
    completed=subprocess.run(command,capture_output=True,text=True,timeout=120)
    write(output/'command.json',{'command':command,'returncode':completed.returncode,
          'stdout':completed.stdout,'stderr':completed.stderr})
    junit=results/'junit.xml';counts={'tests':0,'passed':0,'failed':0,'errors':0,'skipped':0}
    if junit.exists():
        for case in ElementTree.parse(junit).iter('testcase'):
            counts['tests']+=1
            kind=next((name for name in ['failure','error','skipped'] if case.find(name) is not None),None)
            counts[{'failure':'failed','error':'errors','skipped':'skipped'}.get(kind,'passed')]+=1
    infra=completed.returncode in (0,1) and counts['tests']==16 and not counts['errors'] and not counts['skipped']
    report={'task_key':row['task_key'],'task_id':row['original_task_id'],
        'task_success':infra and counts['passed']==16 and completed.returncode==0,'infra_ok':infra,
        'task_result':counts,'oracle_sha256':sha256(task/'scorer/oracle/eval.py'),
        'submission_sha256':sha256(submitted),'image_id':image,'model_calls':0,
        'scope':'Original Oracle score only; log entries are candidate-reported, not independent execution tracing.'}
    write(output/'result.json',report)
    return report


def demonstrate(root,audit_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',audit_id):raise ValueError('Unsafe audit ID')
    target=inside(root,'results/sgb/audits/'+audit_id)
    if target.exists():raise FileExistsError(target)
    task,row=verify_assets(root)
    generation=ExperimentRunner(root).plan(CASE_ID,'clean')
    before=inventory(task);fixtures=inside(root,'tests/fixtures/sgb/pydantic-task-001')
    outcomes={label:score(root,fixtures/label/'agent_output.py',target/label)
              for label in ['correct','swapped_order']}
    good=outcomes['correct']['infra_ok'] and outcomes['correct']['task_success']
    bad=outcomes['swapped_order']['infra_ok'] and not outcomes['swapped_order']['task_success']
    if inventory(task)!=before:raise ValueError('Task assets changed during scoring')
    result={'status':'PASS' if good and bad else 'FAIL','scope':'SOURCE_CASE_AND_ORACLE_ENGINEERING_DEMO',
        'task_id':row['original_task_id'],'case_id':CASE_ID,'generation_plan':generation,
        'outcomes':outcomes,'model_calls':0,'real_generation_runs':0,'real_agent_runs':0,
        'not_yet_verified':['Real generated Skills','Agent NoSkill/CleanSkill outcomes','Skill read/body exposure'],
        'original_oracle_limit':'Candidate-reported logs and permissive after/wrap ordering; retain separately from any stronger rule check.'}
    write(target/'demonstration.json',result)
    return {'status':result['status'],'path':str(target/'demonstration.json'),'model_calls':0,
            'scores':{k:v['task_result'] for k,v in outcomes.items()}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-id',required=True)
    args=parser.parse_args();result=demonstrate(LAB,args.audit_id)
    import json
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS' else 2


if __name__=='__main__':raise SystemExit(main())
