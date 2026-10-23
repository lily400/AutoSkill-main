"""Thin task adapter: native Harbor Agent, unchanged official GitChameleon scoring."""
import argparse,asyncio,hashlib,json,pathlib,shutil,subprocess,sys,uuid
from unittest.mock import patch
from harbor.models.trial.config import TrialConfig
from harbor.trial.trial import Trial
from degradation_lab.io import read,write,inventory
from downstream_eval.integration.skill_install import canonical_packages,copy_packages
from downstream_eval.integration.gitchameleon_agent import GitChameleonTerminus2
LAB=pathlib.Path(__file__).resolve().parents[1]
ROOT=LAB/'runs/gitchameleon/import-20261022-001'
def configure(tid,arm,out,stage,manifest,mode):
    profile=read(LAB/'configs/gitchameleon_pilot/agent.json');model=profile['model'];budget=profile['budget']
    task=LAB/f'downstream_eval/tasks/gitchameleon_{tid}_v1'
    raw={'trial_name':'gch-'+tid+'-'+arm+'-'+uuid.uuid4().hex[:8],'trials_dir':str(out/'trials'),'task':{'path':str(task)},'agent':{'import_path':'downstream_eval.integration.gitchameleon_agent:GitChameleonTerminus2','model_name':model['name'],'model_base_url':model['base_url'],'model_api_format':model['api_format'],'skills':[str(stage)],'override_timeout_sec':budget['agent_timeout_sec'],'override_setup_timeout_sec':budget['setup_timeout_sec'],'kwargs':{'gch_mode':mode,'gch_profile':str(LAB/'configs/gitchameleon_pilot/agent.json'),'gch_manifest':str(manifest),'max_turns':6,'temperature':0,'reasoning_effort':'none','enable_summarize':False,'proactive_summarization_threshold':0,'store_all_messages':True,'record_terminal_session':False,'tmux_pane_width':160,'tmux_pane_height':40,'llm_call_kwargs':{'max_completion_tokens':2048,'num_retries':0,'timeout':45}}},'environment':{'type':'docker','delete':False,'kwargs':{'enable_environment_dir_upload':False}},'verifier':{'disable':True}}
    if mode=='paid':raw['agent']['model_api_key_name']=model['api_key_environment_variable']
    return TrialConfig.model_validate(raw)

async def native_trial(config,zero=False):
    trial=await Trial.create(config)
    if zero:
        with patch('litellm.acompletion',side_effect=AssertionError('No model during probe')) as model:
            result=await trial.run();assert model.call_count==0
    else:result=await trial.run()
    return trial,result.model_dump(mode='json')

def probe():
    reports=[]
    for tid in ['144','164']:
        out=ROOT/('zero-'+tid+'-'+uuid.uuid4().hex[:6]);out.mkdir()
        sid='00000000-0000-4000-8000-000000000099';stage=out/'staged';package=stage/sid;package.mkdir(parents=True)
        (package/'SKILL.md').write_text('---\nname: installation-fixture-only\ndescription: Zero-model package installation check.\n---\nFIXTURE ONLY. This is not an Anything2Skill output.\n')
        manifest=out/'manifest.json';write(manifest,{'metadata':{sid:{'name':'installation-fixture-only','description':'Zero-model package installation check.'}},'files':inventory(stage),'probe_read_skill':tid=='144'})
        config=configure(tid,'probe',out,stage,manifest,'probe');write(out/'trial-config.json',config.model_dump(mode='json',exclude_none=True))
        trial,result=asyncio.run(native_trial(config,True));write(out/'native-result.json',result)
        summary=read(trial.paths.trial_dir/'gch-observer/summary.json') if (trial.paths.trial_dir/'gch-observer/summary.json').exists() else {}
        isolation_path=trial.paths.trial_dir/'gch-observer/isolation.jsonl'
        isolation=json.loads(isolation_path.read_text().splitlines()[-1]) if isolation_path.exists() else {}
        okay=not result.get('exception_info') and summary.get('stopped_before_model') and summary.get('actual_http_attempts')==0 and isolation.get('status')=='PASS'
        reports.append({'task_id':tid,'status':'PASS' if okay else 'FAIL_STOP','path':str(out),'trial_path':str(trial.paths.trial_dir),'image_id':isolation.get('image'),'summary':summary,'exception':result.get('exception_info')})
        if not okay:break
    write(ROOT/'agent_zero_model_validation.json',{'status':'PASS' if len(reports)==2 and all(r['status']=='PASS' for r in reports) else 'FAIL_STOP','reports':reports,'model_calls':0})
    print(json.dumps(reports,indent=2));return 0 if len(reports)==2 and all(r['status']=='PASS' for r in reports) else 2

