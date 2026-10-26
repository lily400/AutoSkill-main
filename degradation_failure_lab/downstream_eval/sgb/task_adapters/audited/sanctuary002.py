"""Sanctuary binding to the existing isolated JSON scorer and paired pilot."""
from pathlib import Path

from degradation_lab.catalog import CaseManager
from degradation_lab.evaluation import validate_evaluation
from degradation_lab.io import inside, read, sha256
from . import fla
from .common import LAB, bind, native_trial

TASK_ID = 'sanctuary_endgame_scheduler_002'
CASE_ID = 'case003_san'
TASK = LAB / 'downstream_eval/tasks/sgb/audited' / TASK_ID
GATE = LAB / 'data/manifests/sgb/gates/t-febd929cffec.json'
SETUP = 'import math\nimport numpy as np\nfrom collections import defaultdict, deque'


def verify_assets():
    manifest = fla.verify_assets(TASK)
    source = manifest['source_document']
    if sha256(LAB / source['path']) != source['sha256']:
        raise ValueError('Sanctuary source document changed')
    if sha256(LAB / source['manifest']) != source['manifest_sha256']:
        raise ValueError('Sanctuary source identity changed')
    original = LAB / manifest['original_task']
    for local, released in [('instruction.md', 'instruction.md'), ('task.original.toml', 'task.toml'),
                            ('oracle/eval.py', 'tests/eval.py'), ('oracle/testcases.json', 'tests/testcases.json')]:
        if sha256(TASK / local) != sha256(original / released):
            raise ValueError('Released Sanctuary asset differs: ' + local)
    manager = CaseManager(LAB)
    case = manager.load(CASE_ID)
    _, inputs = manager.condition(case, 'clean')
    if len(inputs['inputs']) != 1 or inputs['inputs'][0]['sha256'] != source['sha256']:
        raise ValueError('Sanctuary clean input binding differs')
    return manifest


def score(submission, output, *, expected_sha256=None):
    verify_assets()
    return fla.score(submission, output, expected_sha256=expected_sha256, task=TASK,
                     task_id=TASK_ID, expected_tests=8, setup_code=SETUP)


def check_review(generator):
    path = LAB / f'evaluations/{CASE_ID}/clean/{generator}/pre_downstream.json'
    review = validate_evaluation(LAB, read(path))
    rules = {r['rule_id'] for r in CaseManager(LAB).load(CASE_ID)['rules']['rules']}
    records = [r for r in review['records'] if r['judgment_scope'] == 'rule_preservation']
    if (review['reviewer'] == 'pending' or {r['rule_id'] for r in records} != rules
            or any(r['status'] != 'correct' for r in review['records'])
            or len(records) != len(rules) or any(r['status'] != 'correct' or not r['skill_ids']
               or not r['generated_evidence'] or not r['trace_refs'] for r in records)):
        raise RuntimeError('BLOCKED: every target rule needs a completed, evidence-linked quality review')
    return path


def check_authorization(phase, generator='sn3g001', experiment='sn3e001'):
    """Check explicit approval; this function never grants it or changes a ledger."""
    gate = read(GATE)
    if gate.get('status') != 'PASS':
        raise RuntimeError('BLOCKED: Task003 generation budget has not been authorized')
    requested = gate['requested_generation']
    if (requested['run_id'] != generator or requested.get('authorization_status') != 'AUTHORIZED'
            or requested['configuration_sha256'] != sha256(LAB / requested['configuration'])):
        raise RuntimeError('BLOCKED: generation identity/configuration authorization is incomplete')
    config = read(LAB / requested['configuration'])
    if any(requested[k] != config[k] for k in ('max_http_calls', 'max_observed_total_tokens')):
        raise RuntimeError('BLOCKED: generation ceilings differ from the authorized configuration')
    approval = requested.get('approval_evidence', {})
    if not approval.get('file') or sha256(inside(LAB, approval['file'])) != approval.get('sha256'):
        raise RuntimeError('BLOCKED: generation approval provenance is absent or changed')
    if phase == 'downstream':
        approved = gate['downstream']
        if (approved.get('status') != 'PASS' or approved.get('authorization_status') != 'AUTHORIZED'
                or approved['generator_run_id'] != generator or approved['experiment_id'] != experiment
                or approved['profile_sha256'] != sha256(LAB / approved['profile_template'])):
            raise RuntimeError('BLOCKED: this exact paired downstream budget has not been authorized')
        profile = read(LAB / approved['profile_template'])
        if (approved['max_http_calls'] != 2 * profile['budget']['max_requests']
                or approved['conditions'] != {'NoSkill1': 'NoSkill', 'CleanSkill1': 'CleanSkill'}
                or approved['repeats_per_arm'] != 1):
            raise RuntimeError('BLOCKED: paired protocol or HTTP ceiling differs from authorization')
        approval = approved.get('approval_evidence', {})
        if not approval.get('file') or sha256(inside(LAB, approval['file'])) != approval.get('sha256'):
            raise RuntimeError('BLOCKED: downstream approval provenance is absent or changed')
        if approved.get('quality_review_sha256') != sha256(check_review(generator)):
            raise RuntimeError('BLOCKED: downstream authorization must bind the reviewed upstream quality file')
    return {'status': 'AUTHORIZED', 'phase': phase, 'generator': generator, 'experiment': experiment}


execution_config, configure, grade_export, _paid_batch = bind(TASK_ID, score, verify_assets)


def paid_batch(output):
    profile = read(Path(output) / 'profile.json')
    check_authorization('downstream', profile['generator_run_id'], profile['experiment_id'])
    return _paid_batch(output)
