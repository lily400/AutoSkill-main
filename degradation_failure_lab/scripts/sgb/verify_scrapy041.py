"""Scrapy041 real containers and original Oracle, without any Agent/model/Skill run."""
import argparse
import asyncio
import json
from pathlib import Path
import sys
import tomllib

LAB = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(LAB), str(LAB/'src')]
# Reuse the zero-model import guard and Harbor environment constructors.
from scripts.sgb.verify_network_isolation import (
    EnvironmentFactory, TrialPaths, NetworkPolicy, TaskConfig, command)
from downstream_eval.integration.network_isolation import verify_environment_network
from downstream_eval.integration.request_budget import Ledger
from downstream_eval.sgb.task_adapters.scrapy041.adapter import execution_config, configure, export_submission
from downstream_eval.sgb.task_adapters.scrapy041.scoring import TASK, score, verify_assets, docker_executor
from degradation_lab.io import read, sha256, write

MIDDLEWARE_PROBE = """
import json,scrapy
from scrapy.downloadermiddlewares.offsite import OffsiteMiddleware
from scrapy.exceptions import IgnoreRequest
class Stats:
 def inc_value(self,*args,**kwargs):pass
class Demo(scrapy.Spider):
 name='offline-probe'
 allowed_domains=['example.com']
spider=Demo(); middleware=OffsiteMiddleware(Stats()); middleware.spider_opened(spider)
results={}
for label,kwargs in [('metadata',{'meta':{'allow_offsite':True}}),('missing',{}),('dont_filter',{'dont_filter':True})]:
 try:
  middleware.process_request(scrapy.Request('http://other.com/resource',**kwargs),spider)
  results[label]='ALLOWED'
 except IgnoreRequest:
  results[label]='REJECTED'
print(json.dumps({'scrapy':scrapy.__version__,'results':results,'network_requests':0,
 'scope':'direct in-memory middleware method; no crawl or network interception test'}))
"""


def config_fixture(output):
    prepared = output / 'configuration'
    conditions = {'Fixture':'NoSkill'}
    config = execution_config(prepared, 'zero-model-fixture', conditions)
    # Reuse the historical schema, not its identities, ledger, approval or model permission.
    profile = read(LAB / 'runs/eval/sgb/scrapy-task-024/s24d001/profile.json')
    profile.update(task_id=config.task_id, experiment_id=config.experiment_id,
                   generator_run_id=config.generator_run_id, conditions=conditions,
                   budget_scope=config.budget_scope, run_kind='zero_model_acceptance',
                   trial_order=list(conditions), arms=['NoSkill'],
                   approval_environment_variable='SCRAPY041_ALLOW_PAID')
    profile['hard_http_budget'] = {'database':str(prepared/'budget.sqlite3'),
                                  'order':list(conditions),'global_limit':0,'per_arm_limit':0}
    profile['budget']['max_requests'] = 0
    profile['model'] = {**profile['model'], 'name':'NO_MODEL_ZERO_CALLS',
                       'base_url':'http://127.0.0.1:1/forbidden', 'api_key_environment_variable':'UNUSED'}
    write(prepared/'profile.json',profile)
    stage=prepared/'staged/NoSkill';stage.mkdir(parents=True)
    write(prepared/'manifests/Fixture.json',{'arm':'Fixture','generator_run_id':config.generator_run_id,
                                          'staged_root':str(stage),'files':{},'metadata':{}})
    ledger=Ledger.create(prepared/'budget.sqlite3',{'scope':config.budget_scope,'order':['Fixture'],
          'budget':profile['budget'],'global_limit':0,'per_trial_limit':0,
          'trials':{'Fixture':'s41-fixture'},'files':{}})
    raw=configure(prepared,'Fixture','probe',config)
    write(prepared/'native-config.json',raw.model_dump(mode='json'))
    return raw,ledger


