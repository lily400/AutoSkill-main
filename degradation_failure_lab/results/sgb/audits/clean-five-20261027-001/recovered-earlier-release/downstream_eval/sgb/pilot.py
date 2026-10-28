"""Configured SGB pilots: shared preparation and analysis, task-specific execution hooks."""
import asyncio
from contextlib import closing
import importlib
import importlib.metadata
import json
from pathlib import Path
import sqlite3
import subprocess

from degradation_lab.io import inside, inventory, read, sha256, write
from degradation_lab.sgb import selected_tasks, audit_registry
from downstream_eval.integration.skill_freeze import freeze_generation
from downstream_eval.integration.skill_install import copy_packages
from downstream_eval.integration.skill_usage import save_skill_usage
from downstream_eval.sgb import runner


def _validate_binding(root, row, data):
    required = ('task_id', 'task_key', 'case_id', 'adapter', 'task_path', 'runtime_lock',
                'profile_template', 'approval_environment_variable', 'conditions', 'fixtures', 'probes',
                'expected_oracle_tests')
    if data.get('schema_version') != 1 or any(k not in data for k in required):
        raise ValueError('Incomplete pilot task configuration')
    if data['task_id'] != row['original_task_id'] or data['task_key'] != row['task_key']:
        raise ValueError('Pilot task/source identity mismatch')
    if not data['adapter'].startswith('downstream_eval.sgb.task_adapters.'):
        raise ValueError('Pilot adapter must be an explicit local task adapter')
    if row.get('execution_adapter') not in (None, data['adapter']):
        raise ValueError('Pilot adapter differs from task registry')
    for key in ('task_path', 'runtime_lock', 'profile_template', 'fixtures'):
        if not inside(root, data[key]).exists():
            raise ValueError('Missing pilot input: ' + key)
    if Path(data['task_path']).name != data['task_id']:
        raise ValueError('Pilot task directory has a different identity')
    if len(data['conditions']) != 2 or set(data['conditions'].values()) != {'NoSkill', 'CleanSkill'}:
        raise ValueError('This pilot protocol requires one NoSkill and one CleanSkill trial')
    if set(data['probes']) != set(data['conditions']):
        raise ValueError('Each condition requires an explicit zero-model fixture')
    fixtures = read(inside(root, data['fixtures']))
    if any(name not in fixtures for name in data['probes'].values()):
        raise ValueError('Unknown zero-model fixture')
    return data


def register_task(root, selector, config_path):
    """Bind an existing SGB task to configuration; this does not grant runtime admission."""
    root = Path(root).resolve()
    catalog, rows = selected_tasks(root, [selector])
    if len(rows) != 1:
        raise ValueError('One registered SGB task required')
    path = inside(root, config_path)
    data = _validate_binding(root, rows[0], read(path))
    registry = inside(root, catalog['registry'])
    parts = registry.read_bytes().splitlines(keepends=True)
    for index, line in enumerate(parts):
        row = json.loads(line)
        if row['task_key'] != data['task_key']:
            continue
        row['pilot_config'] = {'path': path.relative_to(root).as_posix(), 'sha256': sha256(path)}
        newline = b'\r\n' if line.endswith(b'\r\n') else b'\n'
        parts[index] = json.dumps(row, ensure_ascii=False, separators=(',', ':')).encode() + newline
        break
    registry.write_bytes(b''.join(parts))
    config = read(root / 'configs/datasets/sgb.json')
    config['registry_sha256'] = sha256(registry)
    write(root / 'configs/datasets/sgb.json', config)
    audit_registry(root)
    return {'task_id': data['task_id'], 'binding': row['pilot_config'], 'runtime_admission': 'NOT_RUN'}


