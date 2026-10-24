"""BeautifulSoup Task-037 offline preparation and independent scorer contract."""
import ast
import copy
import json
from pathlib import Path
import re
import tomllib
from xml.etree import ElementTree

from degradation_lab.io import inside, inventory, read, sha256, write
from downstream_eval.integration.harbor_adapter import validate_task_network_modes, verify_sources
from downstream_eval.integration.skill_install import copy_packages
from downstream_eval.sgb import runner
from .scoring import UNSCORABLE

TASK_ID = 'beautifulsoup4-task-037'
TASK_PATH = 'downstream_eval/tasks/sgb/code_doc/' + TASK_ID
MAPPING = TASK_PATH + '/offline_adapter.json'


def verify_assets(root):
    root = Path(root)
    mapping = read(root / MAPPING)
    dataset = read(root / 'configs/datasets/sgb.json')
    registry = inside(root, dataset['registry'])
    snapshot = inside(root, dataset['snapshot'])
    if sha256(registry) != dataset['registry_sha256'] or sha256(snapshot / 'snapshot_manifest.json') != dataset['snapshot_manifest_sha256']:
        raise ValueError('SGB registry or snapshot identity changed')
    saved = read(snapshot / 'snapshot_manifest.json')
    rows = [json.loads(line) for line in registry.read_text(encoding='utf-8').splitlines()]
    matches = [row for row in rows if row['task_key'] == mapping['task_key']]
    if len(matches) != 1:
        raise ValueError('BeautifulSoup task mapping is missing or ambiguous')
    row = matches[0]
    metadata = read(root / TASK_PATH / 'adapter.json')
    if metadata['task_key'] != mapping['task_key'] or any(not s['origin'].startswith(mapping['data_source_root'] + '/materials/docs/') for s in row['sources']):
        raise ValueError('BeautifulSoup metadata/source mapping differs from registry')
    if (mapping['task_id'] != TASK_ID or row['original_task_id'] != TASK_ID
            or mapping['revision'] != dataset['revision'] or saved['revision'] != dataset['revision']
            or row['dataset_revision'] != dataset['revision']
            or mapping['evaluation_root'] + '/task.toml' not in row['official_assets']
            or mapping['source_ids'] != [s['source_id'] for s in row['sources']]):
        raise ValueError('BeautifulSoup task/source identity mismatch')
    for name, digest in row['official_assets'].items():
        if saved['files'].get(name) != digest or sha256(inside(snapshot, name)) != digest:
            raise ValueError('Official BeautifulSoup asset changed: ' + name)
    for source in row['sources']:
        if (sha256(inside(root, source['manifest'])) != source['manifest_sha256']
                or sha256(inside(root, source['path'])) != source['sha256']
                or saved['files'].get(source['origin']) != source['sha256']
                or sha256(inside(snapshot, source['origin'])) != source['sha256']):
            raise ValueError('BeautifulSoup source identity mismatch')
    official = inside(snapshot, mapping['evaluation_root'])
    data = tomllib.loads((official / 'task.toml').read_text(encoding='utf-8'))
    if (data['task']['task_id'] != TASK_ID or data['submission'] != {'kind':'agent_output', 'target_file':'agent_output.py'}
            or data['validation']['runner'] != 'tests/test.sh'):
        raise ValueError('Unsupported BeautifulSoup submission or verifier contract')
    tests = [n.name for n in ast.walk(ast.parse((official / 'tests/eval.py').read_bytes()))
             if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
    if tests != mapping['oracle_tests']:
        raise ValueError('Original BeautifulSoup test inventory changed')
    _, lock = verify_sources(root)
    if lock['harbor_version'] != mapping['harbor_version'] or lock['harbor_commit'] != mapping['harbor_commit']:
        raise ValueError('Pinned Harbor identity differs from adapter')
    return official, mapping


def execution_config(task, profile):
    if profile.get('task_id') != TASK_ID:
        raise ValueError('Explicit BeautifulSoup task identity required')
    generator = profile['generator_run_id']
    if not profile['budget_scope'].startswith(TASK_ID + '/' + generator + '/'):
        raise ValueError('BeautifulSoup budget scope must bind its task and generator')
    return runner.ExecutionConfig(
        task_id=TASK_ID, task_path=Path(task), experiment_id=profile['experiment_id'],
        generator_run_id=generator, budget_scope=profile['budget_scope'],
        agent_import_path='downstream_eval.sgb.beautifulsoup_agent:OfflineBeautifulSoupTerminus2',
        trial_prefix='bs37-', conditions=profile['conditions'],
        skill_conditions=tuple(profile['skill_conditions']),
        unscorable_categories=UNSCORABLE)


def _image(value):
    if not isinstance(value, str) or not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}', value):
        raise ValueError('Explicit image digest required; image availability is NOT verified')
    return json.dumps(value)


