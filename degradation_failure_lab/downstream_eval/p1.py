"""Prepare native Harbor trials and run request-before-stop checks; never pays."""
import asyncio
from contextlib import asynccontextmanager
import hashlib
import json
import os
import re
import shlex
import subprocess
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

from degradation_lab.io import inside, inventory, read, sha256, write
from .checks import materialize_task
from .integration.harbor_adapter import preflight
from .integration.skill_install import canonical_packages, copy_packages
from .tasks.git_restore_explicit_source_both_v1.fixture import TARGET, build, git
from .tasks.git_restore_explicit_source_both_v1.oracle import evaluate, trusted_state


def fairness_identity(config):
    value = json.loads(json.dumps(config))
    for key in ('trial_name', 'trials_dir'):
        value.pop(key, None)
    value['agent'].pop('skills', None)
    value['agent']['kwargs'].pop('p1_manifest', None)
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def gold_check(gold):
    text = gold.read_text(encoding='utf-8')
    rule = re.search(r'```bash\n(.*?)\n```', text, re.S)[1]
    with tempfile.TemporaryDirectory(prefix='p1-gold-') as directory:
        repo = Path(directory) / 'repo'
        fixture = build(repo)
        expected = trusted_state(repo, fixture)
        command = shlex.split(rule.replace('<commit>', fixture['commit_a']).replace('<path>', TARGET))
        if command[0] != 'git':
            raise ValueError('Gold must use the reviewed Git rule')
        git(repo, *command[1:])
        result = evaluate(repo, expected)
    if not result['success']:
        raise ValueError('Gold rule failed the independent Oracle')
    return {'engineering_check': 'PASS', 'human_signoff': 'PENDING_USER_REVIEW',
            'sha256': sha256(gold), 'generic_rule': rule, 'oracle_assertions': result}