def load_binding(root, selector):
    root = Path(root).resolve()
    catalog, rows = selected_tasks(root, [selector])
    if len(rows) != 1 or not rows[0].get('pilot_config'):
        raise ValueError('Task needs a pilot_config binding; use register with a task configuration')
    binding = rows[0]['pilot_config']
    path = inside(root, binding['path'])
    if sha256(path) != binding['sha256']:
        raise ValueError('Pilot task configuration changed; review and register it again')
    snapshot = inside(root, catalog['snapshot'])
    for name, digest in rows[0]['official_assets'].items():
        if sha256(inside(snapshot, name)) != digest:
            raise ValueError('Selected official task asset changed: ' + name)
    for source in rows[0]['sources']:
        if (sha256(inside(root, source['path'])) != source['sha256']
                or sha256(inside(root, source['manifest'])) != source['manifest_sha256']):
            raise ValueError('Selected source document or manifest changed')
    return _validate_binding(root, rows[0], read(path))


def adapter_for(root, task):
    module = importlib.import_module(task['adapter'])
    return module.for_task(root, task) if callable(getattr(module, 'for_task', None)) else module


def output_path(root, task, experiment):
    if not runner._identifier(experiment):
        raise ValueError('Safe experiment ID required')
    return Path(root) / 'runs/eval/sgb' / task['task_id'] / experiment


def plan(root, task, generator, experiment):
    from degradation_lab.artifacts import load_run
    identity, run, result, _ = load_run(root, generator)
    if identity['case_id'] != task['case_id'] or result.get('status') != 'completed':
        raise ValueError('Task requires a matching completed generation')
    output = output_path(root, task, experiment)
    if output.exists():
        raise FileExistsError('Choose a new experiment ID; existing pilots must be preserved')
    profile = read(inside(root, task['profile_template']))
    return {'task_id': task['task_id'], 'generator_run_id': generator, 'output': str(output),
            'model': profile['model'], 'budget': profile['budget'], 'conditions': task['conditions'],
            'max_http_calls': len(task['conditions']) * profile['budget']['max_requests'],
            'runtime': read(inside(root, task['runtime_lock'])), 'model_calls': 0,
            'generation_path': str(run), 'runtime_admission': 'REQUIRES_ZERO_MODEL_PREPARATION'}


def _stage(output, packages, generator, conditions):
    for label, condition in conditions.items():
        stage = output / 'staged' / condition
        expected = {} if condition == 'NoSkill' else inventory(output / 'skills')
        if stage.exists():
            if inventory(stage) != expected:
                raise ValueError('Prepared Skill stage changed')
        elif condition == 'NoSkill':
            stage.mkdir(parents=True)
        else:
            copy_packages({sid: {'path': output / 'skills' / sid / 'SKILL.md', 'files': p['files']}
                           for sid, p in packages.items()}, stage)
        write(output / 'manifests' / (label + '.json'), {
            'arm': label, 'generator_run_id': generator, 'staged_root': str(stage),
            'files': inventory(stage),
            'metadata': {sid: p['metadata'] for sid, p in packages.items()} if condition == 'CleanSkill' else {}})