def _new_external_workspace(root, destination):
    destination = Path(destination).resolve()
    if destination.is_relative_to(Path(root).resolve().parent):
        raise ValueError('Offline preparation must stay outside the project and historical evidence')
    if destination.exists():
        raise FileExistsError('Never overwrite an existing offline workspace')
    return destination


def prepare(root, destination, *, profile, packages, agent_image, verifier_image, verifier_timeout_sec):
    """Materialize a NEW external workspace only; create no ledger, Trial or success result."""
    root = Path(root)
    official, mapping = verify_assets(root)
    destination = _new_external_workspace(root, destination)
    agent, verifier = _image(agent_image), _image(verifier_image)
    if type(verifier_timeout_sec) not in (int, float) or not 0 < verifier_timeout_sec < float('inf'):
        raise ValueError('Explicit finite verifier timeout required')
    profile = copy.deepcopy(profile)
    profile.update(execution_status='OFFLINE_ONLY', model_api_results=False)
    task = destination / TASK_ID
    config = execution_config(task, profile)
    if not packages or any(p['path'].name != 'SKILL.md' or not p.get('metadata') for p in packages.values()):
        raise ValueError('Explicit Skill packages with metadata required; generation provenance remains unverified')
    if not set(config.skill_conditions) or not (set(config.conditions.values()) - set(config.skill_conditions)):
        raise ValueError('Both NoSkill and Skill conditions must be explicit')
    # Identity/profile checks precede any workspace creation.
    if (Path(profile['hard_http_budget']['database']).resolve() != (destination / 'budget.sqlite3').resolve()
            or profile['trial_order'] != list(config.conditions)
            or profile['hard_http_budget']['order'] != list(config.conditions)
            or set(profile['arms']) != set(config.conditions.values())):
        raise ValueError('Offline profile conditions or budget path mismatch')
    task_toml = (
        'schema_version = "1.4"\n'
        'artifacts = [{source = "/workspace/agent_output.py", destination = "workspace/agent_output.py"}]\n\n'
        '[metadata]\ntask_id = "' + TASK_ID + '"\npreparation_status = "OFFLINE_ONLY"\n\n'
        '[agent]\ntimeout_sec = ' + str(profile['budget']['agent_timeout_sec']) + '\n\n'
        '[environment]\ndocker_image = ' + agent + '\nworkdir = "/workspace"\nnetwork_mode = "no-network"\n\n'
        '[verifier]\nenvironment_mode = "separate"\ntimeout_sec = ' + str(verifier_timeout_sec) + '\n\n'
        '[verifier.environment]\ndocker_image = ' + verifier + '\nworkdir = "/workspace"\nnetwork_mode = "no-network"\n')
    tomllib.loads(task_toml)
    destination.mkdir(parents=True)
    (task / 'environment').mkdir(parents=True)
    (task / 'instruction.md').write_bytes((official / 'instruction.md').read_bytes())
    (task / 'task.toml').write_text(task_toml, encoding='utf-8', newline='\n')
    write(destination / 'profile.json', profile)
    for condition in dict.fromkeys(config.conditions.values()):
        stage = destination / 'staged' / condition
        if condition in config.skill_conditions:
            copy_packages(packages, stage)
        else:
            stage.mkdir(parents=True)
    for label, condition in config.conditions.items():
        stage = destination / 'staged' / condition
        metadata = {sid:p['metadata'] for sid, p in packages.items()} if condition in config.skill_conditions else {}
        write(destination / 'manifests' / (label + '.json'),
              {'arm':label, 'task_id':TASK_ID, 'generator_run_id':config.generator_run_id,
               'staged_root':str(stage), 'files':inventory(stage), 'metadata':metadata})
        raw = runner.trial_config(destination, label, 'probe', config)
        write(destination / 'configs' / (label + '.json'), raw)
    report = validate_prepared(root, destination)
    write(destination / 'offline_preparation.json', report)
    return report


