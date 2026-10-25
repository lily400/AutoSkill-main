"""Scrapy041 isolated grading; reuse the existing Docker executor, not its bool bridge."""
import importlib.util
import json
from pathlib import Path
import resource
import subprocess
import tempfile
from xml.etree import ElementTree

from degradation_lab.io import read, sha256, write
from downstream_eval.integration.network_isolation import PROBE, DEFAULT_TARGETS, evaluate

LAB = Path(__file__).resolve().parents[4]
TASK = LAB / 'downstream_eval/tasks/sgb/code_doc/scrapy-task-041'
LOAD_MODES = {
    'test_can_import':'import', 'test_has_spider_class':'classes',
    'test_allowed_domains':'domains', 'test_spider_produces_requests':'requests',
    'test_request_to_other_domain':'requests', 'test_allow_offsite_meta':'requests',
    'test_allow_offsite_is_boolean':'requests'}
TEST_NAMES = ['test_file_exists', 'test_can_import', 'test_imports_scrapy', 'test_has_spider_class',
              'test_allowed_domains', 'test_spider_produces_requests', 'test_request_to_other_domain',
              'test_allow_offsite_meta', 'test_allow_offsite_is_boolean', 'test_no_middleware_modification']
LIMIT = 2 * 1024 * 1024


class CandidateProtocolError(RuntimeError):
    pass


def verify_assets():
    manifest = read(TASK / 'scorer/source_manifest.json')
    for name, digest in manifest['files'].items():
        if sha256(TASK / name) != digest:
            raise ValueError('Scrapy041 asset changed: ' + name)
    if sha256(TASK / 'scorer/oracle/eval.py') != manifest['oracle_sha256']:
        raise ValueError('Original Oracle changed')
    return manifest


def docker_executor(output, image):
    # Load the unchanged 024 Docker utility in a private module namespace.
    # None of its task-specific preparation/scoring functions are called.
    helper = LAB / 'downstream_eval/tasks/sgb/code_doc/scrapy-task-024/scorer/preflight.py'
    spec = importlib.util.spec_from_file_location('scrapy041_reused_docker', helper)
    reused = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reused)
    reused.BASE_IMAGE = image

    class Docker(reused.Docker):
        def call(self, args, *positional, **kwargs):
            if args[0] == 'create':
                args = [args[0], '--dns','127.0.0.1','--cap-drop','NET_ADMIN',
                        '--cap-drop','NET_RAW','--cap-drop','SYS_ADMIN', *args[1:]]
            return super().call(args, *positional, **kwargs)

        def bounded_exec(self, cid, args, *, payload=None, timeout=10):
            command = ['docker','exec', *(['-i'] if payload is not None else []), cid, *args]
            def limit_files():
                resource.setrlimit(resource.RLIMIT_FSIZE, (LIMIT, LIMIT))
            with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
                try:
                    process = subprocess.run(command, input=payload, stdout=out, stderr=err,
                                             text=True, timeout=timeout, preexec_fn=limit_files)
                    timed_out = False
                    code = process.returncode
                except subprocess.TimeoutExpired:
                    timed_out, code = True, None
                out.seek(0); err.seek(0)
                stdout, stderr = out.read(LIMIT+1), err.read(LIMIT+1)
            record = {'command':command, 'return_code':code, 'timed_out':timed_out,
                      'stdout':stdout[:20000].decode('utf-8', 'replace'),
                      'stderr':stderr[:4000].decode('utf-8', 'replace'),
                      'stdout_bytes':len(stdout), 'stderr_bytes':len(stderr)}
            self.records.append(record); write(self.output / 'commands.json', self.records)
            if timed_out:
                raise TimeoutError('Candidate/scorer process deadline exceeded')
            if len(stdout) >= LIMIT or len(stderr) >= LIMIT or code not in (0,1):
                raise CandidateProtocolError('Process failed or exceeded output limit')
            return code, stdout.decode('utf-8')

        def network(self, cid, label):
            inspected = json.loads(self.call(['inspect',cid]).stdout)[0]
            probe = self.execute(cid, ['python','-B','-c',PROBE.read_text(),json.dumps(DEFAULT_TARGETS)])
            report = evaluate(inspected, json.loads(probe.stdout), DEFAULT_TARGETS)
            write(self.output / (label + '-network.json'), report)
            if report['status'] != 'PASS':
                raise RuntimeError('Worker/scorer network admission failed')
            return inspected

    return Docker(Path(output))


def parse_junit(path):
    counts = dict(tests=0, passed=0, failed=0, errors=0, skipped=0)
    failed = []
    if Path(path).is_file():
        for case in ElementTree.parse(path).iter('testcase'):
            counts['tests'] += 1
            kind = next((k for k in ('failure','error','skipped') if case.find(k) is not None), None)
            counts[{'failure':'failed','error':'errors','skipped':'skipped'}.get(kind,'passed')] += 1
            if kind:
                failed.append(case.attrib.get('name'))
    return counts, failed


