"""Skill evidence must distinguish file access, model context, probes and unknown use."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import inventory, write
from downstream_eval.integration.skill_usage import audit_skill_usage


class SkillUsage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.stage = self.output / 'staged/CleanSkill'
        self.skill = self.stage / 'one/SKILL.md'
        self.skill.parent.mkdir(parents=True)
        self.body = '---\nname: One\ndescription: A reusable skill\n---\n# Procedure\nCheck the input, then produce the expected output.\n'
        self.skill.write_text(self.body, encoding='utf-8')
        self.manifest = {'arm': 'C', 'generator_run_id': 'g1', 'staged_root': str(self.stage),
                         'files': inventory(self.stage),
                         'metadata': {'one': {'name': 'One', 'description': 'A reusable skill'}}}
        write(self.output / 'manifests/C.json', self.manifest)
        self.trial = self.output / 'trials/c'
        self.observer = self.trial / 'p1-observer'
        self.observer.mkdir(parents=True)
        self.index = ('<available_skills><skill><name>One</name><description>A reusable skill</description>'
                      '<location>/harbor/skills/one/SKILL.md</location></skill></available_skills>')
        self.event('installation', {'status': 'PASS', 'installed_ids': ['one'], 'discovered_ids': ['one'],
                                    'file_hashes': self.manifest['files']})

    def event(self, name, value):
        (self.observer / ('p1-' + name + '.jsonl')).write_text(json.dumps(value) + '\n', encoding='utf-8')

    def observed(self, body='', reads=(), mode='paid', status=200):
        self.event('model-requests', {'messages': [{'role': 'user', 'content': self.index + body}]})
        if status is not None:
            self.event('model-http', {'logical_request_number': 1, 'http_status': status})
        write(self.observer / 'p1-summary.json',
              {'mode': mode, 'model_read_ids': list(reads) if mode == 'paid' else [],
               'controlled_probe_read_ids': list(reads) if mode == 'probe' else []})
        return audit_skill_usage(self.output, 'C', self.trial)

    def test_index_only_is_not_body_loading_or_behavioral_use(self):
        report = self.observed()
        self.assertEqual(report['status'], 'INDEX_ONLY_OBSERVED')
        self.assertTrue(report['per_skill'][0]['index_in_successful_model_request'])
        self.assertFalse(report['per_skill'][0]['model_file_access_observed'])
        self.assertFalse(report['per_skill'][0]['full_body_in_successful_model_request'])
        self.assertEqual(report['behavioral_use']['status'], 'UNKNOWN')

    def test_full_body_in_successful_request_is_confirmed_but_use_is_unknown(self):
        report = self.observed(self.body, ['one'])
        self.assertEqual(report['status'], 'BODY_CONTEXT_CONFIRMED')
        self.assertTrue(report['per_skill'][0]['full_body_in_successful_model_request'])
        self.assertEqual(report['per_skill'][0]['behavioral_use'], 'UNKNOWN')

    def test_partial_or_truncated_body_does_not_pass_full_delivery(self):
        report = self.observed(self.body[:40], ['one'])
        self.assertEqual(report['status'], 'FILE_ACCESSED_BODY_CONTEXT_NOT_FULLY_CONFIRMED')
        self.assertFalse(report['per_skill'][0]['full_body_in_successful_model_request'])

    def test_failed_http_does_not_count_as_model_delivery(self):
        report = self.observed(self.body, ['one'], status=500)
        self.assertEqual(report['status'], 'INCOMPLETE_EVIDENCE')
        self.assertIsNone(report['per_skill'][0]['full_body_in_successful_model_request'])

    def test_controlled_probe_is_never_model_directed_reading(self):
        report = self.observed(self.body, ['one'], mode='probe', status=None)
        self.assertFalse(report['per_skill'][0]['model_file_access_observed'])
        self.assertTrue(report['per_skill'][0]['controlled_probe_file_access_observed'])
        self.assertIsNone(report['per_skill'][0]['full_body_in_successful_model_request'])

    def test_missing_logs_mean_unknown_not_false(self):
        report = audit_skill_usage(self.output, 'C', self.trial)
        self.assertEqual(report['status'], 'INCOMPLETE_EVIDENCE')
        self.assertIsNone(report['per_skill'][0]['model_file_access_observed'])
        self.assertIsNone(report['per_skill'][0]['index_in_successful_model_request'])

    def test_changed_skill_bytes_are_rejected(self):
        self.skill.write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'unchanged staged files'):
            self.observed()

    def test_changed_delivered_index_is_rejected(self):
        self.index = self.index.replace('A reusable skill', 'Different information')
        with self.assertRaisesRegex(ValueError, 'index metadata'):
            self.observed()

    def test_no_skill_condition_is_explicit(self):
        stage = self.output / 'staged/NoSkill'
        stage.mkdir()
        write(self.output / 'manifests/N.json', {'generator_run_id': 'g1', 'staged_root': str(stage),
                                                'metadata': {}, 'files': {}})
        self.event('installation', {'status': 'PASS', 'installed_ids': [], 'discovered_ids': [], 'file_hashes': {}})
        report = audit_skill_usage(self.output, 'N', self.trial)
        self.assertEqual(report['status'], 'NO_SKILL_CONDITION')
        self.assertEqual(report['expected_skill_count'], 0)


if __name__ == '__main__':
    unittest.main()
