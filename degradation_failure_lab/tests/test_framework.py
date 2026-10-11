import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LAB/'src'))
from degradation_lab.catalog import CaseManager
from degradation_lab.runner import ExperimentRunner, validate_config
from degradation_lab.artifacts import inspect_run, export_run, run_refs
from degradation_lab.evaluation import aggregate, validate_evaluation
from degradation_lab.io import read, write, sha256, inventory
from degradation_lab.schema import check


def fixture_catalog(root):
    """All invented data stay inside TemporaryDirectory; never registered in LAB."""
    write(root/'configs/environment.json',read(LAB/'configs/environment.json'))
    cfg=read(LAB/'configs/generation/deepseek_flash.json')
    cfg['llm']={'provider':'openai','model':'fixture-vendor-model','base_url':'https://fixture.invalid'}
    cfg['provider_service']='FIXTURE'; cfg['credential_env']='FIXTURE_ONLY_KEY'
    write(root/'configs/shared.json',cfg)
    source=root/'data/raw_sources/fixture/source.md'; source.parent.mkdir(parents=True)
    source.write_text('# FIXTURE ONLY\nRun fixture tool with --flag.\n',encoding='utf-8')
    m={'source_id':'fixture-source','source_url':'fixture://not-real-data','source_repository':'fixture',
       'source_commit':'fixture','source_path':'source.md','license':'fixture-test-only','downloaded_at':'2026-10-10',
       'sha256':sha256(source),'document_type':'fixture_markdown','classification':'CUSTOM_TEST_DATA',
       'paper_snapshot_verified':False,'local_path':'data/raw_sources/fixture/source.md'}
    write(root/'data/source.json',m)
    write(root/'data/catalog.json',{'schema_version':1,'datasets':[{'dataset_id':'fixture',
        'description':'Only offline unit-test data','source_manifests':['data/source.json']}]})
    for cid in ('case001_fixture','case002_fixture'):
        base=root/'cases'/cid
        write(base/'case.json',{'schema_version':1,'case_id':cid,'dataset_id':'fixture','title':'fixture case',
            'source_ids':['fixture-source'],'generation_config':'configs/shared.json','pipeline_overrides':{}})
        write(base/'rules.json',{'schema_version':1,'case_id':cid,'classification':'CUSTOM_TEST_DATA',
            'provenance':{},'rules':[{'rule_id':'R1','text':'FIXTURE: --flag only','source_evidence':[{
                'source_id':'fixture-source','lines':[2]}],'rule_type':'fixture','annotation_status':'pending'}]})
        conditions=[]
        for condition in ('clean','damage_a','damage_b','damage_c'):
            p='data/raw_sources/fixture/source.md'
            if condition!='clean':
                p='data/condition_inputs/'+condition+'.md'
                (root/p).parent.mkdir(parents=True, exist_ok=True)
                (root/p).write_text('# FIXTURE '+condition+'\nfixture --flag\n',encoding='utf-8')
            manifest=f'cases/{cid}/inputs/{condition}.json'
            write(root/manifest,{'schema_version':1,'case_id':cid,'condition_id':condition,'inputs':[{
                'input_id':'input001','source_id':'fixture-source','source_sha256':m['sha256'],
                'path':p,'sha256':sha256(root/p)}]})
            conditions.append({'condition_id':condition,'kind':'clean' if condition=='clean' else 'degraded',
                'input_manifest':manifest,'operator':None if condition=='clean' else 'fixture_materialized',
                'parameters':{} if condition=='clean' else {'fixture_only':True}})
        write(base/'conditions.json',{'schema_version':1,'case_id':cid,'conditions':conditions})