def arm(tid,cid,runid):
    gate=read(LAB/'configs/gitchameleon_pilot/gates.json');assert gate['status']=='PASS'
    out=ROOT/'pilot'/tid/cid;out.mkdir(parents=True,exist_ok=False)
    case='case'+tid+'_gch';exports=LAB/'results/exports'/runid
    skills=read(exports/'skill_files.json');count=skills['unique_program_skill_count']
    cfg={'generator_run_id':runid,'case_id':case,'condition':cid,'expected_skill_count':count,'skill_manifest':str((exports/'skill_files.json').relative_to(LAB))}
    packages=canonical_packages(LAB,cfg)
    if not packages:write(out/'result.json',{'status':'NOT_RUN_EMPTY_SKILL','generator_run_id':runid});return 2
    stage=out/'staged';copy_packages(packages,stage)
    zero=read(ROOT/'agent_zero_model_validation.json');image=next(r['image_id'] for r in zero['reports'] if r['task_id']==tid)
    manifest=out/'manifest.json';write(manifest,{'metadata':{sid:p['metadata'] for sid,p in packages.items()},'files':inventory(stage),'frozen_environment_image_id':image})
    config=configure(tid,cid,out,stage,manifest,'paid');write(out/'trial-config.json',config.model_dump(mode='json',exclude_none=True))
    trial,result=asyncio.run(native_trial(config));write(out/'native-result.json',result)
    return finish(tid,out,runid,trial.paths.trial_dir,result)

def finish(tid,out,runid,trial_dir,result,recovered_summary=None):
    submissions=list(trial_dir.rglob('sample_'+tid+'.py'))
    summary_path=trial_dir/'gch-observer/summary.json';summary=recovered_summary if recovered_summary is not None else (read(summary_path) if summary_path.exists() else {})
    if result.get('exception_info') or len(submissions)!=1:
        write(out/'result.json',{'status':'AGENT_INFRA_OR_SUBMISSION_FAILURE','generator_run_id':runid,'submissions':[str(p) for p in submissions],'native_exception':result.get('exception_info'),'summary':summary});return 2
    submitted=out/'submitted.py';shutil.copyfile(submissions[0],submitted)
    base=LAB/'.external/gitchameleon/3a1b6045a6b2a276bd24d715589cb041f8eccb93'
    image=read(ROOT/'official_image_identity.json')['repo_digest']
    script='''import json,pathlib
from gitchameleon.data_model import Example,Solution
from gitchameleon.run_eval import process_record
base=pathlib.Path('/audit');tid='''+repr(tid)+'''
row=next(json.loads(l) for l in (base/'selected_original_rows.jsonl').read_text().splitlines() if json.loads(l)['example_id']==tid)
result=process_record(0,Example.model_validate(row),Solution.model_validate({'example_id':tid,'answer':pathlib.Path('/submission/submitted.py').read_text()}),{int(tid):row['test']},'/audit/venvs','/audit/upstream/dataset/hidden_tests')
pathlib.Path('/results/oracle.json').write_text(json.dumps(result,indent=2))
'''
    script_path=out/'score.py';script_path.write_text(script)
    command=['docker','run','--rm','--network','none','--mount',f'type=bind,source={base},target=/audit,readonly','--mount',f'type=bind,source={out},target=/submission,readonly','--mount',f'type=bind,source={out},target=/results','-e','PYTHONPATH=/audit/upstream',image,'-c','cd /app && pyenv global 3.9.19 && poetry run python /submission/score.py']
    scored=subprocess.run(command,capture_output=True,text=True,timeout=600);write(out/'oracle-command.json',{'command':command,'returncode':scored.returncode,'stdout':scored.stdout,'stderr':scored.stderr})
    oracle=read(out/'oracle.json') if (out/'oracle.json').exists() else {}
    write(out/'result.json',{'status':('COMPLETED_WITH_LOG_RECOVERY' if recovered_summary is not None else 'COMPLETED') if scored.returncode==0 else 'ORACLE_INFRA_FAILURE','generator_run_id':runid,'submitted_sha256':hashlib.sha256(submitted.read_bytes()).hexdigest(),'summary':summary,'oracle':oracle,'task_success':bool(oracle.get('passed') and oracle.get('passed_manual')),'observation_recovery':recovered_summary is not None})
    return 0 if scored.returncode==0 else 2

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['probe','arm']);parser.add_argument('--task');parser.add_argument('--condition');parser.add_argument('--generator-run');args=parser.parse_args()
    raise SystemExit(probe() if args.phase=='probe' else arm(args.task,args.condition,args.generator_run))
