"""Pydantic demo contracts; no real process, model or network calls."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

LAB=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(LAB),str(LAB/'src')]
from degradation_lab.io import read
from degradation_lab.catalog import CaseManager
from degradation_lab.runner import ExperimentRunner
from downstream_eval.sgb.pydantic001 import CASE_ID,TASK_PATH,demonstrate,verify_assets


class PydanticDemo(unittest.TestCase):
    def setUp(self):
        self.net=patch('socket.socket.connect',side_effect=AssertionError('No network/model calls'))
        self.proc=patch('subprocess.run',side_effect=AssertionError('No real processes in unit tests'))
        self.net.start();self.proc.start();self.addCleanup(self.net.stop);self.addCleanup(self.proc.stop)

    def test_only_registered_source_is_generation_input(self):
        task,row=verify_assets(LAB)
        bundle=CaseManager(LAB).load(CASE_ID)
        _,manifest=CaseManager(LAB).condition(bundle,'clean')
        self.assertEqual(task,LAB/TASK_PATH)
        self.assertEqual(len(manifest['inputs']),1)
        self.assertEqual(manifest['inputs'][0]['path'],row['sources'][0]['path'])
        self.assertIn('/data/raw_sources/',('/'+manifest['inputs'][0]['path']))
        self.assertTrue(all('scorer' not in x['path'] and 'fixtures' not in x['path'] for x in manifest['inputs']))

    def test_rules_remain_analyst_annotations_and_paid_generation_is_blocked(self):
        bundle=CaseManager(LAB).load(CASE_ID)
        self.assertEqual(bundle['rules']['rules'][0]['annotation_status'],'analyst_checklist')
        with self.assertRaisesRegex(RuntimeError,'execution gate'):
            ExperimentRunner(LAB).run(CASE_ID,'clean','p001never')

    def test_demo_refuses_invalid_or_existing_evidence_location(self):
        with self.assertRaises(ValueError):demonstrate(LAB,'../escape')
        with self.assertRaises(FileExistsError):demonstrate(LAB,'migration-20261023-001')

    def test_positive_and_negative_fixtures_differ_only_in_validator_order(self):
        base=LAB/'tests/fixtures/sgb/pydantic-task-001'
        good=(base/'correct/agent_output.py').read_text(encoding='utf-8')
        bad=(base/'swapped_order/agent_output.py').read_text(encoding='utf-8')
        self.assertEqual(good.replace('BeforeValidator(before),WrapValidator(wrap)',
                                      'WrapValidator(wrap),BeforeValidator(before)'),bad)


if __name__=='__main__':unittest.main()
