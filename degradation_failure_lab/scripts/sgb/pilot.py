"""One CLI for registered SGB pilots; preparation and analysis make no model requests."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

LAB = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
from degradation_lab.io import inside, read
from downstream_eval.sgb import pilot
from downstream_eval.integration.skill_freeze import freeze_generation


def main(default_task=None, default_generator=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('register', 'plan', 'freeze', 'prepare', 'run', 'status', 'analyze'))
    parser.add_argument('--task', default=default_task, required=default_task is None)
    parser.add_argument('--generator-run', default=default_generator)
    parser.add_argument('--bank-binding', help='Verified immutable snapshot TaskBinding for plan/prepare')
    parser.add_argument('--experiment')
    parser.add_argument('--config', help='Project-relative task configuration, for register')
    parser.add_argument('--output', help='Project-relative freeze/analysis destination')
    parser.add_argument('--watch', action='store_true', help='Read-only status monitoring until completion/stop')
    args = parser.parse_args()
    if args.phase == 'register':
        if not args.config:
            parser.error('register requires --config')
        result = pilot.register_task(LAB, args.task, args.config)
    else:
        task = pilot.load_binding(LAB, args.task)
        if args.phase in ('plan', 'freeze', 'prepare') and not args.generator_run and not (args.bank_binding and args.phase != 'freeze'):
            parser.error('this phase requires --generator-run')
        if args.phase != 'freeze' and not args.experiment:
            parser.error('this phase requires --experiment')
        if args.phase == 'freeze':
            if not args.output:
                parser.error('freeze requires --output')
            entries = freeze_generation(LAB, args.generator_run, inside(LAB, args.output), case_id=task['case_id'])
            result = {'status': 'FROZEN', 'skills': len(entries), 'output': args.output}
        elif args.phase == 'plan':
            result = pilot.plan(LAB, task, args.generator_run, args.experiment,
                                **({'bank_binding_id':args.bank_binding} if args.bank_binding else {}))
        elif args.phase in ('prepare', 'run') and os.name == 'nt':
            runtime = read(LAB / 'configs/downstream_runtime.json')
            mount = runtime['project_mount']
            running = subprocess.run(['docker', 'inspect', runtime['control_container'], '--format', '{{.State.Running}}'],
                                     capture_output=True, text=True, check=True).stdout.strip()
            if running != 'true':
                subprocess.run(['docker', 'start', runtime['control_container']], check=True)
            command = ['docker', 'exec', '--env', 'PYTHONPATH=' + mount + ':' + mount + '/src']
            if args.phase == 'run':
                profile = read(pilot.output_path(LAB, task, args.experiment) / 'profile.json')
                credential = profile['model']['api_key_environment_variable']
                if not os.environ.get(credential):
                    raise RuntimeError('Use scripts/sgb/Invoke-Pilot.ps1 -Phase run to load the saved credential')
                command += ['--env', credential, '--env', task['approval_environment_variable'] + '=1']
            command += [runtime['control_container'], runtime['python_executable'], '-B',
                        mount + '/scripts/sgb/pilot.py', args.phase, '--task', args.task,
                        '--experiment', args.experiment]
            if args.generator_run:
                command += ['--generator-run', args.generator_run]
            if args.bank_binding:
                command += ['--bank-binding', args.bank_binding]
            return subprocess.run(command).returncode
        elif args.phase == 'prepare':
            result = pilot.prepare(LAB, task, args.generator_run, args.experiment,
                                   **({'bank_binding_id':args.bank_binding} if args.bank_binding else {}))
        elif args.phase == 'run':
            return pilot.run(LAB, task, args.experiment)
        elif args.phase == 'status':
            while True:
                result = pilot.status(LAB, task, args.experiment)
                print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
                if not args.watch or result['status'] in ('COMPLETED', 'STOPPED', 'NOT_PREPARED', 'PREPARED'):
                    return 0
                time.sleep(2)
        else:
            destination = inside(LAB, args.output or ('results/sgb/analyses/' + args.experiment))
            result = pilot.analyze(LAB, task, args.experiment, destination)
            result = {'status': result['status']['status'], 'report': str(destination / 'report.md'),
                      'conditions': len(result['results'])}
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
