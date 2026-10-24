import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(LAB),str(LAB/'src')]
from degradation_lab.catalog import CaseManager
from degradation_lab.artifacts import run_refs,resolve_run
from degradation_lab.io import inventory,read,sha256,write,check_windows_run_path
from degradation_lab.layout import case_paths,generation_path
from degradation_lab.runner import ExperimentRunner
from degradation_lab.schema import check
from degradation_lab.sgb import CONFIG,REGISTRY,REVISION,descriptor,load_registry,audit_registry,selected_tasks,import_snapshot
from downstream_eval.sgb import plan,prepare,aggregate
from downstream_eval.scoring.results import trial_record,summarize
from test_framework import fixture_catalog,fixture_artifacts


def registry_fixture(root):
    """Invented records only; no claim that this fixture represents real SGB tasks."""
    snapshot=root/'.external/skillgenbench/fixture'
    write(snapshot/'task.json',{'fixture_only':True})
    write(snapshot/'snapshot_manifest.json',{'revision':REVISION,'files':{'task.json':sha256(snapshot/'task.json')}})
    rows=[]
    for n in range(187):
        rows.append({'task_key':f'fixture-{n}','original_task_id':f'fixture-task-{n}',
            'source_type':'code_repo','source_status':'NO_TASK_LOCAL_DOCUMENTS','research_fit':'UNREVIEWED',
            'source_bundle_id':None,'generation_case_id':None,'sources':[],'official_assets':{'task.json':sha256(snapshot/'task.json')},
            'official_task':{'submission':{'kind':'script'},'runtime':{'docker_image':'fixture-only'}},
            'prior_evidence':None,'rule_evidence':None,'legacy_runs':[],
            'oracle_status':'STATIC_ONLY','runtime_status':'NOT_RUN','calibration_status':'NOT_RUN',
            'oracle_syntax_errors':[],'metadata':{'trailing_commas_removed_in_memory':1,'conflicts':[]},
            'execution_status':'BLOCKED','blockers':['fixture_not_runnable']})
    f=root/REGISTRY;f.parent.mkdir(parents=True)
    f.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
    write(root/CONFIG,{'revision':REVISION,'snapshot':snapshot.relative_to(root).as_posix(),
        'snapshot_manifest_sha256':sha256(snapshot/'snapshot_manifest.json'),'registry':REGISTRY,'registry_sha256':sha256(f)})
    return rows


