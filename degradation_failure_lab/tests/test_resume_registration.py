"""Registration recovery against a real frozen checkpoint; no real model traffic."""
import importlib
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB/'src'))
from degradation_lab.io import inventory,read,resolve_upstream
from degradation_lab.resume import prepare_resume,guard_request
PARENT = LAB/'runs/gen/sgb/case041_scrapy/clean/s41r002'
UPSTREAM = resolve_upstream(LAB)
sys.path.insert(0,str(UPSTREAM))


class RegistrationRecovery(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='rr-',dir=LAB.parent)
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.before=inventory(PARENT)
        for target in ('socket.socket.connect','urllib.request.urlopen','urllib.request.OpenerDirector.open'):
            p=patch(target,side_effect=AssertionError('Network/model forbidden'))
            p.start();self.addCleanup(p.stop)

    def tearDown(self):
        self.assertEqual(self.before,inventory(PARENT))

    def prepare(self,budget=True):
        with patch('degradation_lab.resume.resolve_run',return_value=(read(PARENT/'invocation.json'),PARENT)), \
             patch('degradation_lab.resume.resolve_upstream',return_value=UPSTREAM), \
             patch('degradation_lab.resume.check_windows_run_path'):
            return prepare_resume(self.root,'s41r002','r1',{'max_http_calls':250} if budget else None)

    def test_official_registration_skips_completed_docs_and_cached_decisions(self):
        from degradation_lab.adapter import execute
        from AutoSkill4Doc.store.versioning import VersionManager,ChangeDecision
        pipeline=importlib.import_module('AutoSkill4Doc.pipeline')
        run=self.prepare();resume=read(run/'resume.json')
        self.assertEqual(len(resume['completed_window_ids']),35)
        self.assertEqual(resume['pending_window_ids'],[])
        self.assertEqual(len(resume['completed_registration_doc_ids']),2)
        self.assertEqual(len(resume['cached_registration_decision_ids']),9)
        self.assertEqual(resume['seed_skillbank'],inventory(PARENT/'SkillBank'))
        self.assertEqual(resume['prior_http_attempts'],150)
        self.assertEqual(resume['prior_usage_totals']['total_tokens'],631047)
        self.assertEqual(read(run/'config.json')['max_http_calls'],250)
        self.assertEqual(read(run/'config.json')['max_observed_total_tokens'],900000)
        seen=[];docs=[]
        original=pipeline.DocumentBuildPipeline.register_versions
        def register(self,**kw):
            docs.extend(d.doc_id for d in kw['documents'])
            return original(self,**kw)
        def classify(self,skill,**kw):
            seen.append(skill.skill_id)
            return ChangeDecision(action='discard',skill=skill,reason='OFFLINE_FIXTURE')
        with patch.dict(os.environ,{read(run/'config.json')['credential_env']:'OFFLINE_FIXTURE'}), \
             patch.object(pipeline.DocumentBuildPipeline,'ingest_document',side_effect=AssertionError('Ingest must be cached')), \
             patch.object(pipeline,'extract_skills',side_effect=AssertionError('Extract must be cached')), \
             patch.object(pipeline.DocumentBuildPipeline,'compile_skills',side_effect=AssertionError('Compile must be cached')), \
             patch.object(pipeline.DocumentBuildPipeline,'register_versions',new=register), \
             patch.object(VersionManager,'classify_change',new=classify), \
             patch.object(VersionManager,'link_hierarchy',new=lambda self,**kw:(kw['skills'],[])), \
             patch.object(VersionManager,'consolidate_duplicate_skills',new=lambda self,**kw:kw['result']):
            execute(run)
        self.assertEqual(len(docs),2)
        self.assertFalse(set(docs)&set(resume['completed_registration_doc_ids']))
        self.assertEqual(len(seen),41)
        self.assertEqual(len(set(seen)),41)
        self.assertFalse(set(seen)&set(resume['cached_registration_decision_ids']))
        result=read(run/'official_result.json')
        self.assertTrue(result['intermediate']['resumed'])
        self.assertEqual(result['status'],'completed')
        self.assertFalse(result['errors'])
        self.assertEqual(read(run/'execution.json')['http_attempts'],0)
        self.assertEqual(read(run/'execution.json')['cumulative_http_attempts'],150)
        # Offline discard/hierarchy fixtures validate routing, not real skill quality.

    def test_no_implicit_request_budget_increase(self):
        with self.assertRaisesRegex(ValueError,'Resume budget exhausted'):
            self.prepare(budget=False)
        self.assertFalse((self.root/'runs').exists())

    def test_missing_successful_decision_refuses_replay(self):
        import degradation_lab.resume as module
        original=module.read
        def changed(path):
            value=original(path)
            if Path(path)==PARENT/'http/061/request.json':
                import json
                user=json.loads(value['messages'][1]['content'])
                user['candidate_skill']['skill_id']='missing'
                value['messages'][1]['content']=json.dumps(user)
            return value
        with patch.object(module,'read',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'Uncheckpointed registration decision'):
                self.prepare()

    def test_request_guard_blocks_recompile_and_cached_classification(self):
        run=self.prepare();r=read(run/'resume.json')
        with self.assertRaisesRegex(RuntimeError,'extraction/compilation'):
            guard_request(r,{},[{'function':'compile_skills'}])
        with self.assertRaisesRegex(RuntimeError,'cached registration decision'):
            guard_request(r,read(PARENT/'http/061/request.json'),[{'function':'classify_change'}])


if __name__=='__main__':
    unittest.main()
