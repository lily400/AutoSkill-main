"""Configured workflow checks; no real model or task execution."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import read, write, sha256
from downstream_eval.sgb import pilot


class PilotWorkflow(unittest.TestCase):
    def setUp(self):
        self.task = pilot.load_binding(LAB, 'scrapy-task-041')

    def test_plan_uses_registered_configuration_without_importing_agent(self):
        with patch.object(pilot.importlib, 'import_module', side_effect=AssertionError('No Agent imports in plan')):
            result = pilot.plan(LAB, self.task, 's41r003', 'unit-plan-never-executed')
        self.assertEqual(result['max_http_calls'], 12)
        self.assertEqual(result['model_calls'], 0)
        self.assertFalse(Path(result['output']).exists())

    def test_plan_refuses_reusing_historical_experiment_id(self):
        with self.assertRaises(FileExistsError):
            pilot.plan(LAB, self.task, 's41r003', 's41d001')

    def test_status_reads_existing_ledger_without_mutation(self):
        db = LAB / 'runs/eval/sgb/scrapy-task-041/s41d001/budget.sqlite3'
        before = sha256(db)
        result = pilot.status(LAB, self.task, 's41d001')
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertEqual(result['http_attempts'], 4)
        self.assertEqual(before, sha256(db))

    def test_missing_ledger_is_not_created_by_status(self):
        result = pilot.status(LAB, self.task, 'unit-no-ledger')
        self.assertEqual(result['status'], 'NOT_PREPARED')
        self.assertFalse(Path(result['output']).exists())

    def test_backfill_goes_to_separate_analysis_directory(self):
        original = LAB / 'runs/eval/sgb/scrapy-task-041/s41d001/outcomes/CleanSkill1/result.json'
        before = sha256(original)
        with tempfile.TemporaryDirectory() as temp:
            result = pilot.analyze(LAB, self.task, 's41d001', Path(temp))
            clean = result['results'][1]['skill_usage']
            self.assertEqual(clean['status'], 'INDEX_ONLY_OBSERVED')
            self.assertEqual(clean['counts']['index_in_successful_model_request'], 45)
            self.assertEqual(clean['counts']['model_file_access_observed'], 0)
            self.assertEqual(clean['behavioral_use']['status'], 'UNKNOWN')
        self.assertEqual(sha256(original), before)

    def test_loading_checks_selected_task_without_global_dataset_audit(self):
        with patch.object(pilot, 'audit_registry', side_effect=AssertionError('Global audit only on registration')):
            self.assertEqual(pilot.load_binding(LAB, 'scrapy-task-041')['task_id'], 'scrapy-task-041')

    def test_loading_rejects_selected_source_tampering(self):
        actual = pilot.sha256
        source = LAB / 'data/raw_sources/sgb/5a8bd61d/dad43df16d07e2c3/offsite.md'
        with patch.object(pilot, 'sha256', side_effect=lambda p: '0' * 64 if Path(p) == source else actual(p)):
            with self.assertRaisesRegex(ValueError, 'Selected source'):
                pilot.load_binding(LAB, 'scrapy-task-041')

    def test_source_identity_mismatch_is_not_admitted(self):
        data = deepcopy(self.task)
        data['task_key'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            pilot._validate_binding(LAB, {'original_task_id': self.task['task_id'],
                                         'task_key': self.task['task_key']}, data)


class ProbeProtocol(unittest.TestCase):
    def exercise(self, complete=True, try_model=False):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / 'runs/eval/sgb/test-task/experiment'
            attempt = output / 'engineering/attempt-001'
            fixtures = {'good': {'source': '# fixture', 'passed': 10, 'failed': []},
                        'bad': {'source': '# fixture', 'passed': 8, 'failed': ['meta', 'boolean']}}
            write(root / 'fixtures.json', fixtures)
            write(output / 'profile.json', {'budget': {'max_input_tokens_per_request': 20000}})
            task = {'fixtures': 'fixtures.json', 'conditions': {'N': 'NoSkill', 'C': 'CleanSkill'},
                    'probes': {'N': 'good', 'C': 'bad'}, 'expected_oracle_tests': 10}
            def configure(output, label, mode, config):
                return SimpleNamespace(label=label, trials_dir=None)
            async def run(config, fixture, probe_hook):
                if try_model:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        await client.post('https://invalid.example/forbidden')
                expected = 1 if config.label == 'C' else 0
                trial_dir = attempt / 'native' / config.label
                observer = trial_dir / 'p1-observer'
                write(observer / 'p1-summary.json', {'stopped_before_model': True, 'actual_http_attempts': 0,
                       'controlled_probe_read_ids': ['id'] if expected else []})
                write(trial_dir / 'body-visibility.json', {'all_visible_ids': ['id'] if expected and complete else []})
                index = '<available_skills>index</available_skills>' if expected else ''
                (observer / 'p1-skill-index.xml').write_text(index, encoding='utf-8')
                req = {'messages': [{'content': index}], 'estimated_input_tokens_with_reserve': 100}
                (observer / 'p1-model-requests.jsonl').write_text(json.dumps(req) + '\n', encoding='utf-8')
                trial = SimpleNamespace(paths=SimpleNamespace(trial_dir=trial_dir), label=config.label,
                                        agent_environment=SimpleNamespace(stop=AsyncMock()))
                return trial, {'exception_info': None}
            def grade(trial, output):
                f = fixtures['good' if trial.label == 'N' else 'bad']
                return {'infra_ok': True, 'candidate_binding_verified': True,
                        'task_result': {'tests': 10, 'passed': f['passed']}, 'failed_tests': f['failed']}
            adapter = SimpleNamespace(configure=configure, native_trial=run, grade_export=grade)
            return pilot._probe(output, task, adapter, object(), {'id': {}}, attempt)

    def test_both_explicit_positive_and_negative_fixtures_are_checked(self):
        self.assertEqual([r['status'] for r in self.exercise()], ['PASS', 'PASS'])

    def test_preparation_blocks_accidental_model_transport(self):
        with self.assertRaisesRegex(AssertionError, 'forbids HTTP model calls'):
            self.exercise(try_model=True)

    def test_incomplete_body_delivery_does_not_pass_readiness(self):
        with self.assertRaisesRegex(RuntimeError, 'acceptance failed'):
            self.exercise(complete=False)


if __name__ == '__main__':
    unittest.main()
