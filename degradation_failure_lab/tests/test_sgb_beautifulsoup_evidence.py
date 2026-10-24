"""S0.2: synthetic controller evidence only. No candidate, Oracle or grader is ever executed."""
import ast
import copy
from pathlib import Path
import re
import unittest

from tests import test_sgb_beautifulsoup_smoke as smoke_fixtures
from degradation_lab.io import read, sha256
from downstream_eval.scoring.results import summarize, trial_record
from downstream_eval.sgb import beautifulsoup037 as bs
from downstream_eval.sgb import beautifulsoup_scoring as scorer
from downstream_eval.sgb.beautifulsoup_exports import ExportController, digest

LAB = smoke_fixtures.LAB


class BeautifulSoupEvidence(unittest.TestCase):
    setUp = smoke_fixtures.BeautifulSoupSmoke.setUp
    prepare = smoke_fixtures.BeautifulSoupSmoke.prepare
    evidence = smoke_fixtures.BeautifulSoupSmoke.evidence
    export = smoke_fixtures.BeautifulSoupSmoke.export
    collect = smoke_fixtures.BeautifulSoupSmoke.collect
    inspect = smoke_fixtures.BeautifulSoupSmoke.inspect
    score_request = smoke_fixtures.BeautifulSoupSmoke.score_request
    score_receipt = smoke_fixtures.BeautifulSoupSmoke.score_receipt

    def authenticated_malformed_fixture(self, result):
        # Trusted fixture producer may itself be buggy: authentication must not bypass validation.
        body = {k:v for k, v in result.items() if k not in ('outputs', 'authentication')}
        result['authentication'] = self.controller._mac('scorer-fixture', body)
        return result

    def test_receipt_binds_task_trial_entry_size_config_code_and_source(self):
        artifacts, path, receipt = self.export()
        self.assertEqual(receipt['evidence_kind'], 'offline_fixture')
        self.assertEqual(receipt['trial_id'], self.trial_id)
        self.assertEqual(receipt['task_id'], bs.TASK_ID)
        self.assertEqual(receipt['manifest_entry'], read(artifacts / 'manifest.json')[0])
        self.assertEqual(receipt['candidate_size'], path.stat().st_size)
        self.assertEqual(receipt['candidate_sha256'], sha256(path))
        self.assertEqual(receipt['task_config_sha256'], sha256(self.controller.task_config))
        self.assertEqual(receipt['export_source']['observation'], 'synthetic_fixture')
        self.assertTrue(all(sha256(Path(p)) == h for p, h in receipt['code_version'].items()))
        self.assertEqual(self.collect(artifacts, receipt=receipt), (path, None))

    def test_self_declared_or_rehashed_forgery_and_missing_receipt_are_rejected(self):
        artifacts, _, receipt = self.export()
        forged = copy.deepcopy(receipt)
        forged['candidate_sha256'] = '0' * 64
        body = {k:v for k, v in forged.items() if k not in ('receipt_id', 'authentication')}
        forged['receipt_id'] = digest(body)  # Candidate can recompute hashes but lacks controller key.
        unsigned = {k:v for k, v in receipt.items() if k != 'authentication'}
        for value in (None, {}, unsigned, forged):
            with self.subTest(value=value):
                self.assertEqual(self.collect(artifacts, receipt=value)[1]['failure_category'],
                                 'submission_origin_unknown')

    def test_trial_authority_task_config_and_artifact_root_reuse_are_refused(self):
        artifacts, _, receipt = self.export()
        other = ExportController(LAB, artifacts, task_config=self.controller.task_config,
                                 trial_id=self.trial_id, fixture=True)
        self.assertFalse(other.verify(receipt, artifacts=artifacts, trial_id=self.trial_id))
        self.assertFalse(self.controller.verify(receipt, artifacts=artifacts, trial_id='different-trial'))
        self.assertFalse(self.controller.verify(receipt, artifacts=self.root / 'other', trial_id=self.trial_id))
        self.controller.task_config.write_bytes(b'Changed fixture config')
        self.assertFalse(self.controller.verify(receipt, artifacts=artifacts, trial_id=self.trial_id))

    def test_real_receipt_mode_stops_before_reading_any_export(self):
        with self.assertRaisesRegex(RuntimeError, 'NOT_IMPLEMENTED'):
            ExportController(LAB, self.root / 'never-exported', task_config=self.root / 'absent',
                             trial_id='not-a-real-run', fixture=False)

    def test_controller_rejects_metadata_not_observed_in_manifest(self):
        artifacts, _, _ = self.export()
        metadata = read(artifacts / 'manifest.json')
        metadata[0]['status'] = 'failed'
        with self.assertRaisesRegex(ValueError, 'metadata differs'):
            self.controller.capture_fixture(manifest_entries=metadata, source_observation='file')

    def test_failed_download_is_not_proof_of_remote_absence(self):
        artifacts, _, receipt = self.export(status='failed', candidate=False)
        self.assertEqual(receipt['status'], 'download_failed')
        self.assertEqual(self.collect(artifacts, receipt=receipt)[1]['failure_category'], 'submission_download_failed')
        observed = self.controller.capture_fixture(manifest_entries=read(artifacts / 'manifest.json'),
                                                    source_observation='absent')
        self.assertEqual(self.collect(artifacts, receipt=observed)[1]['failure_category'], 'submission_missing')
        self.assertEqual(observed['evidence_kind'], 'offline_fixture')

    def test_duplicate_export_is_refused_by_both_controller_and_collector(self):
        artifacts, _, receipt = self.export()
        duplicate = artifacts / 'agent_output.py'
        duplicate.write_bytes(b'Second fixture')
        with self.assertRaisesRegex(ValueError, 'Duplicate submission'):
            self.controller.capture_fixture(manifest_entries=read(artifacts / 'manifest.json'),
                                              source_observation='file')
        self.assertEqual(self.collect(artifacts, receipt=receipt)[1]['failure_category'], 'submission_ambiguous')

    def test_request_and_result_have_unbroken_receipt_and_candidate_identity(self):
        _, path, receipt, plan = self.score_request()
        result = self.score_receipt(plan)
        reviewed = self.inspect(plan, result)
        self.assertEqual(reviewed['failure_category'], 'none')
        self.assertEqual(reviewed['export_receipt_id'], receipt['receipt_id'])
        self.assertEqual(reviewed['request_sha256'], plan['request_sha256'])
        self.assertEqual(reviewed['candidate_sha256'], sha256(path))
        self.assertEqual(reviewed['trial_id'], self.trial_id)
        self.assertFalse(reviewed['trusted_score'])
        self.assertIsNone(reviewed['task_success'])

    def test_unsigned_and_wrong_request_results_have_no_trusted_score(self):
        _, _, _, plan = self.score_request()
        result = self.score_receipt(plan)
        cases = [dict(result, authentication='forged'), dict(result, producer='candidate'),
                 self.controller.seal_result_fixture(result | {'request_sha256':'0' * 64}),
                 self.controller.seal_result_fixture(result | {'trial_id':'other-trial'}),
                 self.controller.seal_result_fixture(result | {'export_receipt_id':'0' * 64})]
        for value in cases:
            with self.subTest(value=value):
                score = self.inspect(plan, value)
                self.assertEqual(score['failure_category'], 'environment_error')
                self.assertFalse(score['trusted_score'])
                self.assertIsNone(score['task_success'])

    def test_truncated_stdout_and_duplicate_output_entries_are_rejected(self):
        _, _, _, plan = self.score_request()
        result = self.score_receipt(plan)
        truncated = copy.deepcopy(result)
        truncated['outputs']['stdout'] = truncated['outputs']['stdout'][:-1]
        self.assertEqual(self.inspect(plan, truncated)['error_category'], 'scorer_output_hash_mismatch')
        duplicate = copy.deepcopy(result)
        duplicate['output_manifest'][-1] = duplicate['output_manifest'][0]
        duplicate = self.authenticated_malformed_fixture(duplicate)
        self.assertEqual(self.inspect(plan, duplicate)['failure_category'], 'environment_error')
        missing = copy.deepcopy(result)
        del missing['outputs']['junit_xml']
        self.assertEqual(self.inspect(plan, missing)['failure_category'], 'environment_error')

    def test_junit_duplicate_case_and_reward_disagreement_are_refused(self):
        _, _, _, plan = self.score_request()
        result = self.score_receipt(plan)
        cases = [result | {'outputs':result['outputs'] | {'reward':b'0'}},
                 result | {'outputs':result['outputs'] | {
                     'junit_xml':b'<testsuite>' + b'<testcase name="fallback"/>' * 15 + b'</testsuite>'}},
                 result | {'outputs':result['outputs'] | {'junit_xml':b'<truncated'}}]
        for value in cases:
            with self.subTest(value=value):
                score = self.inspect(plan, self.controller.seal_result_fixture(value))
                self.assertEqual(score['failure_category'], 'environment_error')
                self.assertFalse(bs.task_success(score))

    def test_timeout_and_infrastructure_receipts_do_not_become_answers(self):
        _, _, _, plan = self.score_request()
        result = self.score_receipt(plan)
        for status in ('timeout', 'error', 'not_run'):
            value = self.controller.seal_result_fixture(result | {
                'execution_status':status, 'returncode':None, 'error_type':'FixtureInfrastructureError'})
            score = self.inspect(plan, value)
            self.assertEqual(score['failure_category'], 'environment_error')
            self.assertEqual(score['error_category'], 'scorer_' + status)
            self.assertIsNone(score['score_channels']['original_benchmark']['trusted_score'])
            self.assertIsNone(score['score_channels']['behavior']['trusted_score'])

    def test_unbound_plan_and_mutated_manifest_are_not_scoring_evidence(self):
        artifacts, path, _, plan = self.score_request()
        result = self.score_receipt(plan)
        unbound = bs.scoring_plan(LAB, path, self.root / 'unbound', image=smoke_fixtures.fixtures.VERIFIER_IMAGE,
                                 timeout_sec=20)
        self.assertEqual(self.inspect(unbound, result)['failure_category'], 'environment_error')
        (artifacts / 'manifest.json').write_bytes(b'[]')
        self.assertEqual(self.inspect(plan, result)['error_category'], 'scorer_origin_unknown')

    def test_original_and_behavior_scores_are_separate_and_not_real_agent_outcomes(self):
        _, _, _, plan = self.score_request()
        result = self.score_receipt(plan)
        wrong = self.evidence(failed='test_uses_tag_name_assignment')
        result['outputs'].update(junit_xml=wrong['junit_xml'].encode(), reward=b'0')
        score = self.inspect(plan, self.controller.seal_result_fixture(result))
        channels = score['score_channels']
        self.assertEqual(channels['original_benchmark']['observed']['task_result']['passed'], 14)
        self.assertEqual(channels['behavior']['status'], 'NOT_IMPLEMENTED')
        self.assertIsNone(channels['behavior']['trusted_score'])
        self.assertFalse(score['trusted_score'])
        with self.assertRaises(ValueError):
            trial_record(score, 'fixture', 'fixture')
        with self.assertRaises(ValueError):
            summarize([score])

    def test_behavior_design_preserves_original_hash_and_only_excludes_source_syntax_check(self):
        official, mapping = bs.verify_assets(LAB)
        before = sha256(official / 'tests/eval.py')
        design = scorer.behavior_plan(LAB)
        self.assertEqual(before, 'c7ee6d37d069c02aa9c6059ed6dcc28857ad44dcdd002d73642fa4838a4c7e6c')
        self.assertEqual(design['original_oracle_sha256'], before)
        self.assertEqual(set(design['retained_behavior_checks']),
                         set(mapping['oracle_tests']) - {'test_uses_tag_name_assignment'})
        for name in ('test_object_identity_preserved', 'test_maintains_tree_position',
                     'test_preserves_attributes_multiple', 'test_preserves_tag_contents_nested_tags'):
            self.assertIn(name, design['retained_behavior_checks'])
        self.assertEqual(design['execution_status'], 'NOT_RUN')
        self.assertEqual(sha256(official / 'tests/eval.py'), before)

    def test_controlled_candidate_sources_are_design_fixtures_never_executed(self):
        prefix = 'def rename_tag_preserving_contents(tag, new_name):\n    '
        cases = {
            'direct_assignment':(prefix + 'tag.name = new_name\n    return tag\n', True, True),
            'equivalent_setattr':(prefix + "setattr(tag, 'name', new_name)\n    return tag\n", False, True),
            'wrong_name':(prefix + 'return tag\n', False, False),
            'drops_attributes':(prefix + 'tag.attrs.clear()\n    tag.name = new_name\n    return tag\n', True, False),
            'wrong_identity':(prefix + 'return type(tag)(name=new_name)\n', False, False),
        }
        for name, (source, syntax_expected, behavior_expected) in cases.items():
            with self.subTest(name=name):
                ast.parse(source)  # No exec, import, function call or Oracle execution.
                self.assertEqual(bool(re.search(r'\.name\s*=', source)), syntax_expected)
                self.assertIs(type(behavior_expected), bool)
        self.assertTrue(cases['equivalent_setattr'][2])  # Design expectation, not measured correctness.


if __name__ == '__main__':
    unittest.main()
