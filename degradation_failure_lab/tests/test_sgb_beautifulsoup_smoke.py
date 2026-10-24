"""S0 contracts only: fixtures never import candidates, run a scorer, start a Trial or use a model."""
import base64
import builtins
import copy
import importlib
import contextlib
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tests import test_sgb_beautifulsoup037 as fixtures
from degradation_lab.io import read, sha256, write
from downstream_eval.integration.request_budget import Ledger
from downstream_eval.scoring.results import summarize, trial_record
from downstream_eval.sgb import beautifulsoup037 as bs
from downstream_eval.sgb import beautifulsoup_scoring as scorer
from downstream_eval.sgb import beautifulsoup_smoke as smoke
from downstream_eval.sgb import runner

LAB = fixtures.LAB


class BeautifulSoupSmoke(unittest.TestCase):
    setUp = fixtures.BeautifulSoup037.setUp
    prepare = fixtures.BeautifulSoup037.prepare
    evidence = fixtures.BeautifulSoup037.evidence

    def export(self, *, status='ok', candidate=True, receipt_status='exported'):
        artifacts = self.root / 'artifacts'
        artifacts.mkdir()
        path = artifacts / 'workspace/agent_output.py'
        if candidate:
            path.parent.mkdir()
            path.write_bytes(b'Fixture bytes only; never imported')
        write(artifacts / 'manifest.json', [
            {'source':scorer.SOURCE, 'destination':scorer.DESTINATION, 'type':'file',
             'status':status, 'service':None, 'exclude':[]}])
        from downstream_eval.sgb.beautifulsoup_exports import ExportController
        config = self.root / 'export-task.toml'
        config.write_text('artifacts = [{source = "/workspace/agent_output.py", destination = "workspace/agent_output.py"}]\n'
                          '[metadata]\ntask_id = "' + bs.TASK_ID + '"\n', encoding='utf-8')
        self.controller = ExportController(LAB, artifacts, task_config=config,
                                           trial_id='fixture-trial', fixture=True)
        self.trial_id = self.controller.trial_id
        observed = 'absent' if receipt_status == 'source_absent' else ('file' if candidate else 'unknown')
        receipt = self.controller.capture_fixture(manifest_entries=read(artifacts / 'manifest.json'),
                                                  source_observation=observed)
        return artifacts, path, receipt

    def collect(self, artifacts, *, receipt=None):
        return scorer.collect_export(artifacts, receipt=receipt,
                                     controller=self.controller, trial_id=self.trial_id)

    def inspect(self, plan, result):
        return scorer.inspect_result(plan, result, controller=self.controller)

    def score_request(self):
        artifacts, path, receipt = self.export()
        plan = bs.scoring_plan(LAB, path, self.root / 'score-workspace',
                               image=fixtures.VERIFIER_IMAGE, timeout_sec=20, export_receipt=receipt,
                               export_controller=self.controller, trial_id=self.trial_id)
        return artifacts, path, receipt, plan

    def score_receipt(self, plan):
        evidence = self.evidence()
        return self.controller.seal_result_fixture({'task_id':bs.TASK_ID, 'trial_id':plan['trial_id'],
                'request_sha256':plan['request_sha256'], 'export_receipt_id':plan['export_receipt_id'],
                'candidate_sha256':plan['candidate_sha256'],
                'input_sha256':dict(plan['input_sha256']), 'execution_status':'completed', 'returncode':0,
                'outputs':{'junit_xml':evidence['junit_xml'].encode(), 'reward':b'1\n',
                           'stdout':b'Fixture stdout\x00\xff', 'stderr':b'Fixture stderr\r\n'}})

    def test_probe_never_initializes_model_or_dispatches_paid_batch_or_budget(self):
        self.prepare()
        original = builtins.__import__
        def no_sdk(name, *args, **kwargs):
            if name.split('.')[0] in ('harbor', 'openai', 'anthropic', 'litellm'):
                raise AssertionError('No framework/model SDK import permitted')
            if 'terminus_compat' in name or 'beautifulsoup_agent' in name:
                raise AssertionError('No model agent import permitted')
            return original(name, *args, **kwargs)
        with patch('builtins.__import__', side_effect=no_sdk), \
             patch.object(runner, 'execute_batch', side_effect=AssertionError('No paid batch')) as paid, \
             patch.object(runner, 'configure', side_effect=AssertionError('No native Trial config')) as native, \
             patch.object(Ledger, 'create', side_effect=AssertionError('No ledger')) as ledger:
            importlib.reload(smoke)
            result = smoke.probe(LAB, self.output, self.root / 'engineering', task_id=bs.TASK_ID)
        paid.assert_not_called()
        native.assert_not_called()
        ledger.assert_not_called()
        self.assertEqual(result['run_kind'], 'runtime_smoke')
        self.assertEqual((result['model_calls'], result['actual_http_attempts']), (0, 0))
        self.assertFalse(result['real_agent_outcome'])
        self.assertIsNone(result['task_success'])
        self.assertEqual(result['execution_status'], 'NOT_RUN')
        self.assertFalse(result['generator_identity_verified'])
        self.assertEqual(result['environment_contract']['runtime_observation'], 'NOT_RUN')
        self.assertEqual(result['asset_identity']['task_key'], 't-7f902c444353')
        self.assertEqual(result['code_version']['files']['downstream_eval/sgb/runner.py'],
                         sha256(LAB / 'downstream_eval/sgb/runner.py'))
        self.assertEqual(result, read(self.root / 'engineering/smoke.json'))
        self.assertFalse((self.output / 'budget.sqlite3').exists())
        self.assertFalse((self.output / 'batch.started').exists())

    def test_runtime_actions_and_wrong_task_are_rejected_before_any_work(self):
        with patch.object(bs, 'validate_prepared', side_effect=AssertionError('Must reject before reading inputs')):
            with self.assertRaises(PermissionError):
                smoke.probe(LAB, self.output, self.root / 'engineering', task_id=bs.TASK_ID, runtime=True)
            with self.assertRaisesRegex(ValueError, 'task identity'):
                smoke.probe(LAB, self.output, self.root / 'engineering', task_id='scrapy-task-024')
        self.assertFalse((self.root / 'engineering').exists())

    def test_probe_rejects_mismatched_prepared_task_and_tampered_skill(self):
        self.prepare()
        profile = read(self.output / 'profile.json')
        profile['task_id'] = 'scrapy-task-024'
        write(self.output / 'profile.json', profile)
        with self.assertRaises(ValueError):
            smoke.probe(LAB, self.output, self.root / 'engineering', task_id=bs.TASK_ID)
        profile['task_id'] = bs.TASK_ID
        write(self.output / 'profile.json', profile)
        stage = self.output / 'staged/GeneratedSkill' / next(iter(self.packages)) / 'SKILL.md'
        stage.write_bytes(b'Tampered fixture')
        with self.assertRaisesRegex(ValueError, 'Skill files'):
            smoke.probe(LAB, self.output, self.root / 'engineering', task_id=bs.TASK_ID)
        self.assertFalse((self.root / 'engineering').exists())

    def test_engineering_records_refuse_project_history_overlap_and_overwrite(self):
        self.prepare()
        for output in (LAB / 'runs/eval/sgb/never-created', LAB / 'results/never-created',
                       self.output / 'engineering', self.root):
            with self.subTest(output=output), self.assertRaises((ValueError, FileExistsError)):
                smoke.probe(LAB, self.output, output, task_id=bs.TASK_ID)
        output = self.root / 'engineering'
        smoke.probe(LAB, self.output, output, task_id=bs.TASK_ID)
        digest = sha256(output / 'smoke.json')
        with self.assertRaises(FileExistsError):
            smoke.probe(LAB, self.output, output, task_id=bs.TASK_ID)
        self.assertEqual(sha256(output / 'smoke.json'), digest)

    def test_engineering_records_cannot_be_converted_or_summarized_as_agent_success(self):
        self.prepare()
        result = smoke.probe(LAB, self.output, self.root / 'engineering', task_id=bs.TASK_ID)
        for value in (result, result | {'task_success':True, 'infra_ok':True, 'outcome':'passed',
                                       'condition':'NoSkill', 'label':'fixture'}):
            with self.assertRaisesRegex(ValueError, 'Engineering'):
                trial_record(value, 'fixture', 'fixture')
            with self.assertRaisesRegex(ValueError, 'Engineering'):
                summarize([value])

    def test_exact_export_requires_manifest_and_independent_hash_receipt(self):
        artifacts, path, receipt = self.export()
        self.assertEqual(self.collect(artifacts, receipt=receipt), (path, None))
        _, error = self.collect(artifacts)
        self.assertEqual(error['failure_category'], 'submission_origin_unknown')
        (artifacts / 'manifest.json').unlink()
        _, error = self.collect(artifacts, receipt=receipt)
        self.assertEqual(error['failure_category'], 'submission_origin_unknown')

    def test_missing_submission_requires_trusted_absence_observation(self):
        artifacts, _, receipt = self.export(status='failed', candidate=False, receipt_status='source_absent')
        _, error = self.collect(artifacts, receipt=receipt)
        self.assertEqual(error['failure_category'], 'submission_missing')
        _, error = self.collect(artifacts)
        self.assertEqual(error['failure_category'], 'submission_download_failed')
        self.prepare()
        config = bs.execution_config(self.output / bs.TASK_ID, read(self.output / 'profile.json'))
        self.assertNotIn('submission_missing', config.unscorable_categories)
        self.assertIn(error['failure_category'], config.unscorable_categories)

    def test_download_failure_is_unscorable_even_if_partial_file_exists(self):
        artifacts, _, receipt = self.export(status='failed')
        _, error = self.collect(artifacts, receipt=receipt)
        self.assertEqual(error['failure_category'], 'submission_download_failed')
        row = {'label':'fixture', 'condition':'NoSkill', 'task_success':False, 'infra_ok':False,
               'failure_category':error['failure_category'], 'oracle':error}
        self.assertEqual(trial_record(row, 'fixture', 'fixture')['outcome'], 'unscorable')

    def test_duplicates_and_wrong_exact_path_are_rejected(self):
        artifacts, path, receipt = self.export()
        duplicate = artifacts / 'elsewhere/agent_output.py'
        duplicate.parent.mkdir()
        duplicate.write_bytes(path.read_bytes())
        _, error = self.collect(artifacts, receipt=receipt)
        self.assertEqual(error['failure_category'], 'submission_ambiguous')
        path.unlink()
        _, error = self.collect(artifacts, receipt=receipt)
        self.assertEqual(error['failure_category'], 'submission_origin_unknown')

    def test_manifest_wrong_source_service_status_and_duplicate_entry_are_rejected(self):
        artifacts, _, receipt = self.export()
        original = read(artifacts / 'manifest.json')
        for field, value in (('source', '/wrong/agent_output.py'), ('service', 'sidecar'),
                             ('destination', 'wrong/agent_output.py'), ('status', 'skipped'), ('type', 'directory')):
            entries = copy.deepcopy(original)
            entries[0][field] = value
            write(artifacts / 'manifest.json', entries)
            bound = receipt | {'artifact_manifest_sha256':sha256(artifacts / 'manifest.json')}
            with self.subTest(field=field):
                self.assertEqual(self.collect(artifacts, receipt=bound)[1]['failure_category'],
                                 'submission_origin_unknown')
        write(artifacts / 'manifest.json', original + original)
        self.assertEqual(self.collect(artifacts, receipt=receipt)[1]['failure_category'],
                         'submission_origin_unknown')

    def test_export_hash_and_manifest_hash_are_bound(self):
        artifacts, path, receipt = self.export()
        _, error = self.collect(artifacts, receipt=receipt | {'candidate_sha256':'0' * 64})
        self.assertEqual(error['failure_category'], 'submission_origin_unknown')
        _, error = self.collect(artifacts, receipt=receipt | {'artifact_manifest_sha256':'0' * 64})
        self.assertEqual(error['failure_category'], 'submission_origin_unknown')
        path.write_bytes(b'Changed export')
        self.assertEqual(self.collect(artifacts, receipt=receipt)[1]['failure_category'],
                         'submission_hash_mismatch')

    def test_scorer_plan_keeps_inputs_readonly_and_outputs_new_external_and_separate(self):
        _, path, _, plan = self.score_request()
        self.assertEqual(plan['candidate_sha256'], sha256(path))
        self.assertEqual(plan['input_sha256'][str(path)], sha256(path))
        self.assertEqual(plan['backend_status'], 'NOT_IMPLEMENTED')
        self.assertEqual(plan['preflight_status'], 'NOT_RUN')
        self.assertFalse(Path(plan['workspace']).exists())
        self.assertEqual(set(plan['required_outputs']), {'junit_xml', 'reward', 'stdout', 'stderr'})
        self.assertTrue(all(not m['writable'] for m in plan['mounts'][:-1]))
        for output in (path.parent, LAB / 'results/never-created', self.root / 'artifacts'):
            with self.subTest(output=output), self.assertRaises((ValueError, FileExistsError)):
                bs.scoring_plan(LAB, path, output, image=fixtures.VERIFIER_IMAGE, timeout_sec=20)

    def test_no_runtime_scorer_or_raw_callback_is_activated(self):
        artifacts, _, receipt, plan = self.score_request()
        trial = SimpleNamespace(paths=SimpleNamespace(artifacts_dir=artifacts),
                                config=SimpleNamespace(trial_name=self.trial_id))
        with self.assertRaisesRegex(RuntimeError, 'NOT_IMPLEMENTED'):
            scorer.execute_scoring(plan)
        callback = Mock(side_effect=AssertionError('No scorer process allowed'))
        with self.assertRaisesRegex(RuntimeError, 'callbacks disabled'):
            bs.grade_export(LAB, trial, self.root / 'score', image=fixtures.VERIFIER_IMAGE,
                            timeout_sec=20, execute=callback, export_receipt=receipt, export_controller=self.controller)
        callback.assert_not_called()
        score = bs.grade_export(LAB, trial, self.root / 'score', image=fixtures.VERIFIER_IMAGE,
                               timeout_sec=20, export_receipt=receipt, export_controller=self.controller)
        self.assertEqual(score['error_category'], 'scorer_backend_not_implemented')
        self.assertEqual(score['candidate_sha256'], plan['candidate_sha256'])
        self.assertFalse(bs.task_success(score))
        self.assertFalse((self.root / 'score').exists())

    def test_receipt_binds_candidate_oracle_tests_and_preserves_all_output_bytes(self):
        _, _, _, plan = self.score_request()
        receipt = self.score_receipt(plan)
        score = self.inspect(plan, receipt)
        self.assertEqual(score['failure_category'], 'none')
        self.assertEqual(score['candidate_sha256'], plan['candidate_sha256'])
        for name, data in receipt['outputs'].items():
            self.assertEqual(base64.b64decode(score['outputs'][name]['base64']), data)
        self.assertFalse(score['runtime_isolation_verified'])
        self.assertIsNone(score['task_success'])
        self.assertFalse(bs.task_success(score))
        with self.assertRaisesRegex(ValueError, 'Engineering'):
            trial_record(score, 'fixture', 'fixture')

    def test_wrong_answer_execution_error_and_timeout_receipts_are_distinct(self):
        _, _, _, plan = self.score_request()
        receipt = self.score_receipt(plan)
        wrong = self.evidence(failed='test_preserves_attributes_single')
        receipt['outputs'].update(junit_xml=wrong['junit_xml'].encode(), reward=b'0')
        receipt = self.controller.seal_result_fixture(receipt)
        score = self.inspect(plan, receipt)
        self.assertEqual(score['failure_category'], 'task_assertion_error')
        for state in ('timeout', 'error', 'not_run'):
            with self.subTest(state=state):
                score = self.inspect(plan, self.controller.seal_result_fixture(receipt | {'execution_status':state, 'returncode':None,
                                                               'error_type':'FixtureOnly'}))
                self.assertEqual(score['failure_category'], 'environment_error')
                self.assertEqual(score['error_category'], 'scorer_' + state)
                self.assertFalse(bs.task_success(score))

    def test_missing_junit_bad_exit_or_incomplete_outputs_never_pass(self):
        _, _, _, plan = self.score_request()
        receipt = self.score_receipt(plan)
        mutations = [receipt | {'returncode':1}, receipt | {'returncode':True},
                     receipt | {'outputs':{k:v for k, v in receipt['outputs'].items() if k != 'junit_xml'}},
                     receipt | {'outputs':receipt['outputs'] | {'junit_xml':b'<broken'}},
                     receipt | {'outputs':receipt['outputs'] | {'stderr':None}}]
        for value in mutations:
            with self.subTest(value=value):
                score = self.inspect(plan, value)
                self.assertEqual(score['failure_category'], 'environment_error')
                self.assertFalse(bs.task_success(score))

    def test_result_identity_or_changed_input_is_rejected(self):
        _, path, _, plan = self.score_request()
        receipt = self.score_receipt(plan)
        for mutation in ({'task_id':'scrapy-task-024'}, {'candidate_sha256':'0' * 64}, {'input_sha256':{}}):
            with self.subTest(mutation=mutation):
                score = self.inspect(plan, receipt | mutation)
                self.assertEqual(score['failure_category'], 'environment_error')
        path.write_bytes(b'Changed during grading fixture')
        score = self.inspect(plan, receipt)
        self.assertEqual(score['error_category'], 'scorer_input_changed')
        self.assertFalse(bs.task_success(score))

    def test_cli_is_static_only_and_has_no_runtime_option(self):
        self.prepare()
        args = ['--root', str(LAB), '--prepared', str(self.output),
                '--output', str(self.root / 'engineering'), '--task-id', bs.TASK_ID]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(smoke.main(args), 0)
        self.assertIn('"execution_status": "NOT_RUN"', output.getvalue())
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            smoke.main(args + ['--runtime'])
        self.assertEqual(error.exception.code, 2)

    def test_artifact_io_error_is_unscorable(self):
        artifacts, _, receipt = self.export()
        with patch.object(Path, 'rglob', side_effect=PermissionError('Fixture IO failure')):
            _, error = self.collect(artifacts, receipt=receipt)
        self.assertEqual(error['failure_category'], 'submission_origin_unknown')

    def test_candidate_link_is_rejected_without_reading_its_body(self):
        artifacts, path, receipt = self.export()
        original = Path.is_symlink
        def linked(value):
            return value == path or original(value)
        with patch.object(Path, 'is_symlink', linked):
            _, error = self.collect(artifacts, receipt=receipt)
        self.assertEqual(error['failure_category'], 'submission_origin_unknown')

    def test_agent_rejection_guard_stays_in_place(self):
        fixtures.BeautifulSoup037.test_offline_agent_gate_precedes_any_model_client_initialization(self)


if __name__ == '__main__':
    unittest.main()
