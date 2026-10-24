"""Declarative SGB task binding; current execution proof is restricted to offline fixtures."""
import copy
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import tomllib

from degradation_lab.io import inside, inventory, read, sha256
from degradation_lab.sgb import CONFIG, audit_registry, selected_tasks
from downstream_eval.sgb import runner


@dataclass(frozen=True)
class TaskContract:
    root: Path
    descriptor_path: Path
    descriptor_sha256: str
    data: dict
    execution: runner.ExecutionConfig
    original_assets: dict

    def trial_config(self, output, label, mode):
        raw = runner.trial_config(output, label, mode, self.execution)
        raw['environment'] = copy.deepcopy(self.data['environment'])
        return raw


def load_task(root, selector):
    """Reuse the existing SGB registry. An execution_contract binding is not runtime admission."""
    root = Path(root).resolve()
    catalog, rows = selected_tasks(root, [selector])
    if len(rows) != 1:
        raise ValueError('One unambiguous SGB task is required')
    row = rows[0]
    binding = row.get('execution_contract')
    if not isinstance(binding, dict) or set(binding) != {'path', 'sha256'}:
        raise ValueError('Task has no explicit execution_contract binding')
    path = inside(root, binding['path'])
    if sha256(path) != binding['sha256']:
        raise ValueError('Task contract identity changed')
    data = read(path)
    audit_registry(root)
    try:
        if (data['schema_version'] != 1 or data['task_id'] != row['original_task_id']
                or data['source_type'] != row['source_type']
                or data['source_type'] not in ('code_repo', 'code_doc', 'domain_knowledge_doc')
                or data['source'] != {'task_key':row['task_key'], 'revision':catalog['revision']}):
            raise ValueError('Task/source identity differs from registered SGB task')
        task = data['task']
        task_path = inside(root, task['path'])
        if not task['files'] or inventory(task_path) != task['files']:
            raise ValueError('Prepared task asset identity changed')
        if (task['instruction'], task['config']) != ('instruction.md', 'task.toml'):
            raise ValueError('Nonstandard task inputs need an explicit Harbor adapter')
        for name in ('instruction', 'config'):
            if task[name] not in task['files']:
                raise ValueError('Task input must be an explicitly frozen asset')
            inside(task_path, task[name])
        native = tomllib.loads(inside(task_path, task['config']).read_text(encoding='utf-8'))
        if native.get('schema_version') != '1.4' or native.get('metadata', {}).get('task_id') != data['task_id']:
            raise ValueError('Expected a derived Harbor 1.4 task with matching identity')
        if data['agent_protocol'] != 'p1_compatible_v1':
            raise ValueError('Agent protocol needs an explicit framework adapter')
        if not isinstance(data['environment'], dict) or not data['environment'].get('type'):
            raise ValueError('Explicit native environment configuration required')
        submission = data['submission']
        relative = Path(submission['artifact_path'])
        if (submission['protocol'] != 'single_file_v1' or relative.is_absolute()
                or any(p in ('', '.', '..') for p in relative.parts)
                or relative.name != submission['filename']
                or Path(submission['filename']).name != submission['filename']):
            raise ValueError('Unsupported or unsafe submission protocol')
        source = PurePosixPath(submission['source_path'])
        if not source.is_absolute() or '..' in source.parts or source.name != submission['filename']:
            raise ValueError('Explicit safe Agent submission path required')
        if native.get('artifacts') != [{'source':str(source), 'destination':submission['artifact_path']}]:
            raise ValueError('Native artifact export differs from submission contract')
        grading = data['grading']
        if (grading['protocol'] != 'submission_callback_v1' or not runner._identifier(grading['entrypoint'])
                or type(grading['timeout_sec']) not in (int, float)
                or not 0 < grading['timeout_sec'] < float('inf')):
            raise ValueError('Explicit grading protocol, entrypoint and finite timeout required')
        config = runner.ExecutionConfig(task_id=data['task_id'], task_path=task_path,
            **{k:v for k,v in data['execution'].items() if k != 'skill_conditions'},
            skill_conditions=tuple(data['execution']['skill_conditions']))
        scope = '/'.join((config.task_id, config.generator_run_id, config.experiment_id))
        if config.budget_scope != scope:
            raise ValueError('Budget scope must bind task, generator and experiment')
        if (not config.skill_conditions or not (set(config.conditions.values()) - set(config.skill_conditions))
                or not {'environment_error', 'submission_ambiguous', 'submission_origin_unknown'}
                       <= set(config.unscorable_categories)):
            raise ValueError('Explicit NoSkill/Skill conditions and infrastructure failure categories required')
    except (KeyError, TypeError) as error:
        raise ValueError('Incomplete SGB task contract') from error
    snapshot = inside(root, catalog['snapshot'])
    return TaskContract(root, path, binding['sha256'], data, config,
                        {str(inside(snapshot, name)):digest for name,digest in row['official_assets'].items()})


