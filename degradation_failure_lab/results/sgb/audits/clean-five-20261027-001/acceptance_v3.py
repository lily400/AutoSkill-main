from pathlib import Path
import sys,json
from unittest.mock import patch
root=Path('/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab');sys.path[:0]=[str(root),str(root/'src')]
from downstream_eval.sgb.pilot import load_binding,adapter_for
from downstream_eval.sgb.task_adapters.scrapy041.scoring import docker_executor,parse_junit
from degradation_lab.io import read,write
base=root/'results/sgb/audits/clean-five-20261027-001';rows=[];edges=[]
with patch('httpx.Client.send',side_effect=AssertionError('No model calls')),patch('httpx.AsyncClient.send',side_effect=AssertionError('No model calls')):
 for tid in ['pydantic-task-001','pydantic-task-004','scrapy-task-050']:
  task=load_binding(root,tid);adapter=adapter_for(root,task);fixtures=read(root/task['fixtures'])
  for label,fixture in fixtures.items():
   target=base/'scoring-v3'/tid/label;candidate=target.parent/(label+'.py');candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_text(fixture['source'])
   score=adapter.score(candidate,target)
   assert score['infra_ok'] and score['candidate_binding_verified'],score
   assert score['task_result']['passed']==fixture['passed'] and set(score['failed_tests'])==set(fixture['failed']),score
   rows.append({'task_id':tid,'fixture':label,'score':score,'real_agent_outcome':False,'model_calls':0})
   write(base/'scoring-v3/results.json',rows);print(tid,label,score['task_result'],flush=True)
  if tid=='pydantic-task-001':continue
  good=fixtures['correct']['source']
  if tid=='pydantic-task-004':
   source=good.replace('BaseModel, Discriminator, Tag','BaseModel, Discriminator, Tag, AfterValidator')
   source=source.replace('Pet = Annotated[',"class SpecializedCat(Cat):\n    pass\n\ndef specialize(value):\n    return SpecializedCat.model_validate(value.model_dump()) if type(value) is Cat else value\n\nPet = Annotated[")
   source=source.replace('Discriminator(pet_discriminator)]','Discriminator(pet_discriminator), AfterValidator(specialize)]')
   label='valid_model_subclass'
  else:
   source=good+"\n_finding_calls = 0\n_original_finding = get_depth_limit_zero_finding\ndef get_depth_limit_zero_finding():\n    global _finding_calls\n    _finding_calls += 1\n    result = _original_finding()\n    if _finding_calls > 1:\n        result['effective_max_depth'] = 1\n    return result\n"
   label='inconsistent_second_finding'
  target=base/'edge-cases'/tid;target.mkdir(parents=True,exist_ok=False);candidate=target/'agent_output.py';candidate.write_text(source)
  score=adapter.score(candidate,target/'bridged');lock=read(root/task['runtime_lock']);output=target/'original';output.mkdir();verdict=output/'verdict';verdict.mkdir();verdict.chmod(0o777)
  docker=docker_executor(output,lock['scorer_image_id']);cid=None
  try:
   cid=docker.start([(candidate,'/submission/agent_output.py',False),(root/task['task_path']/'oracle','/oracle',False),(verdict,'/results',True)])
   code,stdout=docker.bounded_exec(cid,['env','PYTHONPATH=/opt/sgb/site','TEST_ROOT_DIR=/submission','python','-B','-m','pytest','-p','no:cacheprovider','/oracle/eval.py','-q','--junitxml=/results/junit.xml'],timeout=30)
   (output/'pytest.stdout.txt').write_text(stdout);counts,failed=parse_junit(verdict/'junit.xml')
   assert score['infra_ok'] and score['task_result']==counts and set(score['failed_tests'])==set(failed),score
   assert score['task_success']==(label=='valid_model_subclass'),score
   row={'task_id':tid,'fixture':label,'assertions_equal':True,'counts':counts,'failed_tests':failed,'bridge_result':score,'real_agent_outcome':False,'model_calls':0};edges.append(row);print(tid,label,counts,flush=True)
   write(base/'edge-cases/results.json',edges)
  finally:
   if cid:docker.stop(cid)
