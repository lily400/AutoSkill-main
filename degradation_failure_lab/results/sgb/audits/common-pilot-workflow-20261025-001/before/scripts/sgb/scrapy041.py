"""Scrapy041 frozen Clean pilot: zero-model preparation followed by one bounded pair."""
import argparse
import asyncio
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

LAB = Path(__file__).resolve().parents[2]
CONTROL = 'harbor-p0-control-20261018'
LINUX_ROOT = '/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab'
sys.path[:0] = [str(LAB),str(LAB/'src')]
os.environ['LITELLM_LOCAL_MODEL_COST_MAP'] = 'True'
from degradation_lab.io import inventory,read,sha256,write
from degradation_lab.artifacts import load_run
from downstream_eval.integration.skill_install import canonical_packages,copy_packages
from downstream_eval.sgb import runner

CONDITIONS = {'NoSkill1':'NoSkill','CleanSkill1':'CleanSkill'}
GENERATOR = 's41r003'


def freeze_skills(output):
    identity,run,result,stages = load_run(LAB,GENERATOR)
    if identity['case_id']!='case041_scrapy' or result.get('status')!='completed' or result.get('errors'):
        raise ValueError('Completed Scrapy041 generation required')
    lineage=[]
    current=run
    while True:
        saved=read(current/'artifact_manifest.json')
        if any(sha256(current/name)!=digest for name,digest in saved.items()):
            raise ValueError('Generator history changed: '+current.name)
        lineage.append({'run_id':current.name,'manifest_sha256':sha256(current/'artifact_manifest.json'),
                        'execution':read(current/'execution.json')})
        if not (current/'resume.json').exists():break
        parent=read(current/'resume.json')['parent_run_id']
        _,current,_,_=load_run(LAB,parent)
    reg=stages['register']; ids={s['id'] for s in reg['upserted_store_skills']}
    registry=run/'SkillBank/.runtime/document_registry'
    active={item['skill_id']:item for path in (registry/'skills').glob('*.json')
            if (item:=read(path))['status']=='active'}
    if not ids or ids!=set(active):raise ValueError('Active registration identities differ')
    canonical=list((run/'SkillBank/Users').rglob('SKILL.md'))
    write(output/'canonical_files.json',{'unique_program_skill_count':len(ids),
                                        'canonical_program_skills':[str(p) for p in canonical]})
    packages=canonical_packages(LAB,{'generator_run_id':GENERATOR,'case_id':'case041_scrapy',
        'condition':'clean','expected_skill_count':len(ids),
        'skill_manifest':(output/'canonical_files.json').relative_to(LAB).as_posix()})
    copy_packages(packages,output/'skills')
    docs={d['doc_id']:d for d in stages['ingest']['documents']}
    supports={item['support_id']:item for path in (registry/'supports').glob('*.json') if (item:=read(path))}
    provenance={item['entity_id']:item for path in (registry/'provenance_links').glob('*.json')
                if (item:=read(path)).get('entity_type')=='skill'}
    entries={}
    for sid,item in packages.items():
        evidence=[supports[s] for s in active[sid]['support_ids']]
        if not evidence or any(e.get('doc_id') not in docs for e in evidence):
            raise ValueError('Missing or foreign source evidence: '+sid)
        entries[sid]={'source_path':item['path'].relative_to(LAB).as_posix(),'files':item['files'],
            'metadata':item['metadata'],'version':active[sid]['version'],
            'support_ids':active[sid]['support_ids'],'evidence':evidence,
            'provenance':provenance.get(sid,{}),'sha256':sha256(item['path'])}
    write(output/'skills_manifest.json',{'generator_run_id':GENERATOR,'packages':entries,
        'source_artifact_manifest_sha256':sha256(run/'artifact_manifest.json'),'lineage':lineage})
    mid=run/'SkillBank/.runtime/intermediate_runs'/result['intermediate']['run_id']
    per_doc=[]
    for did,d in docs.items():
        ext=read(mid/'extract/documents'/(did+'.json'))
        comp=read(mid/'compile/documents'/(did+'.json'))
        registered=read(mid/'register/documents'/(did+'.json'))
        per_doc.append({'doc_id':did,'title':d['title'],'windows':sum(w['doc_id']==did for w in stages['ingest']['windows']),
            'candidates':len(ext['skill_drafts']),'compiled_specs':len(comp['skill_specs']),
            'registered_specs':len(registered['skill_specs']),'errors':registered['errors']})
    texts={sid:(output/'skills'/sid/'SKILL.md').read_text() for sid in packages}
    quality={'status':'FROZEN_WITH_DOCUMENTED_QUALITY_DEFECTS','per_document':per_doc,
        'final_packages':len(packages),'skills_containing_allow_offsite':[sid for sid,t in texts.items() if 'allow_offsite' in t],
        'findings':[
            {'kind':'rule_omission','rule':'meta allow_offsite True','evidence':'No final SKILL.md contains allow_offsite; Offsite skill states offsite requests are ignored without the documented exception.',
             'source_evidence':['input001/offsite.md:57-63','input002/downloader-middleware.md:651-654'],
             'skill_id':'0f70cd3f-8916-5100-949a-b17f1bc29338'},
            {'kind':'template_label','count':sum('Example Therapist Responses' in t for t in texts.values()),
             'evidence':'Psychotherapy-oriented heading survives in programming skills; bodies preserved unchanged.'}],
        'coordination_actions':reg['change_logs'],
        'scope':'All package identities/evidence references/hashes checked; target-rule static review. Not an exhaustive semantic proof for every rule.',
        'policy':'Keep all final active packages; do not repair omissions or select by Oracle score.'}
    write(output/'skill_quality.json',quality)
    write(output/'skill_freeze.json',{'generator_run_id':GENERATOR,'files':inventory(output/'skills'),
        'manifest_sha256':sha256(output/'skills_manifest.json'),'skill_count':len(packages)})
    return entries


