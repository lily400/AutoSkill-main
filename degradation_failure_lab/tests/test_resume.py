"""Offline recovery tests; all network connections are forbidden."""
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB/'src'))
from degradation_lab.io import inventory, read, resolve_upstream, write
from degradation_lab.resume import prepare_resume, guard_request, checked_finder, window_key

PARENT = LAB/'runs/gen/sgb/case024_scrapy/clean/s24m005'
UPSTREAM = resolve_upstream(LAB)
sys.path.insert(0, str(UPSTREAM))


class Recovery(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rs-', dir=LAB.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.original = inventory(PARENT)
        for target in ('socket.socket.connect', 'urllib.request.urlopen', 'urllib.request.OpenerDirector.open'):
            p = patch(target, side_effect=AssertionError('Real model/network forbidden'))
            p.start()
            self.addCleanup(p.stop)

    def tearDown(self):
        self.assertEqual(self.original, inventory(PARENT), 'Historical run changed')

    def prepare(self, name='r1'):
        identity = read(PARENT/'invocation.json')
        with patch('degradation_lab.resume.resolve_run', return_value=(identity, PARENT)), \
             patch('degradation_lab.resume.resolve_upstream', return_value=UPSTREAM), \
             patch('degradation_lab.resume.check_windows_run_path'):
            return prepare_resume(self.root, 's24m005', name)

    def execute(self, run, extract):
        from degradation_lab.adapter import execute
        from AutoSkill4Doc.stages.compiler import SkillCompilationResult
        from AutoSkill4Doc.store.versioning import VersionRegistrationResult
        cfg = read(run/'config.json')
        pipeline = importlib.import_module('AutoSkill4Doc.pipeline')
        original_finder = pipeline.find_intermediate_run_by_resume_key
        with patch.dict(os.environ, {cfg['credential_env']:'FIXTURE_ONLY_NOT_A_REAL_KEY'}), \
             patch.object(pipeline, 'extract_skills', side_effect=extract), \
             patch.object(pipeline.DocumentBuildPipeline, 'ingest_document',
                          side_effect=AssertionError('Outline/ingest must be cached')), \
             patch.object(pipeline.DocumentBuildPipeline, '_resume_or_stream_compile', return_value=SkillCompilationResult()), \
             patch.object(pipeline.DocumentBuildPipeline, '_resume_or_stream_register', return_value=VersionRegistrationResult()):
            result = execute(run)
        self.assertIs(pipeline.find_intermediate_run_by_resume_key, original_finder)
        return result

    def test_real_checkpoint_skips_seven_windows_and_retains_seven_drafts(self):
        from AutoSkill4Doc.stages.extractor import SkillExtractionResult
        run = self.prepare()
        resume = read(run/'resume.json')
        self.assertEqual(len(resume['completed_window_ids']), 7)
        self.assertEqual(len(resume['pending_window_ids']), 14)
        self.assertEqual(resume['prior_http_attempts'], 16)
        self.assertEqual(resume['prior_usage_totals']['total_tokens'], 66540)
        seen = []
        def empty_fixture(**kwargs):
            seen.append(kwargs['windows'][0].window_id)
            return SkillExtractionResult()
        self.execute(run, empty_fixture)
        self.assertEqual(seen, resume['pending_window_ids'])
        result = read(run/'official_result.json')
        self.assertTrue(result['intermediate']['resumed'])
        self.assertEqual(result['total_skill_drafts'], 7)
        self.assertEqual(result['total_support_records'], 7)
        mid = Path(result['intermediate']['run_dir'])
        doc_id = read(mid/'ingest/result.json')['documents'][0]['doc_id']
        aggregate = read(mid/'extract/documents'/(doc_id+'.json'))
        self.assertTrue(aggregate['complete'])
        self.assertEqual(len(aggregate['skill_drafts']), 7)
        execution = read(run/'execution.json')
        self.assertEqual(execution['http_attempts'], 0)
        self.assertEqual(execution['cumulative_http_attempts'], 16)
        self.assertEqual(execution['cumulative_usage_totals']['total_tokens'], 66540)
        # Mocked later stages do not constitute real extraction/compilation success.

    def test_repeated_ssl_failure_keeps_a_resumable_checkpoint(self):
        import ssl
        import urllib.error
        from degradation_lab.adapter import execute
        from degradation_lab.provider_adapter import ConfiguredOpenAIChatLLM
        run = self.prepare()
        cfg = read(run/'config.json')
        sent = []
        def fail_transport(client, *, payload, stream):
            sent.append(payload)
            raise urllib.error.URLError(ssl.SSLEOFError('UNEXPECTED_EOF_WHILE_READING'))
        with patch.dict(os.environ, {cfg['credential_env']:'FIXTURE_ONLY'}), \
             patch.object(ConfiguredOpenAIChatLLM, '_post_json', new=fail_transport):
            self.assertEqual(execute(run), 2)
        self.assertEqual(sent, [read(PARENT/'http/016/request.json')])
        self.assertEqual(read(run/'execution.json')['http_attempts'], 1)  # Fake transport only.
        self.assertEqual(read(run/'execution.json')['cumulative_http_attempts'], 17)
        with patch('degradation_lab.resume.resolve_upstream', return_value=UPSTREAM), \
             patch('degradation_lab.resume.check_windows_run_path'):
            again = prepare_resume(self.root, 'r1', 'r2')
        self.assertEqual(read(again/'resume.json')['completed_window_ids'],
                         read(run/'resume.json')['completed_window_ids'])
        self.assertEqual(read(again/'resume.json')['prior_http_attempts'], 17)

    def test_recovery_does_not_reset_the_request_budget(self):
        from degradation_lab.adapter import execute
        from degradation_lab.provider_adapter import ConfiguredOpenAIChatLLM
        run = self.prepare()
        cfg = read(run/'config.json')
        cfg['max_http_calls'] = 16
        write(run/'config.json', cfg)
        with patch.dict(os.environ, {cfg['credential_env']:'FIXTURE_ONLY'}), \
             patch.object(ConfiguredOpenAIChatLLM, '_post_json',
                          side_effect=AssertionError('Budget must block dispatch')):
            self.assertEqual(execute(run), 2)
        self.assertEqual(read(run/'execution.json')['http_attempts'], 0)
        self.assertIn('budget exhausted', str(read(run/'official_result.json')['errors']))

    def test_mismatched_resume_key_stops_before_any_model_call(self):
        run = self.prepare()
        data = read(run/'resume.json'); data['resume_key'] = 'wrong-key'; write(run/'resume.json', data)
        self.assertEqual(self.execute(run, lambda **kw: self.fail('Extraction must not start')), 1)
        self.assertEqual(read(run/'execution.json')['http_attempts'], 0)
        self.assertIn('Checkpoint identity mismatch', read(run/'exception.json')['message'])

    def test_changed_copied_checkpoint_rejected(self):
        from degradation_lab.adapter import execute
        run = self.prepare()
        (run/'SkillBank/changed').write_text('FIXTURE', encoding='utf-8')
        cfg = read(run/'config.json')
        with patch.dict(os.environ, {cfg['credential_env']:'FIXTURE_ONLY'}):
            with self.assertRaisesRegex(RuntimeError, 'Copied checkpoint changed'):
                execute(run)

    def test_completed_request_and_outline_blocked_pending_allowed(self):
        resume = {'completed_window_keys':[]}
        request = read(PARENT/'http/003/request.json')
        user = json.loads(request['messages'][1]['content'])
        resume['completed_window_keys'] = [window_key(user)]
        with self.assertRaisesRegex(RuntimeError, 'completed window'):
            guard_request(resume, request, [{'function':'_plan_unit_skills'}])
        with self.assertRaisesRegex(RuntimeError, 'Outline'):
            guard_request(resume, request, [{'function':'_outline_matches_from_llm'}])
        guard_request(resume, read(PARENT/'http/016/request.json'), [{'function':'_plan_unit_skills'}])

    def test_successful_uncheckpointed_plan_is_not_resent(self):
        import degradation_lab.resume as module
        original_read = module.read
        def changed(path):
            data = original_read(path)
            if Path(path) == PARENT/'model_calls.json':
                data[-1]['success'] = True
            return data
        with patch.object(module, 'read', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'uncheckpointed calls'):
                self.prepare()
        self.assertFalse((self.root/'runs').exists())

    def test_existing_id_is_never_overwritten(self):
        run = self.prepare()
        before = inventory(run)
        with self.assertRaises(FileExistsError):
            self.prepare()
        self.assertEqual(before, inventory(run))

    def test_cli_resume_routes_to_the_existing_runner(self):
        from degradation_lab.cli import main
        from degradation_lab.runner import ExperimentRunner
        with patch.object(sys, 'argv', ['lab.py','--root',str(LAB),'resume','--run','s24m005','--run-id','s24r005']), \
             patch.object(ExperimentRunner, 'run', return_value=(self.root, 0)) as run:
            self.assertEqual(main(), 0)
        run.assert_called_once_with('case024_scrapy','clean','s24r005',resume_from='s24m005')

    def test_fresh_execution_still_rejects_a_nonempty_store(self):
        from degradation_lab.adapter import execute
        run = self.prepare()
        (run/'resume.json').unlink()
        cfg = read(run/'config.json')
        with patch.dict(os.environ, {cfg['credential_env']:'FIXTURE_ONLY'}):
            with self.assertRaisesRegex(RuntimeError, 'SkillBank must be empty'):
                execute(run)

    def test_finder_requires_the_exact_frozen_checkpoint(self):
        resume = {'resume_key':'key', 'checkpoint_id':'checkpoint'}
        for found in (None, {'run_id':'other'}):
            with self.assertRaisesRegex(RuntimeError, 'Checkpoint identity mismatch'):
                checked_finder(lambda **kw: found, resume)(base_store_root='fixture', resume_key='key')


if __name__ == '__main__':
    unittest.main()
