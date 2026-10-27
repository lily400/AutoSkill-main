import hashlib,json,sys
from pathlib import Path

root=Path(r'D:\AS\AutoSkill-main\degradation_failure_lab');sys.path[:0]=[str(root),str(root/'src')]
from downstream_eval.sgb.attribution import audit_pair,export_report
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
path=root/'configs/attribution/sn3e001.json';spec=read(path)
assert not spec['evidence'] and not spec['rules'] and not spec['claims']
audit=root/'results/sgb/audits/task003-execution-sn3g001'
(audit/'attribution-spec-before.json').write_bytes(path.read_bytes())
base=audit_pair(root,spec)
write(audit/'pair-before-review.json',base)
print('PAIR',base['comparability'],base['task_difference'])
print('NON_EQUAL_CONTROLS',json.dumps([r for r in base['control_checks'] if r['status']!='equal']))
gen=root/'runs/gen/sgb/case003_san/clean/sn3r001'
result=read(gen/'official_result.json')
mid=gen/'SkillBank/.runtime/intermediate_runs'/result['intermediate']['run_id']
ing=read(mid/'ingest/result.json');ext=read(mid/'extract/result.json');comp=read(mid/'compile/result.json')
sid='12088cea-5a72-5997-94e9-56794cb7b6dd'
sp=next(s for s in comp['skill_specs'] if s['skill_id']==sid)
draft=next(d for d in ext['skill_drafts'] if d['draft_id'] in sp['metadata']['source_draft_ids'])
support=next(s for s in comp['support_records'] if s['support_id'] in draft['support_ids'])
window=next(w for w in ing['windows'] if w['window_id']==support['metadata']['window_id'])
manifest=read(root/'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/skills_manifest.json')
skill=root/manifest['packages'][sid]['source_path']
def evidence(eid,p,stage,entity,kind,value,space='artifact',owner='sn3r001',claim='Observed artifact anchor'):
    spec['evidence'].append(dict(evidence_id=eid,artifact_path=p.relative_to(root).as_posix(),
        artifact_sha256=digest(p),run_id=owner,stage=stage,entity_id=entity,
        locator=dict(kind=kind,value=value,coordinate_space=space),claim_status='observed',claim=claim,missing_reason=None))
