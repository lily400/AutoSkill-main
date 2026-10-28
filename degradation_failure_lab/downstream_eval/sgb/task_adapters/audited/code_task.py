"""Configured object-observation pilots over the existing native Agent and Docker scorer."""
import json
from pathlib import Path
from types import SimpleNamespace

from degradation_lab.io import inside,read,sha256,write
from downstream_eval.sgb.downstream_authorization import validate_prepared
from downstream_eval.sgb.task_adapters.scrapy041.scoring import docker_executor,parse_junit,CandidateProtocolError
from . import fla
from .common import bind,native_trial

HERE=Path(__file__).parent


def for_task(root,config):
    root=Path(root).resolve();task=inside(root,config['task_path']);policy=config['code_observation']
    if config['task_path']!='downstream_eval/tasks/sgb/audited/'+config['task_id']:
        raise ValueError('Configured object task location differs')

    def verify_assets():
        manifest=fla.verify_assets(task);original=inside(root,manifest['original_task'])
        for local,published in [('instruction.md','instruction.md'),('task.original.toml','task.toml'),
                                ('oracle/eval.py','tests/eval.py'),('oracle/test.original.sh','tests/test.sh')]:
            if sha256(task/local)!=sha256(original/published):raise ValueError('Released task asset changed: '+local)
        for source in manifest['source_documents']:
            if sha256(inside(root,source['path']))!=source['sha256']:raise ValueError('Source changed')
        if policy['family'] not in ('pydantic001','pydantic004','scrapy050'):
            raise ValueError('Unreviewed object observation family')
        observer=policy.get('crawl_observer')
        if observer and (policy['family']!='scrapy050' or observer['protocol_id']!='sgb-scrapy050-response-received-v2'
                         or sha256(inside(root,observer['path']))!=observer['sha256']):
            raise ValueError('Approved crawl observer identity/hash changed')
        return manifest

    def score(submission,output,*,expected_sha256=None):
        output=Path(output);output.mkdir(parents=True,exist_ok=False)
        result={'task_id':config['task_id'],'task_success':False,'infra_ok':False,'model_calls':0,
                'candidate_binding_verified':False,'failure_category':'environment_error',
                'task_result':dict(tests=0,passed=0,failed=0,errors=0,skipped=0)}
        docker=cid=sid=None;phase='assets'
        try:
            manifest=verify_assets();source=Path(submission)
            if not source.is_file() or source.is_symlink() or source.stat().st_size>131072:
                result.update(infra_ok=True,failure_category='invalid_submission');return result
            digest=sha256(source)
            if expected_sha256 is not None and digest!=expected_sha256:
                result['failure_category']='submission_hash_mismatch';return result
            frozen=output/'agent_output.py';frozen.write_bytes(source.read_bytes())
            image=read(task/'runtime.lock.json')['scorer_image_id'];oracle_hash=manifest['files']['oracle/eval.py']
            docker=docker_executor(output,image)
            assert docker.call(['image','inspect',image,'--format','{{.Id}}']).stdout.strip()==image
            cid=docker.start([(frozen,'/submission/agent_output.py',False),(HERE/'code_worker.py','/runtime/worker.py',False)])
            docker.network(cid,'candidate')
            check="import os,pathlib; assert os.getuid()==65532; assert all(not pathlib.Path(p).exists() for p in ('/oracle','/bridge','/results','/tests','/solution','/observations','/var/run/docker.sock')); print('PASS')"
            assert docker.execute(cid,['python','-B','-c',check]).stdout.strip()=='PASS'
            phase='candidate'
            code,raw=docker.bounded_exec(cid,['python','-I','-B','/runtime/worker.py'],
                payload=json.dumps({'family':policy['family'],'operations':policy['operations']}),timeout=10)
            observation=json.loads(raw)
            if code!=0 or observation.get('candidate_sha256')!=digest or type(observation.get('ok')) is not bool:
                raise CandidateProtocolError('Invalid object observation identity')
            if not observation['ok']:
                write(output/'candidate-error.json',observation)
                result.update(infra_ok=True,failure_category='invalid_submission',candidate_sha256=digest,
                              error=observation.get('error'));return result
            docker.stop(cid);cid=None
            envelope={'family':policy['family'],'candidate_sha256':digest,'oracle_sha256':oracle_hash,
                      'observation':observation,'test_names':policy['test_names']}
            if policy['family']=='scrapy050':
                observer=policy.get('crawl_observer')
                probe=inside(root,observer['path']) if observer else task/'crawl_probe.py'
                envelope['observation_protocol']=observer['protocol_id'] if observer else 'released-parse-probe-v1'
                cid=docker.start([(frozen,'/submission/agent_output.py',False),(probe,'/runtime/crawl_probe.py',False)],writable_workspace=True)
                docker.network(cid,'crawl')
                code,stdout=docker.bounded_exec(cid,['python','-B','/runtime/crawl_probe.py'],timeout=20)
                envelope['crawl']={'returncode':code,'stdout':stdout,'stderr':''}
                docker.stop(cid);cid=None
            assert sha256(frozen)==digest
            path=output/'envelope.json';write(path,envelope)
            verdict=output/'verdict';verdict.mkdir();verdict.chmod(0o777)
            phase='scorer'
            sid=docker.start([(frozen,'/submission/agent_output.py',False),(task/'oracle','/oracle',False),
                (HERE/'code_bridge.py','/bridge/code_bridge.py',False),(path,'/observations/envelope.json',False),
                (verdict,'/results',True)])
            docker.network(sid,'scorer')
            code,stdout=docker.bounded_exec(sid,['env','PYTHONPATH=/bridge:/opt/sgb/site','TEST_ROOT_DIR=/submission',
                'python','-B','-m','pytest','-p','no:cacheprovider','-p','code_bridge','/oracle/eval.py','-q',
                '--junitxml=/results/junit.xml'],timeout=30)
            (output/'pytest.stdout.txt').write_text(stdout,encoding='utf-8')
            counts,failed=parse_junit(verdict/'junit.xml');bridge=read(verdict/'bridge.json')
            bound=(bridge['candidate_sha256']==digest==sha256(source)==sha256(frozen)
                   and bridge['oracle_sha256']==oracle_hash and bridge['candidate_code_imported'] is False)
            infra=bound and counts['tests']==config['expected_oracle_tests'] and not counts['errors'] and not counts['skipped']
            passed=infra and code==0 and counts['passed']==config['expected_oracle_tests']
            result.update(infra_ok=infra,task_success=passed,candidate_binding_verified=bound,
                candidate_sha256=digest,oracle_sha256=oracle_hash,observation_sha256=sha256(path),
                task_result=counts,failed_tests=failed,
                failure_category='none' if passed else ('oracle_assertion_failure' if infra else 'scorer_integrity_error'))
        except TimeoutError as exc:result.update(failure_category=phase+'_timeout',error=str(exc))
        except CandidateProtocolError as exc:result.update(failure_category=phase+'_protocol_error',error=str(exc))
        except Exception as exc:result.update(error_type=type(exc).__name__,error=str(exc))
        finally:
            if docker:
                for container in (cid,sid):
                    if container:docker.stop(container)
            write(output/'result.json',result)
        return result

    execution_config,configure,grade_export,paid=bind(config['task_id'],score,verify_assets)
    def paid_batch(output):
        validate_prepared(root,config,output)
        return paid(output)
    return SimpleNamespace(verify_assets=verify_assets,score=score,execution_config=execution_config,
                           configure=configure,grade_export=grade_export,native_trial=native_trial,paid_batch=paid_batch)
