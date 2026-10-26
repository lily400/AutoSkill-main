"""Zero-model regression checks against the frozen Scrapy041 checkpoint."""
import importlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB/'src'))
from degradation_lab.io import inventory, read, resolve_upstream
from degradation_lab.resume import prepare_resume, guard_request

PARENT = LAB/'runs/gen/sgb/case041_scrapy/clean/r13fe557951'
UPSTREAM = resolve_upstream(LAB)
sys.path.insert(0, str(UPSTREAM))


class MultiDocumentRecovery(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='rm-', dir=LAB.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before = inventory(PARENT)
        for target in ('socket.socket.connect','urllib.request.urlopen','urllib.request.OpenerDirector.open'):
            p = patch(target, side_effect=AssertionError('Real network/model forbidden'))
            p.start()
            self.addCleanup(p.stop)

    def tearDown(self):
        self.assertEqual(self.before, inventory(PARENT), 'Historical run changed')

    def prepare(self, budget=True):
        identity = read(PARENT/'invocation.json')
        with patch('degradation_lab.resume.resolve_run', return_value=(identity,PARENT)), \
             patch('degradation_lab.resume.resolve_upstream', return_value=UPSTREAM), \
             patch('degradation_lab.resume.check_windows_run_path'):
            return prepare_resume(self.root, PARENT.name, 'r1',
                                  {'max_observed_total_tokens':900000} if budget else None)

    def test_real_checkpoint_reuses_34_windows_and_retries_only_failed_window(self):
        from degradation_lab.adapter import execute
        from AutoSkill4Doc.stages.extractor import SkillExtractionResult
        from AutoSkill4Doc.stages.compiler import SkillCompilationResult
        from AutoSkill4Doc.store.versioning import VersionRegistrationResult
        pipeline = importlib.import_module('AutoSkill4Doc.pipeline')
        run = self.prepare()
        resume = read(run/'resume.json')
        self.assertEqual(len(resume['completed_window_ids']), 34)
        self.assertEqual(resume['pending_window_ids'], ['a665c1c0-1e9d-51cc-b809-f6ee35b87f8c'])
        self.assertEqual(resume['prior_http_attempts'], 88)
        self.assertEqual(resume['prior_usage_totals']['total_tokens'], 453608)
        self.assertEqual(read(run/'config.json')['max_http_calls'], 150)
        self.assertEqual(read(run/'config.json')['max_observed_total_tokens'], 900000)
        for relative in resume['excluded_checkpoint_artifacts']:
            self.assertFalse((run/'SkillBank'/relative).exists())
            self.assertTrue((PARENT/'SkillBank'/relative).exists())
        # Every retained checkpoint byte is copied unchanged.
        self.assertTrue(resume['excluded_checkpoint_artifacts'])
        for relative,value in resume['seed_skillbank'].items():
            self.assertEqual(value, inventory(PARENT/'SkillBank')[relative])
        seen, compiled = [], []
        def extract(**kw):
            seen.append(kw['windows'][0].window_id)
            return SkillExtractionResult()
        def compile_fixture(**kw):
            compiled.append(len(kw['skill_drafts']))
            return SkillCompilationResult()
        cfg = read(run/'config.json')
        with patch.dict(os.environ,{cfg['credential_env']:'OFFLINE_FIXTURE_ONLY'}), \
             patch.object(pipeline,'extract_skills',side_effect=extract), \
             patch.object(pipeline.DocumentBuildPipeline,'ingest_document',
                          side_effect=AssertionError('Must reuse ingest; no Outline calls')), \
             patch.object(pipeline.DocumentBuildPipeline,'compile_skills',side_effect=compile_fixture), \
             patch.object(pipeline.DocumentBuildPipeline,'register_versions',
                          return_value=VersionRegistrationResult()):
            execute(run)
        self.assertEqual(seen,resume['pending_window_ids'])
        self.assertEqual(len(compiled),4, 'Empty error caches must not skip three completed documents')
        self.assertEqual(sum(compiled),49)
        result = read(run/'official_result.json')
        self.assertTrue(result['intermediate']['resumed'])
        self.assertEqual(result['total_skill_drafts'],49)
        self.assertEqual(read(run/'execution.json')['http_attempts'],0)
        self.assertEqual(read(run/'execution.json')['cumulative_usage_totals']['total_tokens'],453608)
        # Fixture compiler produces no skills: this is recovery validation, not generation success.
        self.assertEqual(result['total_skill_specs'],0)

    def test_exhausted_budget_rejected_before_creating_child(self):
        with self.assertRaisesRegex(ValueError,'Resume budget exhausted'):
            self.prepare(budget=False)
        self.assertFalse((self.root/'runs').exists())

    def test_pending_success_without_checkpoint_is_not_resent(self):
        import degradation_lab.resume as module
        original = module.read
        def changed(path):
            value = original(path)
            if Path(path)==PARENT/'model_calls.json':
                value[75]['success']=True
            return value
        with patch.object(module,'read',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'uncheckpointed calls'):
                self.prepare()
        self.assertFalse((self.root/'runs').exists())

    def test_successful_compilation_is_not_discarded(self):
        import degradation_lab.resume as module
        original = module.read
        def changed(path):
            value = original(path)
            if 'compile' in Path(path).parts and Path(path).name=='result.json':
                value['skill_specs']=[{'skill_id':'already-compiled'}]
            return value
        with patch.object(module,'read',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'Successful downstream artifacts'):
                self.prepare()

    def test_completed_http_request_blocked_pending_allowed(self):
        run=self.prepare()
        resume=read(run/'resume.json')
        with self.assertRaisesRegex(RuntimeError,'completed window'):
            guard_request(resume,read(PARENT/'http/005/request.json'),[{'function':'_plan_unit_skills'}])
        guard_request(resume,read(PARENT/'http/076/request.json'),[{'function':'_plan_unit_skills'}])

    def test_cli_passes_explicit_cumulative_limits(self):
        from degradation_lab.cli import main
        from degradation_lab.runner import ExperimentRunner
        with patch.object(sys,'argv',['lab.py','--root',str(LAB),'resume','--run',PARENT.name,
                                     '--run-id','s41r002','--max-observed-total-tokens','900000']), \
             patch.object(ExperimentRunner,'run',return_value=(self.root,0)) as run:
            self.assertEqual(main(),0)
        run.assert_called_once_with('case041_scrapy','clean','s41r002',resume_from=PARENT.name,
                                    resume_budget={'max_observed_total_tokens':900000})


if __name__=='__main__':
    unittest.main()
