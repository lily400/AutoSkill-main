"""Offline adapter regressions; no Agent or model invocation."""
import ast
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

LAB=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(LAB),str(LAB/'src')]
from downstream_eval.sgb.task_adapters.scrapy041.scoring import TASK, verify_assets, score, parse_junit, TEST_NAMES
from downstream_eval.sgb.task_adapters.scrapy041.adapter import export_submission, paid_batch, execution_config


class Scrapy041(unittest.TestCase):
    def test_official_oracle_and_instruction_are_exact(self):
        original=LAB/'.external/skillgenbench/5a8bd61d/skill_evaluation/code_doc/scrapy/scrapy-task-041'
        self.assertEqual((TASK/'instruction.md').read_bytes(),(original/'instruction.md').read_bytes())
        self.assertEqual((TASK/'scorer/oracle/eval.py').read_bytes(),(original/'tests/eval.py').read_bytes())
        self.assertEqual((TASK/'task.original.toml').read_bytes(),(original/'task.toml').read_bytes())
        verify_assets()

    def test_all_original_assertion_names_retained(self):
        tree=ast.parse((TASK/'scorer/oracle/eval.py').read_text())
        actual=[node.name for node in ast.walk(tree) if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')]
        self.assertEqual(actual,TEST_NAMES)

    def test_source_bundle_identity_and_bytes(self):
        rows=[json.loads(line) for line in (LAB/'data/manifests/sgb/tasks.jsonl').read_text().splitlines()]
        row=next(r for r in rows if r['original_task_id']=='scrapy-task-041')
        self.assertEqual(row['task_key'],'t-8d3bed6236cf')
        self.assertEqual(row['source_bundle_id'],'b-083578378ffb0792')
        self.assertEqual(len(row['sources']),4)
        for item in row['sources']:
            self.assertEqual(hashlib.sha256((LAB/item['path']).read_bytes()).hexdigest(),item['sha256'])

    def test_invalid_and_hash_mismatch_reject_before_docker(self):
        with tempfile.TemporaryDirectory() as temp, patch(
                'downstream_eval.sgb.task_adapters.scrapy041.scoring.docker_executor',
                side_effect=AssertionError('No Docker expected')):
            root=Path(temp);candidate=root/'agent_output.py';candidate.write_text('pass')
            result=score(candidate,root/'mismatch',expected_sha256='0'*64)
            self.assertFalse(result['task_success'])
            self.assertEqual(result['failure_category'],'submission_hash_mismatch')
            for name,path in [('missing',root/'missing.py'),('directory',root)]:
                result=score(path,root/name)
                self.assertEqual(result['failure_category'],'invalid_submission')
            candidate.write_bytes(b'x'*131073)
            self.assertEqual(score(candidate,root/'large')['failure_category'],'invalid_submission')

    def test_existing_result_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileExistsError):
                score(Path(temp)/'absent',Path(temp))

    def test_missing_junit_cannot_be_success(self):
        with tempfile.TemporaryDirectory() as temp:
            counts,_=parse_junit(Path(temp)/'missing')
            self.assertEqual(counts['tests'],0)
            p=Path(temp)/'junit.xml'
            p.write_text('<testsuite><testcase name="a"><error/></testcase><testcase name="b"><skipped/></testcase></testsuite>')
            counts,failed=parse_junit(p)
            self.assertEqual((counts['passed'],counts['errors'],counts['skipped']),(0,1,1))
            self.assertEqual(failed,['a','b'])

    def test_export_rejects_tampered_download(self):
        class FakeEnvironment:
            async def exec(self,*args,**kwargs):
                return SimpleNamespace(return_code=0,stdout=hashlib.sha256(b'original').hexdigest())
            async def download_file(self,*,source_path,target_path):
                target_path.write_bytes(b'changed')
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,'hash'):
                asyncio.run(export_submission(FakeEnvironment(),Path(temp)/'export'))

    def test_data_bridge_does_not_coerce_bool_or_tuple(self):
        tree=ast.parse((TASK/'scorer/oracle_bridge.py').read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack')
        namespace={}
        exec(compile(ast.Module(body=[function],type_ignores=[]),'<trusted-unpack>','exec'),namespace)
        unpack=namespace['unpack']
        self.assertIs(unpack({'kind':'scalar','value':True}),True)
        self.assertIsNot(unpack({'kind':'scalar','value':'True'}),True)
        self.assertIsNot(unpack({'kind':'scalar','value':1}),True)
        self.assertEqual(unpack({'kind':'tuple','value':[{'kind':'scalar','value':'example.com'}]}),('example.com',))
        with self.assertRaises(ValueError):unpack({'kind':'executable','value':'pass'})

    def test_task_identity_and_budget_scope_are_explicit(self):
        config=execution_config(Path('/tmp/new-run'),'generator-041',{'N':'NoSkill','C':'CleanSkill'})
        self.assertEqual(config.budget_scope,'scrapy-task-041/generator-041/new-run')
        self.assertIn('scrapy041.agent',config.agent_import_path)

    def test_paid_entry_refuses_before_framework_import(self):
        with patch.dict(os.environ,{'SCRAPY041_ALLOW_PAID':'0'}):
            with self.assertRaisesRegex(RuntimeError,'not enabled'):
                paid_batch(Path('/does-not-exist'))

    def test_submission_is_exported_before_native_container_stop(self):
        from harbor.trial.trial import Trial
        from downstream_eval.sgb.task_adapters.scrapy041.adapter import native_trial, grade_export
        payload=b'print("candidate")\n'
        class FakeEnvironment:
            stopped=False
            async def exec(self,*args,**kwargs):
                if self.stopped:
                    raise AssertionError('Export attempted after teardown')
                return SimpleNamespace(return_code=0,stdout=hashlib.sha256(payload).hexdigest())
            async def download_file(self,*,source_path,target_path):
                if self.stopped:
                    raise AssertionError('Download attempted after teardown')
                target_path.write_bytes(payload)
        with tempfile.TemporaryDirectory() as temp:
            trial=SimpleNamespace(agent_environment=FakeEnvironment(),
                                  paths=SimpleNamespace(trial_dir=Path(temp)))
            async def phase(self,*args,**kwargs):
                return None
            async def fake_native(config):
                await Trial._run_agent_phase(trial)
                trial.agent_environment.stopped=True
                return trial,{'exception_info':None}
            with patch.object(Trial,'_run_agent_phase',phase), \
                 patch('downstream_eval.sgb.scrapy024.native_trial',side_effect=fake_native):
                actual,_=asyncio.run(native_trial(object()))
            self.assertTrue(actual.agent_environment.stopped)
            path,digest=actual._scrapy041_export
            self.assertEqual(path.read_bytes(),payload)
            with patch('downstream_eval.sgb.task_adapters.scrapy041.adapter.score',return_value={'ok':True}) as scorer:
                self.assertEqual(grade_export(actual,Path(temp)/'oracle'),{'ok':True})
                scorer.assert_called_once_with(path,Path(temp)/'oracle/score',expected_sha256=digest)
            path.write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'changed after container stop'):
                grade_export(actual,Path(temp)/'oracle2')



if __name__=='__main__':unittest.main()