def run_fixture(task, output, *, configure_trial, run_trial, grader_id, grade_submission):
    """Exercise the common lifecycle in an external disposable root, never admit a real trial.

    configure_trial and run_trial are injected simulated framework hooks. The trusted
    submission callback returns explicit task_success and the existing score protocol.
    No callback is imported from untrusted task data. This proves neither transport
    authenticity, runtime isolation nor enforcement of a grader subprocess timeout.
    """
    root, output = task.root, Path(output).resolve()
    if root.is_relative_to(Path(__file__).resolve().parents[3]):
        raise ValueError('Offline fixture execution must stay outside the research project')
    current = load_task(root, task.execution.task_id)
    if (current.descriptor_sha256 != task.descriptor_sha256 or current.data != task.data
            or current.execution != task.execution or current.original_assets != task.original_assets):
        raise ValueError('Loaded task contract changed')
    config = task.execution
    expected = runner.experiment_output(root, config.task_id, config.experiment_id)
    if output != expected.resolve() or grader_id != task.data['grading']['entrypoint']:
        raise ValueError('Experiment output or grading entrypoint identity mismatch')
    profile = runner.execution_profile(output, config)
    if (profile.get('run_kind') != 'offline_fixture'
            or profile.get('generator_run_id') != config.generator_run_id
            or profile.get('budget_scope') != config.budget_scope
            or profile['hard_http_budget']['global_limit'] != 0
            or profile['hard_http_budget']['per_arm_limit'] != 0):
        raise ValueError('Fixture requires its own explicit zero-HTTP profile')
    # Bind registration, prepared inputs and this run's profile/Skills to the existing ledger.
    frozen = read(output / 'execution_manifest.json')
    catalog, _ = selected_tasks(root, [config.task_id])
    required = {task.descriptor_path.relative_to(root).as_posix():task.descriptor_sha256,
                CONFIG:sha256(root / CONFIG), catalog['registry']:sha256(inside(root, catalog['registry'])),
                (output / 'profile.json').relative_to(root).as_posix():sha256(output / 'profile.json')}
    required.update({(config.task_path / name).relative_to(root).as_posix():digest
                     for name,digest in task.data['task']['files'].items()})
    for label, condition in config.conditions.items():
        manifest = output / 'manifests' / (label + '.json')
        required[manifest.relative_to(root).as_posix()] = sha256(manifest)
        required.update({(output / 'staged' / condition / name).relative_to(root).as_posix():digest
                         for name,digest in read(manifest)['files'].items()})
    if any(frozen.get(name) != digest for name,digest in required.items()):
        raise ValueError('Contract/profile/Skill identities missing from frozen execution')
    code = {str(path):sha256(path)
            for path in (Path(runner.__file__).resolve(), Path(__file__).resolve())}

    def configure(output, label, mode, execution):
        return configure_trial(task.trial_config(output, label, mode))

    def grade(trial, destination):
        artifacts = Path(trial.paths.artifacts_dir)
        submission, failure = runner.collect_submission(artifacts, task.data['submission']['filename'])
        if not failure:
            expected = artifacts / task.data['submission']['artifact_path']
            if (submission.resolve() != expected.resolve() or submission.is_symlink()
                    or not submission.resolve().is_relative_to(artifacts.resolve())):
                failure = {'failure_category':'submission_origin_unknown',
                           'task_result':{'tests':0, 'passed':0}, 'rule_result':{'passed':None}}
        if failure:
            score = {**failure, 'task_success':False}
        else:
            before = sha256(submission)
            score = grade_submission(submission, destination, copy.deepcopy(task.data['grading']))
            if (type(score.get('task_success')) is not bool or not isinstance(score.get('failure_category'), str)
                    or sha256(submission) != before):
                raise ValueError('Grader returned an invalid score or changed the candidate')
            score = {**score, 'candidate_sha256':before}
        return {**score, 'task_contract_sha256':task.descriptor_sha256,
                'source_identity':task.data['source'], 'code_version':code,
                'artifact_transport_verified':False, 'runtime_isolation_verified':False,
                'grader_timeout_enforced':False}

    return runner.execute_batch(root, output, config, run_trial=run_trial, grade=grade,
        exposure=lambda *args:{'model_body_exposed_ids':[], 'runtime_observation':'NOT_RUN'},
        task_success=lambda score:score['task_success'], configure_trial=configure,
        run_kind='offline_fixture')
