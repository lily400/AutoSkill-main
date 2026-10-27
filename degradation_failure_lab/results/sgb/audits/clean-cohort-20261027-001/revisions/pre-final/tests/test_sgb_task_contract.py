"""Invented standard task only: no task adapter, SDK, network, Agent, Docker or Oracle."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

sys.dont_write_bytecode = True
LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src'), str(LAB / 'tests')]
import test_sgb as registry_fixtures
from degradation_lab.io import inventory, read, sha256, write
from degradation_lab.sgb import CONFIG, REGISTRY, REVISION
from downstream_eval.integration.request_budget import Ledger
from downstream_eval.integration.skill_install import copy_packages
from downstream_eval.scoring.results import summarize, trial_record
from downstream_eval.sgb import runner, task_contract


class StandardTaskContract(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='sgb-contract-')
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        for name in ('socket.socket.connect', 'socket.socket.connect_ex',
                     'socket.getaddrinfo', 'subprocess.Popen'):
            guard = patch(name, side_effect=AssertionError('Offline contract fixture only'))
            guard.start()
            self.addCleanup(guard.stop)
        self.prepare_fixture('standard')

    def register(self):
        write(self.description, self.data)
        self.rows[0]['execution_contract'] = {
            'path':self.description.relative_to(self.root).as_posix(), 'sha256':sha256(self.description)}
        registry = self.root / REGISTRY
        registry.write_text(''.join(json.dumps(r) + '\n' for r in self.rows), encoding='utf-8')
        catalog = read(self.root / CONFIG)
        catalog['registry_sha256'] = sha256(registry)
        write(self.root / CONFIG, catalog)

    def prepare_fixture(self, name):
        self.root = self.base / name
        self.rows = registry_fixtures.registry_fixture(self.root)
        self.task_id = 'fixture-task-902'
        self.experiment = 'fixture-experiment-902'
        task = self.root / 'tasks' / self.task_id
        task.mkdir(parents=True)
        (task / 'instruction.md').write_bytes(b'Invented fixture: write an answer JSON; no real task.')
        (task / 'task.toml').write_text('schema_version = "1.4"\nartifacts = [{source = "/work/answer.json", destination = "workspace/answer.json"}]\n[metadata]\ntask_id = "' +
                                       self.task_id + '"\n[environment]\nworkdir = "/work"\n', encoding='utf-8')
        self.rows[0].update(original_task_id=self.task_id, source_type='code_doc')
        self.description = self.root / 'configs/tasks/fixture-902.json'
        self.data = {
            'schema_version':1, 'task_id':self.task_id, 'source_type':'code_doc',
            'source':{'task_key':'fixture-0', 'revision':REVISION},
            'task':{'path':task.relative_to(self.root).as_posix(), 'files':inventory(task),
                    'instruction':'instruction.md', 'config':'task.toml'},
            'agent_protocol':'p1_compatible_v1',
            'environment':{'type':'docker', 'delete':False,
                           'kwargs':{'enable_environment_dir_upload':False}},
            'execution':{'experiment_id':self.experiment, 'generator_run_id':'fixture-gen-902',
                'budget_scope':self.task_id + '/fixture-gen-902/' + self.experiment,
                'agent_import_path':'fixture_framework:NeverInstantiate', 'trial_prefix':'fixture902-',
                'conditions':{'base1':'NoSkill', 'docs1':'Skill'}, 'skill_conditions':['Skill'],
                'unscorable_categories':['environment_error', 'submission_ambiguous', 'submission_origin_unknown']},
            'submission':{'protocol':'single_file_v1', 'filename':'answer.json', 'source_path':'/work/answer.json',
                          'artifact_path':'workspace/answer.json'},
            'grading':{'protocol':'submission_callback_v1', 'entrypoint':'fixture-json-checker', 'timeout_sec':5}}
        self.register()
        self.task = task_contract.load_task(self.root, self.task_id)
        self.output = runner.experiment_output(self.root, self.task_id, self.experiment)
        self.profile = {
            'run_kind':'offline_fixture', 'task_id':self.task_id, 'experiment_id':self.experiment,
            'generator_run_id':'fixture-gen-902', 'budget_scope':self.data['execution']['budget_scope'],
            'trial_order':['base1', 'docs1'], 'arms':['NoSkill', 'Skill'],
            'hard_http_budget':{'database':str(self.output / 'budget.sqlite3'), 'order':['base1', 'docs1'],
                                'global_limit':0, 'per_arm_limit':0},
            'model':{'name':'fixture-only', 'base_url':'https://fixture.invalid', 'api_format':'openai_chat_completions',
                     'temperature':0, 'reasoning_effort':'none', 'api_key_environment_variable':'FIXTURE_ONLY'},
            'budget':{'max_requests':1, 'agent_timeout_sec':30, 'setup_timeout_sec':10, 'request_timeout_sec':5,
                      'max_completion_tokens_per_request':20, 'max_input_tokens_per_request':100,
                      'max_input_tokens_total':200}}
        write(self.output / 'profile.json', self.profile)
        package = self.root / 'fixture-package'
        package.mkdir()
        (package / 'SKILL.md').write_bytes(b'---\nname: fixture\ndescription: invented\n---\nFixture only.\n')
        for label, condition in self.data['execution']['conditions'].items():
            stage = self.output / 'staged' / condition
            if condition == 'Skill':
                copy_packages({'fixture-skill':{'path':package / 'SKILL.md', 'files':inventory(package)}}, stage)
            else:
                stage.mkdir(parents=True)
            write(self.output / 'manifests' / (label + '.json'), {
                'arm':label, 'generator_run_id':'fixture-gen-902', 'staged_root':str(stage), 'files':inventory(stage),
                'metadata':{'fixture-skill':{'name':'fixture', 'description':'invented'}} if condition == 'Skill' else {}})
        frozen = inventory(self.root)
        write(self.output / 'execution_manifest.json', frozen)
        config = self.task.execution
        Ledger.create(self.output / 'budget.sqlite3', {
            'scope':config.budget_scope, 'order':list(config.conditions), 'budget':self.profile['budget'],
            'global_limit':0, 'per_trial_limit':0,
            'trials':{label:config.trial_prefix + label.lower() for label in config.conditions},
            'files':{str(self.root / name):digest for name,digest in frozen.items()}})

    @staticmethod
    def completed(coroutine):
        try:
            coroutine.send(None)
        except StopIteration as done:
            return done.value
        finally:
            coroutine.close()
        raise AssertionError('Fixture coroutine unexpectedly suspended')

    def run_fixture(self, *, submission='valid', execution_error=False, grading_error=False, native_error=False):
        async def run(config):
            if execution_error:
                raise RuntimeError('Fixture execution error')
            trial_dir = self.output / 'fake-framework' / config.trial_name
            artifacts = trial_dir / 'artifacts'
            artifacts.mkdir(parents=True)
            if submission != 'missing':
                path = artifacts / ('other/answer.json' if submission == 'wrong_path' else 'workspace/answer.json')
                write(path, {'answer':42 if config.raw['agent']['skills'] else 0})
                if submission == 'duplicate':
                    write(artifacts / 'duplicate/answer.json', {'answer':42})
            return SimpleNamespace(paths=SimpleNamespace(trial_dir=trial_dir, artifacts_dir=artifacts)), {
                'exception_info':{'type':'FixtureNativeError'} if native_error else None}
        def grade(path, destination, options):
            if grading_error:
                raise TimeoutError('Fixture grader timeout')
            self.assertEqual(options, self.data['grading'])
            success = read(path)['answer'] == 42
            return {'task_success':success, 'failure_category':'none' if success else 'task_assertion_error',
                    'task_result':{'tests':1, 'passed':int(success)}, 'rule_result':{'passed':success}}
        execute = AsyncMock(side_effect=run)
        grader = Mock(side_effect=grade)
        parsed = Mock(side_effect=lambda raw:SimpleNamespace(trial_name=raw['trial_name'], raw=raw))
        with patch.object(runner.asyncio, 'run', side_effect=self.completed):
            status = task_contract.run_fixture(self.task, self.output, configure_trial=parsed,
                run_trial=execute, grader_id='fixture-json-checker', grade_submission=grader)
        return status, execute, grader, parsed

    def test_load_all_source_types_and_native_configuration_without_adapter_module(self):
        for kind in ('code_repo', 'code_doc', 'domain_knowledge_doc'):
            with self.subTest(kind=kind):
                self.rows[0]['source_type'] = self.data['source_type'] = kind
                self.register()
                task = task_contract.load_task(self.root, self.task_id)
                self.assertEqual(task.data['source_type'], kind)
                self.assertTrue(task.original_assets)
                no_skill = task.trial_config(self.output, 'base1', 'probe')
                skill = task.trial_config(self.output, 'docs1', 'probe')
                self.assertEqual(no_skill['agent']['skills'], [])
                self.assertEqual(skill['agent']['skills'], [str(self.output / 'staged/Skill')])
                self.assertEqual(no_skill['environment'], self.data['environment'])
                self.assertEqual(no_skill['agent']['import_path'], 'fixture_framework:NeverInstantiate')
                self.assertEqual(no_skill['agent']['override_timeout_sec'], 30)
                self.assertNotIn('model_api_key_name', no_skill['agent'])
                self.assertFalse(list(self.root.rglob('*.py')))

    def test_standard_lifecycle_collects_and_normalizes_without_claiming_real_success(self):
        status, execute, grade, parsed = self.run_fixture()
        self.assertEqual((status, execute.await_count, grade.call_count, parsed.call_count), (0, 2, 2, 2))
        rows = read(self.output / 'batch_results.json')['results']
        self.assertEqual([r['fixture_outcome'] for r in rows], ['failed', 'passed'])
        self.assertEqual([r['fixture_task_success'] for r in rows], [False, True])
        for row in rows:
            self.assertEqual(row['run_kind'], 'offline_fixture')
            self.assertFalse(row['real_agent_outcome'])
            self.assertFalse(row['model_api_results'])
            self.assertIsNone(row['task_success'])
            self.assertEqual((row['model_calls'], row['actual_http_attempts']), (0, 0))
            self.assertEqual(row['oracle']['task_contract_sha256'], self.task.descriptor_sha256)
            self.assertFalse(row['oracle']['runtime_isolation_verified'])
            self.assertFalse(row['oracle']['grader_timeout_enforced'])
            with self.assertRaisesRegex(ValueError, 'Engineering'):
                trial_record(row, self.task_id, 'fixture')
            with self.assertRaisesRegex(ValueError, 'Engineering'):
                summarize([row])
        self.assertEqual(read(self.output / 'batch_results.json')['ledger']['attempts'], [])

    def test_missing_or_forged_registration_and_task_identity_are_refused(self):
        original = copy.deepcopy(self.data)
        for field, value in (('task_id', 'foreign-task'), ('source_type', 'unknown'),
                             ('source', {'task_key':'foreign', 'revision':REVISION})):
            with self.subTest(field=field):
                self.data = copy.deepcopy(original)
                self.data[field] = value
                self.register()
                with self.assertRaisesRegex(ValueError, 'identity'):
                    task_contract.load_task(self.root, self.task_id)
        self.data = original
        self.register()
        write(self.description, self.data | {'task_id':'unregistered-change'})
        with self.assertRaisesRegex(ValueError, 'identity changed'):
            task_contract.load_task(self.root, self.task_id)
        with self.assertRaisesRegex(ValueError, 'Unknown SGB task'):
            task_contract.load_task(self.root, 'not-registered')

    def test_foreign_budget_scope_and_unsupported_protocols_are_refused(self):
        original = copy.deepcopy(self.data)
        mutations = [('scope', lambda d:d['execution'].update(budget_scope='scrapy-task-024/s24r005/initial-calibration')),
                     ('agent', lambda d:d.update(agent_protocol='unimplemented-agent')),
                     ('submission', lambda d:d['submission'].update(artifact_path='../answer.json'))]
        for name, mutate in mutations:
            with self.subTest(name=name):
                self.data = copy.deepcopy(original)
                mutate(self.data)
                self.register()
                with self.assertRaises(ValueError):
                    task_contract.load_task(self.root, self.task_id)
        self.assertFalse((self.output / 'batch.started').exists())

    def test_task_assets_and_skill_bytes_remain_frozen_before_admission(self):
        instruction = self.task.execution.task_path / 'instruction.md'
        before = instruction.read_bytes()
        instruction.write_bytes(b'changed fixture')
        with self.assertRaisesRegex(ValueError, 'asset identity'):
            task_contract.load_task(self.root, self.task_id)
        instruction.write_bytes(before)
        (self.output / 'staged/Skill/fixture-skill/SKILL.md').write_bytes(b'changed fixture')
        with self.assertRaises(ValueError):
            self.run_fixture()
        self.assertFalse((self.output / 'batch.started').exists())

    def test_fixture_profile_and_frozen_contract_cannot_bypass_existing_budget_checks(self):
        path = self.output / 'profile.json'
        original = path.read_bytes()
        self.profile['hard_http_budget']['global_limit'] = 1
        write(path, self.profile)
        with self.assertRaisesRegex(ValueError, 'zero-HTTP'):
            self.run_fixture()
        path.write_bytes(original)
        frozen = read(self.output / 'execution_manifest.json')
        del frozen[self.description.relative_to(self.root).as_posix()]
        write(self.output / 'execution_manifest.json', frozen)
        with self.assertRaisesRegex(ValueError, 'missing from frozen'):
            self.run_fixture()
        self.assertFalse((self.output / 'batch.started').exists())

    def test_historical_run_is_not_repeated_or_overwritten(self):
        self.assertEqual(self.run_fixture()[0], 0)
        before = inventory(self.output)
        with self.assertRaisesRegex(RuntimeError, 'Historical experiment'):
            self.run_fixture()
        self.assertEqual(inventory(self.output), before)

    def test_missing_duplicate_and_wrong_path_submissions_use_distinct_categories(self):
        for submission, category, outcome in (
                ('missing', 'submission_missing', 'failed'),
                ('duplicate', 'submission_ambiguous', 'unscorable'),
                ('wrong_path', 'submission_origin_unknown', 'unscorable')):
            with self.subTest(submission=submission):
                self.prepare_fixture(submission)
                _, _, grade, _ = self.run_fixture(submission=submission)
                rows = read(self.output / 'batch_results.json')['results']
                self.assertEqual(rows[0]['failure_category'], category)
                self.assertEqual(rows[0]['fixture_outcome'], outcome)
                grade.assert_not_called()

    def test_execution_and_grading_errors_keep_their_lifecycle_stages(self):
        for name, options, stage in (
                ('execution', {'execution_error':True}, 'agent_setup_or_execution'),
                ('grading', {'grading_error':True}, 'independent_oracle')):
            with self.subTest(name=name):
                self.prepare_fixture(name)
                status, _, grade, _ = self.run_fixture(**options)
                self.assertEqual(status, 2)
                self.assertEqual(read(self.output / 'batch_stop.json')['failed_stage'], stage)
                row = read(self.output / 'batch_results.json')['results'][0]
                self.assertEqual(row['failure_kind'], 'infrastructure_failure')
                self.assertIs(row['real_agent_outcome'], False)
                if name == 'execution':
                    grade.assert_not_called()

    def test_native_failure_is_unscorable_and_does_not_claim_real_execution(self):
        status, execute, _, _ = self.run_fixture(native_error=True)
        self.assertEqual((status, execute.await_count), (2, 1))
        row = read(self.output / 'batch_results.json')['results'][0]
        self.assertEqual(row['failure_category'], 'agent_environment_or_execution')
        self.assertEqual(row['fixture_outcome'], 'unscorable')
        self.assertIsNone(row['task_success'])


    def test_foreign_output_grader_and_research_root_are_refused_before_callbacks(self):
        from dataclasses import replace
        hooks = dict(configure_trial=Mock(), run_trial=Mock(), grade_submission=Mock())
        for task, output, grader_id in (
                (self.task, self.root / 'foreign-output', 'fixture-json-checker'),
                (self.task, self.output, 'foreign-grader'),
                (replace(self.task, root=LAB), self.output, 'fixture-json-checker')):
            with self.subTest(output=output, grader=grader_id), self.assertRaises(ValueError):
                task_contract.run_fixture(task, output, grader_id=grader_id, **hooks)
        for hook in hooks.values():
            hook.assert_not_called()

    def test_unknown_evidence_kind_and_fixture_without_simulated_config_are_rejected(self):
        callbacks = dict(run_trial=Mock(), grade=Mock(), exposure=Mock(), task_success=Mock())
        for options in ({'run_kind':'unknown'}, {'run_kind':'offline_fixture'}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                runner.execute_batch(self.root, self.output, self.task.execution, **callbacks, **options)
        self.assertFalse((self.output / 'batch.started').exists())


if __name__ == '__main__':
    unittest.main()
