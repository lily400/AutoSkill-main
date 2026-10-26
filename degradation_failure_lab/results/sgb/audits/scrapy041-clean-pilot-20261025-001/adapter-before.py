"""Task-041 binding to existing SGB runner, budgets, observer and Harbor export."""
import asyncio
import os
from pathlib import Path

from degradation_lab.io import read, sha256, write
from downstream_eval.sgb import runner
from .scoring import TASK, LAB, score, verify_assets


def execution_config(output, generator_run_id, conditions):
    output = Path(output)
    return runner.ExecutionConfig(
        task_id='scrapy-task-041', task_path=TASK, experiment_id=output.name,
        generator_run_id=generator_run_id,
        budget_scope='/'.join(('scrapy-task-041',generator_run_id,output.name)),
        agent_import_path='downstream_eval.sgb.task_adapters.scrapy041.agent:Scrapy041Terminus2',
        trial_prefix='s41-', conditions=conditions,
        skill_conditions=tuple(v for v in ('CleanSkill',) if v in conditions.values()),
        unscorable_categories=('environment_error','submission_missing','submission_ambiguous',
                              'submission_origin_unknown','candidate_timeout','scorer_timeout',
                              'candidate_protocol_error','scorer_protocol_error','scorer_integrity_error',
                              'submission_hash_mismatch','invalid_submission'))


def trial_config(output, label, mode, config):
    raw = runner.trial_config(output, label, mode, config)
    raw['extra_instruction_paths'] = [str(TASK / 'runtime-note.md')]
    return raw


def configure(output, label, mode, config):
    from harbor.models.trial.config import TrialConfig
    return TrialConfig.model_validate(trial_config(output,label,mode,config))


async def export_submission(environment, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    path = destination / 'agent_output.py'
    check = await environment.exec(
        "python -B -c \"from pathlib import Path; import hashlib; "
        "p=Path('/workspace/agent_output.py'); "
        "assert p.is_file() and not p.is_symlink(); print(hashlib.sha256(p.read_bytes()).hexdigest())\"",
        timeout_sec=10)
    if check.return_code:
        raise ValueError('No regular task submission')
    observed = check.stdout.strip()
    await environment.download_file(source_path='/workspace/agent_output.py', target_path=path)
    found, failure = runner.collect_submission(destination, 'agent_output.py')
    if failure or found != path or path.is_symlink() or sha256(path) != observed:
        raise ValueError('Export hash or identity mismatch')
    write(destination / 'receipt.json', {'method':'Harbor Environment.download_file',
          'source':'/workspace/agent_output.py', 'destination':str(path), 'sha256':observed,
          'scope':'controller-observed export; no candidate-supplied score'})
    return path, observed


def grade_export(trial, output):
    path, digest = asyncio.run(export_submission(trial.agent_environment, Path(output) / 'export'))
    return score(path, Path(output) / 'score', expected_sha256=digest)


def paid_batch(output):
    # This entry is not used by zero-model acceptance.
    if os.environ.get('SCRAPY041_ALLOW_PAID') != '1':
        raise RuntimeError('Scrapy041 paid execution is not enabled')
    verify_assets()
    output = Path(output); profile = read(output / 'profile.json')
    if read(output / 'readiness.json')['status'] != 'PASS':
        raise RuntimeError('This frozen experiment has not passed preparation')
    config = execution_config(output, profile['generator_run_id'], profile['conditions'])
    from downstream_eval.sgb.scrapy024 import native_trial, body_exposure
    return runner.execute_batch(LAB, output, config, run_trial=native_trial, grade=grade_export,
        exposure=body_exposure, task_success=lambda result:result['task_success'],
        configure_trial=configure)