def _probe(output, task, adapter, config, packages, attempt):
    from downstream_eval.integration.skill_probe import probe_body_chunks
    from unittest.mock import patch
    fixtures = read(inside(Path(output).parents[4], task['fixtures']))
    reports = []
    for label, fixture_name in task['probes'].items():
        fixture = fixtures[fixture_name]
        path = attempt / 'fixtures' / (fixture_name + '.py')
        write(path.with_suffix('.json'), {'fixture': fixture_name})
        path.write_text(fixture['source'], encoding='utf-8')
        native_config = adapter.configure(output, label, 'probe', config)
        native_config.trials_dir = attempt / 'probe-trials'
        trial = None
        try:
            with patch('httpx.AsyncClient.send', side_effect=AssertionError('Zero-model preparation forbids HTTP model calls')), \
                 patch('httpx.Client.send', side_effect=AssertionError('Zero-model preparation forbids HTTP model calls')):
                trial, native = asyncio.run(adapter.native_trial(native_config, path, probe_hook=probe_body_chunks))
            write(attempt / label / 'native.json', native)
            if native.get('exception_info'):
                raise RuntimeError('Native zero-model trial failed')
            score = adapter.grade_export(trial, attempt / label / 'oracle')
            observer = trial.paths.trial_dir / 'p1-observer'
            summary = read(observer / 'p1-summary.json')
            request = json.loads((observer / 'p1-model-requests.jsonl').read_text(encoding='utf-8').splitlines()[0])
            expected = len(packages) if task['conditions'][label] == 'CleanSkill' else 0
            visibility = read(trial.paths.trial_dir / 'body-visibility.json')
            index = (observer / 'p1-skill-index.xml').read_text(encoding='utf-8')
            prompt = request['messages'][-1]['content']
            budget = read(output / 'profile.json')['budget']
            good = (summary['stopped_before_model'] and summary['actual_http_attempts'] == 0
                    and len(summary['controlled_probe_read_ids']) == expected
                    and len(visibility['all_visible_ids']) == expected
                    and (index in prompt if expected else '<available_skills>' not in prompt)
                    and request['estimated_input_tokens_with_reserve'] <= budget['max_input_tokens_per_request']
                    and score['infra_ok'] and score['candidate_binding_verified']
                    and score['task_result']['tests'] == task['expected_oracle_tests']
                    and score['task_result']['passed'] == fixture['passed']
                    and set(score.get('failed_tests', [])) == set(fixture.get('failed', [])))
            report = {'label': label, 'status': 'PASS' if good else 'FAIL', 'fixture': fixture_name,
                      'summary': summary, 'oracle': score, 'body_visibility': visibility,
                      'model_calls': 0, 'real_agent_outcome': False, 'trial_path': str(trial.paths.trial_dir)}
            write(attempt / label / 'report.json', report)
            reports.append(report)
            if not good:
                raise RuntimeError('Zero-model acceptance failed')
        finally:
            if trial:
                asyncio.run(trial.agent_environment.stop(delete=True))
    return reports


