"""FLA original nine assertions with candidate execution outside the trusted scorer."""
import json
from pathlib import Path

from degradation_lab.io import read, sha256, write
from downstream_eval.sgb.task_adapters.scrapy041.scoring import docker_executor, parse_junit, CandidateProtocolError
from .common import LAB, bind, native_trial

TASK_ID = 'fla_packet_cadence_scope_validator_002'
TASK = LAB / 'downstream_eval/tasks/sgb/audited' / TASK_ID
HERE = Path(__file__).parent


def verify_assets(task=TASK):
    manifest = read(task / 'source_manifest.json')
    for name, digest in manifest['files'].items():
        if sha256(task / name) != digest:
            raise ValueError('Audited task asset changed: ' + name)
    return manifest


def score(submission, output, *, expected_sha256=None, task=TASK, task_id=TASK_ID,
          expected_tests=9, setup_code='import math\nimport numpy as np'):
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    result = {'task_id': task_id, 'task_success': False, 'infra_ok': False, 'model_calls': 0,
              'candidate_binding_verified': False, 'failure_category': 'environment_error',
              'task_result': dict(tests=0, passed=0, failed=0, errors=0, skipped=0)}
    docker = None
    cid = sid = None
    phase = 'assets'
    try:
        manifest = verify_assets(task)
        source = Path(submission)
        if not source.is_file() or source.is_symlink() or source.stat().st_size > 131072:
            result['failure_category'] = 'invalid_submission'
            return result
        digest = sha256(source)
        if expected_sha256 is not None and expected_sha256 != digest:
            result['failure_category'] = 'submission_hash_mismatch'
            return result
        frozen = output / 'agent_output.py'; frozen.write_bytes(source.read_bytes())
        assert sha256(frozen) == digest
        image = read(task / 'runtime.lock.json')['scorer_image_id']
        oracle_hash = manifest['files']['oracle/eval.py']
        bundle = read(task / 'oracle/testcases.json')
        if bundle.get('setup_code', '').strip() != setup_code:
            raise ValueError('Released task setup code changed')
        if len(bundle['test_cases']) != expected_tests:
            raise ValueError('Released task case count changed')
        docker = docker_executor(output, image)
        assert docker.call(['image', 'inspect', image, '--format', '{{.Id}}']).stdout.strip() == image
        cid = docker.start([(frozen, '/submission/agent_output.py', False),
                            (HERE / 'fla_worker.py', '/runtime/worker.py', False)])
        docker.network(cid, 'candidate')
        check = "import pathlib,os; assert os.getuid()==65532; assert all(not pathlib.Path(p).exists() for p in ('/oracle','/observations','/bridge','/results','/tests','/solution','/var/run/docker.sock')); print('PASS')"
        assert docker.execute(cid, ['python', '-B', '-c', check]).stdout.strip() == 'PASS'
        observations = []
        phase = 'candidate'
        for case in bundle['test_cases']:
            code, raw = docker.bounded_exec(cid, ['python', '-I', '-B', '/runtime/worker.py'],
                payload=json.dumps({'input': case['input'], 'setup_code': setup_code}), timeout=10)
            value = json.loads(raw)
            if code != 0 or value.get('candidate_sha256') != digest or type(value.get('ok')) is not bool:
                raise CandidateProtocolError('Invalid candidate observation')
            observations.append(value)
        docker.stop(cid); cid = None
        assert sha256(frozen) == digest
        envelope = output / 'envelope.json'
        write(envelope, {'candidate_sha256': digest, 'oracle_sha256': oracle_hash,
                         'observations': observations})
        verdict = output / 'verdict'; verdict.mkdir(); verdict.chmod(0o777)
        phase = 'scorer'
        sid = docker.start([(frozen, '/submission/agent_output.py', False),
            (task / 'oracle', '/oracle', False), (HERE / 'fla_bridge.py', '/bridge/fla_bridge.py', False),
            (envelope, '/observations/envelope.json', False), (verdict, '/results', True)])
        docker.network(sid, 'scorer')
        code, stdout = docker.bounded_exec(sid, ['env', 'PYTHONPATH=/bridge', 'TEST_ROOT_DIR=/submission',
            'python', '-B', '-m', 'pytest', '-p', 'no:cacheprovider', '-p', 'fla_bridge',
            '/oracle/eval.py', '-q', '--junitxml=/results/junit.xml'], timeout=30)
        (output / 'pytest.stdout.txt').write_text(stdout, encoding='utf-8')
        counts, failures = parse_junit(verdict / 'junit.xml')
        bridge = read(verdict / 'bridge.json')
        bound = (bridge['candidate_sha256'] == digest == sha256(source) == sha256(frozen)
                 and bridge['oracle_sha256'] == oracle_hash and bridge['observations'] == expected_tests
                 and bridge['candidate_code_imported'] is False)
        infra = bound and counts['tests'] == expected_tests and not counts['errors'] and not counts['skipped']
        passed = infra and code == 0 and counts['passed'] == expected_tests
        result.update(task_success=passed, infra_ok=infra, task_result=counts, failed_tests=failures,
            candidate_binding_verified=bound, candidate_sha256=digest, oracle_sha256=oracle_hash,
            observation_sha256=sha256(envelope),
            failure_category='none' if passed else ('oracle_assertion_failure' if infra else 'scorer_integrity_error'))
    except TimeoutError as error:
        result.update(failure_category=phase + '_timeout', error=str(error))
    except CandidateProtocolError as error:
        result.update(failure_category=phase + '_protocol_error', error=str(error))
    except Exception as error:
        result.update(error_type=type(error).__name__, error=str(error))
    finally:
        if docker:
            for container in (cid, sid):
                if container:
                    docker.stop(container)
        write(output / 'result.json', result)
    return result


execution_config, configure, grade_export, paid_batch = bind(TASK_ID, score, verify_assets)
