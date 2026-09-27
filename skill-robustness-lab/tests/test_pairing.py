"""Temporary synthetic records test pairing logic; never saved as study runs."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from evidence import save,sha,freeze,digest,read
from data_contracts import ContractError
from compare_runs import compare
from run_one import baseline_identity

class PairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup); self.root=Path(self.tmp.name)
        save(self.root/'catalog/freeze.json',{'test_only':True})
        self.contract={'case_id':'test-case','source_id':'test-source','source_version':'1','family_id':'test-family','split':'development',
            'dataset_freeze_sha256':sha(self.root/'catalog/freeze.json'),'parameters':{'method_id':'test-method'},'test_only':'unit-test never research evidence'}
        self.clean=self.make('clean',False); self.degraded=self.make('degraded',False)
    def make(self,condition,structural,kind='generation'):
        p=self.root/'runs'/condition; p.mkdir(parents=True,exist_ok=True)
        source=p/'input/source.md'; source.parent.mkdir(); source.write_text(condition,encoding='utf-8')
        h=sha(source); ch=h if condition=='clean' else sha(self.root/'runs/clean/input/source.md')
        v={'schema_version':'4.0','variant_id':'test-'+condition,'version':1,'case_id':'test-case','source_id':'test-source','source_version':'1','family_id':'test-family',
            'condition':condition,'input_file':'cases/test/source.md','input_sha256':h,'clean_variant_id':'test-clean','clean_sha256':ch,
            'contract_id':'test-contract','degradation_file':None if condition=='clean' else 'cases/test/degradation.json','status':'frozen'}
        r={'schema_version':'4.0','run_id':condition,**{k:self.contract[k] for k in ('case_id','source_id','source_version','family_id','split')},
            'variant_id':v['variant_id'],'method_id':'test-method','generation_repeat':1,'kind':kind,'status':'failed',
            'input_sha256':h,'dataset_freeze_sha256':self.contract['dataset_freeze_sha256'],'comparison_fingerprint':digest(self.contract),
            'structural_pass':structural,'semantic_status':'pending','execution_status':'not_run',
            'failure':{'category':'generation','stage':'build','evidence':['test-only']},'program_ir_status':'not_applicable','started_at_utc':'test','finished_at_utc':'test'}
        save(p/'run.json',r); save(p/'status.json',{'status':'failed','structural_pass':structural,'evidence_capture_pass':True})
        save(p/'config/variant.json',v); save(p/'config/comparison_contract.json',self.contract)
        save(p/'config/comparison_fingerprint.json',{'sha256':digest(self.contract)})
        if condition=='degraded': save(p/'config/pair.json',{'baseline_run_id':'clean','baseline_checksums_sha256':sha(self.clean/'checksums.json')})
        freeze(p); return p
    def edit_and_reseal(self,folder,relative,edit):
        p=folder/relative; d=read(p); edit(d); save(p,d)
        # Explicitly allowed only inside temporary unit-test fixture.
        (folder/'checksums.json').unlink(); freeze(folder)
    def test_clean_and_degraded_failure_retained(self):
        result=compare(self.clean,self.degraded)
        self.assertTrue(result['comparable']); self.assertFalse(result['eligible_for_skill_quality_comparison'])
        self.assertIsNone(result['task_success_delta'])
    def test_failed_clean_allowed_as_baseline(self):
        c={k:self.contract[k] for k in ('case_id','source_id','source_version','family_id')}
        v=read(self.degraded/'config/variant.json')
        baseline_identity(self.root,'clean',c,v,{'method_id':'test-method','repeat_id':1})
    def test_wrong_repeat_rejected_before_model(self):
        c={k:self.contract[k] for k in ('case_id','source_id','source_version','family_id')}
        with self.assertRaises(ContractError): baseline_identity(self.root,'clean',c,read(self.degraded/'config/variant.json'),{'method_id':'test-method','repeat_id':2})
    def test_preflight_not_a_baseline(self):
        self.edit_and_reseal(self.clean,'run.json',lambda d:d.update(kind='preflight'))
        with self.assertRaises(ContractError): compare(self.clean,self.degraded)
    def test_wrong_baseline_binding(self):
        self.edit_and_reseal(self.degraded,'config/pair.json',lambda d:d.update(baseline_run_id='other'))
        self.assertFalse(compare(self.clean,self.degraded)['comparable'])
    def test_fingerprint_recomputed(self):
        self.edit_and_reseal(self.degraded,'config/comparison_contract.json',lambda d:d.update(test_only='changed'))
        with self.assertRaises(ContractError): compare(self.clean,self.degraded)
    def test_wrong_clean_hash(self):
        self.edit_and_reseal(self.degraded,'config/variant.json',lambda d:d.update(clean_sha256='f'*64))
        self.assertFalse(compare(self.clean,self.degraded)['comparable'])
    def test_cross_case_variant(self):
        self.edit_and_reseal(self.degraded,'config/variant.json',lambda d:d.update(case_id='other'))
        with self.assertRaises(ContractError): compare(self.clean,self.degraded)
    def test_modified_run_is_rejected(self):
        save(self.clean/'unexpected.json',{'test':True})
        with self.assertRaises(ContractError): compare(self.clean,self.degraded)
if __name__=='__main__': unittest.main()
