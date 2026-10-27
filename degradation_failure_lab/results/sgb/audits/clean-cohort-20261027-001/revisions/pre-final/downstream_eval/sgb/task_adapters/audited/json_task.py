"""Configuration binding for solve(dict)->JSON tasks; reuse the native Agent and scorer."""
from pathlib import Path
from types import SimpleNamespace

from degradation_lab.io import inside, read, sha256
from degradation_lab.catalog import CaseManager
from . import fla
from .common import bind, native_trial


def for_task(root, config):
    root = Path(root).resolve(); task = inside(root, config['task_path'])
    if config['task_path'] != 'downstream_eval/tasks/sgb/audited/' + config['task_id']:
        raise ValueError('Configured JSON task must use the common audited task location')
    policy = config['json_observation']

    def verify_assets():
        manifest = fla.verify_assets(task)
        original = inside(root, manifest['original_task'])
        for local, published in [('instruction.md','instruction.md'), ('task.original.toml','task.toml'),
                                 ('oracle/eval.py','tests/eval.py'), ('oracle/testcases.json','tests/testcases.json')]:
            if sha256(task / local) != sha256(original / published):
                raise ValueError('Published task bytes changed: ' + local)
        for source in manifest['source_documents']:
            if sha256(inside(root, source['path'])) != source['sha256']:
                raise ValueError('Source document changed')
        bundle = read(task / 'oracle/testcases.json')
        if bundle['setup_code'] != policy['setup_code'] or len(bundle['test_cases']) != config['expected_oracle_tests']:
            raise ValueError('JSON observation contract differs from released bundle')
        return manifest

    def score(submission, output, *, expected_sha256=None):
        verify_assets()
        return fla.score(submission, output, expected_sha256=expected_sha256, task=task,
                         task_id=config['task_id'], expected_tests=config['expected_oracle_tests'],
                         setup_code=policy['setup_code'])

    execution_config, configure, grade_export, paid = bind(config['task_id'], score, verify_assets)

    def paid_batch(output):
        # Registration/preparation never grants either generation or downstream authorization.
        case = CaseManager(root).load(config['case_id'])['case']
        gate = read(inside(root, case['execution_gate']))
        profile = read(Path(output) / 'profile.json'); approval = gate.get('downstream', {})
        if (gate.get('status') != 'PASS' or approval.get('authorization_status') != 'AUTHORIZED'
                or approval.get('generator_run_id') != profile['generator_run_id']
                or approval.get('experiment_id') != profile['experiment_id']
                or approval.get('task_config_sha256') != profile['task_config_sha256']
                or approval.get('max_http_calls') != profile['hard_http_budget']['global_limit']):
            raise RuntimeError('Configured JSON task awaits exact downstream authorization')
        return paid(output)

    return SimpleNamespace(verify_assets=verify_assets, execution_config=execution_config,
        configure=configure, native_trial=native_trial, grade_export=grade_export,
        paid_batch=paid_batch, score=score)
