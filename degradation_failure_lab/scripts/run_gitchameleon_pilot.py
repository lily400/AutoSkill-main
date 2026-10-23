"""One six-arm plumbing pilot; existing generator and native Agent, no retries."""
import json,os,pathlib,subprocess,sys,time,uuid
LAB=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB/'src'))
from degradation_lab.runner import ExperimentRunner
from degradation_lab.artifacts import export_run
from degradation_lab.io import read,write
ROOT=LAB/'runs/gitchameleon/import-20261022-001'
CONTROL_ROOT='/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab'

def main():
    assert read(LAB/'configs/gitchameleon_pilot/gates.json')['status']=='PASS'
    if not all(os.environ.get(k) for k in ['ZHIZENGZENG_API_KEY','DEEPSEEK_API_KEY']):raise RuntimeError('Use the configured credential entry; no request sent')
    resumed=sys.argv[1:]==['--resume-after-empty-read-fix']
    if resumed:
        previous=read(ROOT/'pilot_batch.json')
        assert previous[0]['status']=='COMPLETED_WITH_LOG_RECOVERY'
        assert all(r['status']=='NOT_RUN_AFTER_STOP' for r in previous[1:])
        with (ROOT/'pilot_resume.started').open('x') as f:f.write('Resume only five unattempted arms after empty-read logging fix.\n')
    else:
        with (ROOT/'pilot_batch.started').open('x') as f:f.write('Single-use six-arm pipeline pilot; never silently resend.\n')
    records=[];stop=False
    for tid in ['144','164']:
        for cid in ['c00','c01','c02']:
            record={'task_id':tid,'condition_id':cid,'status':'NOT_RUN_AFTER_STOP'};records.append(record)
            if resumed and tid=='144' and cid=='c00':
                records[-1]=previous[0];continue
            if stop:continue
            start=time.monotonic();runid='g'+uuid.uuid4().hex[:12]
            record.update(generator_run_id=runid,status='GENERATING')
            write(ROOT/'pilot_batch.json',records)
            try:
                print('Generating '+tid+'/'+cid+' '+runid,flush=True)
                target,code=ExperimentRunner(LAB).run('case'+tid+'_gch',cid,runid)
                record.update(generator_path=str(target),generator_exit_code=code)
                verification=export_run(LAB,runid,LAB/'results/exports'/runid)
                record['generation_verification']=verification['status']
                execution=read(target/'execution.json');record['generation_execution']=execution
                if code:
                    record['status']='GENERATION_FAILURE';stop=True;continue
                skills=read(LAB/'results/exports'/runid/'skill_files.json')
                record['skill_count']=skills['unique_program_skill_count']
                if not record['skill_count']:
                    record['status']='EMPTY_SKILL';continue
                checks=verification['checks']
                required=['input_hashes','upstream_unchanged','saved_artifact_hashes','all_inputs_parsed','fresh_skillbank','canonical_program_skills','responses_unchanged']
                if not all(checks.get(k) for k in required):raise RuntimeError('Generation integrity check failed')
                command=['docker','exec','--env','ZHIZENGZENG_API_KEY','--env','PYTHONPATH='+CONTROL_ROOT+':'+CONTROL_ROOT+'/src','harbor-p0-control-20261018','/opt/harbor-venv/bin/python','-B','-m','downstream_eval.gitchameleon_pilot','arm','--task',tid,'--condition',cid,'--generator-run',runid]
                print('Executing Agent '+tid+'/'+cid,flush=True)
                result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=1200)
                write(ROOT/('agent-command-'+tid+'-'+cid+'.json'),{'command':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
                agent=read(ROOT/'pilot'/tid/cid/'result.json');record['agent']=agent
                record['status']=agent['status'];stop=record['status']!='COMPLETED'
            except Exception as error:
                # Persist only the exception class; SDK strings can contain credentials.
                record.update(status='PIPELINE_STOP',error_type=type(error).__name__);stop=True
            finally:
                record['elapsed_seconds']=time.monotonic()-start
                write(ROOT/'pilot_batch.json',records)
                print(json.dumps({k:record[k] for k in ['task_id','condition_id','status','elapsed_seconds']}),flush=True)
    write(ROOT/'pilot_batch.json',records)
    return 0 if all(r['status']=='COMPLETED' for r in records) else 2

if __name__=='__main__':raise SystemExit(main())
