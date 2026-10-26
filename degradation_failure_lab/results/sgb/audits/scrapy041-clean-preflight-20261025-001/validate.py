"""Zero-model Scrapy041 input/config validation; not a generation or Agent run."""
import ast
import hashlib
import importlib.abc
import json
from pathlib import Path
import sys
import unittest

LAB = Path('/repo/degradation_failure_lab')
UP = Path('/repo/AutoSkill-main')
OUT = LAB / 'results/sgb/audits/scrapy041-clean-preflight-20261025-001'
sys.path[:0] = [str(LAB), str(LAB/'src'), str(UP)]

class NoAgentModel(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if any(fullname == p or fullname.startswith(p+'.')
               for p in ('openai','litellm','harbor.agents','harbor.trial.trial')):
            raise AssertionError('Model/Agent module forbidden in input preflight: '+fullname)
sys.meta_path.insert(0, NoAgentModel())

boundary = {'active':False,'reads':[]}
def hook(event,args):
    if event in ('socket.connect','socket.getaddrinfo','subprocess.Popen','os.system'):
        raise AssertionError('Network/subprocess forbidden in zero-model preflight')
    if event == 'open' and boundary['active'] and isinstance(args[0],str):
        p=Path(args[0]).resolve()
        if p.is_relative_to(LAB):
            if not p.is_relative_to(OUT/'input-snapshot'):
                raise AssertionError('Loader escaped source-only snapshot: '+str(p))
            boundary['reads'].append(str(p))
sys.addaudithook(hook)
from degradation_lab.catalog import CaseManager
from degradation_lab.runner import ExperimentRunner
from degradation_lab.sgb import audit_registry
from degradation_lab.io import read, sha256
from AutoSkill4Doc.document.file_loader import load_file_units

manager=CaseManager(LAB)
bundle=manager.load('case041_scrapy')
condition,manifest=manager.condition(bundle,'clean')
runner=ExperimentRunner(LAB,manager)
_,_,_,config=runner.resolve('case041_scrapy','clean')
assert config['pipeline']['domain_type']=='scrapy'
assert config['pipeline']['max_documents']==4
assert len(manifest['inputs'])==4
plan=runner.plan('case041_scrapy','clean')
gate_failed=False
try:
    runner.run('case041_scrapy','clean','s41r001')
except RuntimeError as error:
    assert 'execution gate has not passed' in str(error)
    gate_failed=True
assert gate_failed and not (LAB/'runs/gen/sgb/case041_scrapy').exists()
boundary['active']=True
units,loaded=load_file_units(str(OUT/'input-snapshot'),max_files=4)
boundary['active']=False
assert len(units)==4
verified=[]
for unit,item in zip(units,manifest['inputs']):
    expected=LAB/item['path']
    assert Path(unit['source_file']).name==expected.name
    assert unit['text']==expected.read_text(encoding='utf-8')
    assert sha256(Path(unit['source_file']))==item['sha256']
    verified.append({'source_id':item['source_id'],'title':unit['title'],
        'sha256':item['sha256'],'characters':len(unit['text']),'file_read':unit['source_file']})
assert len(set(boundary['reads']))==4
registry=audit_registry(LAB)
# Source-only check of the actual entry: one inputs directory, one run-local store.
adapter=ast.parse((LAB/'src/degradation_lab/adapter.py').read_text(encoding='utf-8'))
calls=[n for n in ast.walk(adapter) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='extract_from_doc']
assert len(calls)==1
assert {k.arg for k in calls[0].keywords} >= {'sdk','file_path','registry_root','metadata'}
result={'status':'PASS','scope':'case mapping + official file loader + closed generation gate; no extraction',
    'task_id':'scrapy-task-041','case_id':'case041_scrapy','plan':plan,'effective_generation_config':config,
    'document_count':len(units),'ordered_sources':verified,'loader_reads':boundary['reads'],
    'loader_input_boundary':'PASS for this loader invocation only; not an OS sandbox for future paid generation',
    'registry_audit':registry,'generation_gate_blocks_before_model_import':gate_failed,
    'initial_generation_store':'NOT_CREATED; runner creates a fresh run-local store after admission',
    'generation_status':'NOT_RUN','agent_status':'NOT_RUN','model_calls':0,
    'unknown':['actual outline/windows','candidate/compiled/registered counts','cross-document decisions',
               'final active deployable Skill set','real Agent Skill exposure and outcome']}
(OUT/'preflight.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
suite=unittest.TestSuite()
for name in ['test_scrapy041','test_sgb_runner','test_sgb_task_contract','test_network_isolation']:
    suite.addTests(unittest.defaultTestLoader.discover(str(LAB/'tests'),pattern=name+'.py'))
with (OUT/'unit-tests.log').open('w',encoding='utf-8') as stream:
    tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
summary={'tests':tests.testsRun,'failures':len(tests.failures),'errors':len(tests.errors),
         'skipped':len(tests.skipped),'status':'PASS' if tests.wasSuccessful() else 'FAIL',
         'model_calls':0,'agent_runs':0}
(OUT/'unit-test-summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preflight':'PASS','documents':len(units),'tests':summary},ensure_ascii=False))
if not tests.wasSuccessful(): raise SystemExit(1)