async def accept(output):
    output.mkdir(parents=True,exist_ok=False)
    manifest=verify_assets()
    fixtures=read(LAB/'tests/fixtures/sgb/scrapy-task-041/candidates.json')
    result={'status':'FAIL','task_id':'scrapy-task-041','run_kind':'zero_model_acceptance',
            'model_calls':0,'agent_runs':0,'generation_runs':0,'outcomes':{}}
    environment=None
    try:
        native,ledger=config_fixture(output)
        task=TaskConfig.model_validate(tomllib.loads((TASK/'task.toml').read_text()))
        paths=TrialPaths(trial_dir=output/'environment-only')
        policy=NetworkPolicy(network_mode='no-network')
        environment=EnvironmentFactory.create_environment_from_config(
            config=native.environment,environment_dir=TASK/'environment',
            environment_name='scrapy041-acceptance',session_id='s41-'+output.name,
            trial_paths=paths,task_env_config=task.environment,
            network_policy=policy,phase_network_policies=[policy])
        await environment.start(force_build=False)
        write(output/'agent-environment-network.json',await verify_environment_network(environment))
        check=await environment.exec("""python -B -c "import importlib.util,json,pathlib; from pathlib import Path
forbidden=['/tests','/solution','/oracle','/bridge','/observations','/workspace/tests','/var/run/docker.sock']
assert all(not Path(p).exists() for p in forbidden)
assert importlib.util.find_spec('scrapy') is None
assert not list(Path('/workspace/docs').iterdir())
assert not list(Path('/workspace/skill').iterdir())
print(json.dumps({'status':'PASS','absent':forbidden,'scrapy_installed':False,'docs_empty':True,'skills_empty':True}))"
""",timeout_sec=10)
        if check.return_code:raise RuntimeError('Task filesystem boundary check failed: '+check.stderr)
        write(output/'agent-environment-boundary.json',json.loads(check.stdout))
        cid=(await environment._run_docker_compose_command(['ps','-q','main'])).stdout.strip()
        inspected=json.loads(command(['inspect',cid]).stdout)[0]
        allowed={str(paths.agent_dir.resolve()),str(paths.verifier_dir.resolve()),
                 str(paths.host_artifact_path('main','/logs/artifacts').resolve())}
        mounts=[m for m in inspected['Mounts'] if m['Type']=='bind']
        if any(m['Source'] not in allowed for m in mounts):
            raise RuntimeError('Task container has unexpected mounts')
        write(output/'agent-environment-mounts.json',mounts)
        input_dir=output/'private-fixtures';input_dir.mkdir()
        for label,fixture in fixtures.items():
            path=input_dir/(label+'.py');path.write_text(fixture['source'])
            await environment.upload_file(source_path=path,target_path='/workspace/agent_output.py')
            exported,digest=await export_submission(environment,output/'exports'/label)
            if digest!=sha256(path):raise RuntimeError('Fixture/transport hash differs')
            outcome=await asyncio.to_thread(score,exported,output/'scores'/label,
                expected_sha256=digest,candidate_timeout=2 if label=='timeout' else 10)
            result['outcomes'][label]=outcome
            if 'category' in fixture:
                ok=not outcome['task_success'] and outcome['failure_category']==fixture['category']
            else:
                ok=(outcome['infra_ok'] and outcome['candidate_binding_verified']
                    and outcome['task_result']['tests']==10
                    and outcome['task_result']['passed']==fixture['passed']
                    and outcome['task_success']==(fixture['passed']==10))
                if 'failed' in fixture:
                    ok=ok and set(outcome['failed_tests'])==set(fixture['failed'])
            write(output/'progress.json',{'completed':label,'matched_expected':ok,'outcomes':result['outcomes']})
            print(json.dumps({'fixture':label,'matched_expected':ok,'score':outcome['task_result'],
                              'category':outcome['failure_category']}),flush=True)
            if not ok:raise RuntimeError('Fixture did not match original Oracle expectations: '+label)
        good=output/'exports/correct/agent_output.py'
        extra={
            'hash_mismatch':await asyncio.to_thread(score,good,output/'scores/hash_mismatch',expected_sha256='0'*64),
            'missing_file':await asyncio.to_thread(score,output/'absent.py',output/'scores/missing_file'),
            'scorer_timeout':await asyncio.to_thread(score,good,output/'scores/scorer_timeout',scorer_timeout=0.001)}
        expected={'hash_mismatch':'submission_hash_mismatch','missing_file':'invalid_submission',
                  'scorer_timeout':'scorer_timeout'}
        for label,outcome in extra.items():
            result['outcomes'][label]=outcome
            if outcome['task_success'] or outcome['failure_category']!=expected[label]:
                raise RuntimeError('Invalid/error case accepted: '+label)
        diagnostic=output/'middleware-diagnostic';diagnostic.mkdir()
        runtime=docker_executor(diagnostic,read(TASK/'runtime.lock.json')['scorer_image_id'])
        worker=runtime.start([])
        try:
            runtime.network(worker,'middleware')
            probe=json.loads(runtime.execute(worker,['python','-B','-c',MIDDLEWARE_PROBE]).stdout)
            if probe['results']!={'metadata':'ALLOWED','missing':'REJECTED','dont_filter':'ALLOWED'}:
                raise RuntimeError('Pinned middleware does not implement the source rule')
            write(diagnostic/'result.json',probe)
        finally:runtime.stop(worker)
        result.update(status='PASS',oracle_sha256=manifest['oracle_sha256'],
                      ledger_attempts=ledger.snapshot()['attempts'],
                      verified={'harbor_export':True,'candidate_scorer_separation':True,
                                'original_10_tests':True,'bounded_execution':True,
                                'direct_middleware_branch':True},
                      not_verified=['Real Agent execution','Generated Skill quality/body exposure',
                                    'Real crawling/network interception'])
        if result['ledger_attempts']:raise RuntimeError('Unexpected model budget attempt')
    except BaseException as error:
        result.update(status='FAIL',error_type=type(error).__name__,error=str(error))
        raise
    finally:
        if environment:
            try:
                await environment.stop(delete=True)
                result['environment_cleanup']='PASS'
            except Exception as error:
                result.update(status='FAIL',environment_cleanup=str(error))
        result['imported_agent_or_model_modules']=[n for n in sys.modules if n.startswith(
            ('harbor.agents','harbor.trial.trial','openai','litellm'))]
        if result['imported_agent_or_model_modules']:result['status']='FAIL'
        write(output/'acceptance.json',result)
        print(json.dumps({'status':result['status'],'path':str(output/'acceptance.json'),
                          'model_calls':0,'agent_runs':0}),flush=True)
    return 0 if result['status']=='PASS' else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raise SystemExit(asyncio.run(accept(args.output)))
