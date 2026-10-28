"""Zero-model contracts for the five newly admitted task slots."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from degradation_lab.io import read,sha256
from degradation_lab.runner import ExperimentRunner
from downstream_eval.sgb.pilot import load_binding,adapter_for
from downstream_eval.sgb import downstream_authorization as authorization

ROOT=Path(__file__).resolve().parents[1]
TASKS=['pydantic-task-001','scrapy-task-050','pydantic-task-004',
       'reviews_csv_conformance_validator_007','referee_attempt_decision_router_009']


class CleanFive(unittest.TestCase):
    @unittest.skipIf(os.name=='nt','Isolated scorer imports Linux resource; verified in the control container')
    def test_all_bindings_keep_original_instructions_and_oracles(self):
        for tid in TASKS:
            with self.subTest(task=tid):
                task=load_binding(ROOT,tid);manifest=adapter_for(ROOT,task).verify_assets()
                original=ROOT/manifest['original_task'];local=ROOT/task['task_path']
                self.assertEqual(sha256(local/'instruction.md'),sha256(original/'instruction.md'))
                self.assertEqual(sha256(local/'oracle/eval.py'),sha256(original/'tests/eval.py'))
                for source in manifest['source_documents']:
                    self.assertEqual(sha256(ROOT/source['path']),source['sha256'])

    def test_new_generation_gates_block_before_any_credentials(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'gate.json').write_text(json.dumps({'status':'BLOCKED'}))
            runner=ExperimentRunner(root,cases=object())
            with patch.object(runner,'resolve',return_value=({'case':{'execution_gate':'gate.json'}},None,None,{})),patch.dict('os.environ',{},clear=True):
                with self.assertRaisesRegex(RuntimeError,'BLOCKED: execution gate'):
                    runner.run('fixture-case','clean','unapproved-test-run')

    def test_exact_grants_support_both_reviewed_adapters_and_reject_others(self):
        for tid in TASKS:
            task=load_binding(ROOT,tid)
            value=authorization.expected_authorization(task,'testgen','testpair')
            self.assertEqual(value['max_http_calls'],12)
            self.assertEqual(value['task_config_sha256'],hashlib.sha256(authorization.task_config_bytes(task)).hexdigest())
            task=dict(task,adapter='unreviewed:Adapter')
            with self.assertRaises(RuntimeError):authorization.expected_authorization(task,'testgen','testpair')

    def test_generation_never_receives_tests_fixtures_or_interface_addenda(self):
        from degradation_lab.catalog import CaseManager
        for tid in TASKS:
            task=load_binding(ROOT,tid);bundle=CaseManager(ROOT).load(task['case_id'])
            path=ROOT/next(x['input_manifest'] for x in bundle['conditions']['conditions'] if x['condition_id']=='clean')
            inputs=read(path)['inputs']
            self.assertTrue(inputs)
            for item in inputs:self.assertTrue(item['path'].startswith('data/raw_sources/sgb/'))
            self.assertNotIn('fixtures',json.dumps(inputs))

    def test_package_sources_are_absent_from_agent_image(self):
        for tid in TASKS:
            task=load_binding(ROOT,tid);lock=read(ROOT/task['runtime_lock'])
            self.assertEqual(lock['agent_image_id'],'sha256:c928e232c35008c42b22727ecd2fe39ed79fe9cb36ebddca669daef309d6b4e4')
        lock=read(ROOT/'downstream_eval/tasks/sgb/audited/scrapy-task-050/runtime.lock.json')
        self.assertEqual(lock['twisted'],'25.5.0')
        self.assertNotEqual(lock['agent_image_id'],lock['scorer_image_id'])

    def test_positive_negative_fixture_contracts_are_complete(self):
        for tid in TASKS:
            task=load_binding(ROOT,tid);fixtures=read(ROOT/task['fixtures'])
            self.assertEqual(fixtures['correct']['passed'],task['expected_oracle_tests'])
            self.assertLess(fixtures['rule_mutant']['passed'],task['expected_oracle_tests'])
            self.assertTrue(fixtures['rule_mutant']['failed'])


if __name__=='__main__':unittest.main()
