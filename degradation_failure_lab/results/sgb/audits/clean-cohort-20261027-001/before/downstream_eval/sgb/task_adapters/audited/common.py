"""Reuse the registered pilot, native export, observer and trial budget."""
from pathlib import Path
import os

from degradation_lab.io import read, sha256
from downstream_eval.sgb import runner
from downstream_eval.sgb.task_adapters.scrapy041.adapter import native_trial

LAB = Path(__file__).resolve().parents[4]


def bind(task_id, score, verify_assets):
    task = LAB / 'downstream_eval/tasks/sgb/audited' / task_id

    def execution_config(output, generator_run_id, conditions):
        output = Path(output)
        return runner.ExecutionConfig(
            task_id=task_id, task_path=task, experiment_id=output.name,
            generator_run_id=generator_run_id,
            budget_scope='/'.join((task_id, generator_run_id, output.name)),
            agent_import_path='downstream_eval.sgb.task_adapters.audited.agent:AuditedTerminus2',
            trial_prefix='audit-', conditions=conditions, skill_conditions=('CleanSkill',),
            unscorable_categories=('environment_error', 'submission_missing', 'submission_ambiguous',
                'submission_origin_unknown', 'candidate_timeout', 'scorer_timeout',
                'candidate_protocol_error', 'scorer_protocol_error', 'scorer_integrity_error',
                'submission_hash_mismatch', 'invalid_submission'))

    def configure(output, label, mode, config):
        from harbor.models.trial.config import TrialConfig
        raw = runner.trial_config(output, label, mode, config)
        raw['extra_instruction_paths'] = [str(task / 'runtime-note.md')]
        return TrialConfig.model_validate(raw)

    def grade_export(trial, output):
        path, digest = trial._scrapy041_export
        if sha256(path) != digest:
            raise ValueError('Native export changed')
        return score(path, Path(output) / 'score', expected_sha256=digest)

    def paid_batch(output):
        if os.environ.get('SGB_AUDIT_ALLOW_PAID') != '1':
            raise RuntimeError('Audited pilot execution is not enabled')
        verify_assets()
        output = Path(output)
        if read(output / 'readiness.json')['status'] != 'PASS':
            raise RuntimeError('Zero-model preparation has not passed')
        profile = read(output / 'profile.json')
        config = execution_config(output, profile['generator_run_id'], profile['conditions'])
        from downstream_eval.sgb.scrapy024 import body_exposure
        return runner.execute_batch(LAB, output, config, run_trial=native_trial, grade=grade_export,
            exposure=body_exposure, task_success=lambda result: result['task_success'],
            configure_trial=configure)

    return execution_config, configure, grade_export, paid_batch
