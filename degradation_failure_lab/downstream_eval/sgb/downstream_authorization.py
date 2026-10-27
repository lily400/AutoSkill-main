"""Per-experiment grants; no credentials, model calls or budget mutation."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import re

from degradation_lab.io import read, sha256

ADAPTER = 'downstream_eval.sgb.task_adapters.audited.json_task'
CONDITIONS = {'NoSkill1': 'NoSkill', 'CleanSkill1': 'CleanSkill'}
CONTRACT = 'sgb-downstream-experiment-v1'


def blocked(reason):
    raise RuntimeError('Configured JSON task awaits exact downstream authorization: ' + reason)


def authorization_path(root, task_id, experiment):
    if any(not isinstance(v, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', v)
           for v in (task_id, experiment)):
        blocked('invalid task or experiment identifier')
    root = Path(root).resolve()
    path = (root / 'data/manifests/sgb/downstream_authorizations' / task_id / (experiment + '.json')).resolve()
    if not path.is_relative_to(root):
        blocked('authorization path escapes project')
    return path


def task_config_bytes(task):
    return (json.dumps(task, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def expected_authorization(task, generator, experiment):
    if task.get('adapter') != ADAPTER or task.get('conditions') != CONDITIONS:
        blocked('task does not use the paired JSON protocol')
    if not isinstance(generator, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', generator):
        blocked('invalid generator identifier')
    return {'schema_version': 1, 'authorization_contract': CONTRACT,
            'authorization_status': 'AUTHORIZED', 'task_id': task['task_id'],
            'generator_run_id': generator, 'experiment_id': experiment,
            'task_config_sha256': hashlib.sha256(task_config_bytes(task)).hexdigest(),
            'conditions': CONDITIONS, 'per_arm_http_limit': 6, 'max_http_calls': 12}


def load_authorization(root, task, generator, experiment):
    path = authorization_path(root, task['task_id'], experiment)
    try:
        data = path.read_bytes()
        value = json.loads(data)
    except (OSError, ValueError):
        blocked('missing or invalid experiment grant')
    expected = expected_authorization(task, generator, experiment)
    if (not isinstance(value, dict) or any(value.get(k) != v for k, v in expected.items())
            or any(type(value.get(k)) is not int for k in ('schema_version', 'per_arm_http_limit', 'max_http_calls'))):
        blocked('experiment grant identity or HTTP limits differ')
    return {'path': path.relative_to(Path(root).resolve()).as_posix(),
            'sha256': hashlib.sha256(data).hexdigest()}, data


def authorize(root, task, generator, experiment):
    """Create once after the CLI has verified generation and protocol admission."""
    path = authorization_path(root, task['task_id'], experiment)
    value = expected_authorization(task, generator, experiment)
    if path.exists():
        load_authorization(root, task, generator, experiment)
        return path, False
    output = Path(root) / 'runs/eval/sgb' / task['task_id'] / experiment
    if output.exists():
        blocked('experiment already exists; authorize a NEW ID before prepare')
    value['authorized_at'] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    return path, True


def freeze_authorization(output, reference, data):
    path = Path(output) / 'authorization.json'
    if path.exists():
        if path.read_bytes() != data:
            blocked('prepared authorization cannot be replaced')
    else:
        with path.open('xb') as stream:
            stream.write(data)
    return reference


def validate_prepared(root, task, output):
    """Fail before admission if the grant, its frozen copy or the profile differs."""
    output = Path(output).resolve()
    try:
        profile = read(output / 'profile.json')
        experiment, generator = profile.get('experiment_id'), profile.get('generator_run_id')
        reference, data = load_authorization(root, task, generator, experiment)
        expected_output = (Path(root) / 'runs/eval/sgb' / task['task_id'] / experiment).resolve()
        budget, hard = profile.get('budget', {}), profile.get('hard_http_budget', {})
        if (output != expected_output or profile.get('task_id') != task['task_id']
                or profile.get('conditions') != CONDITIONS
                or profile.get('task_config_sha256') != expected_authorization(task, generator, experiment)['task_config_sha256']
                or profile.get('downstream_authorization') != reference
                or type(budget.get('max_requests')) is not int or budget.get('max_requests') != 6
                or type(budget.get('num_retries')) is not int or budget.get('num_retries') != 0
                or type(hard.get('per_arm_limit')) is not int or hard.get('per_arm_limit') != 6
                or type(hard.get('global_limit')) is not int or hard.get('global_limit') != 12):
            blocked('prepared profile differs from experiment grant')
        snapshot = output / 'authorization.json'
        frozen = read(output / 'execution_manifest.json')
        if (snapshot.read_bytes() != data or sha256(snapshot) != reference['sha256']
                or frozen.get(reference['path']) != reference['sha256']
                or frozen.get(snapshot.relative_to(Path(root).resolve()).as_posix()) != reference['sha256']):
            blocked('experiment grant is absent from the frozen evidence')
    except (OSError, ValueError, KeyError, TypeError):
        blocked('incomplete prepared authorization evidence')
    return profile
