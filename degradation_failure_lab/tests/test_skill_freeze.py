"""Real frozen generator artifacts; network/model calls are forbidden."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import inventory, read, sha256
from downstream_eval.integration.skill_freeze import freeze_generation
RUN = LAB / 'runs/gen/sgb/case041_scrapy/clean/s41r003'


class SkillFreeze(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='freeze-test-', dir=LAB / 'results')
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / 'new'
        self.before = inventory(RUN)
        for name in ('socket.socket.connect', 'urllib.request.urlopen'):
            guard = patch(name, side_effect=AssertionError('Network/model forbidden'))
            guard.start()
            self.addCleanup(guard.stop)

    def tearDown(self):
        self.assertEqual(self.before, inventory(RUN))

    def test_live_version_and_cross_document_provenance_are_frozen(self):
        packages = freeze_generation(LAB, 's41r003', self.output, case_id='case041_scrapy')
        self.assertEqual(len(packages), 45)
        merged = packages['76394f52-1f81-5c91-8ae3-fd51b942c5e1']
        self.assertEqual(merged['version'], '0.1.1')
        self.assertEqual(len({e['doc_id'] for e in merged['evidence']}), 2)
        for sid, item in packages.items():
            self.assertEqual(sha256(self.output / 'skills' / sid / 'SKILL.md'), item['sha256'])
        frozen = read(self.output / 'skill_freeze.json')
        self.assertEqual(frozen['files'], inventory(self.output / 'skills'))
        self.assertEqual(frozen['manifest_sha256'], sha256(self.output / 'skills_manifest.json'))

    def test_existing_output_is_not_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / 'keep'
        sentinel.write_bytes(b'unchanged')
        with self.assertRaises(FileExistsError):
            freeze_generation(LAB, 's41r003', self.output)
        self.assertEqual(sentinel.read_bytes(), b'unchanged')

    def test_tampered_parent_is_rejected_before_output_creation(self):
        import downstream_eval.integration.skill_freeze as module
        actual = module.sha256
        with patch.object(module, 'sha256', side_effect=lambda p: '0' * 64 if Path(p) == RUN / 'config.json' else actual(p)):
            with self.assertRaisesRegex(ValueError, 'Generator history changed'):
                freeze_generation(LAB, 's41r003', self.output)
        self.assertFalse(self.output.exists())

    def test_fixture_invocation_is_not_a_real_clean_source(self):
        import downstream_eval.integration.skill_freeze as module
        actual = module.read
        def changed(path):
            data = actual(path)
            if Path(path) == RUN / 'invocation.json':
                data['execution_kind'] = 'fixture'
            return data
        with patch.object(module, 'read', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'Fixture generation'):
                freeze_generation(LAB, 's41r003', self.output)

    def test_wrong_task_case_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'matching generation'):
            freeze_generation(LAB, 's41r003', self.output, case_id='another_case')

    def test_empty_active_registry_is_not_replaced_with_a_fake_skill(self):
        import downstream_eval.integration.skill_freeze as module
        actual = module.read
        def inactive(path):
            value = actual(path)
            if Path(path).parent == RUN / 'SkillBank/.runtime/document_registry/skills':
                value['status'] = 'inactive'
            return value
        with patch.object(module, 'read', side_effect=inactive):
            with self.assertRaisesRegex(ValueError, 'Final live registry'):
                freeze_generation(LAB, 's41r003', self.output)
        self.assertFalse(self.output.exists())

    def test_failed_generation_is_not_a_normal_clean_package(self):
        import downstream_eval.integration.skill_freeze as module
        actual = module.load_run
        def failed(*args):
            identity, run, result, stages = actual(*args)
            result['status'] = 'failed'
            return identity, run, result, stages
        with patch.object(module, 'load_run', side_effect=failed):
            with self.assertRaisesRegex(ValueError, 'Completed matching generation'):
                freeze_generation(LAB, 's41r003', self.output)
        self.assertFalse(self.output.exists())

    def test_unsafe_package_is_still_rejected(self):
        path = next((RUN / 'SkillBank/Users').rglob('SKILL.md'))
        with patch.object(Path, 'is_symlink', lambda value: value == path):
            with self.assertRaisesRegex(ValueError, 'Unsupported package symlink'):
                freeze_generation(LAB, 's41r003', self.output)
        self.assertFalse((self.output / 'skill_freeze.json').exists())


if __name__ == '__main__':
    unittest.main()