def prepare(root, task, generator, experiment):
    from downstream_eval.integration.harbor_adapter import verify_sources
    from downstream_eval.integration.request_budget import Ledger
    from downstream_eval.p1 import fairness_identity
    root = Path(root)
    output = output_path(root, task, experiment)
    if (output / 'budget.sqlite3').exists() or (output / 'batch.started').exists():
        raise RuntimeError('Existing pilot budget must never be reset')
    adapter = adapter_for(root, task)
    for hook in ('verify_assets', 'execution_config', 'configure', 'native_trial', 'grade_export', 'paid_batch'):
        if not callable(getattr(adapter, hook, None)):
            raise ValueError('Task needs an explicit adapter hook: ' + hook)
    adapter.verify_assets()
    _, lock = verify_sources(root)
    versions = {n: importlib.metadata.version(n) for n in ('harbor', 'litellm', 'openai', 'httpx')}
    if versions['harbor'] != lock['harbor_version']:
        raise ValueError('Harbor version mismatch')
    runtime = read(inside(root, task['runtime_lock']))
    for key in ('agent_image_id', 'scorer_image_id'):
        actual = subprocess.run(['docker', 'image', 'inspect', runtime[key], '--format', '{{.Id}}'],
                                capture_output=True, text=True, check=True).stdout.strip()
        if actual != runtime[key]:
            raise ValueError('Pinned runtime image mismatch')
    if (output / 'skill_freeze.json').exists():
        frozen = read(output / 'skill_freeze.json')
        if (frozen['generator_run_id'] != generator or inventory(output / 'skills') != frozen['files']
                or sha256(output / 'skills_manifest.json') != frozen['manifest_sha256']):
            raise ValueError('Existing frozen Skills changed')
        packages = read(output / 'skills_manifest.json')['packages']
    else:
        packages = freeze_generation(root, generator, output, case_id=task['case_id'])
    attempt = output / 'engineering' / ('attempt-%03d' % (len(list((output / 'engineering').glob('attempt-*'))) + 1))
    attempt.mkdir(parents=True, exist_ok=False)
    write(output / 'task_config.json', task)
    template = read(inside(root, task['profile_template']))
    config = adapter.execution_config(output, generator, task['conditions'])
    profile = {'experiment_id': experiment, 'task_id': task['task_id'], 'generator_run_id': generator,
               'conditions': task['conditions'], 'arms': list(task['conditions'].values()),
               'trial_order': list(task['conditions']), 'repeats_per_arm': 1,
               'model': template['model'], 'budget': template['budget'],
               'price_usd_per_million_tokens': None, 'frozen_agent_image_id': runtime['agent_image_id'],
               'approval_environment_variable': task['approval_environment_variable'],
               'authorization': 'RUN_REQUIRES_EXPLICIT_INVOCATION', 'protocol_id': 'clean-pair-v1',
               'task_config_sha256': sha256(output / 'task_config.json')}
    limit = profile['budget']['max_requests']
    profile['hard_http_budget'] = {'database': str(output / 'budget.sqlite3'),
        'per_arm_limit': limit, 'global_limit': limit * len(task['conditions']), 'order': list(task['conditions'])}
    write(output / 'profile.json', profile)
    write(output / 'runtime_versions.json', versions)
    _stage(output, packages, generator, task['conditions'])
    configs = {label: adapter.configure(output, label, 'paid', config) for label in task['conditions']}
    from .protocol import validate as validate_protocol
    protocol = validate_protocol(root, profile, {label: c.model_dump(mode='json', exclude_none=True)
                                               for label, c in configs.items()})
    identities = protocol['configuration_hashes']
    for label, c in configs.items():
        write(output / 'configs' / (label + '.json'), c.model_dump(mode='json', exclude_none=True))
    write(output / 'fairness.json', {'status': 'PASS', **protocol, 'runtime': runtime})
    try:
        reports = _probe(output, task, adapter, config, packages, attempt)
    except BaseException as error:
        write(attempt / 'failure.json', {'type': type(error).__name__, 'message': str(error), 'model_calls': 0})
        raise
    write(output / 'readiness.json', {'status': 'PASS', 'model_api_calls': 0, 'reports': reports})
    frozen = {}
    for prefix in ('downstream_eval/integration', 'downstream_eval/sgb', task['task_path']):
        frozen.update({prefix + '/' + name: digest for name, digest in inventory(root / prefix).items()})
    for name in ('configs/sgb/clean_pair_protocol.json', 'downstream_eval/sgb/clean_skill_read.md',
                 'downstream_eval/p1.py', 'downstream_eval/scoring/results.py',
                 'scripts/sgb/pilot.py', 'scripts/sgb/Invoke-Pilot.ps1',
                 'configs/downstream_runtime.json', task['profile_template'], task['runtime_lock'],
                 'configs/datasets/sgb.json', 'data/manifests/sgb/tasks.jsonl',
                 'downstream_eval/configs/runner.lock.json', *task.get('freeze_files', [])):
        frozen[name] = sha256(root / name)
    for name, digest in inventory(root / '.external/harbor-full/src/harbor').items():
        frozen['.external/harbor-full/src/harbor/' + name] = digest
    for name, digest in inventory(output).items():
        if not name.startswith('engineering/') and name not in ('execution_manifest.json', 'budget.sqlite3'):
            frozen[(output / name).relative_to(root).as_posix()] = digest
    write(output / 'execution_manifest.json', frozen)
    Ledger.create(output / 'budget.sqlite3', {
        'scope': config.budget_scope, 'order': list(task['conditions']),
        'global_limit': limit * len(task['conditions']), 'per_trial_limit': limit,
        'trials': {label: c.trial_name for label, c in configs.items()},
        'files': {str(root / name): digest for name, digest in frozen.items()}, 'budget': profile['budget']})
    runner.verify_frozen(root, output)
    runner.verify_ledger(root, output, config, profile)
    return {'status': 'READY', 'output': str(output), 'skill_count': len(packages), 'model_calls': 0}


