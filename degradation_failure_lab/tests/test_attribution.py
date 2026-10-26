"""Offline fixtures only. No Agent, model, container or Oracle execution."""
from copy import deepcopy
from difflib import unified_diff
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import inventory, sha256, write
from downstream_eval.sgb.attribution import EvidenceFiles, audit_pair, classify, export_report
from downstream_eval.sgb.attribution_evidence import _completed_intervention, _pointer, rule_delivery


class OfflineAttribution(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.gen = self.root / 'runs/gen/sgb/case001_test/clean/g1'
        self.gen.mkdir(parents=True)
        write(self.gen/'invocation.json', dict(case_id='case001_test', condition_id='clean', run_id='g1'))
        write(self.gen/'config.json', {'model': 'fixture'})
        write(self.gen/'condition.json', dict(kind='clean', operator=None, parameters={}))
        write(self.gen/'upstream_before.json', {'core.py': 'a'*64})
        write(self.gen/'rules.json', {'rules': [{'rule_id': 'parent'}]})
        write(self.gen/'input_manifest.json', {'inputs': []})
        write(self.gen/'artifact_manifest.json', inventory(self.gen))
        self.run = self.root/'runs/eval/sgb/task/r1'
        self.profile = dict(task_id='task', model={'name':'fixture'}, budget={'requests':5},
                            frozen_agent_image_id='image', generator_run_id='g1',
                            conditions={'NoSkill1':'NoSkill','CleanSkill1':'CleanSkill'})
        write(self.run/'profile.json', self.profile)
        write(self.run/'skills_manifest.json', dict(generator_run_id='g1',case_id='case001_test',condition='clean'))
        write(self.run/'runtime_versions.json', {'agent': 'fixture'})
        write(self.run/'fairness.json', {'runtime': {'agent_image_id':'image', 'scorer_image_id':'scorer'}})
        self.body='---\nid: "one"\nname: One\ndescription: Test\n---\n# Procedure\nUse True for FTP.\n'
        skill=self.run/'staged/CleanSkill/one/SKILL.md';skill.parent.mkdir(parents=True);skill.write_text(self.body,encoding='utf-8')
        self.index='<available_skills><skill><name>One</name><description>Test</description><location>/harbor/skills/one/SKILL.md</location></skill></available_skills>'
        self.spec=dict(schema_version=1, analysis_id='test',pair_id='pair',task_id='task',comparison_kind='no_skill_clean',
            reference={'run_path':self.run.relative_to(self.root).as_posix(),'label':'NoSkill1'},
            target={'run_path':self.run.relative_to(self.root).as_posix(),'label':'CleanSkill1'},
            evidence=[],rules=[],claims=[],interventions=[])
        for label in ['NoSkill1','CleanSkill1']:
            clean=label.startswith('Clean');stage=self.run/('staged/CleanSkill' if clean else 'staged/NoSkill');stage.mkdir(exist_ok=True)
            write(self.run/'configs'/f'{label}.json',dict(trial_name=label.lower(),trials_dir=str(self.run/'trials'),
                task={'path':'/task'},agent={'skills':[str(stage)],'kwargs':{'p1_profile':str(self.run/'profile.json'),
                'p1_manifest':str(self.run/'manifests'/f'{label}.json')}},extra_instruction_paths=[]))
            write(self.run/'manifests'/f'{label}.json',dict(arm=label,generator_run_id='g1',staged_root=str(stage),
                files=inventory(stage),metadata={'one':{'name':'One','description':'Test'}} if clean else {}))
            trial=self.run/'trials'/label.lower();candidate=trial/'submission-export/agent_output.py'
            candidate.parent.mkdir(parents=True);candidate.write_text('value = 1\n',encoding='utf-8')
            write(self.run/'outcomes'/label/'native.json',dict(task_name='task',task_checksum='task-digest',
                agent_info={'name':'fixture','version':'1'},finished_at='2026-01-01',exception_info=None))
            observer=trial/'p1-observer';observer.mkdir(parents=True)
            self.event(observer,'installation',dict(status='PASS',installed_ids=['one'] if clean else [],
                discovered_ids=['one'] if clean else [],file_hashes=inventory(stage)))
            self.event(observer,'model-requests',dict(mode='paid',time=1,messages=[dict(role='user',content=self.index+self.body if clean else 'task')]))
            self.event(observer,'model-http',dict(logical_request_number=1,http_status=200,time=2))
            self.event(observer,'tool-actions',dict(actor='model_tool',stage='submitted',time=3))
            self.event(observer,'skill-reads',dict(actor='model_tool',skill_id='one' if clean else None,time=0.5))
            write(observer/'p1-summary.json',dict(mode='paid',model_read_ids=['one'] if clean else [],controlled_probe_read_ids=[]))
            self.score(label,False)
        self.freeze()

    def event(self,path,name,value):
        (path/('p1-'+name+'.jsonl')).write_text(json.dumps(value)+'\n',encoding='utf-8')

    def score(self,label,passed):
        candidate=self.run/'trials'/label.lower()/'submission-export/agent_output.py'
        oracle=dict(candidate_sha256=sha256(candidate),candidate_binding_verified=True,oracle_sha256='b'*64,
            infra_ok=True,task_result=dict(tests=1,passed=int(passed),failed=int(not passed),errors=0))
        write(self.run/'outcomes'/label/'result.json',dict(label=label,condition='CleanSkill' if label.startswith('Clean') else 'NoSkill',
            task_success=passed,infra_ok=True,model_api_results=True,oracle=oracle))
        p=self.run/'outcomes'/label/'oracle/verdict/junit.xml';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('<testsuite><testcase name="ftp">'+('' if passed else '<failure/>')+'</testcase></testsuite>',encoding='utf-8')

    def freeze(self):
        paths=[self.run/x for x in ['profile.json','skills_manifest.json','runtime_versions.json','fairness.json']]
        paths+=list((self.run/'configs').glob('*.json'))+list((self.run/'manifests').glob('*.json'))
        manifest={p.relative_to(self.root).as_posix():sha256(p) for p in paths if p.is_file()}
        manifest.update({'downstream_eval/agent.py':'a'*64,'downstream_eval/tasks/task/instruction.md':'c'*64})
        write(self.run/'execution_manifest.json',manifest)

    def copy_run(self, generator='g1'):
        previous=self.run;self.run=self.run.parent/'r2';shutil.copytree(previous,self.run)
        for p in [self.run/'profile.json',self.run/'skills_manifest.json',*list((self.run/'manifests').glob('*.json'))]:
            v=json.loads(p.read_text(encoding='utf-8'));v['generator_run_id']=generator
            if 'staged_root' in v:v['staged_root']=v['staged_root'].replace(str(previous),str(self.run))
            write(p,v)
        def relocate(value):
            if isinstance(value,str):return value.replace(str(previous),str(self.run))
            if isinstance(value,list):return [relocate(x) for x in value]
            if isinstance(value,dict):return {k:relocate(v) for k,v in value.items()}
            return value
        for p in (self.run/'configs').glob('*.json'):
            write(p,relocate(json.loads(p.read_text(encoding='utf-8'))))
        self.freeze()
        self.spec['reference']['label']='CleanSkill1'
        self.spec['target']['run_path']=self.run.relative_to(self.root).as_posix()
        return previous

    def audit(self):
        return audit_pair(self.root,self.spec)

    def evidence(self,filename='rules.json',stage='draft'):
        p=self.gen/filename
        entry=dict(evidence_id='E',artifact_path=p.relative_to(self.root).as_posix(),artifact_sha256=sha256(p),
            run_id='g1',stage=stage,entity_id=None,locator=dict(kind='json_pointer',value='/rules/0',coordinate_space='artifact'),
            claim_status='observed',claim='Fixture assertion',missing_reason=None)
        self.spec['evidence']=[entry]
        return entry

    def test_four_outcome_combinations_and_assertions(self):
        for a,b,expected in [(False,False,'both_failed'),(False,True,'possible_help'),(True,False,'possible_harm'),(True,True,'both_passed')]:
            with self.subTest(a=a,b=b):
                self.score('NoSkill1',a);self.score('CleanSkill1',b);r=self.audit()
                self.assertEqual(r['comparability'],'eligible');self.assertEqual(r['task_difference'],expected)
                self.assertEqual(r['assertion_differences'][0]['difference'],expected)

    def test_missing_arm_is_unknown(self):
        self.spec['reference']=None
        self.assertEqual(self.audit()['comparability'],'unknown');self.assertEqual(self.audit()['task_difference'],'unresolved')

    def test_missing_score_is_unresolved(self):
        (self.run/'outcomes/CleanSkill1/result.json').unlink()
        self.assertEqual(self.audit()['task_difference'],'unresolved')

    def test_environment_exception_is_unresolved(self):
        p=self.run/'outcomes/CleanSkill1/native.json';v=json.loads(p.read_text(encoding='utf-8'));v['exception_info']={'exception_type':'TransportError'};write(p,v)
        self.assertEqual(self.audit()['task_difference'],'unresolved')

    def test_oracle_binding_rejection_is_not_task_failure(self):
        p=self.run/'outcomes/CleanSkill1/result.json';v=json.loads(p.read_text(encoding='utf-8'));v['oracle']['candidate_binding_verified']=False;write(p,v)
        self.assertEqual(self.audit()['comparability'],'ineligible')

    def test_oracle_count_mismatch_is_unresolved(self):
        p=self.run/'outcomes/CleanSkill1/result.json';v=json.loads(p.read_text(encoding='utf-8'));v['oracle']['task_result']['tests']=9;write(p,v)
        self.assertEqual(self.audit()['task_difference'],'unresolved')

    def test_malformed_junit_is_unresolved(self):
        (self.run/'outcomes/CleanSkill1/oracle/verdict/junit.xml').write_text('broken',encoding='utf-8')
        self.assertEqual(self.audit()['task_difference'],'unresolved')

    def test_cross_arm_runtime_manifest_is_rejected_even_if_frozen(self):
        p=self.run/'configs/CleanSkill1.json';v=json.loads(p.read_text(encoding='utf-8'))
        v['agent']['kwargs']['p1_manifest']=str(self.run/'manifests/NoSkill1.json');write(p,v);self.freeze()
        self.assertEqual(self.audit()['comparability'],'ineligible')

    def test_empty_no_skill_install_list_is_valid(self):
        p=self.run/'configs/NoSkill1.json';v=json.loads(p.read_text(encoding='utf-8'))
        v['agent']['skills']=[];write(p,v);self.freeze()
        self.assertEqual(self.audit()['comparability'],'eligible')

    def test_frozen_config_tampering_rejected(self):
        p=self.run/'configs/CleanSkill1.json';v=json.loads(p.read_text(encoding='utf-8'));v['timeout_multiplier']=2;write(p,v)
        self.assertEqual(self.audit()['comparability'],'ineligible')

    def test_unknown_runtime_not_equal(self):
        (self.run/'fairness.json').unlink();self.freeze()
        # Use an explicit manifest with the missing file excluded.
        p=self.run/'execution_manifest.json';m=json.loads(p.read_text(encoding='utf-8'));m.pop((self.run/'fairness.json').relative_to(self.root).as_posix(),None);write(p,m)
        self.assertEqual(self.audit()['comparability'],'unknown')

    def test_evidence_tampering_rejected(self):
        e=self.evidence();e['artifact_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'hash mismatch'): self.audit()

    def test_wrong_entity_rejected(self):
        e=self.evidence();e['entity_id']='not-this-entity'
        with self.assertRaisesRegex(ValueError,'entity'): self.audit()

    def test_cross_run_evidence_rejected(self):
        e=self.evidence();e['run_id']='another-run'
        with self.assertRaisesRegex(ValueError,'another run'): self.audit()

    def test_missing_evidence_requires_unknown_and_reason(self):
        e=self.evidence();e.update(artifact_path=self.gen.relative_to(self.root).as_posix()+'/missing',artifact_sha256=None)
        with self.assertRaisesRegex(ValueError,'unknown status'): self.audit()
        e.update(claim_status='unknown',missing_reason='not recorded')
        self.assertEqual(self.audit()['review_evidence'][0]['verification'],'unknown')

    def test_delivery_requires_success_before_action_and_never_proves_use(self):
        trial=self.audit()['trials']['target'];files=EvidenceFiles(self.root)
        link=dict(skill_id='one',skill_lines=[7],action_event=1)
        result=rule_delivery(files,trial,link)
        self.assertTrue(result['before_action']);self.assertEqual(result['behavioral_use'],'UNKNOWN')
        observer=self.run/'trials/cleanskill1/p1-observer'
        self.event(observer,'tool-actions',dict(actor='model_tool',stage='submitted',time=0))
        self.assertFalse(rule_delivery(EvidenceFiles(self.root),trial,link)['before_action'])
        self.event(observer,'model-http',dict(logical_request_number=1,http_status=500,time=2))
        self.assertIsNone(rule_delivery(EvidenceFiles(self.root),trial,link)['before_action'])

    def test_probe_does_not_count(self):
        trial=self.audit()['trials']['target'];link=dict(skill_id='one',skill_lines=[7],action_event=1)
        observer=self.run/'trials/cleanskill1/p1-observer'
        write(observer/'p1-summary.json',dict(mode='probe',controlled_probe_read_ids=['one'],model_read_ids=[]))
        self.assertIsNone(rule_delivery(EvidenceFiles(self.root),trial,link)['before_action'])

    def test_body_text_in_index_or_access_only_after_action_is_not_delivery(self):
        trial=self.audit()['trials']['target'];link=dict(skill_id='one',skill_lines=[7],action_event=1)
        observer=self.run/'trials/cleanskill1/p1-observer'
        self.event(observer,'skill-reads',dict(actor='model_tool',skill_id='one',time=4))
        self.assertFalse(rule_delivery(EvidenceFiles(self.root),trial,link)['before_action'])
        self.event(observer,'skill-reads',dict(actor='model_tool',skill_id='one',time=0.5))
        self.event(observer,'model-requests',dict(mode='paid',time=1,messages=[dict(role='user',content='<available_skills>'+self.body+'</available_skills>')]))
        self.assertFalse(rule_delivery(EvidenceFiles(self.root),trial,link)['before_action'])
        (observer/'p1-model-requests.jsonl').unlink()
        self.assertIsNone(rule_delivery(EvidenceFiles(self.root),trial,link)['before_action'])

    def test_observed_causality_rejected(self):
        self.evidence()
        self.spec['claims']=[dict(claim_id='causal',rule_ids=[],scope='causal',status='observed',text='Unjustified',evidence_ids=['E'],
            downstream_category=None,candidate_causes=[],primary_cause=None,alternatives=[],missing_evidence=[],reviewer='test',intervention_ids=[])]
        with self.assertRaisesRegex(ValueError,'causation'): self.audit()

    def test_planned_intervention_cannot_support_causality(self):
        self.evidence()
        self.spec['rules']=[dict(rule_id='atomic',parent_rule_id='parent',generator_run_id='g1',claim='Fixture',reviewer='test',review_status='provisional',
            stages=[dict(stage='draft',status='omitted',evidence_ids=['E'],rationale='Fixture only')],downstream_links=[])]
        self.spec['interventions']=[dict(intervention_id='repair',version='1',status='planned',scope='skill',parent_evidence_id='E',patch_evidence_id=None,
            child_evidence_id=None,target_rule_ids=['atomic'],expected_effect='Improve',control=None,treatment=None)]
        self.spec['claims']=[dict(claim_id='causal',rule_ids=['atomic'],scope='causal',status='intervention_supported',text='Unjustified',evidence_ids=['E'],
            downstream_category=None,candidate_causes=[],primary_cause=None,alternatives=[],missing_evidence=[],reviewer='test',intervention_ids=['repair'])]
        with self.assertRaisesRegex(ValueError,'completed intervention'): self.audit()

    def test_same_bytes_cannot_be_degraded(self):
        g2=self.gen.parent.parent/'degraded/g2';g2.mkdir(parents=True)
        for name in ['config.json','rules.json','upstream_before.json','input_manifest.json']:
            (g2/name).write_bytes((self.gen/name).read_bytes())
        write(g2/'invocation.json',dict(case_id='case001_test',condition_id='degraded',run_id='g2'))
        write(g2/'condition.json',dict(kind='degraded',operator='drop',parameters={}))
        write(g2/'artifact_manifest.json',inventory(g2))
        self.spec['comparison_kind']='clean_degraded';self.spec['reference']['label']='CleanSkill1'
        # Same input bytes (including an empty input set) must never count as degradation.
        from unittest.mock import patch
        from downstream_eval.sgb import attribution
        original=attribution._load_trial
        calls=[]
        def altered(files,ref,task):
            t=original(files,ref,task);calls.append(t)
            if len(calls)==2:t['generator_run_id']='g2'
            return t
        with patch.object(attribution,'_load_trial',side_effect=altered):r=self.audit()
        self.assertEqual(r['comparability'],'ineligible')
        self.assertTrue(any(c['field']=='input_changed' and c['status']=='different' for c in r['control_checks']))

    def test_clean_degraded_pair_binds_original_and_changed_input(self):
        original=self.root/'data/source.md';original.parent.mkdir();original.write_text('FTP defaults True.\n',encoding='utf-8')
        source_input=self.gen/'input.md';source_input.write_bytes(original.read_bytes())
        item=dict(source_id='source',source_sha256=sha256(original),original_path='data/source.md',path='input.md',sha256=sha256(source_input))
        write(self.gen/'input_manifest.json',{'inputs':[item]})
        write(self.gen/'artifact_manifest.json',{k:v for k,v in inventory(self.gen).items() if k!='artifact_manifest.json'})
        g2=self.gen.parent.parent/'degraded/g2';shutil.copytree(self.gen,g2)
        write(g2/'invocation.json',dict(case_id='case001_test',condition_id='degraded',run_id='g2'))
        write(g2/'condition.json',dict(kind='degraded',operator='drop-rule',parameters={'rule':'FTP'}))
        (g2/'input.md').write_text('FTP.\n',encoding='utf-8');item['sha256']=sha256(g2/'input.md')
        write(g2/'input_manifest.json',{'inputs':[item]})
        write(g2/'artifact_manifest.json',{k:v for k,v in inventory(g2).items() if k!='artifact_manifest.json'})
        self.copy_run('g2');self.spec['comparison_kind']='clean_degraded'
        r=self.audit();self.assertEqual(r['comparability'],'eligible');self.assertEqual(r['task_difference'],'both_failed')
        self.assertEqual(r['trials']['target']['document_condition'],'degraded')
        self.assertNotEqual(r['generations']['g1']['source_inputs']['inputs'][0]['sha256'],r['generations']['g2']['source_inputs']['inputs'][0]['sha256'])

    def test_completed_skill_intervention_keeps_rule_version_and_support_scope(self):
        previous=self.copy_run();self.spec['comparison_kind']='intervention'
        before=previous/'staged/CleanSkill/one/SKILL.md';after=self.run/'staged/CleanSkill/one/SKILL.md'
        after.write_text(self.body.replace('Use True','Default to True'),encoding='utf-8')
        p=self.run/'manifests/CleanSkill1.json';v=json.loads(p.read_text(encoding='utf-8'));v['files']=inventory(after.parent.parent);write(p,v)
        self.event(self.run/'trials/cleanskill1/p1-observer','installation',dict(status='PASS',installed_ids=['one'],discovered_ids=['one'],file_hashes=v['files']))
        self.score('CleanSkill1',True);self.freeze()
        patch=self.run/'patch.diff'
        patch.write_text(''.join(unified_diff(before.read_text(encoding='utf-8').splitlines(True),after.read_text(encoding='utf-8').splitlines(True),fromfile='before',tofile='after')),encoding='utf-8')
        self.spec['evidence']=[dict(evidence_id=k,artifact_path=p.relative_to(self.root).as_posix(),artifact_sha256=sha256(p),run_id=run,
            stage='skill' if k!='patch' else 'intervention',entity_id='one' if k!='patch' else None,
            locator=dict(kind='file',value=None,coordinate_space='skill_body' if k!='patch' else 'artifact'),
            claim_status='observed',claim='Fixture change',missing_reason=None) for k,p,run in [('before',before,'r1'),('after',after,'r2'),('patch',patch,'r2')]]
        self.spec['rules']=[dict(rule_id='atomic',parent_rule_id='parent',generator_run_id='g1',intervention_id='repair',claim='Fixture rule',reviewer='test',review_status='provisional',
            stages=[dict(stage='skill',status='preserved',evidence_ids=['after'],rationale='Fixture review')],
            downstream_links=[dict(side='target',assertions=['ftp'],oracle_not_covered=False,skill_id='one',skill_lines=[],action_event=None,interpretation='Fixture')])]
        self.spec['interventions']=[dict(intervention_id='repair',version='1',status='completed',scope='skill',parent_evidence_id='before',patch_evidence_id='patch',child_evidence_id='after',target_rule_ids=['atomic'],expected_effect='Improve',control=self.spec['reference'],treatment=self.spec['target'])]
        self.spec['claims']=[dict(claim_id='causal',rule_ids=['atomic'],scope='causal',status='intervention_supported',text='Fixture measured change',evidence_ids=['before','after','patch'],downstream_category=None,candidate_causes=[],primary_cause=None,alternatives=[],missing_evidence=[],reviewer='test',intervention_ids=['repair'])]
        r=self.audit();self.assertEqual(r['comparability'],'eligible');self.assertEqual(r['task_difference'],'possible_help')
        self.assertEqual(r['claims'][0]['intervention_scopes'],['skill'])

    def test_completed_patch_must_match_bound_artifacts(self):
        report=self.audit();before=self.run/'trials/noskill1/submission-export/agent_output.py';after=self.run/'trials/cleanskill1/submission-export/agent_output.py'
        after.write_text('value = 2\n',encoding='utf-8');report['trials']['target']['oracle']['candidate_sha256']=sha256(after)
        patch=self.run/'patch.diff';patch.write_text(''.join(unified_diff(before.read_text(encoding='utf-8').splitlines(True),after.read_text(encoding='utf-8').splitlines(True),fromfile='before',tofile='after')),encoding='utf-8')
        evidence={k:dict(artifact_path=p.relative_to(self.root).as_posix(),artifact_sha256=sha256(p),locator={'kind':'file'}) for k,p in [('a',before),('b',after),('p',patch)]}
        # Submission interventions require identical Skill treatment on both sides.
        report['trials']['reference']['skill_files']=report['trials']['target']['skill_files']
        intervention=dict(scope='submission',parent_evidence_id='a',child_evidence_id='b',patch_evidence_id='p')
        _completed_intervention(EvidenceFiles(self.root),intervention,evidence,report['trials'],report['generations'])
        patch.write_text('bogus',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Patch does not describe'):
            _completed_intervention(EvidenceFiles(self.root),intervention,evidence,report['trials'],report['generations'])

    def test_export_never_overwrites_and_history_unchanged(self):
        before=inventory(self.root/'runs');out=self.root/'results/sgb/attributions/test'
        export_report(self.root,self.spec,out)
        self.assertEqual(inventory(self.root/'runs'),before)
        with self.assertRaises(FileExistsError):export_report(self.root,self.spec,out)
        with self.assertRaises(ValueError):export_report(self.root,self.spec,self.root/'runs/report')

    def test_path_escape_and_negative_pointer_rejected(self):
        with self.assertRaises(ValueError):EvidenceFiles(self.root).path('../outside')
        with self.assertRaises(ValueError):_pointer([1], '/-1')


class HistoricalAttribution(unittest.TestCase):
    def test_reviewed_historical_examples_without_runtime_execution(self):
        expected={'s24p001':('eligible','both_failed'),'s24p002':('eligible','possible_help'),'s24p003':('eligible','possible_help'),
                  'f02d001':('eligible','both_failed'),'f02d002':('eligible','both_failed'),'f02d003':('eligible','both_failed'),
                  'f02u003':('unknown','unresolved'),'f02u001-incomplete':('unknown','unresolved'),
                  'cross-protocol':('ineligible','unresolved'),'legacy-new':('ineligible','unresolved')}
        from unittest.mock import patch
        with patch('socket.socket.connect',side_effect=AssertionError('Network prohibited')), patch('subprocess.Popen',side_effect=AssertionError('Runtime launch prohibited')):
            for name,states in expected.items():
                with self.subTest(name=name):
                    spec=json.loads((LAB/'configs/attribution'/f'{name}.json').read_text(encoding='utf-8'))
                    r=audit_pair(LAB,spec);self.assertEqual((r['comparability'],r['task_difference']),states)
                    if name=='s24p001':self.assertEqual(next(x for x in r['assertion_differences'] if x['assertion'].startswith('test_supported_backends[ftp:'))['difference'],'possible_harm')
                    if name=='s24p002':self.assertTrue(r['rule_reviews'][0]['downstream_links'][0]['delivery']['before_action'])
                    if name.startswith('f02d'):self.assertEqual(r['rule_reviews'][0]['first_observed_loss'],'draft')


if __name__=='__main__':
    unittest.main()