async def probe_body_chunks(trial):
    """Verify paging through existing terminal tools; never inject text into paid prompts."""
    import hashlib
    from harbor.agents.terminus_2.terminus_2 import Command
    from downstream_eval.integration.p1_observer import body_visible
    observer=trial.paths.trial_dir/'p1-observer'
    summary=read(observer/'p1-summary.json')
    manifest=trial.agent._p1_manifest
    visible=set(summary['full_body_visible_ids_ignoring_terminal_whitespace'])
    records=[]
    for sid in sorted(set(manifest['metadata'])-visible):
        text=(Path(manifest['staged_root'])/sid/'SKILL.md').read_text()
        pieces=[];current=''
        for line in text.splitlines(keepends=True):
            if current and (len(current)+len(line)>500 or current.count('\n')>=8):
                pieces.append(current);current=''
            while len(line)>500:
                if current:pieces.append(current);current=''
                pieces.append(line[:500]);line=line[500:]
            current+=line
        if current:pieces.append(current)
        offset=0;proof=[]
        for piece in pieces:
            end=offset+len(piece)
            command=("python -c \"from pathlib import Path; print(Path('/harbor/skills/"
                     +sid+"/SKILL.md').read_text()["+str(offset)+":"+str(end)+"],end='')\"\n")
            timed_out,observation=await trial.agent._execute_commands(
                [Command(command,0.2)],trial.agent._session)
            ok=not timed_out and (not piece.strip() or body_visible(piece,observation))
            proof.append({'start':offset,'end':end,'sha256':hashlib.sha256(piece.encode()).hexdigest(),
                          'visible':ok,'observation':observation})
            if not ok:raise RuntimeError('Paged Skill body not visible: '+sid)
            offset=end
        if offset!=len(text):raise ValueError('Incomplete paging')
        visible.add(sid);records.append({'skill_id':sid,'chunks':proof})
    write(trial.paths.trial_dir/'body-visibility.json',{'status':'PASS','single_read_ids':
        summary['full_body_visible_ids_ignoring_terminal_whitespace'],'paged_records':records,
        'all_visible_ids':sorted(visible),'model_calls':0,
        'scope':'Controlled read availability, not evidence of model-directed reading'})