async def zero_probe(config, expected_count):
    from harbor.models.trial.config import TrialConfig
    from harbor.trial.trial import Trial
    value = json.loads(json.dumps(config))
    value['agent']['kwargs']['p1_mode'] = 'probe'
    # The paid config keeps the explicit credential selector; a pre-request probe needs no secret.
    value['agent'].pop('model_api_key_name', None)
    value['trial_name'] += '-zero'
    value['trials_dir'] = str(Path(value['trials_dir']).parent / 'zero_model_trials')
    parsed = TrialConfig.model_validate(value)
    profile = read(Path(value['agent']['kwargs']['p1_profile']))
    verifier_images = []
    original_verifier_env = Trial._separate_verifier_env

    @asynccontextmanager
    async def observe_verifier(trial, *args, **kwargs):
        async with original_verifier_env(trial, *args, **kwargs) as environment:
            container = await environment._run_docker_compose_command(['ps', '-q', 'main'])
            inspected = await asyncio.to_thread(subprocess.run,
                ['docker', 'inspect', container.stdout.strip(), '--format', '{{.Image}}'],
                capture_output=True, check=True)
            image_id = inspected.stdout.decode().strip()
            expected = profile.get('frozen_verifier_image_id')
            if expected and image_id != expected:
                raise RuntimeError('P1 verifier image differs from the frozen image')
            frozen = 'harbor-p1-verifier:sha256-' + image_id.split(':')[-1]
            await asyncio.to_thread(subprocess.run, ['docker', 'tag', image_id, frozen],
                                    capture_output=True, check=True)
            verifier_images.append({'image_id': image_id, 'frozen_image': frozen})
            yield environment

    # Independent tripwire: no fake model response can make this probe pass.
    with patch('litellm.acompletion', side_effect=AssertionError('Model API forbidden')) as completion, \
         patch('litellm.aresponses', side_effect=AssertionError('Model API forbidden')) as responses, \
         patch.object(Trial, '_separate_verifier_env', observe_verifier):
        trial = await Trial.create(parsed)
        result = await trial.run()
        api_calls = completion.call_count + responses.call_count
    observation_dir = trial.paths.trial_dir / 'p1-observer'
    summary_path = observation_dir / 'p1-summary.json'
    summary = read(summary_path) if summary_path.is_file() else {}
    requests_path = observation_dir / 'p1-model-requests.jsonl'
    requests = [json.loads(line) for line in requests_path.read_text(encoding='utf-8').splitlines()] if requests_path.is_file() else []
    index_path = observation_dir / 'p1-skill-index.xml'
    index = index_path.read_text(encoding='utf-8') if index_path.is_file() else ''
    initial_prompt = requests[0]['messages'][-1]['content'] if len(requests) == 1 else ''
    index_in_prompt = bool(index and index in initial_prompt) if expected_count else '<available_skills>' not in initial_prompt
    budget = read(Path(value['agent']['kwargs']['p1_profile']))['budget']
    first_input = requests[0]['estimated_input_tokens_with_reserve'] if len(requests) == 1 else None
    oracle_path = trial.paths.verifier_dir / 'assertions.json'
    oracle = read(oracle_path) if oracle_path.is_file() else {}
    raw = result.model_dump(mode='json')
    isolation_path = observation_dir / 'p1-isolation.jsonl'
    isolation = [json.loads(line) for line in isolation_path.read_text(encoding='utf-8').splitlines()] if isolation_path.is_file() else []
    isolated = next((item for item in isolation if item['status'] == 'PASS'), {})
    ok = (not raw.get('exception_info') and api_calls == 0 and index_in_prompt and bool(isolated) and
          first_input is not None and first_input <= budget['max_input_tokens_per_request'] and
          summary.get('stopped_before_model') is True and summary.get('paid_requests') == 0 and
          summary.get('model_read_ids') == [] and
          len(summary.get('controlled_probe_read_ids', [])) == expected_count and
          len(summary.get('full_body_visible_ids_ignoring_terminal_whitespace', [])) == expected_count and
          raw.get('verifier_environment_mode') == 'separate' and
          (raw.get('verifier_result') or {}).get('rewards') == {'reward': 0.0} and
          len(oracle.get('assertion_results', {})) == 9 and oracle.get('reason') is None and len(verifier_images) == 1)
    return {'status': 'PASS' if ok else 'FAIL', 'execution_kind': 'zero_model_pre_request_probe',
            'model_api_calls': api_calls, 'native_trial_path': str(trial.paths.trial_dir),
            'agent_class': type(trial.agent).__name__, 'summary': summary,
            'environment_image_id': isolated.get('environment_image_id'), 'frozen_image': isolated.get('frozen_image'),
            'verifier_image_id': verifier_images[0]['image_id'] if len(verifier_images) == 1 else None,
            'frozen_verifier_image': verifier_images[0]['frozen_image'] if len(verifier_images) == 1 else None,
            'initial_request_index_complete': index_in_prompt, 'initial_request_input_token_estimate_with_reserve': first_input,
            'native_exception': raw.get('exception_info'),
            'verifier_environment_mode': raw.get('verifier_environment_mode'),
            'oracle_reward_expected_noop': (raw.get('verifier_result') or {}).get('rewards')}


