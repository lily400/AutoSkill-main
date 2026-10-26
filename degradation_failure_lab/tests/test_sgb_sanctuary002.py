"""Deterministic Task003 contracts. Run in the pinned Linux control environment."""
from copy import deepcopy
import importlib.util
import json
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

    def test_incorrect_addition_blocks_even_when_target_rules_pass(self):
        rules=read(LAB/f'cases/sgb/{task.CASE_ID}/rules.json')['rules']
        review={'reviewer':'unit-reviewer','records':[{'rule_id':r['rule_id'],
            'judgment_scope':'rule_preservation','status':'correct','skill_ids':['unit'],
            'generated_evidence':[{'skill_id':'unit','lines':[1]}],
            'trace_refs':[{'stage':'skill','entity_id':'unit'}]} for r in rules]}
        with patch.object(task,'read',return_value=review), patch.object(task,'validate_evaluation',return_value=review):
            task.check_review('unit-generator')
            review['records'].append({'rule_id':rules[0]['rule_id'],
                'judgment_scope':'generated_addition','status':'incorrect'})
            with self.assertRaisesRegex(RuntimeError,'quality review'):
                task.check_review('unit-generator')


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

    def test_baseline_requires_target_rule_context_not_just_an_unrelated_body(self):
        from downstream_eval.sgb import attribution
        rules=read(LAB/f'cases/sgb/{task.CASE_ID}/rules.json')
        conditions={'NoSkill1':'NoSkill','CleanSkill1':'CleanSkill'}
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);quality=root/'quality.json';write(quality,{'fixture':True})
            write(root/f'cases/sgb/{task.CASE_ID}/rules.json',rules)
            stub=SimpleNamespace(TASK_ID=task.TASK_ID,CASE_ID=task.CASE_ID,check_review=lambda _:quality,
                verify_assets=lambda:{'source_document':{'sha256':'0'*64}},execution_config=lambda *args:None)
            for experiment,before_action,expected in [('missing',None,'INCOMPLETE_REVIEW_OR_EXECUTION'),('confirmed',True,'COMPLETE')]:
                output=root/'runs/eval/sgb'/task.TASK_ID/experiment
                write(output/'profile.json',{'task_id':task.TASK_ID,'generator_run_id':'unit-generator'})
                for label in conditions:
                    write(output/'outcomes'/label/'result.json',{'task_success':True,'infra_ok':True,
                        'oracle':{'task_result':{'tests':8,'passed':8}},'http_attempts':1,'token_usage':{}})
                write(root/'configs/attribution'/(experiment+'.json'),{'fixture':True})
                saved=root/'results/sgb/attributions'/(experiment+'-v1')/'report.json'
                write(saved,{'spec_digest':'unit'});saved.with_suffix('.md').write_text('unit fixture')
                usage={'counts':{'full_body_in_successful_model_request':1}}
                write(root/'results/sgb/analyses'/experiment/'analysis.json',
                    {'experiment_id':experiment,'results':[{'label':'CleanSkill1','skill_usage':usage}]})
                reviewed=[{'rule_id':r['rule_id'],'review_status':'reviewed',
                    'stages':[{'stage':s} for s in ['source','window','support','draft','spec','registered','skill']],
                    'downstream_links':[{'side':'target','delivery':{'before_action':before_action}}]} for r in rules['rules']]
                pair={'spec_digest':'unit','comparability':'eligible','task_difference':'both_passed','rule_reviews':reviewed}
                with patch.object(self.cli,'LAB',root),patch.object(attribution,'audit_pair',return_value=pair), \
                     patch.object(pilot,'load_binding',return_value={'conditions':conditions}), \
                     patch.object(pilot,'status',return_value={'status':'COMPLETED','http_attempts':2}), \
                     patch.object(pilot.runner,'verify_frozen'),patch.object(pilot.runner,'verify_ledger'):
                    result=self.cli.baseline_report(stub,'unit-generator',experiment)
                    self.assertEqual(result['status'],expected)


if __name__=='__main__':
    unittest.main()