def prepare(output):
    from downstream_eval.sgb.task_adapters.scrapy041.adapter import execution_config,configure,grade_export,native_trial
    from downstream_eval.sgb.task_adapters.scrapy041.scoring import TASK,verify_assets
    from downstream_eval.integration.harbor_adapter import verify_sources
    from downstream_eval.integration.request_budget import Ledger
    from downstream_eval.p1 import fairness_identity
    if (output/'budget.sqlite3').exists() or (output/'batch.started').exists():
        raise RuntimeError('Existing budget/batch must never be reset')
    output.mkdir(parents=True,exist_ok=True)
    engineering=output/'engineering'/('attempt-%03d' % (len(list((output/'engineering').glob('attempt-*')))+1))
    engineering.mkdir(parents=True,exist_ok=False)
    verify_assets()
    _,lock=verify_sources(LAB)
    versions={n:importlib.metadata.version(n) for n in ('harbor','litellm','openai','httpx')}
    if versions['harbor']!=lock['harbor_version']:raise ValueError('Harbor version mismatch')
    write(output/'runtime_versions.json',versions)
    runtime=read(TASK/'runtime.lock.json')
    for key in ('agent_image_id','scorer_image_id'):
        actual=subprocess.run(['docker','image','inspect',runtime[key],'--format','{{.Id}}'],
                              capture_output=True,text=True,check=True).stdout.strip()
        if actual!=runtime[key]:raise ValueError('Runtime image mismatch')
    if (output/'skill_freeze.json').exists():
        frozen=read(output/'skill_freeze.json')
        if (inventory(output/'skills')!=frozen['files'] or
                sha256(output/'skills_manifest.json')!=frozen['manifest_sha256']):
            raise ValueError('Frozen package changed')
        packages=read(output/'skills_manifest.json')['packages']
    else:
        packages=freeze_skills(output)
    draft_path=LAB/'configs/experiments/sgb/scrapy041_clean.json'
    draft=read(draft_path)
    write(output/'experiment-before.json',draft)
    profile=read(LAB/'downstream_eval/configs/p1_smoke.json')
    profile.update(task_id='scrapy-task-041',experiment_id=output.name,generator_run_id=GENERATOR,
        conditions=CONDITIONS,arms=list(CONDITIONS.values()),trial_order=list(CONDITIONS),repeats_per_arm=1,
        approval_environment_variable='SCRAPY041_ALLOW_PAID',authorization='AUTHORIZED_BY_USER_20261025',
        model=draft['downstream_budget_proposal']['model'],budget=draft['downstream_budget_proposal']['budget'],
        frozen_agent_image_id=runtime['agent_image_id'],price_usd_per_million_tokens=None)
    profile.pop('gold_skill_id',None)
    profile['hard_http_budget']={'database':str(output/'budget.sqlite3'),'per_arm_limit':6,
                                'global_limit':12,'order':list(CONDITIONS)}
    write(output/'profile.json',profile)
    write(output/'authorization.json',{'user_request':'完成啊，完成之后告诉我你增加了哪些内容，然后具备条件就直接运行任务',
        'scope':'One NoSkill and one CleanSkill trial, existing drafted model and budgets',
        'max_http_calls_total':12,'max_http_calls_per_trial':6,'automatic_repeat':False})
    for condition in CONDITIONS.values():
        stage=output/'staged'/condition
        if stage.exists():
            expected={} if condition=='NoSkill' else inventory(output/'skills')
            if inventory(stage)!=expected:raise ValueError('Staged package changed')
        elif condition=='NoSkill':stage.mkdir(parents=True)
        else:copy_packages({sid:{'path':output/'skills'/sid/'SKILL.md','files':p['files']} for sid,p in packages.items()},stage)
    for label,condition in CONDITIONS.items():
        stage=output/'staged'/condition
        write(output/'manifests'/(label+'.json'),{'arm':label,'generator_run_id':GENERATOR,
            'staged_root':str(stage),'files':inventory(stage),
            'metadata':{sid:p['metadata'] for sid,p in packages.items()} if condition=='CleanSkill' else {}})
    config=execution_config(output,GENERATOR,CONDITIONS)
    configs={label:configure(output,label,'paid',config) for label in CONDITIONS}
    identities={label:fairness_identity(c.model_dump(mode='json',exclude_none=True)) for label,c in configs.items()}
    if len(set(identities.values()))!=1:raise ValueError('Trial configurations differ beyond treatment')
    for label,c in configs.items():write(output/'configs'/(label+'.json'),c.model_dump(mode='json',exclude_none=True))
    write(output/'fairness.json',{'status':'PASS','configuration_hashes':identities,
        'instruction_sha256':sha256(TASK/'instruction.md'),'runtime_note_sha256':sha256(TASK/'runtime-note.md'),
        'oracle_sha256':sha256(TASK/'scorer/oracle/eval.py'),'runtime':runtime,
        'NoSkill_packages':0,'CleanSkill_packages':len(packages),'source_docs_provided':False})
    reports=[]
    fixtures=read(LAB/'tests/fixtures/sgb/scrapy-task-041/candidates.json')
    for label,fixture in [('NoSkill1','correct'),('CleanSkill1','dont_filter_only')]:
        path=engineering/'fixtures'/(fixture+'.py')
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(fixtures[fixture]['source'])
        native_config=configure(output,label,'probe',config)
        native_config.trials_dir=engineering/'probe-trials'
        trial=None
        try:
            trial,native=asyncio.run(native_trial(native_config,path,probe_hook=probe_body_chunks))
            write(engineering/label/'native.json',native)
            if native.get('exception_info'):raise RuntimeError('Native zero-model probe failed: '+str(native['exception_info']))
            scored=grade_export(trial,engineering/label/'oracle')
            observer=trial.paths.trial_dir/'p1-observer'
            summary=read(observer/'p1-summary.json')
            requests=[json.loads(line) for line in (observer/'p1-model-requests.jsonl').read_text().splitlines()]
            expected=len(packages) if label=='CleanSkill1' else 0
            index=(observer/'p1-skill-index.xml').read_text()
            index_ok=(index in requests[0]['messages'][-1]['content']) if expected else '<available_skills>' not in requests[0]['messages'][-1]['content']
            good=(summary['stopped_before_model'] and summary['actual_http_attempts']==0
                and len(summary['controlled_probe_read_ids'])==expected
                and len(read(trial.paths.trial_dir/'body-visibility.json')['all_visible_ids'])==expected
                and index_ok and requests[0]['estimated_input_tokens_with_reserve']<=profile['budget']['max_input_tokens_per_request']
                and scored['infra_ok'] and scored['task_result']['tests']==10
                and scored['task_result']['passed']==fixtures[fixture]['passed'])
            report={'label':label,'status':'PASS' if good else 'FAIL','fixture':fixture,'summary':summary,
                'initial_input_tokens':requests[0]['estimated_input_tokens_with_reserve'],'index_in_initial_prompt':index_ok,
                'body_visibility':read(trial.paths.trial_dir/'body-visibility.json'),
                'oracle':scored,'model_api_calls':0,'real_agent_outcome':False,'trial_path':str(trial.paths.trial_dir)}
            write(engineering/label/'report.json',report);reports.append(report)
            print(json.dumps({'probe':label,'status':report['status'],'initial_tokens':report['initial_input_tokens']}),flush=True)
            if not good:raise RuntimeError('Zero-model acceptance did not pass')
        finally:
            if trial:asyncio.run(trial.agent_environment.stop(delete=True))
    write(output/'readiness.json',{'status':'PASS','model_api_calls':0,'reports':reports})
    draft.update(status='PREPARED_FOR_AUTHORIZED_PILOT',generator_run_id=GENERATOR,
                 downstream_experiment_id=output.name,prepared_output=output.relative_to(LAB).as_posix())
    draft['downstream_budget_proposal']['authorization']='AUTHORIZED_BY_USER_20261025'
    draft['generation_budget_proposal']['authorization']='HISTORICAL_AUTHORIZATIONS_IN_RUN_LINEAGE'
    write(draft_path,draft)
    frozen={}
    for prefix in ('downstream_eval/integration','downstream_eval/sgb','downstream_eval/tasks/sgb/code_doc/scrapy-task-041'):
        frozen.update({prefix+'/'+p:h for p,h in inventory(LAB/prefix).items()})
    for rel in ('scripts/sgb/scrapy041.py','scripts/Invoke-ProjectCredential.ps1','downstream_eval/configs/runner.lock.json',
                'downstream_eval/tasks/sgb/code_doc/scrapy-task-024/scorer/preflight.py','configs/experiments/sgb/scrapy041_clean.json'):
        frozen[rel]=sha256(LAB/rel)
    for p,h in inventory(LAB/'.external/harbor-full/src/harbor').items():frozen['.external/harbor-full/src/harbor/'+p]=h
    for p,h in inventory(output).items():
        if not p.startswith('engineering/') and p not in ('execution_manifest.json','budget.sqlite3'):
            frozen[(output/p).relative_to(LAB).as_posix()]=h
    write(output/'execution_manifest.json',frozen)
    Ledger.create(output/'budget.sqlite3',{'scope':config.budget_scope,'order':list(CONDITIONS),
        'global_limit':12,'per_trial_limit':6,'trials':{k:c.trial_name for k,c in configs.items()},
        'files':{str(LAB/k):h for k,h in frozen.items()},'budget':profile['budget']})
    runner.verify_frozen(LAB,output)
    runner.verify_ledger(LAB,output,config,profile)
    print(json.dumps({'status':'READY','output':str(output),'skill_count':len(packages),'model_calls':0}),flush=True)
    return 0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=('prepare','run'))
    parser.add_argument('--experiment',required=True)
    args=parser.parse_args()
    output=runner.experiment_output(LAB,'scrapy-task-041',args.experiment)
    if os.name=='nt':
        command=['docker','exec','--env','PYTHONPATH='+LINUX_ROOT+':'+LINUX_ROOT+'/src']
        if args.phase=='run':
            if not os.environ.get('ZHIZENGZENG_API_KEY'):raise RuntimeError('Use Invoke-ProjectCredential.ps1 -Action')
            command+=['--env','ZHIZENGZENG_API_KEY','--env','SCRAPY041_ALLOW_PAID=1']
        command+=[CONTROL,'/opt/harbor-venv/bin/python','-B',LINUX_ROOT+'/scripts/sgb/scrapy041.py',
                  args.phase,'--experiment',args.experiment]
        return subprocess.run(command).returncode
    if args.phase=='prepare':return prepare(output)
    from downstream_eval.sgb.task_adapters.scrapy041.adapter import paid_batch
    versions={n:importlib.metadata.version(n) for n in ('harbor','litellm','openai','httpx')}
    if versions!=read(output/'runtime_versions.json'):raise ValueError('Runtime package versions changed')
    return paid_batch(output)


if __name__=='__main__':
    raise SystemExit(main())