def fixture_artifacts(run):
    """Synthetic intermediate records for exporter tests, marked FIXTURE throughout."""
    i=read(run/'input_manifest.json')['inputs'][0]; path=i['execution_path']
    mid=run/'SkillBank/.runtime/intermediate_runs/fixture'; mid.mkdir(parents=True)
    support={'support_id':'support-fixture','doc_id':'doc-fixture','source_file':path,
             'metadata':{'window_id':'window-fixture'},'excerpt':'fixture --flag'}
    spec={'skill_id':'skill-fixture','name':'Fixture generic skill','support_ids':['support-fixture'],
          'metadata':{'source_draft_ids':['draft-fixture']},'skill_body':'fixture body','workflow_steps':['fixture only']}
    write(mid/'ingest/result.json',{'documents':[{'doc_id':'doc-fixture','metadata':{'source_file':path}}],
        'text_units':[{'text':'fixture --flag'}],'windows':[{'window_id':'window-fixture',
        'doc_id':'doc-fixture','span':{'start':0,'end':10},'text':'fixture --flag'}]})
    write(mid/'extract/result.json',{'skill_drafts':[{'draft_id':'draft-fixture','doc_id':'doc-fixture',
                                                  'support_ids':['support-fixture']}]})
    write(mid/'compile/result.json',{'support_records':[support],'skill_specs':[spec]})
    write(mid/'register/result.json',{'upserted_store_skills':[{'id':'skill-fixture'}],
        'provenance_links':[{'entity_id':'skill-fixture','doc_ids':['doc-fixture'],'support_added':['support-fixture']}]})
    skill=run/'SkillBank/Users/fixture-user/fixture-skill/SKILL.md'; skill.parent.mkdir(parents=True)
    skill.write_text('---\nid: "skill-fixture"\n---\nfixture body\n',encoding='utf-8')
    write(run/'SkillBank/visible/references/evidence_manifest.json',{'skill_id':'skill-fixture',
        'supports':[{'support_id':'support-fixture','quote':'fixture --flag'}]})
    write(run/'official_result.json',{'intermediate':{'run_dir':str(mid)},'status':'completed','errors':[],
        'skipped_documents':0,'reused_nodes':[]})
    write(run/'execution.json',{'exit_code':0,'usage_totals':{}})
    write(run/'upstream_after.json',read(run/'upstream_before.json'))
    write(run/'artifact_manifest.json',inventory(run))


