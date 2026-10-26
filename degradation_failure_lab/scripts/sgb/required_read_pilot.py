"""Explicit single-arm correction to SGB's MUST-load-skill contract.

Reuse each matching original NoSkill trial; do not reset or alter old ledgers.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

LAB = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
from degradation_lab.io import read, write
from downstream_eval.sgb import pilot

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('phase', choices=('prepare', 'run', 'analyze'))
parser.add_argument('--task', required=True, choices=('scrapy-task-024', 'fla_packet_cadence_scope_validator_002'))
parser.add_argument('--generator-run', required=True)
parser.add_argument('--experiment', required=True)
parser.add_argument('--control-experiment', required=True)
args = parser.parse_args()
task = dict(pilot.load_binding(LAB, args.task))
task.update(adapter='downstream_eval.sgb.task_adapters.audited.read_required',
    conditions={'CleanSkill1': 'CleanSkill'}, probes={'CleanSkill1': task['probes']['CleanSkill1']},
    protocol='SGB-required-skill-loading; existing matched NoSkill control',
    control_experiment=args.control_experiment)
task['freeze_files'] = [*task.get('freeze_files', []), 'scripts/sgb/required_read_pilot.py']
output = pilot.output_path(LAB, task, args.experiment)
control = LAB / 'runs/eval/sgb' / args.task / args.control_experiment
control_profile = read(control / 'profile.json')
assert control_profile['generator_run_id'] == args.generator_run
assert read(control / 'outcomes/NoSkill1/result.json')['infra_ok'] is True

if os.name == 'nt' and args.phase in ('prepare', 'run'):
    runtime = read(LAB / 'configs/downstream_runtime.json')
    mount = runtime['project_mount']
    command = ['docker', 'exec', '--env', 'PYTHONPATH=' + mount + ':' + mount + '/src']
    if args.phase == 'run':
        credential = control_profile['model']['api_key_environment_variable']
        if not os.environ.get(credential):
            raise RuntimeError('Use the configured project credential loader')
        command += ['--env', credential, '--env', 'SGB_AUDIT_ALLOW_PAID=1']
    command += [runtime['control_container'], runtime['python_executable'], '-B',
                mount + '/scripts/sgb/required_read_pilot.py', *sys.argv[1:]]
    raise SystemExit(subprocess.run(command).returncode)
if args.phase == 'prepare':
    result = pilot.prepare(LAB, task, args.generator_run, args.experiment)
    profile = read(output / 'profile.json')
    for field in ('model', 'budget', 'frozen_agent_image_id', 'generator_run_id'):
        assert profile[field] == control_profile[field], 'Control mismatch: ' + field
    write(output / 'control_comparison.json', {'status': 'PASS', 'control_experiment': args.control_experiment,
        'equal_fields': ['model', 'budget', 'frozen_agent_image_id', 'generator_run_id'],
        'treatment': 'same frozen CleanSkill packages plus mandatory body loading instruction',
        'official_reference': '.external/skillgenbench/5a8bd61d/scripts/claude_runner.py:224-228',
        'official_runner_reproduction': False, 'reason': 'Harbor terminal reads substitute for Claude Skill tool'})
elif args.phase == 'run':
    if read(output / 'control_comparison.json')['status'] != 'PASS':
        raise RuntimeError('No matched control comparison')
    raise SystemExit(pilot.run(LAB, task, args.experiment))
else:
    result = pilot.analyze(LAB, task, args.experiment, LAB / 'results/sgb/analyses' / args.experiment)
    result = {'status': result['status']['status'], 'experiment': args.experiment}
print(json.dumps(result, ensure_ascii=False, indent=2))
