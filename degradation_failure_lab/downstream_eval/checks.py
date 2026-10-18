"""One offline entry through scripts/lab.py; artifacts reuse lab/runs."""
import hashlib
import json
import shutil
import subprocess
import uuid
from pathlib import Path

from degradation_lab.io import inside, inventory, read, sha256, utc, write
from .integration.harbor_adapter import preflight, validate_task_network_modes
from .integration.skill_install import check_skills
from .tasks.git_restore_explicit_source_both_v1.fixture import OTHER, SENTINEL, TARGET, build, git
from .tasks.git_restore_explicit_source_both_v1.oracle import evaluate, trusted_state


def oracle_probes(output):
    cases = ('correct', 'from_head', 'worktree_only', 'index_only', 'wrong_file', 'move_head',
             'unrelated_worktree', 'delete_sentinel', 'change_sentinel', 'noop', 'extra_commit',
             'extra_untracked', 'unrelated_index', 'target_mode', 'poison_git_config', 'fake_reward',
             'corrupt_index', 'assume_unchanged')
    records = []
    for repeat in range(2):
        for case in cases:
            directory = output / f'repeat-{repeat}' / case
            repo = directory / 'repo'
            fixture = build(repo)
            trusted = trusted_state(repo, fixture)
            write(directory / 'trusted-initial.json', trusted)
            commands = []
            def action(*args):
                commands.append(['git', *args])
                git(repo, *args)
            source = '--source=' + fixture['commit_a']
            if case == 'correct' or (case in cases[5:] and case != 'noop'):
                action('restore', source, '--staged', '--worktree', '--', TARGET)
            if case == 'from_head':
                action('restore', '--source=HEAD', '--staged', '--worktree', '--', TARGET)
            elif case == 'worktree_only':
                action('restore', source, '--worktree', '--', TARGET)
            elif case == 'index_only':
                action('restore', source, '--staged', '--', TARGET)
            elif case == 'wrong_file':
                action('restore', source, '--staged', '--worktree', '--', OTHER)
            elif case == 'move_head':
                action('update-ref', 'HEAD', fixture['commit_a'])
            elif case == 'unrelated_worktree':
                (repo / OTHER).write_bytes(b'damaged\n')
            elif case == 'delete_sentinel':
                (repo / SENTINEL).unlink()
            elif case == 'change_sentinel':
                (repo / SENTINEL).write_bytes(b'damaged\n')
            elif case == 'extra_commit':
                tree = git(repo, 'rev-parse', 'HEAD^{tree}').strip().decode()
                commit = git(repo, 'commit-tree', tree, '-p', fixture['head'], data=b'extra commit\n').strip().decode()
                action('update-ref', 'HEAD', commit)
            elif case == 'extra_untracked':
                (repo / 'extra.txt').write_bytes(b'extra\n')
            elif case == 'unrelated_index':
                action('update-index', '--cacheinfo', '100644,' + fixture['target_blob'] + ',' + OTHER)
            elif case == 'target_mode':
                action('update-index', '--chmod=+x', TARGET)
            elif case == 'poison_git_config':
                with (repo / '.git/config').open('ab') as stream:
                    stream.write(b'\n[core]\n fsmonitor = !touch /tmp/SHOULD_NEVER_RUN\n')
            elif case == 'fake_reward':
                write(repo / 'expected.json', {'target_blob': 'attacker'})
                (repo / 'reward.txt').write_text('1\n')
            elif case == 'corrupt_index':
                (repo / '.git/index').write_bytes(b'not an index')
            elif case == 'assume_unchanged':
                action('update-index', '--assume-unchanged', OTHER)
            result = evaluate(repo, trusted)
            again = evaluate(repo, trusted)
            expected_success = case == 'correct'
            result.update(case=case, repeat=repeat, expected_success=expected_success, commands=commands,
                          fixture=fixture, repeatable=result == again)
            result['test_status'] = 'PASS' if result['success'] == expected_success and result['repeatable'] else 'FAIL'
            write(directory / 'oracle-result.json', result)
            records.append(result)
    return {'status': 'PASS' if all(x['test_status'] == 'PASS' for x in records) else 'FAIL',
            'scope': 'independent native Git fixture and raw-state Oracle; not Harbor verifier', 'records': records}


