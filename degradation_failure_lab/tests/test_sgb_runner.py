"""Offline execution contracts; all evidence and ledgers here are temporary fixtures."""
from dataclasses import replace
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import inventory, read, sha256, write
from downstream_eval.integration.request_budget import Ledger
from downstream_eval.integration.skill_install import copy_packages
from downstream_eval.scoring.results import trial_record
from downstream_eval.sgb import runner, scrapy024


class SGBRunner(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='sgb-runner-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for name in ('socket.socket.connect', 'socket.socket.connect_ex', 'socket.getaddrinfo', 'subprocess.Popen'):
            guard = patch(name, side_effect=AssertionError('No real network, model or subprocess'))
            guard.start()
            self.addCleanup(guard.stop)
        self.config = runner.ExecutionConfig(
            task_id='fixture-task-901', task_path=self.root / 'tasks/fixture-task-901',
            experiment_id='fixture-experiment-1', generator_run_id='fixture-gen-1',
            budget_scope='fixture-task-901/fixture-gen-1/test-only',
            agent_import_path='fixture_only:NeverInstantiate', trial_prefix='fixture-',
            conditions={'control1':'WithoutDocs', 'docs1':'WithDocs'},
            skill_conditions=('WithDocs',), unscorable_categories=('environment_error', 'submission_ambiguous'))
        self.output = runner.experiment_output(self.root, self.config.task_id, 'fixture-run-1')
        # Reuse the real profile schema, but bind every identity/path to this disposable fixture.
        profile = read(LAB / 'runs/eval/sgb/scrapy-task-024/s24d001/profile.json')
        profile.update(task_id=self.config.task_id, experiment_id=self.config.experiment_id,
                       trial_order=list(self.config.conditions), arms=['WithoutDocs', 'WithDocs'])
        profile['hard_http_budget'] = {'database':str(self.output / 'budget.sqlite3'),
                                      'per_arm_limit':2, 'global_limit':4, 'order':list(self.config.conditions)}
        profile['budget']['max_requests'] = 2
        write(self.output / 'profile.json', profile)
        for label, condition in self.config.conditions.items():
            stage = self.output / 'staged' / condition
            stage.mkdir(parents=True)
            metadata = {}
            if condition in self.config.skill_conditions:
                (stage / 'fixture-skill').mkdir()
                (stage / 'fixture-skill/SKILL.md').write_bytes(b'---\r\nname: fixture\r\n---\r\nFrozen body.\r\n')
                metadata = {'fixture-skill':{'name':'fixture', 'description':'Fixture only'}}
            write(self.output / 'manifests' / (label + '.json'),
                  {'arm':label, 'generator_run_id':self.config.generator_run_id,
                   'staged_root':str(stage), 'files':inventory(stage), 'metadata':metadata})
        self.payload = self.root / 'frozen-evidence.bin'
        self.payload.write_bytes(b'Unchanged evidence\r\n')
        self.frozen = {'frozen-evidence.bin':sha256(self.payload)}
        write(self.output / 'execution_manifest.json', self.frozen)
        self.ledger = Ledger.create(self.output / 'budget.sqlite3',
            {'scope':self.config.budget_scope, 'order':list(self.config.conditions),
             'budget':profile['budget'], 'global_limit':4, 'per_trial_limit':2,
             'trials':{label:self.config.trial_prefix + label.lower() for label in self.config.conditions},
             'files':{str(self.root / name):digest for name, digest in self.frozen.items()}})

    @staticmethod
    def parsed(output, label, mode, config):
        raw = runner.trial_config(output, label, mode, config)
        return SimpleNamespace(trial_name=raw['trial_name'], raw=raw)

    @staticmethod
    def completed_fixture(coroutine):
        # These async fixtures never suspend. Avoid Windows event-loop socketpair setup
        # while the test's network tripwire is active; no Harbor lifecycle is run.
        try:
            coroutine.send(None)
        except StopIteration as completed:
            return completed.value
        finally:
            coroutine.close()
        raise AssertionError('Offline async fixture unexpectedly suspended')

    def execute(self, *, native_exception=None, grade_error=None, run_error=None, category='none', passed=2):
        async def run(config):
            if run_error:
                raise run_error
            trial = SimpleNamespace(paths=SimpleNamespace(trial_dir=self.output / 'fake-native' / config.trial_name))
            return trial, {'exception_info':native_exception}
        run_mock = AsyncMock(side_effect=run)
        grade = Mock(side_effect=grade_error) if grade_error else Mock(return_value={
            'failure_category':category, 'task_result':{'tests':2, 'passed':passed}, 'rule_result':{'passed':passed == 2}})
        observe = Mock(return_value={'model_body_exposed_ids':[]})
        with patch.object(runner, 'configure', side_effect=self.parsed), \
             patch.object(runner.asyncio, 'run', side_effect=self.completed_fixture):
            status = runner.execute_batch(self.root, self.output, self.config, run_trial=run_mock,
                grade=grade, exposure=observe,
                task_success=lambda score:score['task_result']['tests'] == score['task_result']['passed'] == 2)
        return status, run_mock, grade

    def test_explicit_config_uses_fixture_identities_and_skill_conditions(self):
        raw = runner.trial_config(self.output, 'docs1', 'paid', self.config)
        self.assertEqual(raw['task']['path'], str(self.config.task_path))
        self.assertEqual(raw['agent']['import_path'], self.config.agent_import_path)
        self.assertEqual(raw['trial_name'], 'fixture-docs1')
        self.assertEqual(raw['agent']['skills'], [str(self.output / 'staged/WithDocs')])
        self.assertEqual(raw['agent']['kwargs']['max_turns'], 2)
        self.assertEqual(runner.execution_profile(self.output, self.config)['experiment_id'], 'fixture-experiment-1')
        probe = runner.trial_config(self.output, 'control1', 'probe', self.config)
        self.assertEqual(probe['agent']['skills'], [])
        self.assertNotIn('model_api_key_name', probe['agent'])
        self.assertFalse(raw['environment']['kwargs']['enable_environment_dir_upload'])
        self.assertTrue(raw['verifier']['disable'])
        from downstream_eval.integration.network_isolation import environment_config
        self.assertEqual(raw['environment'], environment_config())

    def test_missing_or_mismatched_task_and_experiment_are_rejected(self):
        for key in ('task_id', 'experiment_id'):
            for value in (None, 'another-identity'):
                with self.subTest(key=key, value=value):
                    profile = read(self.output / 'profile.json')
                    original = profile[key]
                    if value is None:
                        del profile[key]
                    else:
                        profile[key] = value
                    write(self.output / 'profile.json', profile)
                    with self.assertRaisesRegex(ValueError, 'identity'):
                        runner.trial_config(self.output, 'control1', 'paid', self.config)
                    profile[key] = original
                    write(self.output / 'profile.json', profile)

    def test_public_config_has_no_task_or_experiment_defaults(self):
        with self.assertRaises(TypeError):
            runner.ExecutionConfig()
        for field, value in (('task_id', ''), ('experiment_id', ''), ('generator_run_id', ''), ('budget_scope', '')):
            with self.subTest(field=field), self.assertRaises(ValueError):
                replace(self.config, **{field:value})
        with self.assertRaisesRegex(ValueError, 'Task path'):
            replace(self.config, task_id='another-task')
        for value in ('../escape', '/absolute', 'task/child'):
            with self.assertRaises(ValueError):
                runner.experiment_output(self.root, value, 'fixture-run')
        for label, mode in (('unknown', 'paid'), ('docs1', 'unknown')):
            with self.assertRaises(ValueError):
                runner.trial_config(self.output, label, mode, self.config)

    def test_profile_cannot_point_at_another_experiment_ledger(self):
        profile = read(self.output / 'profile.json')
        profile['hard_http_budget']['database'] = str(self.root / 'historical-budget.sqlite3')
        write(self.output / 'profile.json', profile)
        with self.assertRaisesRegex(ValueError, 'budget database'):
            runner.trial_config(self.output, 'control1', 'paid', self.config)

    def test_manifest_cannot_reuse_other_generator_or_trial_identity(self):
        path = self.output / 'manifests/docs1.json'
        original = read(path)
        for field, value in (('generator_run_id', 'another-run'), ('arm', 'control1'), ('staged_root', str(self.root))):
            with self.subTest(field=field):
                write(path, dict(original, **{field:value}))
                with self.assertRaisesRegex(ValueError, 'Skill manifest identity'):
                    runner.trial_config(self.output, 'docs1', 'paid', self.config)

    def test_changed_skill_bytes_are_rejected_before_admission(self):
        (self.output / 'staged/WithDocs/fixture-skill/SKILL.md').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Staged Skill'):
            self.execute()
        self.assertFalse((self.output / 'batch.started').exists())
        self.assertTrue(all(arm['state'] == 'NEW' for arm in self.ledger.snapshot()['arms']))

    def test_no_skill_condition_cannot_silently_install_skills(self):
        stage = self.output / 'staged/WithoutDocs'
        (stage / 'SKILL.md').write_bytes(b'contamination')
        manifest = read(self.output / 'manifests/control1.json')
        manifest['files'] = inventory(stage)
        write(self.output / 'manifests/control1.json', manifest)
        with self.assertRaisesRegex(ValueError, 'No-Skill condition'):
            runner.trial_config(self.output, 'control1', 'paid', self.config)

    def test_existing_skill_copy_keeps_all_bytes_and_rejects_wrong_hash(self):
        source = self.output / 'staged/WithDocs/fixture-skill'
        packages = {'fixture-skill':{'path':source / 'SKILL.md', 'files':inventory(source)}}
        copy_packages(packages, self.root / 'copy')
        self.assertEqual(inventory(self.root / 'copy/fixture-skill'), inventory(source))
        packages['fixture-skill']['files']['SKILL.md'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'Package bytes changed'):
            copy_packages(packages, self.root / 'bad-copy')

    def test_budget_scope_mismatch_does_not_admit_or_recreate_budget(self):
        digest = sha256(self.output / 'budget.sqlite3')
        self.config = replace(self.config, budget_scope='another/scope')
        with self.assertRaisesRegex(ValueError, 'Budget scope'):
            self.execute()
        self.assertEqual(sha256(self.output / 'budget.sqlite3'), digest)
        self.assertFalse((self.output / 'batch.started').exists())

    def test_budget_frozen_file_set_must_match_execution_manifest(self):
        write(self.output / 'execution_manifest.json', {})
        with self.assertRaisesRegex(ValueError, 'frozen identities'):
            self.execute()
        self.assertFalse((self.output / 'batch.started').exists())

    def test_missing_budget_is_never_created(self):
        self.config = replace(self.config, experiment_id='fixture-experiment-2')
        profile = read(self.output / 'profile.json')
        new_output = self.root / 'another-experiment'
        profile.update(experiment_id=self.config.experiment_id)
        profile['hard_http_budget']['database'] = str(new_output / 'budget.sqlite3')
        write(new_output / 'profile.json', profile)
        write(new_output / 'execution_manifest.json', self.frozen)
        import sqlite3
        with self.assertRaises(sqlite3.OperationalError):
            runner.verify_ledger(self.root, new_output, self.config, profile)
        self.assertFalse((new_output / 'budget.sqlite3').exists())

    def test_frozen_execution_changes_and_escape_are_rejected(self):
        self.payload.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Frozen execution file changed'):
            runner.verify_frozen(self.root, self.output)
        write(self.output / 'execution_manifest.json', {'../escape':sha256(self.payload)})
        with self.assertRaisesRegex(ValueError, 'escapes project'):
            runner.verify_frozen(self.root, self.output)

    def test_wrong_answer_is_scorable_and_does_not_stop_next_trial(self):
        status, run, _ = self.execute(category='fixture_wrong_answer', passed=1)
        self.assertEqual(status, 0)
        self.assertEqual(run.await_count, 2)
        rows = read(self.output / 'batch_results.json')['results']
        self.assertEqual([r['condition'] for r in rows], ['WithoutDocs', 'WithDocs'])
        self.assertTrue(all(trial_record(r, self.config.task_id, 'fixture')['outcome'] == 'failed' for r in rows))
        self.assertNotIn('P1_BUDGET_LEASE', os.environ)
        with self.assertRaises(FileExistsError):
            self.execute()
        self.assertTrue(all(a['state'] == 'DONE' for a in self.ledger.snapshot()['arms']))

    def test_native_failure_is_unscorable_and_stops_next_trial(self):
        status, run, _ = self.execute(native_exception={'type':'FixtureExecutionError'})
        self.assertEqual((status, run.await_count), (2, 1))
        row = read(self.output / 'batch_results.json')['results'][0]
        self.assertEqual(row['failure_category'], 'agent_environment_or_execution')
        self.assertEqual(trial_record(row, self.config.task_id, 'fixture')['outcome'], 'unscorable')

    def test_scorer_environment_failure_is_unscorable(self):
        status, run, _ = self.execute(category='environment_error', passed=0)
        self.assertEqual((status, run.await_count), (2, 1))
        row = read(self.output / 'batch_results.json')['results'][0]
        self.assertEqual(row['failure_category'], 'environment_error')
        self.assertEqual(trial_record(row, self.config.task_id, 'fixture')['outcome'], 'unscorable')

    def test_scorer_exception_records_grading_stage_and_stops_batch(self):
        status, run, grade = self.execute(grade_error=ValueError('fixture grader'))
        self.assertEqual(status, 2)
        self.assertEqual(run.await_count, 1)
        self.assertEqual(read(self.output / 'batch_stop.json')['failed_stage'], 'independent_oracle')
        self.assertEqual(read(self.output / 'batch_stop.json')['error_type'], 'ValueError')
        self.assertNotIn('P1_BUDGET_LEASE', os.environ)
        self.assertFalse((self.output / 'batch_results.json').exists())

    def test_successful_fixture_is_recorded_without_using_scrapy_assertion_count(self):
        status, run, _ = self.execute()
        self.assertEqual((status, run.await_count), (0, 2))
        rows = read(self.output / 'batch_results.json')['results']
        self.assertTrue(all(trial_record(r, self.config.task_id, 'fixture')['outcome'] == 'passed' for r in rows))
        self.assertEqual([call.args[0].raw['agent']['skills'] for call in run.call_args_list],
                         [[], [str(self.output / 'staged/WithDocs')]])

    def test_execution_exception_is_recorded_before_grading(self):
        status, _, grade = self.execute(run_error=RuntimeError('fixture execution'))
        self.assertEqual(status, 2)
        self.assertEqual(read(self.output / 'batch_stop.json')['failed_stage'], 'agent_setup_or_execution')
        self.assertEqual(read(self.output / 'batch_stop.json')['error_type'], 'RuntimeError')
        grade.assert_not_called()

    def test_submission_collection_does_not_invoke_oracle_for_missing_or_ambiguous_output(self):
        artifacts = self.root / 'artifacts'
        artifacts.mkdir()
        trial = SimpleNamespace(paths=SimpleNamespace(artifacts_dir=artifacts))
        with patch.object(scrapy024, 'scorer_module', side_effect=AssertionError('No Oracle execution')):
            self.assertEqual(scrapy024.grade_export(trial, self.root / 'score')['failure_category'], 'submission_missing')
            for name in ('first', 'second'):
                (artifacts / name).mkdir()
                (artifacts / name / 'agent_output.py').write_bytes(b'fixture')
            self.assertEqual(scrapy024.grade_export(trial, self.root / 'score')['failure_category'], 'submission_ambiguous')

    def test_collects_explicit_submission_filename(self):
        path = self.root / 'artifacts/nested'
        path.mkdir(parents=True)
        (path / 'answer.txt').write_bytes(b'fixture')
        self.assertEqual(runner.collect_submission(path.parent, 'answer.txt'), (path / 'answer.txt', None))

    def test_scrapy_entry_preserves_identity_and_passes_config_to_common_layer(self):
        output = self.root / 's24d002'
        config = scrapy024.execution_config(output)
        self.assertEqual(config.task_id, 'scrapy-task-024')
        self.assertEqual(config.experiment_id, 'scrapy024-s24r005-s24d002')
        self.assertEqual(config.generator_run_id, 's24r005')
        self.assertEqual(config.budget_scope, 'scrapy-task-024/s24r005/initial-calibration')
        self.assertEqual(list(config.conditions), scrapy024.ORDER)
        self.assertEqual(config.skill_conditions, ('CleanSkill',))
        with patch.object(runner, 'configure', return_value='fixture parsed') as common:
            self.assertEqual(scrapy024.configure(output, 'CleanSkill1', 'probe'), 'fixture parsed')
        self.assertEqual(common.call_args.args, (output, 'CleanSkill1', 'probe', config))

    def test_scrapy_paid_entry_keeps_approval_readiness_runtime_and_task_success_policy(self):
        import importlib.metadata
        import os
        output = self.root / 's24d002'
        with patch.dict(os.environ, {'SCRAPY024_ALLOW_PAID':'1', 'ZHIZENGZENG_API_KEY':'FIXTURE_ONLY'}), \
             patch.object(scrapy024, 'read', side_effect=[{'status':'PASS'}, dict.fromkeys(('harbor','litellm','openai','httpx'), 'fixture')]), \
             patch.object(scrapy024, 'verify_frozen') as frozen, \
             patch.object(importlib.metadata, 'version', return_value='fixture'), \
             patch.object(runner, 'execute_batch', return_value=0) as common:
            self.assertEqual(scrapy024.paid_batch(output), 0)
        frozen.assert_called_once_with(output)
        self.assertEqual(common.call_args.args, (scrapy024.LAB, output, scrapy024.execution_config(output)))
        hooks = common.call_args.kwargs
        self.assertIs(hooks['run_trial'], scrapy024.native_trial)
        self.assertIs(hooks['grade'], scrapy024.grade_export)
        self.assertIs(hooks['exposure'], scrapy024.body_exposure)
        self.assertTrue(hooks['task_success']({'task_result':{'tests':19, 'passed':19}}))
        self.assertFalse(hooks['task_success']({'task_result':{'tests':2, 'passed':2}}))


if __name__ == '__main__':
    unittest.main()
