"""Task-037 offline contracts. Original Oracle, Agent, network and Docker never execute."""
import ast
import copy
import importlib
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch
from xml.etree import ElementTree

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import inventory, read, sha256, write
from downstream_eval.integration.request_budget import Ledger
from downstream_eval.scoring.results import trial_record
from downstream_eval.sgb import beautifulsoup037 as bs
from downstream_eval.sgb import runner

AGENT_IMAGE = 'fixture-agent-not-built@sha256:' + '1' * 64
VERIFIER_IMAGE = 'fixture-verifier-not-built@sha256:' + '2' * 64


class BeautifulSoup037(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='bs37-offline-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.output = self.root / 'prepared'
        for name in ('socket.socket.connect', 'socket.socket.connect_ex', 'socket.getaddrinfo', 'subprocess.Popen'):
            guard = patch(name, side_effect=AssertionError('No network, model, process or Docker'))
            guard.start()
            self.addCleanup(guard.stop)
        package = self.root / 'fixture-package'
        package.mkdir()
        (package / 'SKILL.md').write_bytes(
            b'---\r\nid: "00000000-0000-0000-0000-000000000037"\r\nname: fixture\r\ndescription: Offline fixture only\r\n---\r\nFixture body.\r\n')
        self.packages = {'00000000-0000-0000-0000-000000000037':
                         {'path':package / 'SKILL.md', 'files':inventory(package),
                          'metadata':{'name':'fixture', 'description':'Offline fixture only'}}}
        self.profile = {
            'task_id':bs.TASK_ID, 'experiment_id':'bs37-offline-fixture', 'generator_run_id':'bs37-fixture-gen',
            'budget_scope':bs.TASK_ID + '/bs37-fixture-gen/offline-fixture',
            'conditions':{'NoSkill1':'NoSkill', 'GeneratedSkill1':'GeneratedSkill'},
            'skill_conditions':['GeneratedSkill'], 'trial_order':['NoSkill1', 'GeneratedSkill1'],
            'arms':['NoSkill', 'GeneratedSkill'],
            'hard_http_budget':{'database':str(self.output / 'budget.sqlite3'), 'per_arm_limit':1,
                                'global_limit':2, 'order':['NoSkill1', 'GeneratedSkill1']},
            'model':{'name':'fixture-only', 'base_url':'https://fixture.invalid', 'api_format':'openai_chat_completions',
                     'temperature':0, 'reasoning_effort':'none', 'api_key_environment_variable':'BS37_FIXTURE_ONLY'},
            'budget':{'max_requests':1, 'agent_timeout_sec':30, 'setup_timeout_sec':10, 'request_timeout_sec':5,
                      'max_completion_tokens_per_request':20, 'max_input_tokens_per_request':1000,
                      'max_input_tokens_total':2000}}

    def prepare(self):
        return bs.prepare(LAB, self.output, profile=self.profile, packages=self.packages,
                          agent_image=AGENT_IMAGE, verifier_image=VERIFIER_IMAGE, verifier_timeout_sec=20)

    def evidence(self, *, failed=None, errors=False, reward=None):
        _, mapping = bs.verify_assets(LAB)
        suite = ElementTree.Element('testsuite')
        for name in mapping['oracle_tests']:
            case = ElementTree.SubElement(suite, 'testcase', name=name)
            if name == failed:
                ElementTree.SubElement(case, 'failure', message='Fixture assertion only')
            if errors and name == mapping['oracle_tests'][0]:
                ElementTree.SubElement(case, 'error', message='Fixture environment error')
        return {'returncode':0, 'junit_xml':ElementTree.tostring(suite, encoding='unicode'),
                'reward':reward if reward is not None else str(int(not failed and not errors))}

    def test_real_source_mapping_and_original_oracle_inventory(self):
        official, mapping = bs.verify_assets(LAB)
        self.assertEqual(mapping['task_key'], 't-7f902c444353')
        self.assertEqual(mapping['revision'], '5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d')
        self.assertEqual(len(mapping['source_ids']), 4)
        self.assertEqual(len(mapping['oracle_tests']), 15)
        self.assertEqual(sha256(official / 'tests/eval.py'),
                         'c7ee6d37d069c02aa9c6059ed6dcc28857ad44dcdd002d73642fa4838a4c7e6c')
        self.assertEqual(read(LAB / bs.TASK_PATH / 'adapter.json')['status'], 'METADATA_ONLY')

    def test_preparation_reuses_explicit_runner_config_without_claiming_execution(self):
        report = self.prepare()
        config = bs.execution_config(self.output / bs.TASK_ID, read(self.output / 'profile.json'))
        profile = runner.execution_profile(self.output, config)
        self.assertEqual(profile['experiment_id'], self.profile['experiment_id'])
        self.assertEqual(config.budget_scope, self.profile['budget_scope'])
        self.assertEqual(config.generator_run_id, 'bs37-fixture-gen')
        no_skill = runner.trial_config(self.output, 'NoSkill1', 'probe', config)
        skill = runner.trial_config(self.output, 'GeneratedSkill1', 'probe', config)
        self.assertEqual(no_skill['agent']['skills'], [])
        self.assertEqual(skill['agent']['skills'], [str(self.output / 'staged/GeneratedSkill')])
        self.assertEqual(skill['agent']['kwargs']['p1_mode'], 'probe')
        self.assertEqual(report['execution_status'], 'NOT_RUN')
        self.assertIsNone(report['task_success'])
        self.assertFalse(report['model_api_results'])
        self.assertFalse(report['generator_identity_verified'])
        self.assertEqual(report['status'], 'OFFLINE_PREPARED')
        self.assertFalse((self.output / 'budget.sqlite3').exists())
        self.assertFalse((self.output / 'batch.started').exists())
        self.assertFalse((self.output / 'readiness.json').exists())

    def test_derived_task_omits_clean_docs_tests_and_build_context(self):
        self.prepare()
        task = self.output / bs.TASK_ID
        self.assertEqual(set(inventory(task)), {'instruction.md', 'task.toml'})
        self.assertEqual(list((task / 'environment').iterdir()), [])
        official, _ = bs.verify_assets(LAB)
        self.assertEqual((task / 'instruction.md').read_bytes(), (official / 'instruction.md').read_bytes())
        self.assertFalse((task / 'context').exists())
        self.assertFalse((task / 'tests').exists())
        self.assertEqual(inventory(self.output / 'staged/NoSkill'), {})
        self.assertEqual(inventory(self.output / 'staged/GeneratedSkill' / next(iter(self.packages))),
                         next(iter(self.packages.values()))['files'])

    def test_full_pinned_taskconfig_accepts_conversion_and_rejects_original_schema(self):
        self.prepare()
        source = LAB / '.external/harbor-full/src'
        namespaces = {}
        # Load exact pinned schema modules, bypassing only absent installed-distribution metadata.
        # This is source-level schema validation, not a claim that Harbor/Terminus is installed.
        for name in ('harbor', 'harbor.models', 'harbor.models.task', 'harbor.utils'):
            module = ModuleType(name)
            module.__path__ = [str(source / Path(*name.split('.')))]
            namespaces[name] = module
        with patch.dict(sys.modules, namespaces):
            schema = importlib.import_module('harbor.models.task.config')
            parsed = schema.TaskConfig.model_validate_toml((self.output / bs.TASK_ID / 'task.toml').read_text(encoding='utf-8'))
            self.assertEqual(parsed.environment.workdir, '/workspace')
            self.assertEqual(parsed.environment.network_mode.value, 'no-network')
            self.assertEqual(parsed.verifier.environment_mode.value, 'separate')
            self.assertEqual(parsed.artifacts[0].source, '/workspace/agent_output.py')
            official, _ = bs.verify_assets(LAB)
            with self.assertRaises(ValueError):
                schema.TaskConfig.model_validate_toml((official / 'task.toml').read_text(encoding='utf-8'))

    def test_wrong_identity_budget_or_missing_skill_package_is_refused(self):
        for field, value in (('task_id', 'scrapy-task-024'), ('budget_scope', 'scrapy-task-024/s24r005/initial-calibration'),
                             ('generator_run_id', ''), ('experiment_id', '')):
            with self.subTest(field=field):
                profile = copy.deepcopy(self.profile)
                profile[field] = value
                with self.assertRaises((KeyError, ValueError)):
                    bs.execution_config(self.output / bs.TASK_ID, profile)
        with self.assertRaisesRegex(ValueError, 'Skill packages'):
            bs.prepare(LAB, self.output, profile=self.profile, packages={},
                       agent_image=AGENT_IMAGE, verifier_image=VERIFIER_IMAGE, verifier_timeout_sec=20)
        self.assertFalse(self.output.exists())

    def test_asset_missing_or_source_mapping_mismatch_is_refused_without_editing_assets(self):
        real_sha = bs.sha256
        def missing(path):
            if Path(path).name == 'eval.py':
                raise FileNotFoundError('Fixture simulation of missing Oracle')
            return real_sha(path)
        with patch.object(bs, 'sha256', side_effect=missing):
            with self.assertRaises(FileNotFoundError):
                self.prepare()
        real_read = bs.read
        def mismatch(path):
            data = real_read(path)
            if Path(path).name == 'offline_adapter.json':
                data['source_ids'] = []
            return data
        with patch.object(bs, 'read', side_effect=mismatch):
            with self.assertRaisesRegex(ValueError, 'identity mismatch'):
                self.prepare()
        self.assertFalse(self.output.exists())

    def test_changed_environment_skill_or_false_success_status_is_refused(self):
        self.prepare()
        task = self.output / bs.TASK_ID / 'task.toml'
        original = task.read_bytes()
        task.write_bytes(original.replace(b'workdir = "/workspace"', b'workdir = "/wrong"'))
        with self.assertRaisesRegex(ValueError, 'contract mismatch'):
            bs.validate_prepared(LAB, self.output)
        task.write_bytes(original)
        profile = read(self.output / 'profile.json')
        profile['model_api_results'] = True
        write(self.output / 'profile.json', profile)
        with self.assertRaisesRegex(ValueError, 'cannot authorize'):
            bs.validate_prepared(LAB, self.output)

    def test_preparation_cannot_overwrite_workspace_or_write_into_project_history(self):
        self.prepare()
        digest = sha256(self.output / 'profile.json')
        with self.assertRaises(FileExistsError):
            self.prepare()
        self.assertEqual(sha256(self.output / 'profile.json'), digest)
        with self.assertRaisesRegex(ValueError, 'outside the project'):
            bs.prepare(LAB, LAB / 'runs/eval/sgb/beautifulsoup4-task-037/never-created',
                       profile=self.profile, packages=self.packages,
                       agent_image=AGENT_IMAGE, verifier_image=VERIFIER_IMAGE, verifier_timeout_sec=20)

    def test_offline_agent_gate_precedes_any_model_client_initialization(self):
        path = LAB / 'downstream_eval/sgb/beautifulsoup_agent.py'
        tree = ast.parse(path.read_bytes())
        node = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        class ForbiddenBase:
            def __init__(self, *args, **kwargs):
                raise AssertionError('Base/model initialization forbidden')
        namespace = {'CompatibleTerminus2':ForbiddenBase}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
        with self.assertRaisesRegex(RuntimeError, 'OFFLINE_ONLY'):
            namespace['OfflineBeautifulSoupTerminus2']()

    def test_scorer_plan_uses_original_shell_isolated_paths_and_junit(self):
        submission = self.root / 'agent_output.py'
        submission.write_bytes(b'Fixture only, never imported')
        plan = bs.scoring_plan(LAB, submission, self.root / 'score', image=VERIFIER_IMAGE, timeout_sec=20)
        self.assertEqual(plan['command'], ['bash', '/workspace/tests/test.sh'])
        self.assertEqual(plan['workdir'], '/workspace')
        self.assertEqual(plan['network_mode'], 'no-network')
        self.assertEqual(len(plan['oracle_tests']), 15)
        self.assertTrue(all(not m['writable'] for m in plan['mounts'][:-1]))
        self.assertEqual(plan['mounts'][-1]['target'], '/logs/verifier')
        self.assertIn('--junitxml=', plan['env']['PYTEST_ADDOPTS'])
        self.assertFalse(plan['image_verified'])
        self.assertIn('UNVERIFIED', plan['candidate_isolation'])
        self.assertTrue(all('/context/docs/' not in m['source'] for m in plan['mounts']))
        with self.assertRaises(ValueError):
            bs.scoring_plan(LAB, submission, self.root / 'score', image='light', timeout_sec=20)

    def test_original_reward_zero_exit_and_ctrf_fallback_cannot_masquerade_as_success(self):
        _, mapping = bs.verify_assets(LAB)
        score = bs.normalize_score({'returncode':0, 'reward':'1', 'junit_xml':'<testsuite><testcase name="fallback"/></testsuite>'},
                                   mapping['oracle_tests'])
        self.assertEqual(score['failure_category'], 'environment_error')
        self.assertFalse(bs.task_success(score))
        failed = bs.normalize_score(self.evidence(failed='test_preserves_attributes_single'), mapping['oracle_tests'])
        self.assertEqual(failed['failure_category'], 'task_assertion_error')
        self.assertEqual(failed['task_result']['passed'], 14)
        error = bs.normalize_score(self.evidence(errors=True), mapping['oracle_tests'])
        self.assertEqual(error['failure_category'], 'environment_error')
        inconsistent = bs.normalize_score(self.evidence(reward='0'), mapping['oracle_tests'])
        self.assertEqual(inconsistent['failure_category'], 'environment_error')

    @staticmethod
    def completed_fixture(coroutine):
        # Fixtures do not suspend; no Windows event-loop socketpair or Harbor lifecycle is needed.
        try:
            coroutine.send(None)
        except StopIteration as done:
            return done.value
        finally:
            coroutine.close()
        raise AssertionError('Fixture unexpectedly suspended')

    def batch(self, *, failed=None, errors=False, execution_error=False, scorer_error=False):
        self.prepare()
        config = bs.execution_config(self.output / bs.TASK_ID, read(self.output / 'profile.json'))
        # A disposable test ledger validates the contract; no research budget is opened or modified.
        payload = self.root / 'fixture.bin'
        payload.write_bytes(b'Fixture evidence')
        frozen = {'fixture.bin':sha256(payload)}
        write(self.output / 'execution_manifest.json', frozen)
        Ledger.create(self.output / 'budget.sqlite3',
                      {'scope':config.budget_scope, 'order':list(config.conditions), 'budget':self.profile['budget'],
                       'global_limit':2, 'per_trial_limit':1,
                       'trials':{label:'bs37-' + label.lower() for label in config.conditions},
                       'files':{str(payload):sha256(payload)}})
        artifacts = self.root / 'artifacts'
        artifacts.mkdir()
        candidate = artifacts / 'workspace/agent_output.py'
        candidate.parent.mkdir()
        candidate.write_bytes(b'Fixture only; never imported')
        from downstream_eval.sgb.beautifulsoup_scoring import SOURCE, DESTINATION, collect_export
        write(artifacts / 'manifest.json', [
            {'source':SOURCE, 'destination':DESTINATION, 'type':'file', 'status':'ok'}])
        from downstream_eval.sgb.beautifulsoup_exports import ExportController
        controller = ExportController(LAB, artifacts, task_config=self.output / bs.TASK_ID / 'task.toml',
                                      trial_id='fixture-trial', fixture=True)
        receipt = controller.capture_fixture(manifest_entries=read(artifacts / 'manifest.json'),
                                             source_observation='file')
        trial = SimpleNamespace(paths=SimpleNamespace(artifacts_dir=artifacts, trial_dir=self.root / 'fake-trial'))
        async def run(config):
            if execution_error:
                raise RuntimeError('Fixture execution failure')
            return trial, {'exception_info':None}
        backend = Mock(side_effect=ValueError('Fixture grader failure')) if scorer_error else Mock(return_value=self.evidence(failed=failed, errors=errors))
        def grade(trial, output):
            # Common Runner simulation only; no runtime backend or isolation is asserted here.
            submission, failure = collect_export(trial.paths.artifacts_dir, receipt=receipt,
                                                  controller=controller, trial_id=controller.trial_id)
            if failure:
                return failure
            plan = bs.scoring_plan(LAB, submission, output, image=VERIFIER_IMAGE, timeout_sec=20,
                                   export_controller=controller, export_receipt=receipt, trial_id=controller.trial_id)
            score = bs.normalize_score(backend(plan), plan['oracle_tests'])
            score.update(oracle_original_sha256=plan['oracle_sha256'], candidate_sha256=plan['candidate_sha256'])
            return score
        def parsed(output, label, mode, config):
            raw = runner.trial_config(output, label, mode, config)
            return SimpleNamespace(trial_name=raw['trial_name'])
        run_mock = AsyncMock(side_effect=run)
        with patch.object(runner, 'configure', side_effect=parsed), patch.object(runner.asyncio, 'run', side_effect=self.completed_fixture):
            status = runner.execute_batch(self.root, self.output, config, run_trial=run_mock, grade=grade,
                exposure=lambda *args:{'model_body_exposed_ids':[]}, task_success=bs.task_success)
        return status, backend, run_mock

    def test_common_batch_accepts_beautifulsoup_normalized_fixture_results(self):
        status, backend, run = self.batch()
        self.assertEqual((status, run.await_count), (0, 2))
        rows = read(self.output / 'batch_results.json')['results']
        self.assertTrue(all(row['oracle']['task_result']['tests'] == 15 for row in rows))
        self.assertTrue(all(row['oracle']['oracle_original_sha256'] ==
                            'c7ee6d37d069c02aa9c6059ed6dcc28857ad44dcdd002d73642fa4838a4c7e6c' for row in rows))
        self.assertTrue(all(trial_record(row, bs.TASK_ID, 'OFFLINE_FIXTURE')['outcome'] == 'passed' for row in rows))
        # Core contract simulation must not promote the adapter's preparation/evidence status.
        self.assertEqual(read(self.output / 'offline_preparation.json')['execution_status'], 'NOT_RUN')

    def test_common_batch_records_wrong_answer_as_scorable(self):
        status, _, run = self.batch(failed='test_preserves_attributes_single')
        self.assertEqual((status, run.await_count), (0, 2))
        rows = read(self.output / 'batch_results.json')['results']
        self.assertTrue(all(trial_record(r, bs.TASK_ID, 'OFFLINE_FIXTURE')['outcome'] == 'failed' for r in rows))

    def test_common_batch_distinguishes_scorer_environment_failure(self):
        status, _, run = self.batch(errors=True)
        self.assertEqual((status, run.await_count), (2, 1))
        row = read(self.output / 'batch_results.json')['results'][0]
        self.assertEqual(row['failure_category'], 'environment_error')
        self.assertEqual(trial_record(row, bs.TASK_ID, 'OFFLINE_FIXTURE')['outcome'], 'unscorable')

    def test_common_batch_records_scorer_exception_at_oracle_stage(self):
        status, _, run = self.batch(scorer_error=True)
        self.assertEqual((status, run.await_count), (2, 1))
        self.assertEqual(read(self.output / 'batch_stop.json')['failed_stage'], 'independent_oracle')

    def test_common_batch_records_execution_failure_before_grading(self):
        status, backend, _ = self.batch(execution_error=True)
        self.assertEqual(status, 2)
        self.assertEqual(read(self.output / 'batch_stop.json')['failed_stage'], 'agent_setup_or_execution')
        backend.assert_not_called()


if __name__ == '__main__':
    unittest.main()
