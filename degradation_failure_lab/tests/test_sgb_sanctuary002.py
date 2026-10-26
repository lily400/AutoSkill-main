"""Deterministic Task003 contracts. Run in the pinned Linux control environment."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import read, write, inventory, sha256
from downstream_eval.p1 import fairness_identity
from downstream_eval.sgb import pilot
from downstream_eval.sgb.task_adapters.audited import sanctuary002 as task


class SanctuaryContracts(unittest.TestCase):
    def test_released_assets_and_source_are_bound(self):
        source = task.verify_assets()['source_document']
        self.assertEqual(source['sha256'], '7cfb819b60252946ec058d5430460b8795e93b4670381cd89efaf3d45ab66b0c')
        self.assertEqual(pilot.load_binding(LAB, task.TASK_ID)['case_id'], task.CASE_ID)

    def test_source_tampering_is_rejected(self):
        actual = task.sha256
        source = LAB / task.verify_assets()['source_document']['path']
        with patch.object(task, 'sha256', side_effect=lambda p: '0'*64 if Path(p)==source else actual(p)):
            with self.assertRaisesRegex(ValueError, 'source document changed'):
                task.verify_assets()

    def test_original_oracle_and_setup_contract(self):
        self.assertEqual(sha256(task.TASK/'oracle/eval.py'),
                         '57eb8902f1d0a5601bef71f1affaa944c2b946427c0e2e40e9a58c5d48f437eb')
        bundle = read(task.TASK/'oracle/testcases.json')
        self.assertEqual(bundle['setup_code'], task.SETUP)
        self.assertEqual(len(bundle['test_cases']), 8)

    def test_independently_audited_eight_expected_schedules(self):
        # Derived by hand from source p.8 + explicit trigger-turn recycling scope.
        gold = [('B',[1],['C','D','A'],{'A':5,'B':10},False),
                ('C',[3],[],{},False),
                ('B',[2,3],['C','D','A'],{'A':5,'B':10,'D':5},True),
                ('A',[1,2],['B','C','D'],{'A':10,'B':5,'D':5},False),
                ('D',[2],['A','B','C'],{'A':5,'B':5,'D':10},False),
                ('D',[1],['A','B','C'],{'B':5,'D':10},False),
                ('C',[1],['D','A','B'],{'C':10},False),
                ('B',[1],['C','D','A'],{'B':10},False)]
        for index,(case, (player,conditions,schedule,points,recycled)) in enumerate(zip(read(task.TASK/'oracle/testcases.json')['test_cases'],gold)):
            expected = case['expected_output']
            self.assertEqual(expected['end_trigger']['turn_index'],[1,2,1,0,3,3,2,1][index])
            self.assertEqual(expected['end_trigger']['player'],player)
            self.assertEqual(expected['end_trigger']['conditions_met'],conditions)
            self.assertEqual(expected['scheduled_turns_after_trigger'],schedule)
            self.assertEqual(expected['markers'],{p:points.get(p,0) for p in case['input']['players']})
            self.assertIs(expected['pile_recycled'],recycled)

    def test_task_does_not_supply_the_three_target_constants(self):
        instruction = (task.TASK/'instruction.md').read_text()
        for text in ['4 Conservation', '10-point', '5-point']:
            self.assertNotIn(text,instruction)
        self.assertIn('on the trigger turn when (1)/(2)',instruction)

    def test_paired_required_read_instructions_and_empty_control(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'test-pair'; output.mkdir()
            conditions={'NoSkill1':'NoSkill','CleanSkill1':'CleanSkill'}
            config=task.execution_config(output,'test-generator',conditions)
            template=read(LAB/'downstream_eval/configs/p1_smoke.json')
            write(output/'profile.json', dict(task_id=task.TASK_ID,experiment_id=output.name,
                trial_order=list(conditions),arms=list(conditions.values()),
                hard_http_budget={'database':str(output/'budget.sqlite3'),'order':list(conditions)},
                model=template['model'],budget=template['budget']))
            for label,condition in conditions.items():
                stage=output/'staged'/condition; stage.mkdir(parents=True)
                if condition=='CleanSkill':
                    (stage/'unit').mkdir(); (stage/'unit/SKILL.md').write_text('test fixture only')
                write(output/'manifests'/(label+'.json'),dict(arm=label,generator_run_id='test-generator',
                    staged_root=str(stage),files=inventory(stage),metadata={'unit':{}} if condition=='CleanSkill' else {}))
            configs=[task.configure(output,label,'paid',config).model_dump(mode='json',exclude_none=True) for label in conditions]
            self.assertEqual(fairness_identity(configs[0]),fairness_identity(configs[1]))
            self.assertEqual(configs[0]['agent']['skills'],[])
            self.assertEqual(configs[0]['extra_instruction_paths'],configs[1]['extra_instruction_paths'])
            self.assertIn('read the complete SKILL.md',(task.TASK/'runtime-note.md').read_text())

    def test_no_budget_is_granted_by_admission_or_status(self):
        with patch.object(task,'read',return_value={'status':'BLOCKED'}):
            with self.assertRaisesRegex(RuntimeError,'not been authorized'):
                task.check_authorization('generation')
        self.assertEqual(pilot.status(LAB,pilot.load_binding(LAB,task.TASK_ID),'unit-never-prepared')['status'],'NOT_PREPARED')

    def test_wrong_authorized_run_cannot_be_used(self):
        gate=deepcopy(read(task.GATE)); gate['status']='PASS'
        gate['requested_generation']['authorization_status']='AUTHORIZED'
        with patch.object(task,'read',return_value=gate):
            with self.assertRaisesRegex(RuntimeError,'identity/configuration'):
                task.check_authorization('generation','different-run')



class HistoricalProtection(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('task003_cli',LAB/'scripts/sgb/sanctuary002.py')
        self.cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.cli)

    def test_append_only_index_and_immutable_artifact_are_distinguished(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'runs').mkdir();(root/'results').mkdir()
            artifact=root/'runs/old.json';artifact.write_text('old bytes')
            index=root/'results/run_index.jsonl';index.write_text('first\n')
            with patch.object(self.cli,'LAB',root):
                self.cli.history('snapshot',create=True)
                index.write_text('first\nsecond\n')
                self.assertEqual(self.cli.history('snapshot')['status'],'PASS')
                artifact.write_text('changed')
                with self.assertRaisesRegex(ValueError,'Historical files changed'):
                    self.cli.history('snapshot')

    def test_existing_snapshot_cannot_be_reset(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(self.cli,'LAB',Path(directory)):
            self.cli.history('snapshot',create=True)
            with self.assertRaises(FileExistsError):
                self.cli.history('snapshot',create=True)



class CompletedReview(unittest.TestCase):
    def setUp(self):
        from test_framework import fixture_catalog, fixture_artifacts
        from degradation_lab.runner import ExperimentRunner
        from degradation_lab.evaluation import init_evaluation
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        upstream=self.root/'fixture-upstream'
        for name in ['AutoSkill4Doc/pipeline.py','autoskill/__init__.py']:
            p=upstream/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('# TEST ONLY; no generation code\n')
        self.env=patch.dict(os.environ,{'ANYTHING2SKILL_SOURCE':str(upstream),'SGB_AUDIT_ALLOW_PAID':'1'})
        self.env.start();self.addCleanup(self.env.stop)
        fixture_catalog(self.root)
        self.run=ExperimentRunner(self.root).prepare('case002_fixture','clean','unit-review',fixture=True)
        fixture_artifacts(self.run)
        self.path=init_evaluation(self.root,self.run.name,'pre_downstream')
        self.review=read(self.path);self.review['reviewer']='unit-reviewer'
        self.review['records'][0].update(status='correct',skill_ids=['skill-fixture'],
            generated_evidence=[{'skill_id':'skill-fixture','lines':[4]}],
            trace_refs=[{'stage':'skill','entity_id':'skill-fixture'}],notes='TEST ONLY: inspected final artifact')
        self.gate=self.root/'gate.json'
        approval=self.root/'approval.txt';approval.write_text('UNIT TEST ONLY. Not a real approval.')
        profile=self.root/'profile-template.json';write(profile,read(LAB/'downstream_eval/configs/p1_smoke.json'))
        cfg=read(self.root/'configs/shared.json')
        evidence={'file':'approval.txt','sha256':sha256(approval)}
        self.authorization={'status':'PASS','requested_generation':{'run_id':self.run.name,
            'case_id':'case002_fixture','condition_id':'clean','repeat':1,'authorization_status':'AUTHORIZED',
            'configuration':'configs/shared.json','configuration_sha256':sha256(self.root/'configs/shared.json'),
            'max_http_calls':cfg['max_http_calls'],'max_observed_total_tokens':cfg['max_observed_total_tokens'],
            'approval_evidence':evidence},'downstream':{'status':'PASS','authorization_status':'AUTHORIZED',
            'generator_run_id':self.run.name,'experiment_id':'unit-pair','profile_template':'profile-template.json',
            'profile_sha256':sha256(profile),'max_http_calls':12,'repeats_per_arm':1,
            'conditions':{'NoSkill1':'NoSkill','CleanSkill1':'CleanSkill'},'approval_evidence':evidence}}
        self.output=self.root/'unit-pair';write(self.output/'profile.json',dict(generator_run_id=self.run.name,
            experiment_id='unit-pair',conditions=self.authorization['downstream']['conditions']))
        write(self.output/'readiness.json',{'status':'PASS'})
        # Copy only task assets into a temporary engineering fixture; never stage a real Skill.
        self.assets=self.root/'task';self.original=self.root/'original'
        manifest=read(task.TASK/'source_manifest.json')
        for name in manifest['files']:
            target=self.assets/name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((task.TASK/name).read_bytes())
        for local,released in [('instruction.md','instruction.md'),('task.original.toml','task.toml'),
                              ('oracle/eval.py','tests/eval.py'),('oracle/testcases.json','tests/testcases.json')]:
            target=self.original/released;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((self.assets/local).read_bytes())
        source=read(self.root/'data/source.json')
        manifest.update(original_task='original',source_document={'path':source['local_path'],
            'sha256':source['sha256'],'manifest':'data/source.json','manifest_sha256':sha256(self.root/'data/source.json')})
        write(self.assets/'source_manifest.json',manifest)
        for name,value in [('LAB',self.root),('CASE_ID','case002_fixture'),('GATE',self.gate),('TASK',self.assets)]:
            p=patch.object(task,name,value);p.start();self.addCleanup(p.stop)
        self.save()

    def save(self):
        write(self.path,self.review)
        self.authorization['downstream']['quality_review_sha256']=sha256(self.path)
        write(self.gate,self.authorization)

    def enter_backend(self):
        with patch.object(pilot.runner,'execute_batch',return_value=0) as backend:
            self.assertEqual(task.paid_batch(self.output),0)
            backend.assert_called_once()

    def test_completed_verdicts_allow_measurement_and_keep_their_values(self):
        from degradation_lab.evaluation import validate_evaluation
        for status in ['correct','incorrect','uncertain']:
            with self.subTest(status=status):
                self.review['records'][0]['status']=status;self.save()
                self.assertEqual(validate_evaluation(self.root,self.review)['records'][0]['status'],status)
                self.assertEqual(task.check_review(self.run.name),self.path)
                self.enter_backend()
                self.assertEqual(read(self.path)['records'][0]['status'],status)

    def test_incorrect_addition_is_recorded_instead_of_vetoing_execution(self):
        addition=deepcopy(self.review['records'][0])
        addition.update(record_id='addition',judgment_scope='generated_addition',status='incorrect',
                        error_types=['unsupported_addition'],notes='TEST ONLY: unsupported statement')
        self.review['records'].append(addition);self.save();self.enter_backend()
        self.assertEqual(task.review_findings(self.review)[1]['semantic_finding'],'incorrect')

    def test_quality_cli_reports_the_defect_without_calling_it_correct(self):
        import io
        from contextlib import redirect_stdout
        p=importlib.util.spec_from_file_location('quality_cli',LAB/'scripts/sgb/sanctuary002.py')
        cli=importlib.util.module_from_spec(p);p.loader.exec_module(cli)
        self.review['records'][0]['status']='incorrect';self.save()
        stream=io.StringIO()
        with patch('sys.argv',['sanctuary002.py','quality','--generator-run',self.run.name]),redirect_stdout(stream):
            self.assertEqual(cli.main(),0)
        value=json.loads(stream.getvalue())
        self.assertEqual(value['review_status'],'reviewed')
        self.assertEqual(value['semantic_findings'][0]['status'],'incorrect')
        self.assertEqual(value['model_calls'],0)

    def test_omission_needs_inspection_provenance_not_a_nonexistent_body_anchor(self):
        p=self.root/'inspection.json'
        write(p,{'test_only':True,'inspected':{'skill-fixture':sha256(self.run/'SkillBank/Users/fixture-user/fixture-skill/SKILL.md')},
                 'finding':'Expected --flag absent from the inspected final body'})
        self.review['provenance']={'file':'inspection.json','sha256':sha256(p)}
        self.review['records'][0].update(status='incorrect',error_types=['rule_omission'],
            skill_ids=[],generated_evidence=[],trace_refs=[],notes='Expected source rule absent; inspected complete final body')
        self.save();self.enter_backend()
        self.assertEqual(task.review_findings(self.review)[0]['semantic_finding'],'omitted')
        self.review['provenance']={};self.save()
        with self.assertRaisesRegex(RuntimeError,'inspection provenance'):task.check_review(self.run.name)

    def test_uncertain_can_have_no_final_anchor_but_unreviewed_or_deleted_rule_cannot_pass(self):
        record=self.review['records'][0]
        record.update(status='uncertain',skill_ids=[],generated_evidence=[],trace_refs=[],notes='Inspected but mapping remains ambiguous')
        self.save();self.enter_backend()
        record['status']='unreviewed';self.save()
        with self.assertRaises(RuntimeError):task.check_review(self.run.name)
        self.review['records']=[dict(record,judgment_scope='generated_addition',status='uncertain')];self.save()
        with self.assertRaises(RuntimeError):task.check_review(self.run.name)

    def test_review_identity_and_source_hash_are_still_enforced(self):
        from test_framework import fixture_artifacts
        from degradation_lab.runner import ExperimentRunner
        other=ExperimentRunner(self.root).prepare('case002_fixture','clean','another-run',fixture=True)
        fixture_artifacts(other)
        self.review['run_id']=other.name;self.save()
        with self.assertRaises(ValueError):task.check_review(self.run.name)
        self.review['run_id']=self.run.name;self.save()
        source=self.root/'data/raw_sources/fixture/source.md';source.write_text('changed')
        with self.assertRaises(ValueError):task.check_review(self.run.name)

    def test_review_and_approval_hash_mismatch_still_block_before_backend(self):
        for changed in ['review','approval','config']:
            with self.subTest(changed=changed),patch.object(pilot.runner,'execute_batch') as backend:
                if changed=='review':
                    self.review['records'][0]['notes']='changed after approval';write(self.path,self.review)
                elif changed=='approval':(self.root/'approval.txt').write_text('tampered')
                else:(self.root/'configs/shared.json').write_text('{}')
                with self.assertRaises((ValueError,RuntimeError)):task.paid_batch(self.output)
                backend.assert_not_called()
                if changed=='review':self.save()

    def test_valid_review_does_not_bypass_asset_integrity(self):
        task.verify_assets()
        with patch.object(pilot.runner,'execute_batch') as backend:
            (self.assets/'instruction.md').write_text('tampered')
            with self.assertRaises(ValueError):task.paid_batch(self.output)
            backend.assert_not_called()


class ReportStates(unittest.TestCase):
    def setUp(self):
        from test_attribution import OfflineAttribution
        self.fixture=OfflineAttribution();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.root=self.fixture.root;self.output=self.fixture.run
        p=importlib.util.spec_from_file_location('task003_report',LAB/'scripts/sgb/sanctuary002.py')
        self.cli=importlib.util.module_from_spec(p);p.loader.exec_module(self.cli)
        self.binding={'task_id':'task','conditions':{'NoSkill1':'NoSkill','CleanSkill1':'CleanSkill'},'expected_oracle_tests':1}
        self.fixture.profile['experiment_id']='r1';write(self.output/'profile.json',self.fixture.profile)
        write(self.root/'cases/sgb/case001_test/rules.json',{'rules':[{'rule_id':'parent'}]})
        self.review=self.root/'evaluations/case001_test/clean/g1/pre_downstream.json'
        self.stub=SimpleNamespace(TASK_ID='task',CASE_ID='case001_test',GATE=self.root/'gate.json',
            check_review=lambda _:self.review,review_findings=lambda review:[],execution_config=lambda *args:None,
            verify_assets=lambda:{'source_document':{'sha256':'0'*64},'files':{'oracle/eval.py':'b'*64}})
        self.patchers=[patch.object(self.cli,'LAB',self.root),patch.object(pilot,'load_binding',return_value=self.binding)]
        for p in self.patchers:p.start();self.addCleanup(p.stop)

    def rule(self,stages=None):
        from downstream_eval.sgb.attribution_contract import STAGES
        return dict(rule_id='atom',parent_rule_id='parent',generator_run_id='g1',claim='TEST ONLY',
            reviewer='unit',review_status='reviewed',stages=stages or [dict(stage=s,status='unknown',evidence_ids=[],rationale='Missing') for s in STAGES],
            downstream_links=[dict(side='target',assertions=['ftp'],oracle_not_covered=False,skill_id='one',
                                  skill_lines=[7],action_event=1,interpretation='Synthetic anchor')])

    def report(self,write_spec=True):
        if write_spec:write(self.root/'configs/attribution/r1.json',self.fixture.spec)
        self.fixture.freeze()
        self.cli.baseline_report(self.stub,'g1','r1')
        return read(self.root/'results/sgb/baselines/r1/baseline.json')

    def test_no_body_still_has_completed_execution_and_valid_failure_scores(self):
        observer=self.output/'trials/cleanskill1/p1-observer'
        self.fixture.event(observer,'model-requests',dict(mode='paid',time=1,messages=[dict(role='user',content=self.fixture.index)]))
        write(observer/'p1-summary.json',dict(mode='paid',model_read_ids=[],controlled_probe_read_ids=[]))
        self.fixture.spec['rules']=[self.rule()]
        value=self.report()
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['skill_usage_status']['CleanSkill1'],'INDEX_ONLY_OBSERVED')
        self.assertEqual(value['task_success'],{'NoSkill1':False,'CleanSkill1':False})
        self.assertEqual(value['attribution_status'],'insufficient_evidence')
        self.assertNotIn('status',value)

    def test_missing_stages_do_not_change_execution_completion(self):
        self.fixture.spec['rules']=[self.rule([dict(stage='source',status='unknown',evidence_ids=[],rationale='Missing')])]
        value=self.report()
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['attribution_status'],'insufficient_evidence')

    def test_all_unknown_stage_names_do_not_establish_attribution(self):
        self.fixture.spec['rules']=[self.rule()];value=self.report()
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['skill_usage_status']['CleanSkill1'],'BODY_CONTEXT_CONFIRMED')
        self.assertEqual(value['attribution_status'],'insufficient_evidence')
        self.assertEqual(value['task_difference'],'both_failed')
        self.assertEqual(value['attribution_details']['claims'],[])

    def test_body_after_action_does_not_become_causal_reliance_or_incomplete_execution(self):
        observer=self.output/'trials/cleanskill1/p1-observer'
        self.fixture.event(observer,'model-requests',dict(mode='paid',time=4,
            messages=[dict(role='user',content=self.fixture.index+self.fixture.body)]))
        self.fixture.event(observer,'model-http',dict(logical_request_number=1,http_status=200,time=5))
        self.fixture.spec['rules']=[self.rule()];value=self.report()
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['skill_usage_status']['CleanSkill1'],'BODY_CONTEXT_CONFIRMED')
        self.assertIs(value['attribution_details']['rule_reviews'][0]['downstream_links'][0]['delivery']['before_action'],False)
        self.assertEqual(value['attribution_details']['claims'],[])

    def verified_rule(self):
        from downstream_eval.sgb.attribution_contract import STAGES
        entities={'source':{'doc_id':'doc','text':'Use True for FTP'},
            'window':{'window_id':'w','doc_id':'doc','text':'Use True for FTP'},
            'support':{'support_id':'s','metadata':{'window_id':'w'},'excerpt':'Use True for FTP'},
            'draft':{'draft_id':'d','support_ids':['s']},
            'spec':{'skill_id':'one','metadata':{'source_draft_ids':['d']}},
            'registered':{'skill_id':'one'},'skill':{'skill_id':'one','body':'Use True for FTP'}}
        path=self.fixture.gen/'stage-entities.json';write(path,entities)
        manifest=inventory(self.fixture.gen);manifest.pop('artifact_manifest.json')
        write(self.fixture.gen/'artifact_manifest.json',manifest)
        evidence=[dict(evidence_id=s,artifact_path=path.relative_to(self.root).as_posix(),artifact_sha256=sha256(path),
            run_id='g1',stage=s,entity_id={'source':'doc','window':'w','support':'s','draft':'d',
                'spec':'one','registered':'one','skill':'one'}[s],
            locator=dict(kind='json_pointer',value='/'+s,coordinate_space='artifact'),
            claim_status='observed',claim='TEST ONLY stage observation',missing_reason=None) for s in STAGES]
        self.fixture.spec['evidence']=evidence
        self.fixture.spec['rules']=[self.rule([dict(stage=s,status='preserved',evidence_ids=[s],rationale='TEST ONLY') for s in STAGES])]

    def test_reviewed_stage_evidence_does_not_automatically_create_causal_claims(self):
        self.verified_rule()
        value=self.report()
        self.assertEqual(value['attribution_status'],'reviewed')
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['attribution_details']['claims'],[])

    def test_verified_upstream_trace_without_downstream_mapping_remains_insufficient(self):
        self.verified_rule();self.fixture.spec['rules'][0]['downstream_links']=[]
        value=self.report()
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['attribution_status'],'insufficient_evidence')

    def test_missing_review_analysis_and_export_are_reported_without_inventing_results(self):
        value=self.report(write_spec=False)
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['upstream_review_status'],'missing')
        self.assertEqual(value['attribution_status'],'pending_review')
        self.assertGreaterEqual(len(value['missing_evidence']),4)

    def test_missing_trial_is_partial_and_its_score_is_null(self):
        (self.output/'outcomes/CleanSkill1/result.json').unlink()
        value=self.report()
        self.assertEqual(value['experiment_execution_status'],'partial')
        self.assertIsNone(value['task_success']['CleanSkill1'])
        self.assertIs(value['task_success']['NoSkill1'],False)
        self.assertEqual(value['attribution_status'],'not_comparable')

    def test_no_started_trials_is_not_started(self):
        import shutil
        shutil.rmtree(self.output/'trials');shutil.rmtree(self.output/'outcomes')
        value=self.report()
        self.assertEqual(value['experiment_execution_status'],'not_started')
        self.assertEqual(value['task_success'],{'NoSkill1':None,'CleanSkill1':None})

    def test_missing_declared_control_does_not_erase_completed_trials(self):
        self.fixture.spec['reference']=None;value=self.report()
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['comparability'],'unknown')
        self.assertEqual(value['attribution_status'],'not_comparable')
        self.assertEqual(value['task_difference'],'unresolved')

    def test_missing_control_result_is_not_filled_from_another_run(self):
        (self.output/'outcomes/NoSkill1/result.json').unlink()
        value=self.report()
        self.assertEqual(value['experiment_execution_status'],'partial')
        self.assertIsNone(value['task_success']['NoSkill1'])
        self.assertIs(value['task_success']['CleanSkill1'],False)
        self.assertEqual(value['attribution_status'],'not_comparable')

    def test_different_models_are_completed_but_not_comparable(self):
        path=self.output/'configs/CleanSkill1.json';config=read(path)
        config['agent']['model_name']='another-model';write(path,config)
        value=self.report()
        self.assertEqual(value['experiment_execution_status'],'completed')
        self.assertEqual(value['comparability'],'ineligible')
        self.assertEqual(value['attribution_status'],'not_comparable')

    def test_missing_profile_can_produce_partial_report(self):
        self.fixture.freeze();(self.output/'profile.json').unlink()
        # Do not refreeze away the missing required evidence.
        write(self.root/'configs/attribution/r1.json',self.fixture.spec)
        self.cli.baseline_report(self.stub,'g1','r1')
        value=read(self.root/'results/sgb/baselines/r1/baseline.json')
        self.assertEqual(value['experiment_execution_status'],'partial')
        self.assertIn('runs/eval/sgb/task/r1/profile.json',value['missing_evidence'])

    def test_frozen_hash_conflict_rejects_instead_of_becoming_partial(self):
        self.fixture.freeze();(self.output/'profile.json').write_text('{}')
        with self.assertRaises(ValueError):self.cli.baseline_report(self.stub,'g1','r1')
        self.assertFalse((self.root/'results/sgb/baselines/r1').exists())

    def test_candidate_hash_conflict_is_not_downgraded_to_missing_evidence(self):
        (self.output/'trials/cleanskill1/submission-export/agent_output.py').write_text('tampered')
        with self.assertRaisesRegex(ValueError,'Submitted bytes disagree'):self.report()

    def test_bound_review_hash_conflict_is_rejected(self):
        write(self.review,{'records':[]})
        write(self.stub.GATE,{'downstream':{'experiment_id':'r1','generator_run_id':'g1',
                                          'quality_review_sha256':'0'*64}})
        with self.assertRaisesRegex(ValueError,'Review hash differs'):self.report()

    def test_wrong_oracle_is_rejected(self):
        path=self.output/'outcomes/CleanSkill1/result.json';value=read(path)
        value['oracle']['oracle_sha256']='c'*64;write(path,value)
        with self.assertRaisesRegex(ValueError,'another Oracle'):self.report()

    def test_incomplete_native_record_does_not_falsify_an_existing_valid_score(self):
        path=self.output/'outcomes/CleanSkill1/native.json';native=read(path)
        native['finished_at']=None;write(path,native)
        value=self.report()
        self.assertEqual(value['experiment_execution_status'],'partial')
        self.assertIs(value['task_success']['CleanSkill1'],False)
        self.assertEqual(value['task_difference'],'unresolved')

    def test_offline_fixture_score_cannot_become_a_real_agent_result(self):
        path=self.output/'outcomes/CleanSkill1/result.json';value=read(path)
        value['model_api_results']=False;write(path,value)
        result=self.report()
        self.assertEqual(result['experiment_execution_status'],'partial')
        self.assertIsNone(result['task_success']['CleanSkill1'])
        self.assertEqual(result['task_difference'],'unresolved')

    def test_score_from_another_task_is_rejected_even_with_same_generic_oracle(self):
        path=self.output/'outcomes/CleanSkill1/result.json';value=read(path)
        value['oracle']['task_id']='foreign-domain-task';write(path,value)
        with self.assertRaisesRegex(ValueError,'another task'):self.report()

    def test_source_rule_evidence_hash_conflict_is_not_hidden_by_partial_reporting(self):
        path=self.fixture.gen/'rules.json'
        self.fixture.spec['evidence']=[dict(evidence_id='source',artifact_path=path.relative_to(self.root).as_posix(),
            artifact_sha256='0'*64,run_id='g1',stage='source',entity_id=None,
            locator=dict(kind='json_pointer',value='/rules/0',coordinate_space='artifact'),
            claim_status='observed',claim='TEST ONLY',missing_reason=None)]
        with self.assertRaisesRegex(ValueError,'Evidence hash mismatch'):self.report()

    def test_generation_source_hash_conflict_is_rejected(self):
        (self.fixture.gen/'config.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'Generation/source integrity'):self.report()

    def test_foreign_trial_reference_is_not_used_to_fill_a_pair(self):
        self.fixture.spec['reference']['run_path']='runs/eval/sgb/task/foreign'
        with self.assertRaisesRegex(ValueError,'another batch'):self.report()

    def test_existing_report_cannot_be_overwritten(self):
        self.report()
        with self.assertRaises(FileExistsError):self.cli.baseline_report(self.stub,'g1','r1')


if __name__=='__main__':
    unittest.main()
