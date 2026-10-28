import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / 'src'))
from degradation_lab.io import write, sha256
from degradation_lab.runner import ExperimentRunner


class ExactResume(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.parent = self.root / 'parent'
        self.config = json.loads((LAB / 'configs/generation/deepseek_flash.json').read_text(encoding='utf-8'))
        self.case = {'case_id': 'fixture', 'generation_config': 'config.json', 'execution_gate': 'gate.json'}
        write(self.root / 'config.json', self.config)
        write(self.parent / 'config.json', self.config)
        write(self.parent / 'case.json', self.case)
        write(self.parent / 'artifact_manifest.json', {'fixture': 'hash'})
        self.request = {'authorization_status': 'AUTHORIZED', 'run_id': 'recovery',
            'case_id': 'fixture', 'condition_id': 'clean', 'configuration': 'config.json',
            'configuration_sha256': sha256(self.root / 'config.json'),
            'max_http_calls': 500, 'max_observed_total_tokens': 1500000,
            'resume_from': 'parent', 'parent_manifest_sha256': sha256(self.parent / 'artifact_manifest.json')}
        self.target = self.root / 'recovery'
        self.target.mkdir()
        (self.root / 'results').mkdir()
        self.runner = ExperimentRunner(self.root, cases=object())
        self.budget = {'max_http_calls': 500, 'max_observed_total_tokens': 1500000}
        for target in ('socket.socket.connect', 'urllib.request.urlopen'):
            p = patch(target, side_effect=AssertionError('No network in regression tests'))
            p.start(); self.addCleanup(p.stop)

    def run_resume(self, request=None, budget=None):
        write(self.root / 'gate.json', {'status': 'PASS', 'authorization_contract': 'exact-generation-v1',
                                      'requested_generation': request or self.request})
        with patch('degradation_lab.artifacts.resolve_run', return_value=({'case_id': 'fixture', 'condition_id': 'clean'}, self.parent)), \
             patch('degradation_lab.resume.prepare_resume', return_value=self.target) as prepare, \
             patch('degradation_lab.adapter.execute', return_value=0) as execute, \
             patch.dict(os.environ, {self.config['credential_env']: 'FIXTURE_ONLY'}):
            result = self.runner.run('fixture', 'clean', 'recovery', resume_from='parent',
                                     resume_budget=self.budget if budget is None else budget)
        prepare.assert_called_once_with(self.root, 'parent', 'recovery', budget_overrides=self.budget if budget is None else budget)
        execute.assert_called_once_with(self.target)
        return result

    def test_exact_parent_hash_and_increased_cumulative_limits_are_admitted(self):
        self.assertEqual(self.run_resume(), (self.target, 0))

    def test_fresh_grant_does_not_authorize_resume(self):
        request = dict(self.request)
        request.pop('resume_from'); request.pop('parent_manifest_sha256')
        with self.assertRaisesRegex(RuntimeError, 'not authorized'):
            self.run_resume(request)

    def test_other_parent_and_changed_manifest_are_blocked(self):
        for key in ('resume_from', 'parent_manifest_sha256'):
            request = dict(self.request); request[key] = 'wrong'
            with self.assertRaisesRegex(RuntimeError, 'not authorized'):
                self.run_resume(request)

    def test_unapproved_budget_or_decrease_is_blocked(self):
        with self.assertRaisesRegex(RuntimeError, 'not authorized'):
            self.run_resume(budget={**self.budget, 'max_http_calls': 501})
        with self.assertRaisesRegex(ValueError, 'nondecreasing'):
            self.run_resume(budget={'max_http_calls': 1})


if __name__ == '__main__':
    unittest.main(verbosity=2)