def validate_prepared(root, destination):
    official, mapping = verify_assets(root)
    destination = Path(destination)
    profile = read(destination / 'profile.json')
    task = destination / TASK_ID
    config = execution_config(task, profile)
    if profile.get('execution_status') != 'OFFLINE_ONLY' or profile.get('model_api_results') is not False:
        raise ValueError('Offline preparation cannot authorize execution or model results')
    if set(inventory(task)) != {'instruction.md', 'task.toml'} or not (task / 'environment').is_dir():
        raise ValueError('Agent task must contain only instruction/config and an empty image environment')
    if sha256(task / 'instruction.md') != sha256(official / 'instruction.md'):
        raise ValueError('Original instruction identity changed')
    data = tomllib.loads((task / 'task.toml').read_text(encoding='utf-8'))
    if (data.get('schema_version') != '1.4' or data['metadata'].get('task_id') != TASK_ID
            or data['artifacts'] != [{'source':'/workspace/agent_output.py', 'destination':'workspace/agent_output.py'}]
            or data['environment'].get('workdir') != '/workspace'
            or data['verifier']['environment'].get('workdir') != '/workspace'
            or data['environment'].get('network_mode') != 'no-network'
            or data['verifier']['environment'].get('network_mode') != 'no-network'):
        raise ValueError('Prepared Harbor environment/submission contract mismatch')
    for environment in (data['environment'], data['verifier']['environment']):
        _image(environment['docker_image'])
    validate_task_network_modes(root, task)
    for label in config.conditions:
        raw = runner.trial_config(destination, label, 'probe', config)
        if read(destination / 'configs' / (label + '.json')) != raw:
            raise ValueError('Saved trial configuration differs from current explicit profile')
    return {'status':'OFFLINE_PREPARED', 'execution_status':'NOT_RUN', 'task_id':TASK_ID,
            'experiment_id':config.experiment_id, 'generator_run_id':config.generator_run_id,
            'budget_scope':config.budget_scope, 'generator_identity_verified':False,
            'task_success':None, 'model_api_results':False, 'model_calls':0,
            'task_schema_validation':'static contract; full pinned TaskConfig tested separately',
            'agent_visible_files':['instruction.md', 'task.toml'],
            'skill_installation':'host byte copies only; remote install NOT_RUN',
            'skill_paths':{'instruction_declares':'/workspace/skill', 'harbor_injection':'/harbor/skills',
                           'status':'native Skill index; runtime mapping unverified'},
            'blockers':['runtime_images_unverified', 'agent_isolation_not_executed', 'no_execution_budget_created',
                        'generator_provenance_unverified', 'original_oracle_revision_required',
                        'verifier_candidate_isolation_unverified', 'no_real_trial'],
            'oracle_tests':len(mapping['oracle_tests'])}


def scoring_plan(root, submission, output, *, image, timeout_sec,
                 export_receipt=None, export_controller=None, trial_id=None):
    from .scoring import regular_file
    official, mapping = verify_assets(root)
    _image(image)
    if type(timeout_sec) not in (int, float) or not 0 < timeout_sec < float('inf'):
        raise ValueError('Explicit finite scorer timeout required')
    submission = Path(submission).absolute()
    if not regular_file(submission, submission.parent):
        raise ValueError('Exported regular submission missing')
    workspace = _new_external_workspace(root, output)
    inputs = [submission, official / 'tests/eval.py', official / 'tests/test.sh']
    if any(p.resolve().is_relative_to(workspace) or workspace.is_relative_to(p.resolve()) for p in inputs):
        raise ValueError('Scorer workspace overlaps a readonly input')
    plan = {'task_id':TASK_ID, 'image':image, 'image_verified':False, 'timeout_sec':timeout_sec,
            'execution_status':'NOT_RUN', 'backend_status':'NOT_IMPLEMENTED',
            'workspace':str(workspace), 'output_dir':str(workspace / 'outputs'),
            'candidate_source':str(submission), 'candidate_sha256':sha256(submission),
            'input_sha256':{str(p):sha256(p) for p in inputs},
            'required_outputs':{'junit_xml':'junit.xml', 'reward':'reward.txt',
                                'stdout':'stdout.bin', 'stderr':'stderr.bin'},
            'network_mode':'no-network', 'workdir':'/workspace',
            'required_preinstalled':{'beautifulsoup4':'4.12.3', 'pytest':'8.4.1'},
            'preflight_required':True, 'preflight_status':'NOT_RUN',
            'candidate_isolation':'UNVERIFIED: original pytest imports the submitted module in its own process',
            'mounts':[
                {'source':str(submission), 'target':'/workspace/agent_output.py', 'writable':False},
                {'source':str(official / 'tests/eval.py'), 'target':'/workspace/tests/eval.py', 'writable':False},
                {'source':str(official / 'tests/test.sh'), 'target':'/workspace/tests/test.sh', 'writable':False},
                {'source':str(workspace / 'outputs'), 'target':'/logs/verifier', 'writable':True}],
            'command':['bash', '/workspace/tests/test.sh'],
            'env':{'TEST_ROOT_DIR':'/workspace', 'PYTHON':'python3', 'PYTHONDONTWRITEBYTECODE':'1',
                   'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1',
                   'PYTEST_ADDOPTS':'-p no:cacheprovider --junitxml=/logs/verifier/junit.xml'},
            'oracle_sha256':sha256(official / 'tests/eval.py'), 'oracle_tests':mapping['oracle_tests'],
            'result_protocol':'Original shell reward + added JUnit; CTRF fallback 1-test summary is not coverage proof'}

    from .exports import digest
    plan.update(export_receipt_id=None, export_receipt=None, trial_id=None, task_config_sha256=None)
    if export_receipt is not None or export_controller is not None or trial_id is not None:
        from .scoring import collect_export
        if export_controller is None:
            raise ValueError('Trusted export controller required')
        candidate, error = collect_export(export_controller.artifacts, receipt=export_receipt,
                                          controller=export_controller, trial_id=trial_id)
        if error or candidate.resolve() != submission.resolve():
            raise ValueError('Scorer input has no valid bound export receipt')
        plan.update(export_receipt_id=export_receipt['receipt_id'], export_receipt=export_receipt,
                    trial_id=trial_id, task_config_sha256=export_receipt['task_config_sha256'])
    plan['request_sha256'] = digest(plan)
    return plan


