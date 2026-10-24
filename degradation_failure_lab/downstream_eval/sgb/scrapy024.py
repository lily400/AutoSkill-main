"""Frozen six-trial Task-024 calibration using native Harbor/Terminus and the preflight scorer."""
import argparse
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
from unittest.mock import patch

os.environ['LITELLM_LOCAL_MODEL_COST_MAP']='True'
from degradation_lab.io import inventory,read,sha256,write
from downstream_eval.integration.skill_install import copy_packages
from downstream_eval.integration.request_budget import Ledger
from downstream_eval.integration.p1_observer import body_visible
from downstream_eval.p1 import fairness_identity
from downstream_eval.sgb import runner

LAB=Path(__file__).resolve().parents[2]
TASK=LAB/'downstream_eval/tasks/sgb/code_doc/scrapy-task-024'
ORDER=['NoSkill1','CleanSkill1','NoSkill2','CleanSkill2','NoSkill3','CleanSkill3']


def execution_config(output):
    return runner.ExecutionConfig(
        task_id='scrapy-task-024',task_path=TASK,experiment_id='scrapy024-s24r005-'+output.name,
        generator_run_id='s24r005',budget_scope='scrapy-task-024/s24r005/initial-calibration',
        agent_import_path='downstream_eval.sgb.scrapy_agent:ScrapyTerminus2',trial_prefix='s24-',
        conditions={label:'CleanSkill' if label.startswith('CleanSkill') else 'NoSkill' for label in ORDER},
        skill_conditions=('CleanSkill',),unscorable_categories=('environment_error','submission_ambiguous'))


def calibration_output(root,experiment):
    if not re.fullmatch(r's24d[0-9]{3}',experiment):raise ValueError('Use an s24dNNN experiment ID')
    return runner.experiment_output(root,'scrapy-task-024',experiment,
                                    legacy_roots=(Path(root)/'runs/downstream/scrapy-task-024',))