def score(submission, output, *, expected_sha256=None, candidate_timeout=10, scorer_timeout=30):
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    result = {'task_id':'scrapy-task-041', 'task_success':False, 'infra_ok':False,
              'model_calls':0, 'run_kind':'isolated_oracle',
              'failure_category':'environment_error', 'task_result':dict(tests=0,passed=0,failed=0,errors=0,skipped=0)}
    cid = sid = None
    docker = None
    phase = 'assets'
    try:
        manifest = verify_assets()
        lock = read(TASK / 'runtime.lock.json')
        image = lock['scorer_image_id']
        source = Path(submission)
        if not source.is_file() or source.is_symlink() or source.stat().st_size > 131072:
            result['failure_category'] = 'invalid_submission'
            return result
        digest = sha256(source)
        result['candidate_sha256'] = digest
        if expected_sha256 is not None and digest != expected_sha256:
            result['failure_category'] = 'submission_hash_mismatch'
            return result
        candidate = output / 'candidate'; candidate.mkdir()
        frozen = candidate / 'agent_output.py'; frozen.write_bytes(source.read_bytes())
        if sha256(frozen) != digest:
            raise ValueError('Submission changed during freezing')
        result.update(oracle_sha256=manifest['oracle_sha256'], image_id=image,
                      protocol='unchanged original 10 tests + isolated object observations')
        docker = docker_executor(output, image)
        actual = docker.call(['image','inspect',image,'--format','{{.Id}}']).stdout.strip()
        if actual != image:
            raise ValueError('Scoring image identity changed')
        cid = docker.start([(frozen,'/submission/agent_output.py',False),
                            (TASK / 'scorer/worker.py','/runtime/worker.py',False)])
        inspected = docker.network(cid, 'candidate')
        # A separate command verifies the execution boundary independently of submitted code.
        boundary_code = """import json,pathlib,os
paths=['/oracle','/bridge','/observations','/results','/tests','/solution','/var/run/docker.sock']
assert os.getuid()==65532
assert all(not pathlib.Path(p).exists() for p in paths)
print(json.dumps({'uid':os.getuid(),'absent':paths}))
"""
        boundary = json.loads(docker.execute(cid, ['python','-B','-c',boundary_code]).stdout)
        write(output / 'candidate-boundary.json', {'status':'PASS', **boundary,
              'mounts':[{'source':m['Source'],'target':m['Destination'],'rw':m['RW']}
                        for m in inspected['Mounts'] if m['Type']=='bind']})
        loads = {}
        phase = 'candidate'
        for name, mode in LOAD_MODES.items():
            code, stdout = docker.bounded_exec(cid, ['python','-I','-B','/runtime/worker.py'],
                                              payload=json.dumps({'mode':mode}), timeout=candidate_timeout)
            try:
                value = json.loads(stdout)
                if (code != 0 or type(value) is not dict or value.get('schema_version') != 1
                        or value.get('candidate_sha256') != digest or type(value.get('ok')) is not bool):
                    raise ValueError('Invalid observation identity')
                if value['ok'] and (type(value.get('spiders')) is not list or len(value['spiders']) > 64):
                    raise ValueError('Invalid Spider observation')
            except (ValueError, TypeError) as error:
                raise CandidateProtocolError(str(error)) from error
            loads[name] = value
        docker.stop(cid); cid = None
        if sha256(frozen) != digest:
            raise ValueError('Frozen candidate changed')
        observations = output / 'observations'; observations.mkdir()
        envelope = observations / 'envelope.json'
        write(envelope, {'protocol':'scrapy041-object-observation-v1', 'candidate_sha256':digest,
                         'oracle_sha256':manifest['oracle_sha256'], 'loads':loads, 'test_names':TEST_NAMES})
        verdict = output / 'verdict'; verdict.mkdir(); verdict.chmod(0o777)
        phase = 'scorer'
        sid = docker.start([(frozen,'/submission/agent_output.py',False),
                            (TASK / 'scorer/oracle','/oracle',False),
                            (TASK / 'scorer/oracle_bridge.py','/bridge/oracle_bridge.py',False),
                            (envelope,'/observations/envelope.json',False),
                            (verdict,'/results',True)])
        docker.network(sid, 'scorer')
        code, _ = docker.bounded_exec(sid, ['env','PYTHONPATH=/bridge','TEST_ROOT_DIR=/submission',
            'python','-B','-m','pytest','-p','no:cacheprovider','-p','oracle_bridge',
            '/oracle/eval.py','-q','--junitxml=/results/junit.xml'], timeout=scorer_timeout)
        counts, failures = parse_junit(verdict / 'junit.xml')
        bridge = read(verdict / 'bridge.json')
        bound = (bridge['candidate_sha256'] == digest and bridge['oracle_sha256'] == manifest['oracle_sha256']
                 and not bridge['candidate_code_imported'] and not bridge['candidate_marker_visible']
                 and bridge['loads'] == list(LOAD_MODES) and sha256(frozen) == digest)
        infra = bound and counts['tests'] == 10 and not counts['errors'] and not counts['skipped']
        passed = infra and code == 0 and counts['passed'] == 10
        result.update(task_success=passed, infra_ok=infra, task_result=counts, failed_tests=failures,
                      observation_sha256=sha256(envelope), candidate_binding_verified=bound,
                      failure_category='none' if passed else ('oracle_assertion_failure' if infra else 'scorer_integrity_error'))
    except TimeoutError as error:
        result.update(failure_category=phase + '_timeout', error=str(error))
    except CandidateProtocolError as error:
        result.update(failure_category=phase + '_protocol_error', error=str(error))
    except Exception as error:
        result.update(failure_category='environment_error', error_type=type(error).__name__, error=str(error))
    finally:
        if docker:
            for container in (cid,sid):
                if container:
                    docker.stop(container)
        write(output / 'result.json', result)
    return result