class Framework(unittest.TestCase):
    def setUp(self):
        # An accidental paid/network call fails every new framework test.
        self.network=patch('urllib.request.urlopen',side_effect=AssertionError('No network/model calls permitted'))
        self.network.start(); self.addCleanup(self.network.stop)

    def test_actual_case001_and_original_rules_unchanged(self):
        manager=CaseManager(LAB); self.assertEqual(manager.list_cases(),['case001_qsv_select'])
        b=manager.load('case001_qsv_select'); manager.condition(b,'clean')
        self.assertEqual([r['rule_id'] for r in b['rules']['rules']], ['R1','R2','R3','R4','R5','R6','R7'])
        self.assertEqual(b['rules']['provenance'], {})
        source=b['case']['source_ids'][0]
        manifest=manager.sources.sources[source]
        clean=read(LAB/'cases/case001_qsv_select/inputs/clean.json')['inputs'][0]
        self.assertEqual(manifest['local_path'],clean['path'])
        self.assertTrue(manifest['local_path'].startswith('data/raw_sources/'))
        self.assertEqual(sha256(LAB/manifest['local_path']),manifest['sha256'])
        self.assertEqual(read(LAB/'data/catalog.json')['datasets'][0]['source_manifests'],
                         ['data/manifests/qsv_select.json'])
        self.assertFalse((LAB/'data/manifests/qsv_select_canonical.json').exists())

    def test_no_active_legacy_files(self):
        for name in ('legacy','data/legacy_bytes','data/sources','runs/legacy_index.json'):
            self.assertFalse((LAB/name).exists(),name)

    def test_strict_schema_missing_unknown_type_and_id(self):
        case=read(LAB/'cases/case001_qsv_select/case.json')
        for mutation in ({'unknown':1},{'case_id':'run001'},{'source_ids':'source'}):
            v=dict(case,**mutation)
            with self.assertRaises(ValueError): check('case',v)
        v=dict(case); v.pop('dataset_id')
        with self.assertRaises(ValueError): check('case',v)
        with self.assertRaises(ValueError): check('catalog',{'schema_version':True,'datasets':[]})

    def test_fixture_case002_shares_source_without_core_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root); manager=CaseManager(root)
            a=manager.load('case001_fixture'); b=manager.load('case002_fixture')
            self.assertEqual(a['case']['source_ids'],b['case']['source_ids'])
            self.assertEqual(len(manager.sources.sources),1)
            self.assertEqual(len(b['conditions']['conditions']),4)

    def test_three_conditions_three_runs_isolated_and_collision_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root); runner=ExperimentRunner(root)
            paths=[]
            for c in ('damage_a','damage_b','damage_c'):
                self.assertEqual(runner.plan('case002_fixture',c,3)['repeat'],3)
                for n in range(3):
                    p=runner.prepare('case002_fixture',c,f'fixture_{c}_{n}',fixture=True)
                    self.assertEqual(list((p/'SkillBank').iterdir()),[])
                    (p/'SkillBank/sentinel').write_text(str(n)); paths.append(p)
                    self.assertFalse(read(p/'invocation.json')['real_generation'])
                    self.assertEqual(sha256(p/read(p/'input_manifest.json')['inputs'][0]['path']),
                                     read(p/'input_manifest.json')['inputs'][0]['sha256'])
            self.assertEqual(len(set(paths)),9); self.assertEqual(len(run_refs(root)),9)
            with self.assertRaises(FileExistsError): runner.prepare('case002_fixture','damage_a','fixture_damage_a_0',fixture=True)
            with self.assertRaises(FileExistsError): runner.prepare('case002_fixture','damage_b','fixture_damage_a_0',fixture=True)
            with self.assertRaises(ValueError): runner.prepare('case002_fixture','damage_a','../escape',fixture=True)

    def test_condition_and_parent_hash_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root); manager=CaseManager(root)
            p=root/'cases/case002_fixture/inputs/damage_a.json'; v=read(p)
            v['inputs'][0]['source_sha256']='0'*64; write(p,v)
            with self.assertRaises(ValueError): manager.condition(manager.load('case002_fixture'),'damage_a')
            p=root/'cases/case002_fixture/inputs/clean.json'; v=read(p); v['inputs'][0]['path']='../escape'; write(p,v)
            with self.assertRaises(ValueError): manager.condition(manager.load('case002_fixture'),'clean')

    def test_case_multiple_sources_condition_resolution(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root)
            m=read(root/'data/source.json'); m=dict(m,source_id='fixture-source-two',local_path='data/two.md')
            (root/'data/two.md').write_text('# FIXTURE second\nSecond step.\n',encoding='utf-8')
            m['sha256']=sha256(root/'data/two.md'); write(root/'data/two.json',m)
            catalog=read(root/'data/catalog.json'); catalog['datasets'][0]['source_manifests'].append('data/two.json')
            write(root/'data/catalog.json',catalog)
            base=root/'cases/case002_fixture'; case=read(base/'case.json'); case['source_ids'].append(m['source_id']); write(base/'case.json',case)
            inputs=read(base/'inputs/clean.json'); inputs['inputs'].append({'input_id':'input002','source_id':m['source_id'],
                'source_sha256':m['sha256'],'path':m['local_path'],'sha256':m['sha256']}); write(base/'inputs/clean.json',inputs)
            runner=ExperimentRunner(root); p=runner.prepare('case002_fixture','clean','fixture_multisource',fixture=True)
            from AutoSkill4Doc.document.file_loader import load_file_units
            units,_=load_file_units(str(p/'inputs'),max_files=2)
            self.assertEqual(len(units),2); self.assertEqual(len(read(p/'sources.json')),2)
            self.assertEqual(read(p/'config.json')['pipeline']['max_documents'],2)

    def test_unchanged_bytes_cannot_be_labeled_degraded(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root); p=root/'cases/case002_fixture/inputs/damage_a.json'
            value=read(p); source=read(root/'data/source.json')
            value['inputs'][0].update(path=source['local_path'],sha256=source['sha256']); write(p,value)
            manager=CaseManager(root)
            with self.assertRaises(ValueError): manager.condition(manager.load('case002_fixture'),'damage_a')

    def test_generic_trace_export_not_qsv_or_model_specific(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root)
            p=ExperimentRunner(root).prepare('case002_fixture','damage_a','fixture_export',fixture=True)
            fixture_artifacts(p); report,exports=inspect_run(root,p.name)
            self.assertEqual(report['status'],'FIXTURE'); self.assertFalse(report['checks']['real_model_calls'])
            self.assertEqual(exports['traceability'][0]['sources'][0]['source_id'],'fixture-source')
            self.assertTrue(report['checks']['canonical_program_skills'])
            self.assertEqual(len(exports['skill_files']['canonical_program_skills']),1)
            export_run(root,p.name,root/'results/export')
            self.assertTrue((root/'results/export/traceability.json').exists())
            with self.assertRaises(ValueError): export_run(root,p.name,p/'exports')
            self.assertEqual(aggregate(root,root/'results/summary')['runs'],0)

    def test_new_run_evaluation_contract(self):
        from degradation_lab.evaluation import init_evaluation
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root)
            run=ExperimentRunner(root).prepare('case002_fixture','clean','fixture_review',fixture=True)
            fixture_artifacts(run)
            path=init_evaluation(root,run.name,'review001')
            review=read(path)
            self.assertEqual(review['records'][0]['status'],'unreviewed')
            review['records'][0]['status']='correct'
            review['records'][0]['skill_ids']=['skill-fixture']
            validate_evaluation(root,review)
            wrong=copy.deepcopy(review)
            wrong['records'][0]['skill_ids']=['missing-skill']
            with self.assertRaises(ValueError): validate_evaluation(root,wrong)
            self.assertEqual(aggregate(root,root/'results/summary')['runs'],0)

    def test_mock_keys_and_custom_connectors_rejected(self):
        cfg=read(LAB/'configs/generation/deepseek_flash.json')
        for change in ({'provider':'mock'},{'api_key':'fixture'},{'response':'fixture'},
                       {'connector_factory':'arbitrary:build'}):
            value=copy.deepcopy(cfg); value['llm'].update(change)
            with self.assertRaises(ValueError): validate_config(value)

    def test_missing_credential_does_not_create_run(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root)
            with patch.dict('os.environ',{},clear=True):
                with self.assertRaisesRegex(RuntimeError,'BLOCKED'):
                    ExperimentRunner(root).run('case002_fixture','clean')
            self.assertFalse((root/'runs').exists())

    def test_official_loader_multisource_and_signature_without_llm(self):
        upstream=Path(read(LAB/'configs/environment.json')['upstream_path'])
        sys.path.insert(0,str(upstream))
        from AutoSkill4Doc import extract_from_doc
        from AutoSkill4Doc.document.file_loader import load_file_units
        import inspect
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'one.md').write_text('# FIXTURE one\nStep one.\n')
            (root/'two.md').write_text('# FIXTURE two\nStep two.\n')
            units,_=load_file_units(str(root),max_files=2)
            self.assertEqual(len(units),2)
            cfg=read(LAB/'configs/generation/deepseek_flash.json')
            inspect.signature(extract_from_doc).bind(sdk=None,file_path=str(root),metadata={},
                registry_root=str(root/'store'),continue_on_error=False,dry_run=False,logger=None,**cfg['pipeline'])

    def test_new_adapter_changes_only_model_parameter(self):
        sys.path.insert(0,read(LAB/'configs/environment.json')['upstream_path'])
        from autoskill.llm.factory import build_llm
        from degradation_lab.provider_adapter import build
        cfg={'provider':'openai','model':'fixture-model','max_tokens':256}
        args={'system':'unchanged','user':'unchanged','temperature':0,'stream':False}
        baseline=build_llm(cfg)._build_payload(**args); adapted=build(cfg)._build_payload(**args)
        self.assertEqual(adapted.pop('thinking'),{'type':'disabled'}); self.assertEqual(adapted,baseline)

    def test_setup_failure_persisted_and_secret_redacted(self):
        sys.path.insert(0,read(LAB/'configs/environment.json')['upstream_path'])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); fixture_catalog(root)
            # Fault-injection test, not a real run or model response.
            with patch.dict('os.environ',{'FIXTURE_ONLY_KEY':'fixture-secret-only'}), \
                 patch('autoskill.AutoSkill',side_effect=RuntimeError('fixture-secret-only setup failure')):
                p,code=ExperimentRunner(root).run('case002_fixture','clean','fixture_setup_failure')
            self.assertEqual(code,1); self.assertEqual(read(p/'status.json')['state'],'FAILED')
            self.assertNotIn('fixture-secret-only',(p/'exception.json').read_text(encoding='utf-8'))
            self.assertEqual(read(p/'execution.json')['http_attempts'],0)
            self.assertTrue(all(sha256(p/rel)==h for rel,h in read(p/'artifact_manifest.json').items()))


if __name__=='__main__': unittest.main()
