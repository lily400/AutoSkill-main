import os
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
sys.path.insert(0, str(LAB / 'src'))

from degradation_lab.io import read
from downstream_eval.checks import materialize_task, oracle_probes
from downstream_eval.integration.harbor_adapter import official_probe_class, official_resolve_skills, verify_sources, validate_task_network_modes
from downstream_eval.integration.skill_install import canonical_packages, copy_packages
from downstream_eval.tasks.git_restore_explicit_source_both_v1.fixture import TARGET, build, git
from downstream_eval.tasks.git_restore_explicit_source_both_v1.oracle import evaluate, index_entries, trusted_state


class DownstreamTests(unittest.TestCase):
    def test_windows_generation_run_path_is_portable_in_linux(self):
        from degradation_lab.artifacts import load_run, resolve_run
        identity, run = resolve_run(LAB, 'r18307cee4f4c')
        with patch('degradation_lab.artifacts.resolve_run', return_value=(identity, run)), \
             patch('degradation_lab.artifacts.Path', PurePosixPath):
            stages = load_run(LAB, 'r18307cee4f4c')[3]
        self.assertEqual(len(stages['register']['upserted_store_skills']), 14)

    def test_fixed_dependency_git_blob_identity(self):
        _, lock = verify_sources(LAB)
        self.assertEqual(lock['harbor_commit'], '2de4605b9404eada7d341388291e6e469c90330b')
        self.assertFalse(lock['allow_model_execution'])

    def test_official_parser_lf_crlf_crcrlf_and_chinese_extra_fields(self):
        original = official_probe_class(LAB, patched=False)
        patched = official_probe_class(LAB)
        text = '---\nname: 中文技能\ndescription: 中文描述\nextra: 保留\n---\n正文\n'
        for newline in ('\n', '\r\n', '\r\r\n'):
            content = text.replace('\n', newline)
            self.assertEqual(patched._parse_skill_frontmatter(content), {'name': '中文技能', 'description': '中文描述'})
            self.assertEqual(original._parse_skill_frontmatter(content) is not None, newline == '\n')
        for invalid in ('body only', '---\nname: missing-description\n---', '---\n[]\n---'):
            self.assertIsNone(patched._parse_skill_frontmatter(invalid))

    def test_all_real_canonical_ids_and_frozen_bytes(self):
        config = read(LAB / 'downstream_eval/configs/git_restore_pilot.json')
        packages = canonical_packages(LAB, config)
        self.assertEqual(len(packages), 14)
        for sid, package in packages.items():
            self.assertIn(sid, package['path'].read_bytes().decode('utf-8'))

    def test_lossless_resources_and_collision_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            (source / 'SKILL.md').write_bytes(b'---\r\nname: x\r\ndescription: y\r\n---\r\n')
            (source / 'assets').mkdir()
            (source / 'assets/run.sh').write_bytes(b'#!/bin/sh\r\necho x\r\n')
            from degradation_lab.io import inventory
            packages = {'id-1': {'path': source / 'SKILL.md', 'files': inventory(source)}}
            copy_packages(packages, root / 'installed')
            self.assertEqual(inventory(source), inventory(root / 'installed/id-1'))
            with self.assertRaises(FileExistsError):
                copy_packages(packages, root / 'installed')

    def test_official_resolver_last_wins_is_neutralized_by_id_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for parent in ('a', 'b'):
                p = root / parent / 'same-name'
                p.mkdir(parents=True)
                (p / 'SKILL.md').write_text('skill')
            resolved = official_resolve_skills(LAB, [root / 'a/same-name', root / 'b/same-name'])
            self.assertEqual(len(resolved), 1)
            self.assertEqual(resolved[0].source, (root / 'b/same-name').resolve())
            with self.assertRaises(ValueError):
                official_resolve_skills(LAB, [root])

    def test_fixture_reproducible_and_independent_oracle_matrix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = oracle_probes(root)
            self.assertEqual(report['status'], 'PASS', [(r['case'], r['assertion_results']) for r in report['records'] if r['test_status'] != 'PASS'])
            self.assertEqual(len(report['records']), 36)
            self.assertTrue(all(r['repeatable'] for r in report['records']))
            fixtures = [r['fixture'] for r in report['records']]
            self.assertTrue(all(f == fixtures[0] for f in fixtures))

    def test_poisoned_host_git_environment_does_not_reach_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = os.environ.get('GIT_DIR')
            os.environ['GIT_DIR'] = str(root / 'must-not-be-used')
            try:
                fixture = build(root / 'repo')
            finally:
                if old is None:
                    os.environ.pop('GIT_DIR', None)
                else:
                    os.environ['GIT_DIR'] = old
            self.assertEqual(len(set(fixture['versions_sha256'])), 4)
            self.assertFalse((root / 'must-not-be-used').exists())

    def test_oracle_rejects_symlinks_without_following_them(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = build(root / 'repo')
            expected = trusted_state(root / 'repo', fixture)
            try:
                (root / 'repo/escape').symlink_to(root / 'private')
            except OSError as error:
                self.skipTest('BLOCKED: Windows symlink privilege unavailable: ' + str(error))
            self.assertFalse(evaluate(root / 'repo', expected)['success'])

    def test_artifact_roundtrip_preserves_hidden_git_index_and_refs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = build(root / 'agent')
            trusted = trusted_state(root / 'agent', fixture)
            git(root / 'agent', 'restore', '--source=' + fixture['commit_a'], '--staged', '--worktree', '--', TARGET)
            archive = root / 'artifact.tar'
            with tarfile.open(archive, 'w') as stream:
                stream.add(root / 'agent', arcname='repo')
            with tarfile.open(archive) as stream:
                stream.extractall(root / 'verifier', filter='data')
            self.assertTrue(evaluate(root / 'verifier/repo', trusted)['success'])
            self.assertEqual(index_entries(root / 'verifier/repo/.git/index')[TARGET]['blob'], fixture['target_blob'])

    def test_oracle_never_executes_agent_owned_git_or_scripts(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / 'repo'
            fixture = build(repo)
            trusted = trusted_state(repo, fixture)
            git(repo, 'restore', '--source=' + fixture['commit_a'], '--staged', '--worktree', '--', TARGET)
            with patch('subprocess.run', side_effect=AssertionError('Oracle must only read bytes')):
                self.assertTrue(evaluate(repo, trusted)['success'])

    def test_verifier_uses_trusted_code_and_instruction_has_no_answer(self):
        with tempfile.TemporaryDirectory() as directory:
            config = read(LAB / 'downstream_eval/configs/git_restore_pilot.json')
            task, fixture = materialize_task(LAB, config, Path(directory))
            instruction = (task / 'instruction.md').read_text(encoding='utf-8')
            self.assertIn(fixture['commit_a'], instruction)
            self.assertNotIn('--source', instruction)
            self.assertNotIn('git restore', instruction)
            dockerfile = (task / 'environment/Dockerfile').read_text()
            self.assertNotIn('oracle.py', dockerfile)
            self.assertNotIn('COPY .', dockerfile)
            self.assertIn('environment_mode = "separate"', (task / 'task.toml').read_text())
            self.assertEqual(validate_task_network_modes(LAB, task)['status'], 'PASS')
            invalid = (task / 'task.toml').read_text().replace('no-network', 'none')
            (task / 'task.toml').write_text(invalid)
            with self.assertRaises(ValueError):
                validate_task_network_modes(LAB, task)
            self.assertEqual((task / 'tests/oracle.py').read_bytes(), (LAB / config['task_template'] / 'oracle.py').read_bytes())


if __name__ == '__main__':
    unittest.main()
