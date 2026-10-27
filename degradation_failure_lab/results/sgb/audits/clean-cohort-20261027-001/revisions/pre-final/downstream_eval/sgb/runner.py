"""Small SGB execution mechanisms; task policy and external adapters stay explicit."""
import asyncio
from dataclasses import dataclass
from contextlib import closing
import json
import os
from pathlib import Path
import re
import sqlite3
import time

from degradation_lab.io import inventory, read, sha256, write
from downstream_eval.integration.request_budget import Ledger
from downstream_eval.integration.network_isolation import environment_config
from downstream_eval.scoring.results import trial_record, failure_kind


def _identifier(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', value)


@dataclass(frozen=True)
class ExecutionConfig:
    task_id: str
    task_path: Path
    experiment_id: str
    generator_run_id: str
    budget_scope: str
    agent_import_path: str
    trial_prefix: str
    conditions: dict
    skill_conditions: tuple
    unscorable_categories: tuple

    def __post_init__(self):
        if not all(_identifier(v) for v in (self.task_id, self.experiment_id, self.generator_run_id)):
            raise ValueError('Explicit task, experiment and generator identities are required')
        if Path(self.task_path).name != self.task_id:
            raise ValueError('Task path does not match task identity')
        if (not self.budget_scope or any(p in ('', '.', '..') for p in self.budget_scope.split('/'))
                or ':' not in self.agent_import_path or not _identifier(self.trial_prefix)):
            raise ValueError('Explicit budget scope, agent import and trial prefix are required')
        if (not self.conditions or not all(_identifier(v) for pair in self.conditions.items() for v in pair)
                or not set(self.skill_conditions) <= set(self.conditions.values())):
            raise ValueError('Explicit trial labels and Skill conditions are required')


def experiment_output(root, task_id, experiment, *, legacy_roots=()):
    if not _identifier(task_id) or not _identifier(experiment):
        raise ValueError('Explicit safe task and experiment identities are required')
    output = Path(root) / 'runs/eval/sgb' / task_id / experiment
    if any((Path(p) / experiment).exists() for p in legacy_roots) or (output / 'batch.started').exists():
        raise RuntimeError('Historical experiment ID already exists; preserve its ledger and results')
    return output


def execution_profile(output, config):
    output = Path(output)
    profile = read(output / 'profile.json')
    if profile.get('task_id') != config.task_id or profile.get('experiment_id') != config.experiment_id:
        raise ValueError('Task or experiment identity differs from explicit execution config')
    order = list(config.conditions)
    policy = profile['hard_http_budget']
    if (profile.get('trial_order') != order or policy.get('order') != order
            or set(profile.get('arms', [])) != set(config.conditions.values())
            or Path(policy['database']).resolve() != (output / 'budget.sqlite3').resolve()):
        raise ValueError('Trial conditions or budget database differ from explicit execution config')
    return profile


def trial_config(output, label, mode, config):
    """Build native Harbor input without importing or running the external framework."""
    output = Path(output)
    profile = execution_profile(output, config)
    if label not in config.conditions or mode not in ('paid', 'probe'):
        raise ValueError('Unknown trial label or execution mode')
    condition = config.conditions[label]
    stage = output / 'staged' / condition
    manifest = read(output / 'manifests' / (label + '.json'))
    if (manifest.get('arm') != label or manifest.get('generator_run_id') != config.generator_run_id
            or Path(manifest['staged_root']).resolve() != stage.resolve()):
        raise ValueError('Skill manifest identity differs from explicit execution config')
    if not stage.is_dir() or inventory(stage) != manifest['files']:
        raise ValueError('Staged Skill files differ from frozen manifest')
    skills_enabled = condition in config.skill_conditions
    if not skills_enabled and (manifest['files'] or manifest['metadata']):
        raise ValueError('No-Skill condition contains Skill files or metadata')
    model, budget = profile['model'], profile['budget']
    raw = {'trial_name':config.trial_prefix + label.lower(),
           'trials_dir':str(output / ('probe-trials' if mode == 'probe' else 'trials')),
           'task':{'path':str(config.task_path)},
           'agent':{'import_path':config.agent_import_path,
                    'model_name':model['name'], 'model_base_url':model['base_url'], 'model_api_format':model['api_format'],
                    'skills':[str(stage)] if skills_enabled else [],
                    'override_timeout_sec':budget['agent_timeout_sec'], 'override_setup_timeout_sec':budget['setup_timeout_sec'],
                    'kwargs':{'p1_mode':mode, 'p1_profile':str(output / 'profile.json'),
                              'p1_manifest':str(output / 'manifests' / (label + '.json')),
                              'max_turns':budget['max_requests'], 'temperature':model['temperature'],
                              'reasoning_effort':model['reasoning_effort'], 'enable_summarize':False,
                              'proactive_summarization_threshold':0, 'store_all_messages':True,
                              'record_terminal_session':False, 'tmux_pane_width':160, 'tmux_pane_height':40,
                              'llm_call_kwargs':{'max_completion_tokens':budget['max_completion_tokens_per_request'],
                                                 'num_retries':0, 'timeout':budget['request_timeout_sec']}}},
           'environment':environment_config(),
           'verifier':{'disable':True}}
    if mode == 'paid':
        raw['agent']['model_api_key_name'] = model['api_key_environment_variable']
    return raw


def configure(output, label, mode, config):
    raw = trial_config(output, label, mode, config)
    from harbor.models.trial.config import TrialConfig
    return TrialConfig.model_validate(raw)


def collect_submission(artifacts, filename):
    submitted = list(Path(artifacts).rglob(filename))
    if len(submitted) != 1:
        return None, {'failure_category':'submission_missing' if not submitted else 'submission_ambiguous',
                      'task_result':{'tests':0, 'passed':0}, 'rule_result':{'passed':None}}
    return submitted[0], None


def verify_frozen(root, output):
    root = Path(root).resolve()
    manifest = read(Path(output) / 'execution_manifest.json')
    for name, digest in manifest.items():
        path = (root / name).resolve()
        if Path(name).is_absolute() or not path.is_relative_to(root):
            raise ValueError('Frozen execution path escapes project: ' + name)
        if sha256(path) != digest:
            raise ValueError('Frozen execution file changed: ' + name)


def verify_ledger(root, output, config, profile):
    """Read existing policy only; never create, reset or migrate a budget."""
    output = Path(output)
    with closing(sqlite3.connect((output / 'budget.sqlite3').resolve().as_uri() + '?mode=ro', uri=True)) as db:
        policy = json.loads(db.execute('SELECT data FROM policy WHERE id=1').fetchone()[0])
    frozen = read(output / 'execution_manifest.json')
    expected = {'scope':config.budget_scope, 'order':list(config.conditions),
                'budget':profile['budget'], 'global_limit':profile['hard_http_budget']['global_limit'],
                'per_trial_limit':profile['hard_http_budget']['per_arm_limit'],
                'trials':{label:config.trial_prefix + label.lower() for label in config.conditions},
                'files':{str(Path(root) / name):digest for name, digest in frozen.items()}}
    if any(policy.get(key) != value for key, value in expected.items()):
        raise ValueError('Budget scope, trials or frozen identities differ from explicit execution config')


def execute_batch(root, output, config, *, run_trial, grade, exposure, task_success,
                  configure_trial=None, run_kind='agent_trial'):
    """Coordinate the existing Trial, scorer and observer; no replacement Agent loop."""
    if run_kind not in ('agent_trial', 'offline_fixture'):
        raise ValueError('Unknown execution evidence kind')
    fixture = run_kind == 'offline_fixture'
    if fixture and configure_trial is None:
        raise ValueError('Offline fixture requires an explicit simulated config loader')
    output = Path(output)
    profile = execution_profile(output, config)
    verify_frozen(root, output)
    verify_ledger(root, output, config, profile)
    # Validate every condition before the durable admission marker or any Agent execution.
    if fixture and Ledger(output / 'budget.sqlite3').snapshot()['attempts']:
        raise ValueError('Offline fixture cannot reuse HTTP attempt history')
    configs = {label:(configure_trial or configure)(output, label, 'probe' if fixture else 'paid', config)
               for label in config.conditions}
    if profile.get('protocol_id'):
        from .protocol import validate as validate_protocol
        raw = {label: c.model_dump(mode='json', exclude_none=True) for label, c in configs.items()}
        validate_protocol(root, profile, raw)
        if any(raw[label] != read(output / 'configs' / (label + '.json')) for label in raw):
            raise ValueError('Execution differs from frozen paired configuration')
    with (output / 'batch.started').open('x') as stream:
        stream.write('One frozen batch; do not restart or resend.\n')
    ledger = Ledger(output / 'budget.sqlite3')
    results = []
    for label, native_config in configs.items():
        lease = ledger.begin(label, native_config.trial_name)
        os.environ['P1_BUDGET_LEASE'] = lease
        start = time.monotonic()
        stage = 'agent_setup_or_execution'
        score = {}
        try:
            trial, native = asyncio.run(run_trial(native_config))
            write(output / 'outcomes' / label / 'native.json', native)
            stage = 'independent_oracle'
            score = grade(trial, output / 'outcomes' / label / 'oracle')
            stage = 'body_exposure_analysis'
            observed = exposure(trial, output, label)
            from downstream_eval.integration.skill_usage import save_skill_usage
            usage_report = save_skill_usage(output, label, trial.paths.trial_dir,
                output / 'outcomes' / label / 'skill_usage.json')
            attempts = [a for a in ledger.snapshot()['attempts'] if a['arm'] == label]
            kind = failure_kind(dict(score, task_success=task_success(score)), native.get('exception_info'), attempts=attempts)
            infra = kind != 'infrastructure_failure'
            success = bool(task_success(score)) if infra and kind != 'budget_exhausted' else False
            tools = trial.paths.trial_dir / 'p1-observer/p1-tool-actions.jsonl'
            tool_calls = sum(json.loads(line).get('stage') == 'submitted' for line in tools.read_text().splitlines()) if tools.exists() else 0
            record = {'label':label, 'condition':config.conditions[label],
                      'task_success':success, 'infra_ok':infra, 'oracle':score, 'exposure':observed,
                      'outcome_schema':2, 'failure_kind':kind,
                      'elapsed_seconds':time.monotonic() - start, 'model_api_results':True,
                      'failure_category':score.get('failure_category') if not native.get('exception_info') else 'agent_environment_or_execution',
                      'native_exception':native.get('exception_info'), 'tool_calls':tool_calls,
                      'skill_usage':{'status':usage_report['status'], 'counts':usage_report['counts'],
                                     'behavioral_use':usage_report['behavioral_use']},
                      'http_attempts':len(attempts),
                      'token_usage':{k:sum(a.get(k) or 0 for a in attempts) for k in ['input_tokens','cached_tokens','output_tokens']},
                      'unknown_usage_attempts':sum(a['input_tokens'] is None for a in attempts)}
            if fixture:
                if ledger.snapshot()['attempts']:
                    raise RuntimeError('Offline fixture recorded an HTTP attempt')
                outcome = trial_record(record, config.task_id, 'offline_fixture')['outcome']
                record.update(run_kind='offline_fixture', real_agent_outcome=False,
                              model_api_results=False, task_success=None,
                              fixture_task_success=success, fixture_outcome=outcome,
                              model_calls=0, actual_http_attempts=0)
            results.append(record)
            write(output / 'outcomes' / label / 'result.json', record)
            proceed = ledger.finish(label, native_config.trial_name, lease,
                                    {'infra_ok':infra, 'task_success':success,
                                     'skill_read':bool(observed['model_body_exposed_ids'])})
            write(output / 'batch_results.json', {'results':results, 'ledger':ledger.snapshot()})
            if not proceed:
                break
        except BaseException as error:
            attempts = [a for a in ledger.snapshot()['attempts'] if a['arm'] == label]
            kind = failure_kind({}, error=error, stage=stage, attempts=attempts)
            infra = kind != 'infrastructure_failure'
            record = {'label':label, 'condition':config.conditions[label], 'outcome_schema':2,
                      'task_success':False if infra else None, 'infra_ok':infra, 'failure_kind':kind,
                      'failure_category':kind, 'failed_stage':stage, 'error_type':type(error).__name__,
                      'elapsed_seconds':time.monotonic() - start, 'model_api_results':not fixture,
                      'oracle':score, 'http_attempts':len(attempts),
                      'token_usage':{k:sum(a.get(k) or 0 for a in attempts)
                                     for k in ('input_tokens','cached_tokens','output_tokens')},
                      'unknown_usage_attempts':sum(a.get('input_tokens') is None for a in attempts)}
            if fixture:
                record.update(run_kind='offline_fixture', real_agent_outcome=False, task_success=None,
                              fixture_task_success=False, model_calls=0, actual_http_attempts=0)
            results.append(record)
            write(output / 'outcomes' / label / 'result.json', record)
            proceed = ledger.finish(label, native_config.trial_name, lease,
                                    {'infra_ok':infra, 'task_success':False, 'skill_read':False})
            write(output / 'batch_results.json', {'results':results, 'ledger':ledger.snapshot()})
            stop = {'label':label, 'failed_stage':stage, 'error_type':type(error).__name__,
                    'failure_kind':kind, 'elapsed_seconds':time.monotonic() - start, 'ledger':ledger.snapshot()}
            write(output / 'outcomes' / label / 'stop.json', stop)
            if not proceed:
                write(output / 'batch_stop.json', stop)
                return 2
        finally:
            os.environ.pop('P1_BUDGET_LEASE', None)
    return 0 if len(results) == len(config.conditions) else 2