class SGB(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='sgbtest-',dir=LAB.parent);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        net=patch('socket.socket.connect',side_effect=AssertionError('Tests forbid real network/model calls'))
        net.start();self.addCleanup(net.stop)

    def test_descriptor_only_removes_structural_trailing_commas(self):
        p=self.root/'task.json'
        p.write_text('{"text":"literal ,} and ,] and \\\"", "items":[1,2,],}',encoding='utf-8')
        before=p.read_bytes();value,count=descriptor(p)
        self.assertEqual(value,{'text':'literal ,} and ,] and "','items':[1,2]})
        self.assertEqual(count,2);self.assertEqual(p.read_bytes(),before)

    def test_duplicate_keys_and_other_malformed_json_are_rejected(self):
        p=self.root/'task.json'
        for text in ['{"a":1,"a":2,}','{"a": undefined,}','{"a":1 /* comment */,}']:
            p.write_text(text,encoding='utf-8')
            with self.assertRaises(ValueError):descriptor(p)

    def fixture_cases(self):
        fixture_catalog(self.root)
        source=self.root/'cases/case002_fixture';target=self.root/'cases/sgb/case002_fixture'
        target.parent.mkdir()
        self.assertTrue(source.resolve().is_relative_to(self.root.resolve()))
        self.assertTrue(target.resolve().is_relative_to(self.root.resolve()))
        source.rename(target)
        conditions=read(target/'conditions.json')
        for c in conditions['conditions']:
            c['input_manifest']=c['input_manifest'].replace('cases/case002_fixture/','cases/sgb/case002_fixture/')
        write(target/'conditions.json',conditions)

    def test_namespaced_case_and_historical_case_remain_discoverable(self):
        self.fixture_cases();manager=CaseManager(self.root)
        self.assertEqual(manager.list_cases(),['case001_fixture','case002_fixture'])
        for cid in manager.list_cases():manager.condition(manager.load(cid),'clean')
        self.assertEqual(generation_path(self.root,'case001_fixture','clean','r1'),self.root/'runs/case001_fixture/clean/r1')
        self.assertEqual(generation_path(self.root,'case002_fixture','clean','r2'),self.root/'runs/gen/sgb/case002_fixture/clean/r2')

    def test_duplicate_case_identity_across_layouts_is_rejected(self):
        self.fixture_cases();shutil.copytree(self.root/'cases/sgb/case002_fixture',self.root/'cases/case002_fixture')
        with self.assertRaisesRegex(ValueError,'Duplicate case_id'):case_paths(self.root)

    def test_new_and_old_runs_are_resolved_and_duplicate_run_ids_fail(self):
        for path,cid,rid in [('runs/case001_fixture/clean/r1','case001_fixture','r1'),
                             ('runs/gen/sgb/case002_fixture/clean/r2','case002_fixture','r2')]:
            write(self.root/path/'invocation.json',{'case_id':cid,'condition_id':'clean','run_id':rid})
        self.assertEqual(len(run_refs(self.root)),2)
        self.assertEqual(resolve_run(self.root,'r2')[1],self.root/'runs/gen/sgb/case002_fixture/clean/r2')
        write(self.root/'runs/case003_fixture/clean/r2/invocation.json',{'case_id':'case003_fixture','condition_id':'clean','run_id':'r2'})
        with self.assertRaisesRegex(ValueError,'Globally unique'):run_refs(self.root)

    def test_generation_snapshot_and_export_work_in_both_layouts(self):
        self.fixture_cases();runner=ExperimentRunner(self.root)
        for cid,rid in [('case001_fixture','fixture_old'),('case002_fixture','fixture_new')]:
            with patch('degradation_lab.runner.check_windows_run_path'):
                p=runner.prepare(cid,'clean',rid,fixture=True)
            fixture_artifacts(p)
            from degradation_lab.artifacts import inspect_run
            report,_=inspect_run(self.root,rid)
            self.assertEqual(report['execution_kind'],'fixture')
            self.assertEqual(read(p/'invocation.json')['case_id'],cid)

    def test_identifier_escape_is_rejected_before_creating_files(self):
        self.fixture_cases()
        for value in ['../escape','x/y','/absolute']:
            with self.assertRaises(ValueError):generation_path(self.root,'case002_fixture',value,'r1')

    def test_new_windows_layout_fits_current_project_for_standard_conditions(self):
        for condition in ['clean','related','irrelevant']:
            check_windows_run_path(Path(r'D:\AS\AutoSkill-main\degradation_failure_lab')/
                f'runs/gen/sgb/case024_sgb/{condition}/r1234567890',windows=True)

    def test_gate_blocks_paid_generation_before_credential_lookup(self):
        self.fixture_cases();p=self.root/'cases/sgb/case002_fixture/case.json';value=read(p)
        value['execution_gate']='gate.json';write(p,value);write(self.root/'gate.json',{'status':'BLOCKED'})
        with self.assertRaisesRegex(RuntimeError,'execution gate'):
            ExperimentRunner(self.root).run('case002_fixture','clean')
        self.assertFalse((self.root/'runs').exists())

    def test_static_registry_audit_does_not_claim_runtime_admission(self):
        registry_fixture(self.root);report=audit_registry(self.root)
        self.assertEqual(report['tasks'],187);self.assertEqual(report['executable_tasks'],0)
        self.assertEqual(report['agent_runs'],0);self.assertEqual(report['counts']['runtime_status'],{'NOT_RUN':187})

    def test_registry_and_snapshot_drift_are_rejected(self):
        registry_fixture(self.root)
        p=self.root/'.external/skillgenbench/fixture/task.json';p.write_text('changed')
        with self.assertRaisesRegex(ValueError,'Snapshot file drift'):audit_registry(self.root)
        (self.root/REGISTRY).write_text('changed')
        with self.assertRaisesRegex(ValueError,'Registry changed'):load_registry(self.root)

    def test_dataset_snapshot_does_not_claim_paper_version_verified(self):
        fixture_catalog(self.root);value=read(self.root/'data/source.json')
        value.update(classification='PUBLISHED_DATASET_SNAPSHOT',paper_snapshot_verified=False)
        check('source',value)

    def test_source_manifest_metadata_tampering_is_rejected(self):
        rows=registry_fixture(self.root)
        manifest=self.root/'data/manifests/source.json';write(manifest,{'fixture_only':True})
        rows[0]['sources']=[{'manifest':manifest.relative_to(self.root).as_posix(),'manifest_sha256':sha256(manifest)}]
        registry=self.root/REGISTRY
        registry.write_text(''.join(json.dumps(r)+'\n' for r in rows),encoding='utf-8')
        config=read(self.root/CONFIG);config['registry_sha256']=sha256(registry);write(self.root/CONFIG,config)
        write(manifest,{'fixture_only':'changed'})
        with self.assertRaisesRegex(ValueError,'Source manifest drift'):audit_registry(self.root)

    def test_unknown_task_selector_does_not_silently_select_nothing(self):
        registry_fixture(self.root)
        self.assertEqual(len(selected_tasks(self.root,['fixture-task-0'])[1]),1)
        with self.assertRaisesRegex(ValueError,'Unknown SGB task'):selected_tasks(self.root,['missing'])

    def test_preparation_is_nonexecuting_and_refuses_overwrite(self):
        registry_fixture(self.root);result=prepare(self.root,['fixture-task-0'],'prep1')
        self.assertEqual(result['tasks'],1);self.assertEqual(result['runnable'],0)
        self.assertFalse((self.root/'runs').exists())
        with self.assertRaises(FileExistsError):prepare(self.root,None,'prep1')
        with self.assertRaises(ValueError):prepare(self.root,None,'../escape')

    def test_empty_aggregate_never_invents_success(self):
        registry_fixture(self.root);result=aggregate(self.root,None,'a1')
        self.assertEqual(result['observed_trials'],0);self.assertEqual(result['conditions'],{})
        self.assertEqual(result['tasks_without_observed_trials_count'],187)

    def test_result_summary_is_mean_and_keeps_unscorable_separate(self):
        rows=[]
        for n,(success,infra) in enumerate([(False,True),(True,True),(False,True),(False,False)]):
            rows.append(trial_record({'label':str(n),'condition':'CleanSkill','task_success':success,'infra_ok':infra},'fixture','fixture'))
        group=summarize(rows)['conditions']['CleanSkill']
        self.assertEqual(group['success_rate_among_scorable'],1/3)
        self.assertEqual(group['unscorable'],1);self.assertEqual(group['observed'],4)
        with self.assertRaises(ValueError):trial_record({'label':'x','condition':'x','task_success':True},'fixture','fixture')


if __name__=='__main__':unittest.main()
