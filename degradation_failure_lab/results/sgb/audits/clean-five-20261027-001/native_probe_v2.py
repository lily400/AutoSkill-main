from pathlib import Path
import asyncio,json,sys,traceback
from unittest.mock import patch
root=Path('/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab')
sys.path[:0]=[str(root),str(root/'src')]
from degradation_lab.io import read,write,inventory,sha256
from downstream_eval.sgb import pilot,protocol
from downstream_eval.integration.skill_install import copy_packages
from downstream_eval.integration.skill_probe import probe_body_chunks
base=root/'results/sgb/audits/clean-five-20261027-001'
borrowed=root/'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001'
source=read(borrowed/'skills_manifest.json')['packages'];sid=next(iter(source));package=source[sid]
rows=[]
with patch('httpx.Client.send',side_effect=AssertionError('No model calls')),patch('httpx.AsyncClient.send',side_effect=AssertionError('No model calls')):
 for identity in read(base/'planned-identities.json'):
  if identity['task_id']!='pydantic-task-001':continue
  tid=identity['task_id'];task=pilot.load_binding(root,tid);adapter=pilot.adapter_for(root,task);output=base/'native-probes-v2'/tid
  output.mkdir(parents=True,exist_ok=False)
  # One historical package is borrowed solely to test transport. This is not this task's generation.
  copy_packages({sid:{'path':borrowed/'skills'/sid/'SKILL.md','files':package['files']}},output/'skills')
  packages={sid:package};conditions=task['conditions'];generator='borrowed-sanctuary-engineering-only'
  config=adapter.execution_config(output,generator,conditions);template=read(root/task['profile_template'])
  write(output/'task_config.json',task)
  profile={'experiment_id':output.name,'task_id':tid,'generator_run_id':generator,'conditions':conditions,
   'arms':list(conditions.values()),'trial_order':list(conditions),'repeats_per_arm':1,
   'model':template['model'],'budget':template['budget'],'protocol_id':'clean-pair-v1',
   'frozen_agent_image_id':read(root/task['runtime_lock'])['agent_image_id'],
   'task_config_sha256':sha256(output/'task_config.json'),'real_agent_outcome':False,
   'hard_http_budget':{'database':str(output/'budget.sqlite3'),'global_limit':12,'per_arm_limit':6,'order':list(conditions)}}
  write(output/'profile.json',profile);pilot._stage(output,packages,generator,conditions)
  paired={label:adapter.configure(output,label,'paid',config).model_dump(mode='json',exclude_none=True) for label in conditions}
  fairness=protocol.validate(root,profile,paired);write(output/'fairness.json',fairness)
  fixtures=read(root/task['fixtures'])
  for label,fixture_name in task['probes'].items():
   if label!='CleanSkill1':continue
   trial=None
   try:
    fixture=fixtures[fixture_name];path=output/(fixture_name+'.py');path.write_text(fixture['source'])
    native_config=adapter.configure(output,label,'probe',config)
    native_config.trial_name='audit5-p01-clean-retry'
    trial,native=asyncio.run(adapter.native_trial(native_config,path,probe_hook=probe_body_chunks))
    write(output/label/'native.json',native)
    assert not native.get('exception_info'),native.get('exception_info')
    score=adapter.grade_export(trial,output/label/'oracle')
    summary=read(trial.paths.trial_dir/'p1-observer/p1-summary.json')
    visibility=read(trial.paths.trial_dir/'body-visibility.json')
    expected=1 if label=='CleanSkill1' else 0
    accepted=(summary['stopped_before_model'] and summary['actual_http_attempts']==0
     and len(summary['controlled_probe_read_ids'])==expected and len(visibility['all_visible_ids'])==expected
     and score['infra_ok'] and score['candidate_binding_verified']
     and score['task_result']['passed']==fixture['passed'] and set(score['failed_tests'])==set(fixture['failed']))
    row={'task_id':tid,'condition':label,'status':'PASS' if accepted else 'FAIL','score':score,
         'model_calls':0,'real_agent_outcome':False,'skill_package_scope':'borrowed historical package; transport test only',
         'stopped_before_model':summary['stopped_before_model'],'body_ids_read':summary['controlled_probe_read_ids']}
   except Exception as exc:
    row={'task_id':tid,'condition':label,'status':'ERROR','error':str(exc),'traceback':traceback.format_exc(),'model_calls':0,'real_agent_outcome':False}
   finally:
    if trial:asyncio.run(trial.agent_environment.stop(delete=True))
   rows.append(row);write(base/'native-probe-results-v2.json',rows);print(json.dumps(row,ensure_ascii=False),flush=True)
