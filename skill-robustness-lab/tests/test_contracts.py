"""Synthetic negative fixtures live only in temporary folders, not benchmark data."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from data_contracts import load_dataset,freeze_dataset,select,ContractError,validate_object,safe
from evidence import read,save,sha,freeze,check_frozen,digest
from compare_runs import compare
from run_one import baseline_identity,load_credentials
from unittest.mock import patch

class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root=Path(self.tmp.name)
        for part in ('cases','standards','catalog','scripts'): shutil.copytree(ROOT/part,self.root/part)
        self.casefile=self.root/'cases/case001/case.json'; self.case=read(self.casefile)
    def broken(self,relative,edit):
        p=self.root/relative; d=read(p); edit(d); save(p,d)
        with self.assertRaises((ContractError,KeyError,ValueError)): load_dataset(self.root)
    def test_original_valid(self): self.assertEqual(len(load_dataset(self.root)['tasks']),11)
    def test_missing_source_id(self): self.broken('cases/case001/case.json',lambda d:d.pop('source_id'))
    def test_wrong_type(self): self.broken('cases/case001/case.json',lambda d:d.update(version=True))
    def test_unknown_family(self): self.broken('cases/case001/case.json',lambda d:d.update(family_id='unknown'))
    def test_cross_case_source(self): self.broken('cases/case001/case.json',lambda d:d.update(source_file='cases/another/clean/source.md'))
    def test_cross_case_task(self): self.broken(self.case['task_files'][0],lambda d:d.update(case_id='another-v1'))
    def test_wrong_judge_reference(self): self.broken(self.case['task_files'][0],lambda d:d.update(judge_id='missing'))
    def test_duplicate_task(self): self.broken('cases/case001/case.json',lambda d:d['task_files'].append(d['task_files'][0]))
    def test_unexpected_score_in_contract(self): self.broken(self.case['contract_file'],lambda d:d.update(score=1))
    def test_changed_fixture_answer(self): self.broken(self.case['task_files'][0],lambda d:d['expected']['outputs'].update({'summary.csv':'incorrect'}))
    def test_case_metadata_tamper(self): self.broken('cases/case001/case.json',lambda d:d.update(title='modified'))
    def test_split_change(self): self.broken('catalog/split.json',lambda d:d['assignments'][0].update(split='heldout_test'))
    def test_source_family_leakage_with_consistent_metadata(self):
        # Create a SECOND TEMPORARY TEST RECORD only, with locally consistent
        # IDs but the same source/family across development and validation.
        for parent in ('cases','standards'):
            shutil.copytree(self.root/parent/'case001',self.root/parent/'unitclone')
            for file in (self.root/parent/'unitclone').rglob('*.json'):
                text=file.read_text(encoding='utf-8').replace('case001-v2','unitclone-v1').replace('cases/case001/','cases/unitclone/').replace('standards/case001/','standards/unitclone/')
                d=__import__('json').loads(text)
                if 'case_key' in d: d['case_key']='unitclone'; d['usage']='research'
                if 'split' in d: d['split']='validation'
                if d.get('purpose')=='development': d['purpose']='validation'
                if 'task_files' in d: d['task_files']=[p.replace('case001-v2','unitclone-v1') for p in d['task_files']]
                save(file,d)
            for file in list((self.root/parent/'unitclone').rglob('case001-v2.*.json')):
                file.rename(file.with_name(file.name.replace('case001-v2','unitclone-v1')))
        index=read(self.root/'catalog/cases.json'); index['case_files'].append('cases/unitclone/case.json'); save(self.root/'catalog/cases.json',index)
        split=read(self.root/'catalog/split.json'); item=copy.deepcopy(split['assignments'][0]); item.update(case_id='unitclone-v1',split='validation'); split['assignments'].append(item); save(self.root/'catalog/split.json',split)
        with self.assertRaisesRegex(ContractError,'crosses splits'): load_dataset(self.root,False)
    def test_input_tamper(self):
        (self.root/self.case['source_file']).write_text('tampered',encoding='utf-8')
        with self.assertRaises(ContractError): load_dataset(self.root)
    def test_added_unregistered_file(self):
        (self.root/'cases/case001/unregistered.txt').write_text('x')
        with self.assertRaises(ContractError): load_dataset(self.root)
    def test_refreeze_refuses_tamper(self):
        d=read(self.casefile); d['title']='changed'; save(self.casefile,d)
        with self.assertRaises(ContractError): freeze_dataset(self.root)
    def test_idempotent_freeze(self):
        before=sha(self.root/'catalog/freeze.json'); freeze_dataset(self.root)
        self.assertEqual(before,sha(self.root/'catalog/freeze.json'))
    def test_wrong_clean_pair(self): self.broken('cases/case001/variants/clean.json',lambda d:d.update(clean_variant_id='missing'))
    def test_path_traversal(self):
        for p in ('../secret','C:/secret','/secret','cases/../../secret','cases\\secret'):
            with self.subTest(p=p),self.assertRaises(ContractError): safe(self.root,p)
    def test_unsafe_task_filename(self): self.broken(self.case['task_files'][0],lambda d:d['inputs'].update({'../x':'x'}))
    def add_degraded(self,pending=False):
        c=read(self.casefile); v=read(self.root/c['variant_files'][0]); text=(self.root/c['source_file']).read_bytes().decode('utf-8')
        vid=c['case_id']+'.test-degraded'; path='cases/case001/degradation/files/test.md'
        target=self.root/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes((text+'\n').encode('utf-8'))
        generator='cases/case001/degradation/generators/test.py'; g=self.root/generator; g.parent.mkdir(parents=True,exist_ok=True); g.write_text('# unittest-only append newline\n')
        dep='cases/case001/degradation/test.json'; vp='cases/case001/variants/test.json'
        save(self.root/dep,{'schema_version':'4.0','degradation_id':'unittest-only','case_id':c['case_id'],'variant_id':vid,
            'type':'unittest-only','severity':{'value':1,'unit':'newline'},'seed':0,'generator':{'file':generator,'sha256':sha(g),'version':'test'},
            'parameters':{},'edits':[{'start':len(text),'end':len(text),'before':'','after':'\n'}],
            'recoverability':{'status':'pending' if pending else 'recoverable','reviewer':None if pending else 'unittest',
                'evidence':'Synthetic validator fixture; not a research degradation',
                'rule_ids':[r['rule_id'] for r in read(self.root/c['contract_file'])['rules']]}})
        v.update(variant_id=vid,condition='degraded',input_file=path,input_sha256=sha(target),degradation_file=dep)
        save(self.root/vp,v); c['variant_files'].append(vp); save(self.casefile,c)
        (self.root/'catalog/freeze.json').unlink(); freeze_dataset(self.root)
        return vid,dep
    def test_edit_replay_valid(self):
        vid,_=self.add_degraded(); self.assertEqual(select(self.root,'case001',vid)[2]['condition'],'degraded')
    def test_edit_replay_rejects_lie(self):
        _,dep=self.add_degraded(); self.broken(dep,lambda d:d['edits'][0].update(after='different'))
    def test_recoverability_pending_not_runnable(self):
        vid,_=self.add_degraded(True)
        with self.assertRaises(ContractError): select(self.root,'case001',vid)

class ResultTests(unittest.TestCase):
    def test_no_score_for_not_run(self):
        j={'schema_version':'4.0','judgment_id':'j','execution_id':'e','case_id':'c','task_id':'t','judge_id':'judge',
            'status':'not_run','passed':True,'checks':[],'reason':'test','execution_checksums_sha256':'a'*64,'judge_sha256':'b'*64,'created_at_utc':'test'}
        with self.assertRaises(ContractError): validate_object('judgment',j)
    def test_ir_cycles_and_forward_links_rejected(self):
        ir={'schema_version':'4.0','ir_id':'ir','case_id':'c','source_id':'s','variant_id':'v','run_id':'r','ir_version':'1',
            'status':'generated','goal':'g','inputs':[],'preconditions':[],'steps':[{'step_id':'a','action':'x','depends_on':['a'],'kind':'action'}],
            'branches':[],'invariants':[],'outputs':['output'],'checks':[],'unresolved':[],'provenance_file':None,'validation_reason':'test'}
        with self.assertRaises(ContractError): validate_object('program_ir',ir)
    def test_run_seal_refuses_rewrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); save(p/'result.json',{'status':'not_run'}); freeze(p)
            save(p/'result.json',{'status':'passed'})
            self.assertFalse(check_frozen(p)['valid'])
            with self.assertRaises(ValueError): freeze(p)
    def test_credentials_literal_parser(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict('os.environ',{},clear=True):
            p=Path(tmp)/'.env'; p.write_text('IGNORED=42\nDASHSCOPE_API_KEY="unit-test-literal" # comment\n')
            self.assertEqual(load_credentials(p),('unit-test-literal','configured_file'))

if __name__=='__main__': unittest.main()