def normalize_score(result, expected_tests):
    """Interpret original pytest evidence; no HTML business assertions are implemented here."""
    empty = {'failure_category':'environment_error', 'task_result':{'tests':0, 'passed':0},
             'rule_result':{'passed':None}}
    try:
        cases = list(ElementTree.fromstring(result['junit_xml']).iter('testcase'))
        names = [c.attrib['name'] for c in cases]
        if result['returncode'] != 0 or len(names) != len(expected_tests) or set(names) != set(expected_tests):
            return empty
        errors = sum(c.find('error') is not None or c.find('skipped') is not None for c in cases)
        failed = sum(c.find('failure') is not None for c in cases)
        passed = len(cases) - failed - errors
        reward = float(result['reward'])
        if errors or reward not in (0, 1) or (reward == 1) != (passed == len(cases)):
            return empty
        target = next(c for c in cases if c.attrib['name'] == 'test_uses_tag_name_assignment')
        return {'failure_category':'task_assertion_error' if failed else 'none',
                'task_result':{'tests':len(cases), 'passed':passed, 'failed':failed, 'errors':0},
                'rule_result':{'passed':target.find('failure') is None,
                               'assertion':'test_uses_tag_name_assignment (original syntax restriction)'}}
    except (KeyError, TypeError, ValueError, ElementTree.ParseError):
        return empty


def grade_export(root, trial, output, *, image, timeout_sec, execute=None, export_receipt=None, export_controller=None):
    """Validate exports and plan only. Raw callback execution is disabled until isolation is reviewed."""
    from .scoring import collect_export, failure
    if execute is not None:
        raise RuntimeError('Unreviewed scorer callbacks disabled; no execution authorized')
    trial_id = getattr(getattr(trial, 'config', None), 'trial_name', None)
    submission, error = collect_export(trial.paths.artifacts_dir, receipt=export_receipt,
                                      controller=export_controller, trial_id=trial_id)
    if error:
        return error
    plan = scoring_plan(root, submission, output, image=image, timeout_sec=timeout_sec,
                        export_receipt=export_receipt, export_controller=export_controller, trial_id=trial_id)
    # shortcut: runtime backend is unavailable; implement after Oracle isolation review.
    score = failure('environment_error', 'scorer_backend_not_implemented')
    score.update(candidate_sha256=plan['candidate_sha256'], oracle_original_sha256=plan['oracle_sha256'],
                 execution_status='NOT_RUN', scoring_plan=plan, export_receipt_id=plan['export_receipt_id'],
                 request_sha256=plan['request_sha256'], real_agent_outcome=False, task_success=None)
    return score


def task_success(score):
    return (score.get('real_agent_outcome') is not False
            and score.get('failure_category') == 'none'
            and score['task_result']['tests'] > 0
            and score['task_result']['passed'] == score['task_result']['tests'])