def run(root, task, experiment):
    output = output_path(root, task, experiment)
    if (output / 'batch.started').exists():
        raise RuntimeError('Pilot already started; inspect status/analyze instead of restarting')
    if read(output / 'task_config.json') != task:
        raise ValueError('Task binding changed after preparation')
    versions = {n: importlib.metadata.version(n) for n in ('harbor', 'litellm', 'openai', 'httpx')}
    if versions != read(output / 'runtime_versions.json'):
        raise ValueError('Prepared runtime package versions changed')
    return adapter_for(root, task).paid_batch(output)


def status(root, task, experiment):
    output = output_path(root, task, experiment)
    if not (output / 'budget.sqlite3').is_file():
        return {'status': 'NOT_PREPARED', 'output': str(output)}
    with closing(sqlite3.connect((output / 'budget.sqlite3').resolve().as_uri() + '?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        arms = [dict(r) for r in db.execute('SELECT arm,state FROM arms')]
        attempts = db.execute('SELECT count(*) FROM attempts').fetchone()[0]
        halt = db.execute('SELECT halt FROM policy').fetchone()[0]
    state = ('COMPLETED' if all(x['state'] == 'DONE' for x in arms) else
             'STOPPED' if halt or (output / 'batch_stop.json').exists() else
             'RUNNING' if (output / 'batch.started').exists() else 'PREPARED')
    return {'status': state, 'output': str(output), 'arms': arms, 'http_attempts': attempts, 'halt': halt}


def analyze(root, task, experiment, destination):
    output, destination = output_path(root, task, experiment), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    profile = read(output / 'profile.json')
    reports = []
    for label in profile['conditions']:
        config = read(output / 'configs' / (label + '.json'))
        trial = output / 'trials' / config['trial_name']
        usage = save_skill_usage(output, label, trial, destination / (label + '-skill-usage.json'))
        path = output / 'outcomes' / label / 'result.json'
        outcome = read(path) if path.is_file() else {}
        reports.append({'label': label, 'task_success': outcome.get('task_success'),
                        'infra_ok': outcome.get('infra_ok'), 'http_attempts': outcome.get('http_attempts'),
                        'failure_kind': outcome.get('failure_kind'), 'failure_category': outcome.get('failure_category'),
                        'oracle': outcome.get('oracle'), 'skill_usage': usage})
    manifest_path = output / 'skills_manifest.json'
    if manifest_path.is_file():
        skills = read(manifest_path)['packages']
        catalog = ['# Frozen Skills', '', '| Skill | Version | Frozen body |', '|---|---|---|']
        for sid, package in sorted(skills.items()):
            name = package['metadata']['name'].replace('|', '\\|')
            path = (output / 'skills' / sid / 'SKILL.md').resolve().as_posix()
            catalog.append(f"| {name} | {package['version']} | [SKILL.md](<{path}>) |")
        (destination / 'skills.md').write_text('\n'.join(catalog) + '\n', encoding='utf-8')
    result = {'experiment_id': experiment, 'status': status(root, task, experiment),
              'results': reports, 'behavioral_use': 'UNKNOWN unless separately assessed from rule/action evidence'}
    write(destination / 'analysis.json', result)
    lines = ['# Pilot result and Skill usage', '', '| Condition | Task pass | Failure class | Skill evidence | Body reads | Full body in context |',
             '|---|---|---|---|---:|---:|']
    for row in reports:
        u = row['skill_usage']
        lines.append(f"| {row['label']} | {row['task_success']} | {row['failure_kind']} | {u['status']} | "
                     f"{u['counts']['model_file_access_observed']} | {u['counts']['full_body_in_successful_model_request']} |")
    lines += ['', 'Reading/context delivery does not prove behavioral reliance. Missing logs remain unknown.',
              'This analysis writes only to its destination; original runs, scores and ledgers are not modified.']
    (destination / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return result
