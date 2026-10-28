from pathlib import Path
import sys,json,traceback
from unittest.mock import patch
root=Path('/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab')
sys.path[:0]=[str(root),str(root/'src')]
from downstream_eval.sgb.pilot import load_binding,adapter_for
from degradation_lab.io import read,write
base=root/'results/sgb/audits/clean-five-20261027-001'
rows=[]
with patch('httpx.Client.send',side_effect=AssertionError('Model calls forbidden')),patch('httpx.AsyncClient.send',side_effect=AssertionError('Model calls forbidden')):
 for identity in read(base/'planned-identities.json'):
  if identity['task_id'] not in ('scrapy-task-050','reviews_csv_conformance_validator_007'):continue
  task=load_binding(root,identity['task_id']);adapter=adapter_for(root,task)
  for label,fixture in read(root/task['fixtures']).items():
   target=base/'scoring-v2'/identity['task_id']/label
   candidate=target.parent/(label+'.py');candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_text(fixture['source'],encoding='utf-8')
   try:score=adapter.score(candidate,target)
   except Exception as error:score={'error':str(error),'traceback':traceback.format_exc()}
   rows.append({'task_id':identity['task_id'],'fixture':label,'score':score,'model_calls':0,'real_agent_outcome':False})
   write(base/'scoring-v2/results.json',rows)
   print(json.dumps({'task':identity['task_id'],'fixture':label,'score':score},ensure_ascii=False),flush=True)
