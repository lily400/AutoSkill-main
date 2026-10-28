"""No model, network, Docker or Agent execution."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import read, write, sha256, inventory
from downstream_eval.scoring.results import failure_kind, trial_record, summarize, completion_state
from downstream_eval.sgb import cohort, protocol


class FailureClassification(unittest.TestCase):
    def test_candidate_failure_overrides_legacy_infra_flag(self):
        for category in ('submission_missing', 'invalid_submission', 'candidate_timeout', 'oracle_assertion_failure'):
            self.assertEqual(failure_kind({'failure_category':category, 'infra_ok':False}), 'task_failure')

    def test_scorer_infra_is_not_a_candidate_failure(self):
        self.assertEqual(failure_kind({'failure_category':'none', 'infra_ok':False}), 'infrastructure_failure')
        self.assertEqual(failure_kind({'failure_category':'environment_error'}), 'infrastructure_failure')
        self.assertEqual(failure_kind({'failure_category':'candidate_protocol_error'}), 'infrastructure_failure')

    def test_unknown_http_is_never_free_budget_exhaustion(self):
        from downstream_eval.integration.request_budget import BudgetStop
        self.assertEqual(failure_kind({}, error=BudgetStop('Arm HTTP limit 6 reached'),
                         attempts=[{'state':'UNKNOWN'}]), 'infrastructure_failure')
        self.assertEqual(failure_kind({}, error=BudgetStop('Wire model or approved parameters changed')),
                         'infrastructure_failure')

    def test_budget_failure_stays_in_success_denominator(self):
        rows = [trial_record({'label':'N','condition':'NoSkill','task_success':False,'infra_ok':True,
                             'failure_kind':'budget_exhausted'}, 'task', 'evidence')]
        result = summarize(rows)['conditions']['NoSkill']
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['success_rate_among_scorable'], 0)


    def native_completion(self, flags):
        return {'agent_result':{'metadata':{'n_episodes':6,'all_messages':[
            {'role':'assistant','content':json.dumps({'task_complete':x})} for x in flags]}}}

    def test_false_completion_at_turn_limit_is_budget_exhaustion(self):
        self.assertEqual(failure_kind({'task_success':False},native_result=self.native_completion([False,False]),
                                      max_turns=6),'budget_exhausted')

    def test_one_completion_request_at_limit_is_not_confirmed(self):
        self.assertEqual(failure_kind({'task_success':True},native_result=self.native_completion([False,True]),
                                      max_turns=6),'budget_exhausted')

    def test_confirmed_completion_at_exact_limit_is_not_budget_exhaustion(self):
        self.assertEqual(failure_kind({'task_success':True},native_result=self.native_completion([True,True]),
                                      max_turns=6),'none')

    def test_missing_completion_evidence_is_not_inferred_from_six_calls(self):
        native={'agent_result':{'metadata':{'n_episodes':6,'all_messages':[]}}}
        self.assertEqual(completion_state(native,6)['status'],'unknown')
        self.assertEqual(failure_kind({'task_success':False},native_result=native,max_turns=6),'task_failure')

    def test_http_infrastructure_failure_precedes_turn_limit(self):
        self.assertEqual(failure_kind({},native_result=self.native_completion([False,False]),max_turns=6,
                                      attempts=[{'state':'UNKNOWN'}]),'infrastructure_failure')

    def test_fenced_completion_is_decoded_as_data(self):
        native=self.native_completion([False,False])
        native['agent_result']['metadata']['all_messages'][-1]['content']='```json\n{"task_complete": false}\n```'
        self.assertEqual(completion_state(native,6)['status'],'turn_limit_unconfirmed')


class CohortContracts(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup); self.root = Path(temp.name)
        for name in ('socket.socket.connect', 'socket.getaddrinfo', 'subprocess.Popen'):
            guard = patch(name, side_effect=AssertionError('Zero-model test')); guard.start(); self.addCleanup(guard.stop)
        write(self.root / protocol.CONFIG, read(LAB / protocol.CONFIG))
        note = read(LAB / protocol.CONFIG)['skill_read_instruction']
        (self.root / note).parent.mkdir(parents=True, exist_ok=True)
        (self.root / note).write_bytes((LAB / note).read_bytes())
        self.config = {'schema_version':1,'cohort_id':'fixture','protocol_id':'clean-pair-v1',
                       'history_index':'history.json','tasks':[{'task_id':'task'+str(n),'status':'NEEDS_WORK',
                                                              'pair':None} for n in range(10)]}
        write(self.root / 'cohort.json', self.config); write(self.root / 'history.json', {'files':{}})

    def test_pending_tasks_do_not_become_zero_scores(self):
        result = cohort.report(self.root, 'cohort.json')
        self.assertEqual((result['planned_tasks'],result['completed_pairs'],result['records']), (10,0,[]))
        self.assertEqual(result['conditions'], {})

    def test_duplicate_task_and_cross_task_pair_are_rejected(self):
        self.config['tasks'][1]['task_id'] = 'task0'; write(self.root / 'cohort.json', self.config)
        with self.assertRaisesRegex(ValueError, 'distinct'):cohort.load(self.root,'cohort.json')
        self.config['tasks'][1]['task_id'] = 'task1'
        self.config['tasks'][0].update(status='READY',pair={'run_path':'runs/eval/sgb/task1/pair',
            'reference_label':'NoSkill1','target_label':'CleanSkill1'})
        write(self.root / 'cohort.json', self.config)
        with self.assertRaisesRegex(ValueError, 'another task'):cohort.load(self.root,'cohort.json')

    def test_archive_alias_requires_matching_historical_hash(self):
        old = self.root / 'old.py'; old.write_text('old')
        digest = sha256(old); archive = self.root / 'archive.py'; archive.write_bytes(old.read_bytes())
        old.write_text('new'); write(self.root / 'history.json', {'files':{digest:['archive.py']}})
        self.assertEqual(cohort.trace(self.root, {'old.py':digest}, 'history.json')['status'], 'VERIFIED')
        archive.write_text('tampered')
        self.assertEqual(cohort.trace(self.root, {'old.py':digest}, 'history.json')['status'], 'INCOMPLETE')

    def partial_pair(self, generator='g1'):
        row=self.config['tasks'][0]
        row.update(status='READY',case_id='case1',generator_run_id='g1',
                   pair={'run_path':'runs/eval/sgb/task0/pair','reference_label':'NoSkill1','target_label':'CleanSkill1'})
        write(self.root/'cohort.json',self.config)
        write(self.root/row['pair']['run_path']/'profile.json',{'budget':{'max_requests':6}})
        write(self.root/row['pair']['run_path']/'batch_results.json',{'results':[{
            'label':'NoSkill1','condition':'NoSkill','model_api_results':True,
            'outcome_schema':2,'task_success':False,'infra_ok':True,'failure_kind':'budget_exhausted'}]})
        trial={'generator_run_id':generator,'case_id':'case1','integrity_issues':[],'scorable':True}
        with patch.object(cohort,'protocol_evidence',return_value={'status':'VERIFIED'}), \
             patch.object(cohort,'audit_pair',return_value={'comparability':'unknown',
                   'trials':{'reference':trial,'target':None}}):
            return cohort.report(self.root,'cohort.json')

    def test_partial_pair_keeps_observed_budget_failure_and_unstarted_arm(self):
        result=self.partial_pair()
        self.assertEqual(result['completed_pairs'],0)
        self.assertEqual(result['records'],[])
        self.assertEqual(result['tasks'][0]['execution'],'PARTIAL')
        self.assertEqual(result['observed_summary']['conditions']['NoSkill']['failed'],1)
        self.assertNotIn('CleanSkill',result['observed_summary']['conditions'])

    def test_formal_index_rejects_another_generation(self):
        result=self.partial_pair('different-generator')
        self.assertFalse(result['tasks'][0]['generation_identity_matches'])
        self.assertEqual(result['observed_records'],[])

    def test_protocol_rejects_equal_but_wrong_native_model(self):
        definition = read(self.root / protocol.CONFIG)
        profile = {k:definition[k] for k in ('protocol_id','model','budget','conditions','repeats_per_arm')}
        from downstream_eval.integration.network_isolation import environment_config
        raw = {'agent':{'model_name':'wrong','kwargs':{}}, 'extra_instruction_paths':[],
               'environment':environment_config(),'verifier':{'disable':True}}
        with self.assertRaisesRegex(ValueError, 'Native model'):
            protocol.validate(self.root, profile, {'NoSkill1':deepcopy(raw),'CleanSkill1':deepcopy(raw)})



    def score_revision_fixture(self, *, approved=True, wrong_candidate=False):
        run = self.root / 'runs/eval/sgb/task0/pair'
        destination = self.root / 'results/sgb/rescores/fixture'
        values = []; paths = {}
        for label, condition in [('NoSkill1','NoSkill'),('CleanSkill1','CleanSkill')]:
            counts = dict(tests=1,passed=0,failed=1,errors=0,skipped=0)
            raw = {'label':label,'condition':condition,'task_success':False,'infra_ok':True,
                   'model_api_results':True,'failure_kind':'task_failure','native_exception':None,
                   'http_attempts':2,'token_usage':{'input_tokens':123,'output_tokens':45},
                   'oracle':{'candidate_sha256':'a'*64,'oracle_sha256':'b'*64,'task_result':counts}}
            values.append(raw); source = run / 'outcomes' / label / 'result.json'; write(source,raw)
            grade = dict(raw['oracle'],task_success=True,infra_ok=True,model_calls=0,
                         candidate_binding_verified=True,failure_category='none',
                         task_result=dict(counts,passed=1,failed=0))
            if wrong_candidate:grade['candidate_sha256']='c'*64
            path = label+'/result.json'; paths[label]=path
            write(destination/path,{'label':label,'source_result_sha256':sha256(source),
                                    'oracle':grade,'scoring_revision':'approved-observer-v2'})
        write(run/'batch_results.json',{'results':values})
        manifest = destination/'manifest.json'
        write(manifest,{'schema_version':1,'user_approved':approved,'model_calls':0,
                        'protocol_id':'approved-observer-v2','run_path':run.relative_to(self.root).as_posix(),
                        'source_batch_results_sha256':sha256(run/'batch_results.json'),
                        'results':paths,'files':inventory(destination)})
        row={'pair':{'run_path':run.relative_to(self.root).as_posix()},
             'score_revision':{'path':manifest.relative_to(self.root).as_posix(),'sha256':sha256(manifest)}}
        return run, destination, row, values

    def test_approved_rescore_preserves_original_results_and_model_usage(self):
        run, destination, row, values = self.score_revision_fixture()
        before = sha256(run/'batch_results.json')
        revised = cohort.revised_values(self.root,run,row,values)
        self.assertTrue(all(x['task_success'] for x in revised))
        self.assertTrue(all(not x['task_success'] for x in values))
        self.assertEqual(before,sha256(run/'batch_results.json'))
        self.assertEqual(revised[0]['token_usage'],values[0]['token_usage'])
        self.assertEqual(revised[0]['http_attempts'],2)
        self.assertFalse(revised[0]['scoring_revision']['original_task_success'])

    def test_rescore_rejects_changed_evidence_bytes(self):
        run, destination, row, values = self.score_revision_fixture()
        (destination/'NoSkill1/result.json').write_text('tampered')
        with self.assertRaisesRegex(ValueError,'artifact hash'):
            cohort.revised_values(self.root,run,row,values)

    def test_rescore_rejects_another_candidate_even_with_valid_artifact_hash(self):
        run, destination, row, values = self.score_revision_fixture(wrong_candidate=True)
        with self.assertRaisesRegex(ValueError,'binding'):
            cohort.revised_values(self.root,run,row,values)

    def test_rescore_requires_explicit_user_approval(self):
        run, destination, row, values = self.score_revision_fixture(approved=False)
        with self.assertRaisesRegex(ValueError,'approval'):
            cohort.revised_values(self.root,run,row,values)


class TerminalAttribution(unittest.TestCase):
    def test_budget_failure_is_not_dropped_for_missing_junit(self):
        sys.path.insert(0, str(LAB / 'tests'))
        from test_attribution import OfflineAttribution
        fixture = OfflineAttribution(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        for label in ('NoSkill1','CleanSkill1'):
            p = fixture.run / 'configs' / (label + '.json'); c = read(p)
            c['agent']['import_path'] = 'fixture:Agent'; write(p,c)
        p = fixture.run / 'outcomes/NoSkill1/result.json'; result = read(p)
        result.update(outcome_schema=2, failure_kind='budget_exhausted', task_success=False, oracle={})
        write(p,result); fixture.freeze()
        manifest = read(fixture.run / 'execution_manifest.json')
        manifest['downstream_eval/tasks/task/oracle/eval.py'] = 'b'*64
        write(fixture.run / 'execution_manifest.json', manifest)
        result = fixture.audit()
        self.assertEqual(result['comparability'], 'eligible')
        self.assertEqual(result['trials']['reference']['execution_state'], 'budget_exhausted')
        self.assertFalse(result['trials']['reference']['task_success'])

    def test_candidate_preflight_failure_is_counted_without_completed_binding(self):
        sys.path.insert(0,str(LAB/'tests'))
        from test_attribution import OfflineAttribution
        for category in ('candidate_timeout','invalid_submission'):
            fixture=OfflineAttribution();fixture.setUp();self.addCleanup(fixture.doCleanups)
            p=fixture.run/'outcomes/NoSkill1/result.json'; result=read(p)
            result.update(outcome_schema=2,failure_kind='task_failure',task_success=False)
            result['oracle'].update(failure_category=category,candidate_binding_verified=False,
                infra_ok=False,task_result={'tests':0,'passed':0,'failed':0,'errors':0,'skipped':0})
            write(p,result)
            report=fixture.audit()
            self.assertTrue(report['trials']['reference']['scorable'])
            self.assertEqual(report['comparability'],'eligible')

    def test_normal_wrong_answer_still_requires_valid_junit(self):
        sys.path.insert(0, str(LAB / 'tests'))
        from test_attribution import OfflineAttribution
        fixture = OfflineAttribution(); fixture.setUp(); self.addCleanup(fixture.doCleanups)
        p=fixture.run/'outcomes/NoSkill1/result.json'; result=read(p)
        result.update(outcome_schema=2,failure_kind='task_failure');write(p,result)
        (fixture.run/'outcomes/NoSkill1/oracle/verdict/junit.xml').write_text('broken')
        self.assertFalse(fixture.audit()['trials']['reference']['scorable'])


class ConfiguredJSON(unittest.TestCase):
    def test_exact_generation_gate_blocks_before_credentials(self):
        from degradation_lab.runner import ExperimentRunner
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root/'gate.json',{'status':'BLOCKED'})
            runner=ExperimentRunner(root,cases=object())
            with patch.object(runner,'resolve',return_value=({'case':{'execution_gate':'gate.json'}},None,None,{})):
                with self.assertRaisesRegex(RuntimeError,'execution gate'):
                    runner.run('fixture-case','clean','unapproved-test-run')

    def test_original_json_assets_and_blocked_paid_entry(self):
        from downstream_eval.sgb.pilot import adapter_for, load_binding
        for tid in ('monitoring_gap_brief_classifier_001','capacity_aware_edge_admission_controller_006'):
            config=load_binding(LAB,tid); adapter=adapter_for(LAB,config)
            self.assertGreater(len(adapter.verify_assets()['files']),0)
            with tempfile.TemporaryDirectory() as d:
                write(Path(d)/'profile.json',{'generator_run_id':'never-paid','experiment_id':'never-paid'})
                with self.assertRaisesRegex(RuntimeError,'awaits exact downstream authorization'):
                    adapter.paid_batch(Path(d))

if __name__ == '__main__':unittest.main()