def scorer_module():
    path=TASK/'scorer/preflight.py'
    spec=importlib.util.spec_from_file_location('scrapy024_original_preflight',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.verify()
    return module


def configure(output,label,mode):
    return runner.configure(output,label,mode,execution_config(output))


def grade_export(trial,output):
    submitted,failure=runner.collect_submission(trial.paths.artifacts_dir,'agent_output.py')
    if failure:return failure
    module=scorer_module()
    class ScoringDocker(module.Docker):
        def start(self, mounts, writable_workspace=False):
            for source,target,writable in mounts:
                if writable and target=='/results':
                    # Only this new score-output directory is writable to UID65532.
                    source.chmod(0o777)
            return super().start(mounts,writable_workspace)
    return module.score_submission(submitted,output,ScoringDocker(output))


async def native_trial(config,fixture=None):
    from harbor.trial.trial import Trial
    trial=await Trial.create(config)
    if fixture:
        native_phase=Trial._run_agent_phase
        async def phase(self,*args,**kwargs):
            result=await native_phase(self,*args,**kwargs)
            await self.agent_environment.upload_file(source_path=fixture,target_path='/workspace/agent_output.py')
            return result
        with patch.object(Trial,'_run_agent_phase',phase), \
             patch('litellm.acompletion',side_effect=AssertionError('Zero-model probe forbids model calls')), \
             patch('litellm.aresponses',side_effect=AssertionError('Zero-model probe forbids model calls')):
            result=await trial.run()
    else:
        result=await trial.run()
    return trial,result.model_dump(mode='json')


def verify_frozen(output):
    return runner.verify_frozen(LAB,output)


def preparation(output):
    if (output/'readiness.json').exists() and read(output/'readiness.json')['status']=='PASS':
        verify_frozen(output)
        return 0
    if (output/'budget.sqlite3').exists():
        raise RuntimeError('Prepared budget exists; never re-prepare or reset it')
    attempt=output/'engineering'/('attempt-%03d' % (len(list((output/'engineering').glob('attempt-*')))+1))
    attempt.mkdir(parents=True,exist_ok=False)
    import importlib.metadata
    from downstream_eval.integration.harbor_adapter import verify_sources
    _,lock=verify_sources(LAB)
    if importlib.metadata.version('harbor')!=lock['harbor_version']:
        raise ValueError('Harbor version mismatch')
    write(output/'runtime_versions.json',{n:importlib.metadata.version(n) for n in ['harbor','litellm','openai','httpx']})
    image='scrapy024-agent:s24r005'
    build=subprocess.run(['docker','build','--network=none','--pull=false','-t',image,str(TASK/'environment')],
                         capture_output=True,text=True)
    write(output/'image-build.json',{'returncode':build.returncode,'stdout':build.stdout,'stderr':build.stderr})
    if build.returncode:raise RuntimeError('Offline Task-024 image build failed')
    image_id=subprocess.run(['docker','image','inspect',image,'--format','{{.Id}}'],
                            capture_output=True,text=True,check=True).stdout.strip()
    # The task adapter adds only a pinned runtime image; instruction and Oracle bytes stay unchanged.
    toml=(TASK/'task.original.toml').read_text(encoding='utf-8')
    toml=toml.replace('[environment]\n','[environment]\ndocker_image = "'+image+'"\n')
    (TASK/'task.toml').write_text(toml,encoding='utf-8')
    profile=read(LAB/'downstream_eval/configs/p1_smoke.json')
    profile.update(experiment_id='scrapy024-s24r005-'+output.name,task_id='scrapy-task-024',arms=['NoSkill','CleanSkill'],trial_order=ORDER,
                   repeats_per_arm=3,approval_environment_variable='SCRAPY024_ALLOW_PAID',
                   price_usd_per_million_tokens=None,frozen_agent_image_id=image_id)
    profile.pop('gold_skill_id',None)
    profile['hard_http_budget']={'database':str(output/'budget.sqlite3'),'per_arm_limit':6,'global_limit':36,'order':ORDER}
    write(output/'profile.json',profile)
    skill_manifest=read(output/'skills_manifest.json')
    metadata={sid:v['metadata'] for sid,v in skill_manifest['packages'].items()}
    for arm in ['NoSkill','CleanSkill']:
        stage=output/'staged'/arm
        if not stage.exists():
            if arm=='NoSkill':stage.mkdir(parents=True)
            else:
                packages={sid:{'path':output/'skills'/sid/'SKILL.md','files':p['files']} for sid,p in skill_manifest['packages'].items()}
                copy_packages(packages,stage)
    for label in ORDER:
        arm='CleanSkill' if label.startswith('CleanSkill') else 'NoSkill'
        stage=output/'staged'/arm
        write(output/'manifests'/(label+'.json'),{'arm':label,'staged_root':str(stage),'files':inventory(stage),
              'metadata':metadata if arm=='CleanSkill' else {},'generator_run_id':'s24r005',
              'target_rule_id':'scrapy024.ftp-default-overwrite',
              'package_versions':{sid:p['version'] for sid,p in skill_manifest['packages'].items()} if arm=='CleanSkill' else {}})
    configs={label:configure(output,label,'paid') for label in ORDER}
    identities={label:fairness_identity(c.model_dump(mode='json',exclude_none=True)) for label,c in configs.items()}
    if len(set(identities.values()))!=1:raise ValueError('Conditions differ beyond Skill treatment/output identity')
    for label,c in configs.items():write(output/'configs'/(label+'.json'),c.model_dump(mode='json',exclude_none=True))
    write(output/'fairness.json',{'status':'PASS','shared_config_hashes':identities,'order':ORDER,
          'repeats_per_condition':3,'instruction_sha256':sha256(TASK/'instruction.md'),
          'no_skill_count':0,'clean_skill_count':len(metadata),'image_id':image_id,
          'native_verifier_disabled':True,'independent_scorer':'original 19 assertions + isolated candidate response bridge'})
    reports=[]
    for label,fixture,passed in [('NoSkill1','correct',19),('CleanSkill1','ftp_mutant',18)]:
        config=configure(output,label,'probe')
        config.trials_dir=attempt/'trials'
        trial,native=asyncio.run(native_trial(config,TASK/'scorer/fixtures/submissions'/fixture/'agent_output.py'))
        write(attempt/label/'native.json',native)
        score=grade_export(trial,attempt/label/'oracle')
        summary=read(trial.paths.trial_dir/'p1-observer/p1-summary.json') if (trial.paths.trial_dir/'p1-observer/p1-summary.json').exists() else {}
        expected=len(metadata) if label.startswith('CleanSkill') else 0
        good=(not native.get('exception_info') and summary.get('stopped_before_model') and
              summary.get('actual_http_attempts')==0 and score['task_result']['tests']==19 and
              score['task_result']['passed']==passed and score['rule_result']['passed']==(passed==19) and
              len(summary.get('controlled_probe_read_ids',[]))==expected and
              len(summary.get('full_body_visible_ids_ignoring_terminal_whitespace',[]))==expected)
        report={'label':label,'status':'PASS' if good else 'FAIL','controlled_fixture':fixture,
                'native_exception':native.get('exception_info'),'trial':str(trial.paths.trial_dir),
                'summary':summary,'oracle':score,'model_api_calls':0,'real_agent_outcome':False}
        write(attempt/label/'report.json',report);reports.append(report)
        if not good:break
    checks={'status':'PASS' if len(reports)==2 and all(r['status']=='PASS' for r in reports) else 'BLOCKED',
            'model_api_calls':0,'real_agent_runs':0,'reports':reports,'image_id':image_id,
            'harbor_version':lock['harbor_version'],'harbor_commit':lock['harbor_commit']}
    write(output/'readiness.json',checks)
    if checks['status']!='PASS':return 2
    frozen={}
    for prefix in ['downstream_eval/integration','downstream_eval/sgb','downstream_eval/tasks/sgb/code_doc/scrapy-task-024']:
        for name,h in inventory(LAB/prefix).items():frozen[prefix+'/'+name]=h
    for rel in ['scripts/sgb/scrapy024.py','scripts/sgb/Invoke-Scrapy024Calibration.ps1',
                'scripts/Invoke-ProjectCredential.ps1','downstream_eval/configs/runner.lock.json']:
        frozen[rel]=sha256(LAB/rel)
    for name,h in inventory(LAB/'.external/harbor-full/src/harbor').items():
        frozen['.external/harbor-full/src/harbor/'+name]=h
    for name,h in inventory(output).items():
        if not name.startswith(('probes/','probe-trials/','engineering/')) and name not in ['execution_manifest.json','budget.sqlite3']:
            frozen[(output/ name).relative_to(LAB).as_posix()]=h
    write(output/'execution_manifest.json',frozen)
    if not (output/'budget.sqlite3').exists():
        Ledger.create(output/'budget.sqlite3',{'scope':'scrapy-task-024/s24r005/initial-calibration','order':ORDER,
          'global_limit':36,'per_trial_limit':6,'trials':{k:c.trial_name for k,c in configs.items()},
          'files':{str(LAB/k):h for k,h in frozen.items()},'budget':profile['budget']})
    return 0


def body_exposure(trial,output,label):
    observer=trial.paths.trial_dir/'p1-observer'
    summary=read(observer/'p1-summary.json') if (observer/'p1-summary.json').exists() else {}
    requests=[json.loads(s) for s in (observer/'p1-model-requests.jsonl').read_text().splitlines()] if (observer/'p1-model-requests.jsonl').exists() else []
    responses=[json.loads(s) for s in (observer/'p1-model-http.jsonl').read_text().splitlines()] if (observer/'p1-model-http.jsonl').exists() else []
    successful={r['logical_request_number'] for r in responses if r.get('http_status') and 200<=r['http_status']<300}
    manifest=read(output/'manifests'/(label+'.json'))
    exposed=[]
    for sid in summary.get('model_read_ids',[]):
        text=(Path(manifest['staged_root'])/sid/'SKILL.md').read_text(encoding='utf-8')
        if any(n in successful and body_visible(text,'\n'.join(m['content'] for m in req['messages'] if isinstance(m.get('content'),str)))
               for n,req in enumerate(requests,1)):
            exposed.append(sid)
    return {'summary':summary,'model_body_exposed_ids':sorted(exposed),
            'evidence':'kernel access + entire frozen body in messages of a successful HTTP model request',
            'rule_following':'Not inferred; assess output and independent Oracle separately'}


def paid_batch(output):
    if os.environ.get('SCRAPY024_ALLOW_PAID')!='1' or not os.environ.get('ZHIZENGZENG_API_KEY'):
        raise RuntimeError('Use the explicit credential launch command')
    if read(output/'readiness.json')['status']!='PASS':raise RuntimeError('Engineering readiness has not passed')
    verify_frozen(output)
    import importlib.metadata
    if read(output/'runtime_versions.json')!={n:importlib.metadata.version(n) for n in ['harbor','litellm','openai','httpx']}:
        raise RuntimeError('Frozen Harbor/SDK runtime versions changed')
    return runner.execute_batch(LAB,output,execution_config(output),
        run_trial=native_trial,grade=grade_export,exposure=body_exposure,
        task_success=lambda score:score['task_result'].get('passed')==19 and score['task_result'].get('tests')==19)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['prepare','run']);parser.add_argument('--experiment',required=True)
    args=parser.parse_args()
    output=calibration_output(LAB,args.experiment)
    return preparation(output) if args.phase=='prepare' else paid_batch(output)


if __name__=='__main__':raise SystemExit(main())
