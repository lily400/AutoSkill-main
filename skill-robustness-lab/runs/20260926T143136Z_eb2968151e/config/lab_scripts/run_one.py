"""Isolated unchanged official build, complete evidence, no repair fallback."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
from uuid import uuid4
import zipfile
from evidence import collect,digest,freeze,manifest,read,save,sha
from data_contracts import select,require,safe,sealed_run,validate_object,utc,VERSION

LAB=Path(__file__).resolve().parents[1]
CLI_KEYS=('llm_provider','llm_model','llm_base_url','embeddings_provider','embeddings_model','embeddings_dims',
    'domain','domain_type','family_name','extract_workers','extract_strategy','section_outline_mode',
    'max_section_chars','max_chars_per_chunk','overlap_chars','max_candidates_per_unit','max_units_per_document',
    'max_documents','extract_retries','extract_retry_backoff_s','maintenance_strategy')

def framework_sources(root):
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*')) if p.is_file()
        and not any(x.startswith('.') or x=='__pycache__' for x in p.relative_to(root).parts)
        and p.suffix.lower() in ('.py','.toml','.yaml','.yml','.json','.md','.txt')}

def load_credentials(path):
    """Read one literal .env key without evaluating/interpolating the file."""
    key=os.environ.get('DASHSCOPE_API_KEY','').strip()
    if key: return key,'environment'
    if not path.is_file(): return '','missing'
    values=[]
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        match=re.match(r'^\s*(?:export\s+)?DASHSCOPE_API_KEY\s*=\s*(.*?)\s*$',line)
        if not match: continue
        raw=match.group(1)
        if raw.startswith(('"',"'")):
            quote=raw[0]; end=raw.find(quote,1)
            require(end>0 and (not raw[end+1:].strip() or raw[end+1:].strip().startswith('#')),'Unsupported quoted credential assignment')
            raw=raw[1:end]
        else: raw=re.split(r'\s+#',raw,1)[0].strip()
        values.append(raw)
    require(len(values)<=1,'Duplicate DASHSCOPE_API_KEY assignments')
    return values[0] if values else '', 'configured_file'

def baseline_identity(root,baseline_id,c,v,cfg):
    p,r,ct=sealed_run(root,baseline_id)
    require(r['case_id']==c['case_id'] and r['source_id']==c['source_id'] and r['source_version']==c['source_version'],'Baseline source/case mismatch')
    require(r['family_id']==c['family_id'] and r['variant_id']==v['clean_variant_id'],'Baseline must be this clean variant')
    require(r['input_sha256']==v['clean_sha256'],'Baseline clean bytes mismatch')
    require(r['method_id']==cfg['method_id'] and r['generation_repeat']==cfg['repeat_id'],'Baseline method/repeat mismatch')
    require(r['dataset_freeze_sha256']==sha(Path(root)/'catalog/freeze.json'),'Baseline uses another frozen dataset')
    return p,r,ct

def classify_failure(status,run,audit):
    if status['status']=='preflight_only': return {'category':'none','stage':None,'evidence':[]}
    if status['status']=='interrupted': return {'category':'interrupted','stage':status.get('failed_stage'),'evidence':['status.json']}
    if status.get('pipeline_pass') and status.get('evidence_capture_pass'): return {'category':'none','stage':None,'evidence':[]}
    if status.get('failed_stage') in ('prepare','credentials','preflight'): category='infrastructure'
    elif status.get('status')=='framework_changed': category='evidence'
    elif status.get('official_exit_code')==0: category='evidence' if not status.get('evidence_capture_pass') else 'generation'
    else:
        calls=[read(p) for p in (run/'trace').glob('*.json') if p.name!='session.json' and not p.name.startswith('runtime-')]
        failed=[c for c in calls if c.get('state')=='failed']
        category='infrastructure' if failed and all(c.get('http_status') in (401,403,408,429,500,502,503,504) or c.get('error_type') in ('URLError','TimeoutError') for c in failed) else 'unknown'
    return {'category':category,'stage':status.get('failed_stage','build'),'evidence':['status.json','logs/','trace/','audit.json']}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--config',required=True)
    p.add_argument('--baseline-run'); p.add_argument('--preflight-only',action='store_true'); a=p.parse_args(argv)
    cfg=read(a.config); root=Path(cfg['framework_root']).resolve()
    require(root!=LAB and root not in LAB.parents and LAB not in root.parents,'Framework and lab must be separate')
    for name in ('AutoSkill4Doc/__init__.py','autoskill/__init__.py','pyproject.toml'): require((root/name).is_file(),'Missing official '+name)
    require(Path(cfg['python_executable']).is_file(),'Python executable is not a file')
    require(cfg['llm_provider']=='dashscope' and cfg['embeddings_provider']=='dashscope' and cfg['extract_workers']==1,'Only single-worker DashScope configuration supported')
    ds,case,variant=select(LAB,cfg['case_key'],cfg.get('variant_id'))
    require(cfg['case_manifest']==f"cases/{case['case_key']}/case.json",'Config points to another case')
    require(variant['condition']=='degraded' if a.baseline_run else variant['condition']=='clean','Degraded runs require baseline; clean runs forbid it')
    baseline=baseline_identity(LAB,a.baseline_run,case,variant,cfg) if a.baseline_run else None
    source=safe(LAB,variant['input_file']); require(source.suffix.lower()=='.md','Markdown input required')
    rid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid4().hex[:10]
    run=LAB/'runs'/rid; run.mkdir(parents=True,exist_ok=False)
    for name in ('input','config','logs','official','tmp','trace'): (run/name).mkdir()
    start=time.monotonic(); before=manifest(root); key=''; stage='prepare'; exit_code=2; audit={}
    status={'schema':'skill-lab-v4','run_id':rid,'case_key':case['case_key'],'case_id':case['case_id'],
        'method_id':cfg['method_id'],'condition':variant['condition'],'started_at_utc':utc(),'status':'preflight',
        'pipeline_pass':False,'structural_pass':None,'semantic_review':'pending','task_execution':'not_run','independent_judging':'not_run','overall_pass':None}
    record={'schema_version':VERSION,'run_id':rid,**{k:case[k] for k in ('case_id','source_id','source_version','family_id','split')},
        'variant_id':variant['variant_id'],'method_id':cfg['method_id'],'generation_repeat':cfg['repeat_id'],
        'kind':'preflight' if a.preflight_only else 'generation','status':'preflight','input_sha256':variant['input_sha256'],
        'dataset_freeze_sha256':sha(LAB/'catalog/freeze.json'),'comparison_fingerprint':None,'structural_pass':None,
        'semantic_status':'pending','execution_status':'not_run','failure':{'category':'none','stage':None,'evidence':[]},
        'program_ir_status':'not_applicable','started_at_utc':status['started_at_utc'],'finished_at_utc':None}
    def redact(text): return text.replace(key,'[REDACTED]') if key else text
    save(run/'run.json',record)
    try:
        snapshot=run/'input/source.md'; shutil.copyfile(source,snapshot)
        require(sha(snapshot)==variant['input_sha256'],'Input changed while snapshotting')
        save(run/'config/config.json',cfg); save(run/'config/case_manifest.json',case); save(run/'config/variant.json',variant)
        save(run/'case_ref.json',{k:record[k] for k in ('case_id','source_id','source_version','family_id','variant_id','method_id','generation_repeat')})
        save(run/'config/framework_before.json',before)
        shutil.copytree(LAB/'scripts',run/'config/lab_scripts',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        save(run/'config/standards_ref.json',{'dataset_freeze_sha256':record['dataset_freeze_sha256'],
            'contract_id':variant['contract_id'],'standards':'kept outside generation workspace'})
        if variant['degradation_file']:
            deg=read(safe(LAB,variant['degradation_file'])); save(run/'config/degradation.json',deg)
            shutil.copyfile(safe(LAB,deg['generator']['file']),run/'config/degradation_generator.py')
        sources=framework_sources(root); save(run/'config/framework_sources.json',sources)
        with zipfile.ZipFile(run/'config/framework_source.zip','x',zipfile.ZIP_DEFLATED) as z:
            for name in sources: z.write(root/name,name)
        env=os.environ.copy()
        prefixes=('AUTOSKILL_','DASHSCOPE_','OPENAI_','ANTHROPIC_','BIGMODEL_','INTERNLM_','ZHIPUAI_')
        for name in list(env):
            if name.startswith(prefixes): env.pop(name)
        env.update({'PYTHONPATH':str(root),'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','PYTHONUNBUFFERED':'1',
            'PYTHONHASHSEED':'0','PYTHONNOUSERSITE':'1','TEMP':str(run/'tmp'),'TMP':str(run/'tmp'),'TMPDIR':str(run/'tmp'),
            'DASHSCOPE_BASE_URL':cfg['llm_base_url'],'DASHSCOPE_EMB_BASE_URL':cfg['embeddings_base_url'],
            'AUTOSKILL_TIMEOUT_S':str(cfg['timeout_s']),'DASHSCOPE_MAX_TOKENS':str(cfg['max_tokens']),
            'SKILL_LAB_FRAMEWORK':str(root),'SKILL_LAB_TRACE':str(run/'trace')})
        python=cfg['python_executable']; stage='preflight'
        probe_code="import AutoSkill4Doc,autoskill,sys,json,platform,importlib.metadata as m;print(json.dumps({'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'AutoSkill4Doc':AutoSkill4Doc.__file__,'autoskill':autoskill.__file__,'packages':sorted((d.metadata['Name'],d.version) for d in m.distributions() if d.metadata['Name'])}))"
        probe=subprocess.run([python,'-B','-c',probe_code],cwd=run,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60,check=True)
        runtime=json.loads(probe.stdout); save(run/'config/runtime.json',runtime)
        for module in ('AutoSkill4Doc','autoskill'): require(Path(runtime[module]).resolve()==root/module/'__init__.py','Unexpected module origin')
        for suffix,args in [('main',['--help']),('build',['build','--help'])]:
            result=subprocess.run([python,'-B','-m','AutoSkill4Doc',*args],cwd=run,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60,check=True)
            (run/'logs'/('help_'+suffix+'.txt')).write_text(result.stdout+result.stderr,encoding='utf-8')
        params={k:cfg[k] for k in CLI_KEYS+('timeout_s','max_tokens','run_timeout_s','method_id','embeddings_base_url')}
        contract={**{k:case[k] for k in ('case_id','source_id','source_version','family_id','split')},
            'clean_sha256':variant['clean_sha256'],'clean_variant_id':variant['clean_variant_id'],
            'dataset_freeze_sha256':record['dataset_freeze_sha256'],'parameters':params,
            'framework_source_hash':digest(sources),'lab_script_hash':digest(manifest(run/'config/lab_scripts')),
            'runtime':{k:runtime[k] for k in ('python','platform','packages')},
            'selection_policy':'all native task skills; no selection by clean success',
            'access_policy':'fixed official CLI input only; standards not copied; no downstream executor',
            'model_seed':'unsupported by official CLI; repeat number is not deterministic seed'}
        save(run/'config/comparison_contract.json',contract); fp=digest(contract); record['comparison_fingerprint']=fp
        save(run/'config/comparison_fingerprint.json',{'sha256':fp,'generation_repeat':cfg['repeat_id']})
        if baseline:
            require(digest(baseline[2])==fp,'Baseline method/code/environment/standard differs')
            save(run/'config/pair.json',{'baseline_run_id':a.baseline_run,'baseline_checksums_sha256':sha(baseline[0]/'checksums.json')})
        command=[python,'-B',str(run/'config/lab_scripts/official_entry.py'),'build','--file',str(snapshot),
            '--store-path',str(run/'official/store'),'--registry-root',str(run/'official/registry')]
        for name in CLI_KEYS: command.extend(['--'+name.replace('_','-'),str(cfg[name])])
        command.extend(['--embeddings-base-url',cfg['embeddings_base_url'],'--fail-fast','--json'])
        save(run/'config/command.json',{'argv':command,'cwd':str(run),'entry':'runpy.run_module(AutoSkill4Doc)',
            'official_files_modified_by_wrapper':False,'credential_values_saved':False,
            'env_overrides_without_credentials':{k:env[k] for k in ('PYTHONPATH','PYTHONHASHSEED','PYTHONNOUSERSITE','DASHSCOPE_BASE_URL','DASHSCOPE_EMB_BASE_URL','AUTOSKILL_TIMEOUT_S','DASHSCOPE_MAX_TOKENS')}})
        if a.preflight_only:
            save(run/'config/credential_status.json',{'checked':False,'reason':'Offline preflight never reads credentials'})
            status['status']='preflight_only'; exit_code=0
        else:
            stage='credentials'; key,origin=load_credentials(Path(cfg['credential_file']))
            save(run/'config/credential_status.json',{'checked':True,'available':bool(key),'source':origin})
            require(bool(key),'Missing DASHSCOPE_API_KEY'); env['DASHSCOPE_API_KEY']=key
            stage='build'; status['status']='running'; save(run/'status.json',status)
            print('RUN_DIR='+str(run),flush=True); timed_out=threading.Event()
            with (run/'logs/build.log').open('x',encoding='utf-8') as log:
                process=subprocess.Popen(command,cwd=run,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
                def stop():
                    if process.poll() is None: timed_out.set(); process.kill()
                timer=threading.Timer(cfg['run_timeout_s'],stop); timer.start()
                try:
                    for line in process.stdout: log.write(redact(line)); log.flush()
                    exit_code=process.wait()
                finally:
                    timer.cancel()
                    if process.poll() is None: process.kill(); process.wait()
            status.update(official_exit_code=exit_code,status='timeout' if timed_out.is_set() else 'completed_unreviewed' if exit_code==0 else 'failed')
            if timed_out.is_set(): exit_code=124
    except KeyboardInterrupt:
        status.update(status='interrupted',failed_stage=stage); exit_code=130
    except Exception as exc:
        status.update(status='failed',failed_stage=stage,error=redact(str(exc))); exit_code=2
        (run/'logs/wrapper_error.txt').write_text(redact(str(exc)),encoding='utf-8')
    finally:
        after=manifest(root); save(run/'config/framework_after.json',after)
        delta={'changed':sorted(k for k in before.keys()&after.keys() if before[k]!=after[k]),'removed':sorted(before.keys()-after.keys()),'added':sorted(after.keys()-before.keys())}
        save(run/'framework_integrity.json',{'unchanged':before==after,'file_count':len(before),**delta})
        status.update(framework_unchanged=before==after,finished_at_utc=utc(),elapsed_s=time.monotonic()-start)
        if not a.preflight_only:
            try: audit=collect(run,contract=ds['contracts'][variant['contract_id']])
            except Exception as exc: audit={'pipeline_pass':False,'errors':['audit failure: '+redact(str(exc))],'trace':{'available':False,'errors':['audit failed']},'rule_coverage':[]}
            save(run/'audit.json',audit)
            trace_ok=audit['trace']['available'] and not audit['trace']['errors']
            status['pipeline_pass']=status.get('official_exit_code')==0 and audit['pipeline_pass'] and before==after and status['status']=='completed_unreviewed'
            status['structural_pass']=status['pipeline_pass']; status['evidence_capture_pass']=trace_ok
            if exit_code==0 and not(status['pipeline_pass'] and trace_ok): status['status']='artifact_validation_failed'; exit_code=4
        if before!=after: status['status']='framework_changed'; exit_code=3
        status['wrapper_exit_code']=exit_code
        record.update(status=status['status'],structural_pass=status['structural_pass'],finished_at_utc=status['finished_at_utc'],failure=classify_failure(status,run,audit))
        validate_object('run',record); save(run/'run.json',record); save(run/'status.json',status)
        save(run/'official_artifacts_sha256.json',manifest(run/'official')); freeze(run)
        save(LAB/'reports'/(rid+'_status.json'),status)
        print('RUN_DIR='+str(run)); print('STATUS='+status['status']+'; semantic=pending; execution=not_run')
    return exit_code
if __name__=='__main__': raise SystemExit(main())