def materialize_task(root, config, output, oracle_solution=True):
    template = inside(root, config['task_template'])
    task = output / 'harbor_task'
    shutil.copytree(template, task, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    reference = output / 'task_reference'
    fixture = build(reference)
    instruction = (task / 'instruction.md').read_text(encoding='utf-8').replace('{{COMMIT_A}}', fixture['commit_a'])
    (task / 'instruction.md').write_text(instruction, encoding='utf-8')
    # Docker builds only environment/; trusted verifier code only enters /tests later.
    shutil.copyfile(template / 'fixture.py', task / 'environment/fixture.py')
    for name in ('fixture.py', 'oracle.py'):
        shutil.copyfile(template / name, task / 'tests' / name)
    # This script is exclusively for the native, zero-model oracle Agent probe.
    if oracle_solution:
        solution = task / 'solution'
        solution.mkdir()
        (solution / 'solve.sh').write_text('#!/bin/bash\nset -euo pipefail\ncd /work/repo\ngit restore --source=' +
                                         fixture['commit_a'] + ' --staged --worktree -- target.txt\n', encoding='utf-8', newline='\n')
    return task, fixture


def check_harbor(root, config, output, environment):
    task, fixture = materialize_task(root, config, output)
    # Full import and Docker are separate gates; method-level checks cannot satisfy them.
    result = {'status': 'BLOCKED', 'task_path': task.relative_to(root).as_posix(),
              'fixture': fixture, 'official_task_parse': 'BLOCKED', 'separate_verifier_runtime': 'BLOCKED',
              'reason': 'Full pinned Harbor installation and Linux Docker daemon are required.'}
    result['static_network_contract'] = validate_task_network_modes(root, task)
    identity_ok = any(x['name'] == 'installed_harbor_identity' and x['status'] == 'PASS' for x in environment['checks'])
    if not identity_ok:
        return result
    try:
        from harbor.models.task.config import TaskConfig
        import tomllib
        parsed = TaskConfig.model_validate(tomllib.loads((task / 'task.toml').read_text()))
        if parsed.verifier.environment_mode.value != 'separate':
            raise ValueError('Task must use native separate verifier')
        result['official_task_parse'] = 'PASS'
    except ImportError as error:
        result['reason'] += ' ' + str(error)
        return result
    if environment['status'] != 'PASS':
        return result
    probes = []
    restore = 'git restore --source=' + fixture['commit_a']
    correct = restore + ' --staged --worktree -- target.txt'
    cases = [('correct', correct, 1, None),
             ('from_head', 'git restore --source=HEAD --staged --worktree -- target.txt', 0, 'target_worktree_bytes_and_mode'),
             ('worktree_only', restore + ' --worktree -- target.txt', 0, 'target_index_blob_and_mode'),
             ('index_only', restore + ' --staged -- target.txt', 0, 'target_worktree_bytes_and_mode'),
             ('delete_sentinel', correct + '\nrm -- sentinel.txt', 0, 'untracked_sentinel_preserved'),
             ('noop', 'true', 0, 'target_worktree_bytes_and_mode')]
    for case, operation, expected_reward, rejected_assertion in cases:
        case_task = task
        if case != 'correct':
            case_task = output / ('harbor_task_' + case)
            shutil.copytree(task, case_task)
            (case_task / 'solution/solve.sh').write_text('#!/bin/bash\nset -euo pipefail\ncd /work/repo\n' + operation + '\n', encoding='utf-8', newline='\n')
        trials = output / 'harbor_trials' / case
        command = ['harbor', 'trials', 'start', '--path', str(case_task), '--agent', 'oracle', '--env', 'docker',
                   '--trials-dir', str(trials), '--trial-name', 'p0-native-' + case]
        invocation = subprocess.run(command, capture_output=True, timeout=900)
        (output / ('harbor-' + case + '.stdout.log')).write_bytes(invocation.stdout)
        (output / ('harbor-' + case + '.stderr.log')).write_bytes(invocation.stderr)
        results = list(trials.glob('*/result.json'))
        raw = read(results[0]) if len(results) == 1 else {}
        rewards = (raw.get('verifier_result') or {}).get('rewards')
        assertions_path = results[0].parent / 'verifier/assertions.json' if len(results) == 1 else None
        assertions = read(assertions_path) if assertions_path and assertions_path.is_file() else {}
        checks = assertions.get('assertion_results', {})
        hidden_git = bool(len(results) == 1 and (results[0].parent / 'artifacts/repo/.git/index').is_file())
        ok = (invocation.returncode == 0 and bool(rewards) and
              all(v == expected_reward for v in rewards.values()) and not raw.get('exception_info') and
              raw.get('verifier_environment_mode') == 'separate' and
              hidden_git and len(checks) == 9 and assertions.get('reason') is None and
              assertions.get('success') == bool(expected_reward) and
              (rejected_assertion is None or checks.get(rejected_assertion) is False))
        probes.append({'case': case, 'command': command, 'exit_code': invocation.returncode,
                       'operation': operation, 'rewards': rewards, 'expected_reward': expected_reward,
                       'verifier_environment_mode': raw.get('verifier_environment_mode'),
                       'artifact_contains_hidden_git': hidden_git, 'assertions': assertions,
                       'status': 'PASS' if ok else 'FAIL'})
    result.update(status='PASS' if all(x['status'] == 'PASS' for x in probes) else 'FAIL', probes=probes,
                  separate_verifier_runtime='PASS' if all(x['status'] == 'PASS' for x in probes) else 'FAIL', reason=None)
    return result


def run_checks(root, section='all', run_id=None):
    root = Path(root).resolve()
    config = read(root / 'downstream_eval/configs/git_restore_pilot.json')
    run_id = run_id or 'p0-' + uuid.uuid4().hex[:12]
    if not run_id.startswith('p0-') or not all(c.isalnum() or c in '-_' for c in run_id):
        raise ValueError('Use a unique p0- run ID')
    output = inside(root, config['result_parent'] + '/' + run_id)
    output.mkdir(parents=True, exist_ok=False)
    source = read(inside(root, config['source_manifest']))
    if sha256(inside(root, source['local_path'])) != source['sha256']:
        raise ValueError('Frozen Git source changed')
    environment = preflight(root)
    result = {'run_id': run_id, 'started_at': utc(), 'execution_kind': 'zero_model_checks',
              'source_id': source['source_id'], 'source_version': source['source_commit'], 'source_hash': source['sha256'],
              'generator_run_id': config['generator_run_id'], 'skill_manifest': config['skill_manifest'],
              'task_id': config['task_id'], 'task_version': config['task_version'],
              'runner_version': read(root / 'downstream_eval/configs/runner.lock.json')['harbor_commit'],
              'model_config': None, 'condition': config['condition'], 'installed_skill_ids': [], 'discovered_skill_ids': [],
              'read_events': None, 'tool_events': None, 'verifier_version': 'git-state-v1',
              'fixture_hash': None, 'assertion_results': None, 'success': None, 'checks': {}}
    write(output / 'preflight.json', environment)
    result['checks']['preflight'] = environment
    for name, action in [('skills', lambda: check_skills(root, config, output, environment)),
                         ('oracle', lambda: oracle_probes(output / 'oracle')),
                         ('harbor', lambda: check_harbor(root, config, output, environment))]:
        if section not in ('all', name):
            continue
        try:
            report = action()
        except (FileNotFoundError, ModuleNotFoundError) as error:
            report = {'status': 'BLOCKED', 'reason': type(error).__name__ + ': ' + str(error)}
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
            report = {'status': 'FAIL', 'reason': type(error).__name__ + ': ' + str(error)}
        write(output / (name + '.json'), report)
        result['checks'][name] = report
    if result['checks'].get('skills', {}).get('status') == 'PASS':
        result['installed_skill_ids'] = result['checks']['skills']['expected_ids']
        result['discovered_skill_ids'] = result['checks']['skills']['discovered_ids']
    if result['checks'].get('oracle', {}).get('status') == 'PASS':
        sample = result['checks']['oracle']['records'][0]
        trusted = read(output / 'oracle/repeat-0/correct/trusted-initial.json')
        result['fixture_hash'] = hashlib.sha256(json.dumps(trusted, sort_keys=True).encode()).hexdigest()
        result['assertion_results'] = sample['assertion_results']
    statuses = [c['status'] for c in result['checks'].values()]
    result['infra_status'] = 'FAIL' if 'FAIL' in statuses else ('BLOCKED' if 'BLOCKED' in statuses else 'PASS')
    result['ended_at'] = utc()
    write(output / 'result.json', result)
    write(output / 'artifact_manifest.json', inventory(output))
    return {'infra_status': result['infra_status'], 'path': str(output),
            'checks': {k: {'status': v['status'], 'reason': v.get('reason')} for k, v in result['checks'].items()}}