source=root/read(gen/'input_manifest.json')['inputs'][0]['original_path']
evidence('E-SOURCE',source,'source','sgb-0d13982799c95cfa','lines',[38,94,95],'original_source')
evidence('E-WINDOW',mid/'ingest/result.json','window',window['window_id'],'json_pointer','/windows/'+str(ing['windows'].index(window)))
evidence('E-SUPPORT',mid/'compile/result.json','support',support['support_id'],'json_pointer','/support_records/'+str(comp['support_records'].index(support)))
evidence('E-DRAFT',mid/'extract/result.json','draft',draft['draft_id'],'json_pointer','/skill_drafts/'+str(ext['skill_drafts'].index(draft)))
evidence('E-SPEC',mid/'compile/result.json','spec',sid,'json_pointer','/skill_specs/'+str(comp['skill_specs'].index(sp)))
evidence('E-REGISTERED',gen/'SkillBank/.runtime/document_registry/skills'/(sid+'.json'),'registered',sid,'json_pointer','')
trial=base['trials']['target'];trialroot=root/trial['paths']['trial']
tools=read_lines=lambda p:[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
actions=read_lines(trialroot/'p1-observer/p1-tool-actions.jsonl')
action=next((i for i,x in enumerate(actions,1) if x.get('stage')=='submitted' and x.get('actor')=='model_tool'
             and 'agent_output.py' in json.dumps(x) and 'def solve' in json.dumps(x)),None)
for side,label in [('reference','NoSkill1'),('target','CleanSkill1')]:
    t=base['trials'][side];owner=t['run_id'];p=root/t['paths']['candidate']
    evidence('E-CODE-'+label,p,'submission',None,'file',None,owner=owner,claim='Actual hash-bound submitted implementation')
    evidence('E-SCORE-'+label,root/t['paths']['run']/'outcomes'/label/'result.json','oracle',None,
             'json_pointer','/oracle/task_result',owner=owner,claim='Original valid eight-case Oracle result')
assertions=list(trial['assertions'])
mapping={int(n.split('[',1)[1].split('-',1)[0]):n for n in assertions}
rules=read(gen/'rules.json')['rules'];reviewer='Codex assistant (source-grounded review; not independent human sign-off)'
locations=[[58],[61],[63],list(range(61,72))]
test_numbers=[[1,3,4,5,6,7,8],[1,3,4,5,6,7,8],[1,3,4,5,6],list(range(1,9))]
stages=['source','window','support','draft','spec','registered','skill']
common=['E-SOURCE','E-WINDOW','E-SUPPORT','E-DRAFT','E-SPEC','E-REGISTERED']
for index,rule in enumerate(rules):
    eid='E-SKILL-'+str(index+1)
    evidence(eid,skill,'skill',sid,'lines',locations[index],'skill_body',claim=rule['text'])
    uncertainty=index==3
    anchors=common+[eid]
    spec['rules'].append(dict(rule_id=rule['rule_id'],parent_rule_id=rule['rule_id'],generator_run_id='sn3r001',
        claim=rule['text'],reviewer=reviewer,review_status='reviewed',
        stages=[dict(stage=s,status='ambiguous' if uncertainty and s!='source' else 'preserved',evidence_ids=[e],
            rationale=('One-turn/exclusion/immediate-end clauses are explicit; full clockwise extra-turn ordering is not explicit at this anchor. Separate ordinary-turn Skills do not settle the full conjunction.'
                       if uncertainty and s!='source' else 'Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.'))
                for s,e in zip(stages,anchors)],
        downstream_links=[dict(side='target',assertions=[mapping[n] for n in test_numbers[index]],oracle_not_covered=False,
            skill_id=sid,skill_lines=locations[index],action_event=action,
            interpretation='Anchored code-writing action; delivery check concerns the retained excerpt only. Reading is not proof of reliance; task itself explicitly supplies scheduling structure.')]))
    if not uncertainty:
        spec['claims'].append(dict(claim_id='C-PRESERVE-'+str(index+1),rule_ids=[rule['rule_id']],scope='preservation',
            status='observed',text='The source-backed numeric rule, including role/timing, is present in the actual final Skill body.',
            evidence_ids=anchors,downstream_category=None,candidate_causes=[],primary_cause=None,alternatives=[],missing_evidence=[],reviewer=reviewer,intervention_ids=[]))
spec['claims'].append(dict(claim_id='C-IMPLEMENTATIONS',rule_ids=[r['rule_id'] for r in rules[:3]],scope='behavior',status='observed',
    text='NoSkill submitted objective threshold 1 and marker values 2/1; CleanSkill submitted threshold 4 and markers 10/5. Original Oracle results are 0/8 versus 8/8 in this pair.',
    evidence_ids=['E-CODE-NoSkill1','E-CODE-CleanSkill1','E-SCORE-NoSkill1','E-SCORE-CleanSkill1'],downstream_category='TIF.IRF',
    candidate_causes=[],primary_cause=None,alternatives=[],missing_evidence=[],reviewer=reviewer,intervention_ids=[]))
spec['claims'].append(dict(claim_id='C-POSSIBLE-HELP',rule_ids=[r['rule_id'] for r in rules[:3]],scope='causal',status='hypothesis',
    text='The delivered numeric rules may explain the improvement, conditional on eligible pairing and pre-action excerpt delivery. This is a single-pair mechanism hypothesis, not a verified causal or stable-success conclusion.',
    evidence_ids=['E-SKILL-1','E-SKILL-2','E-SKILL-3','E-CODE-NoSkill1','E-CODE-CleanSkill1'],downstream_category=None,
    candidate_causes=['insufficient_evidence'],primary_cause=None,
    alternatives=['Model prior knowledge and generation variation','Independent choice of constants after reading task/Skill index'],
    missing_evidence=['No controlled numeric-rule intervention','No generation or downstream repetitions'],reviewer=reviewer,intervention_ids=[]))
checked=audit_pair(root,spec)
write(path,spec)
output=root/'results/sgb/attributions/sn3e001-v1'
final=export_report(root,spec,output)
print(json.dumps({'comparability':final['comparability'],'difference':final['task_difference'],
    'action_event':action,'delivery':{r['rule_id']:r['downstream_links'][0]['delivery'] for r in final['rule_reviews']},
    'evidence':len(final['review_evidence']),'report':str(output/'report.md')},ensure_ascii=False))