def prepare(root, run_id=None):
    from harbor.models.trial.config import TrialConfig
    root = Path(root).resolve()
    pilot = read(root / 'downstream_eval/configs/git_restore_pilot.json')
    profile = read(root / 'downstream_eval/configs/p1_smoke.json')
    lock = read(root / 'downstream_eval/configs/runner.lock.json')
    run_id = run_id or 'p1-' + uuid.uuid4().hex[:12]
    if not re.fullmatch(r'p1-[A-Za-z0-9_-]+', run_id):
        raise ValueError('Use a unique p1- run ID')
    output = inside(root, pilot['result_parent'] + '/' + run_id)
    output.mkdir(parents=True, exist_ok=False)
    environment = preflight(root)
    write(output / 'preflight.json', environment)
    if environment['status'] != 'PASS':
        return {'status': 'BLOCKED', 'path': str(output), 'reason': 'Pinned Harbor and Linux Docker are required'}
    write(output / 'profile.json', profile)
    write(output / 'runner.lock.json', lock)
    task, fixture = materialize_task(root, pilot, output, oracle_solution=False)
    if (task / 'solution').exists():
        raise ValueError('P1 task must not contain a reference solution')
    packages = canonical_packages(root, pilot)
    golden = root / 'downstream_eval/gold/SKILL.md'
    gold_review = gold_check(golden)
    write(output / 'gold-review.json', gold_review)
    configurations = {}
    manifests = {}
    model, budget = profile['model'], profile['budget']
    for arm in profile['arms']:
        stage = output / 'staged' / arm
        if arm == 'A1':
            selected = packages
        elif arm == 'Gold':
            from .integration.harbor_adapter import official_probe_class
            sid = profile['gold_skill_id']
            selected = {sid: {'path': golden, 'metadata': official_probe_class(root)._parse_skill_frontmatter(golden.read_text(encoding='utf-8')),
                              'files': inventory(golden.parent)}}
        else:
            selected = {}
        copy_packages(selected, stage)
        manifest = {'arm': arm, 'staged_root': str(stage), 'files': inventory(stage),
                    'metadata': {sid: item['metadata'] for sid, item in sorted(selected.items())}}
        manifest_path = output / 'skill-manifests' / (arm + '.json')
        write(manifest_path, manifest)
        raw = {'trial_name': run_id + '-' + arm, 'trials_dir': str(output / 'paid_trials'),
               'task': {'path': str(task)},
               'agent': {'import_path': lock['agent_import_path'], 'model_name': model['name'],
                         'model_base_url': model['base_url'], 'model_api_key_name': model['api_key_environment_variable'],
                         'model_api_format': model['api_format'], 'skills': [str(stage)] if selected else [],
                         'override_timeout_sec': budget['agent_timeout_sec'],
                         'override_setup_timeout_sec': budget['setup_timeout_sec'],
                         'kwargs': {'p1_mode': 'paid', 'p1_profile': str(output / 'profile.json'),
                                    'p1_manifest': str(manifest_path), 'max_turns': budget['max_requests'],
                                    'temperature': model['temperature'], 'reasoning_effort': model['reasoning_effort'],
                                    'enable_summarize': False, 'proactive_summarization_threshold': 0,
                                    'store_all_messages': True, 'record_terminal_session': profile['terminal']['record_asciinema'],
                                    'tmux_pane_width': profile['terminal']['width'], 'tmux_pane_height': profile['terminal']['height'],
                                    'llm_call_kwargs': {'max_completion_tokens': budget['max_completion_tokens_per_request'],
                                                        'num_retries': budget['num_retries'], 'timeout': budget['request_timeout_sec']}}},
               # Native Docker stop(delete=False) removes containers with compose down, retaining image cache.
               'environment': {'type': 'docker', 'delete': False, 'kwargs': {'enable_environment_dir_upload': False}},
               'verifier': {'override_timeout_sec': budget['verifier_timeout_sec']}}
        parsed = TrialConfig.model_validate(raw)
        configurations[arm] = parsed.model_dump(mode='json', exclude_none=True)
        manifests[arm] = manifest
        write(output / 'configs' / (arm + '.json'), configurations[arm])
    identities = {arm: fairness_identity(value) for arm, value in configurations.items()}
    if len(set(identities.values())) != 1:
        raise ValueError('A0/A1/Gold differ beyond the Skill treatment and output identity')
    write(output / 'fairness.json', {'status': 'PASS', 'shared_config_hashes': identities,
          'fixture': fixture, 'task_files': inventory(task), 'expected_skill_counts': {'A0': 0, 'A1': 14, 'Gold': 1},
          'instruction_sha256': sha256(task / 'instruction.md'), 'independent_environments': True})
    reports = {}
    for arm in profile['arms']:
        reports[arm] = asyncio.run(zero_probe(configurations[arm], len(manifests[arm]['metadata'])))
        write(output / (arm + '-zero-model.json'), reports[arm])
        if arm == 'A0' and reports[arm]['status'] == 'PASS':
            profile['frozen_agent_image_id'] = reports[arm]['environment_image_id']
            profile['frozen_agent_image'] = reports[arm]['frozen_image']
            profile['frozen_verifier_image_id'] = reports[arm]['verifier_image_id']
            profile['frozen_verifier_image'] = reports[arm]['frozen_verifier_image']
            write(output / 'profile.json', profile)
            task_toml = task / 'task.toml'
            text = task_toml.read_text(encoding='utf-8').replace('[environment]\n', '[environment]\ndocker_image = "' + profile['frozen_agent_image'] + '"\n')
            text = text.replace('[verifier.environment]\n', '[verifier.environment]\ndocker_image = "' + profile['frozen_verifier_image'] + '"\n')
            task_toml.write_text(text, encoding='utf-8', newline='\n')
    image_ids = {arm: report['environment_image_id'] for arm, report in reports.items()}
    image_consistent = len(set(image_ids.values())) == 1 and all(image_ids.values())
    verifier_ids = {arm: report['verifier_image_id'] for arm, report in reports.items()}
    verifier_consistent = len(set(verifier_ids.values())) == 1 and all(verifier_ids.values())
    write(output / 'fairness.json', {'status': 'PASS' if image_consistent and verifier_consistent else 'FAIL', 'shared_config_hashes': identities,
          'fixture': fixture, 'task_files': inventory(task), 'expected_skill_counts': {'A0': 0, 'A1': 14, 'Gold': 1},
          'instruction_sha256': sha256(task / 'instruction.md'), 'independent_environments': True,
          'actual_environment_image_ids': image_ids, 'frozen_image': profile.get('frozen_agent_image'),
          'actual_verifier_image_ids': verifier_ids, 'frozen_verifier_image': profile.get('frozen_verifier_image')})
    rates = profile['price_usd_per_million_tokens']
    per_arm = ((budget['max_input_tokens_total'] * rates['input'] + budget['max_requests'] * budget['max_completion_tokens_per_request'] * rates['output']) / 1_000_000) if rates else None
    result = {'status': 'PASS' if image_consistent and verifier_consistent and all(r['status'] == 'PASS' for r in reports.values()) else 'FAIL',
              'execution_kind': 'zero_model_preparation_only', 'path': str(output),
              'real_agent_execution': 'AWAITING_USER_APPROVAL', 'model_api_calls': 0,
              'api_key_present': bool(os.environ.get(model['api_key_environment_variable'])),
              'model': model, 'arms': reports, 'gold_review': gold_review,
              'estimated_budget_cost_usd_all_three': per_arm * 3 if per_arm is not None else None,
              'pricing_status': profile.get('pricing_status', 'fixed_reference_rates'),
              'cost_note': 'Token-budget estimate; actual provider usage, unreported failed requests and taxes are not verified',
              'proposed_commands': {arm: ['harbor', 'trials', 'start', '--config', str(output / 'configs' / (arm + '.json'))] for arm in profile['arms']},
              'remaining_blockers': ['Explicit user approval for paid inference', 'Human sign-off on Gold rule'] +
                                    ([] if os.environ.get(model['api_key_environment_variable']) else [model['api_key_environment_variable'] + ' is absent from control process']) +
                                    ([] if rates else ['Provider account tariff is unverified; no actual budget cost calculated'])}
    write(output / 'result.json', result)
    write(output / 'artifact_manifest.json', inventory(output))
    return {'status': result['status'], 'path': str(output), 'model_api_calls': 0,
            'real_agent_execution': result['real_agent_execution'],
            'arms': {arm: report['status'] for arm, report in reports.items()},
            'remaining_blockers': result['remaining_blockers']}
