"""Isolated official build + auditable evidence. No generation/repair fallback."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
from uuid import uuid4
import zipfile
from evidence import collect, digest, freeze, manifest, read, save, sha, check_frozen

LAB=Path(__file__).resolve().parents[1]
CLI_KEYS=('llm_provider','llm_model','llm_base_url','embeddings_provider','embeddings_model','embeddings_dims',
          'domain','domain_type','family_name','extract_workers','extract_strategy','section_outline_mode',
          'max_section_chars','max_chars_per_chunk','overlap_chars','max_candidates_per_unit','max_units_per_document',
          'max_documents','extract_retries','extract_retry_backoff_s','maintenance_strategy')

def utc(): return datetime.now(timezone.utc).isoformat()
def inside(value):
    p=(LAB/value).resolve()
    if not p.is_relative_to(LAB): raise ValueError('Path must stay inside lab: '+str(value))
    return p

def framework_sources(root):
    # Source/prompt/taxonomy evidence only: never archive credentials or bytecode.
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*')) if p.is_file()
            and not any(x.startswith('.') or x=='__pycache__' for x in p.relative_to(root).parts)
            and p.suffix.lower() in ('.py','.toml','.yaml','.yml','.json','.md','.txt')}

def load_credentials(path):
    key=os.environ.get('DASHSCOPE_API_KEY','').strip()
    if key: return key,'environment'
    if not path.is_file(): return '', 'missing'
    from dotenv import dotenv_values
    return (dotenv_values(path,interpolate=False).get('DASHSCOPE_API_KEY') or '').strip(),'configured_file'

def resolve_case(cfg,variant_path):
    case=read(inside(cfg['case_manifest']))
    case_root=inside(cfg['case_manifest']).parent
    if case.get('status')!='ready': raise ValueError('Case must be frozen and ready')
    clean=inside(case['clean_file'])
    if sha(clean)!=case['clean_sha256']: raise ValueError('Clean document changed; create a new case version')
    if manifest(inside(case['evaluation_dir']))!=case['evaluation_sha256']:
        raise ValueError('Frozen evaluation contract/fixtures changed; create a new case version')
    variant={'case_id':case['case_id'],'condition':'clean','input_file':case['clean_file'],
             'input_sha256':case['clean_sha256'],'clean_sha256':case['clean_sha256'],
             'degradation':None,'repeat_id':cfg.get('repeat_id',1)}
    if variant_path:
        variant=read(variant_path)
        for k in ('case_id','condition','input_file','input_sha256','clean_sha256','degradation','repeat_id'):
            if k not in variant: raise ValueError('Missing variant field '+k)
        if variant['case_id']!=case['case_id'] or variant['clean_sha256']!=case['clean_sha256']:
            raise ValueError('Variant does not refer to this frozen clean case')
        if variant['condition']!='degraded': raise ValueError('Variant condition must be degraded')
        for k in ('type','severity','seed','generator_file','generator_sha256','parameters','edits'):
            if k not in variant['degradation']: raise ValueError('Missing degradation field '+k)
        generator=inside(variant['degradation']['generator_file'])
        if not generator.is_relative_to(case_root/'degradation'):
            raise ValueError('Generator must be inside this case degradation directory')
        if sha(generator)!=variant['degradation']['generator_sha256']: raise ValueError('Generator hash mismatch')
        if not variant['degradation']['edits']: raise ValueError('Degradation edits must be recorded')
        if variant['input_sha256']==case['clean_sha256']: raise ValueError('Degraded input is identical to clean')
    source=inside(variant['input_file'])
    if not source.is_relative_to(case_root): raise ValueError('Input belongs to a different case')
    if sha(source)!=variant['input_sha256']: raise ValueError('Input/variant hash mismatch')
    if source.suffix.lower()!='.md': raise ValueError('This validated runner currently supports Markdown only')
    return case,variant,source

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True,help='Internal resolved config; normally use run_case.py')
    parser.add_argument('--variant',help='Frozen degraded variant JSON; no generation happens here')
    parser.add_argument('--baseline-run',help='Required clean run ID for a degraded run')
    parser.add_argument('--preflight-only',action='store_true',help='Imports/help/dependencies only; no model calls')
    args=parser.parse_args(argv)
    cfg=read(args.config)
    root=Path(cfg['framework_root']).resolve()
    if root==LAB or root in LAB.parents or LAB in root.parents: raise ValueError('Lab and framework must be independent')
    for name in ('AutoSkill4Doc/__init__.py','autoskill/__init__.py','pyproject.toml'):
        if not (root/name).is_file(): raise ValueError('Missing framework file '+name)
    if cfg['llm_provider']!='dashscope' or cfg['embeddings_provider']!='dashscope' or cfg['extract_workers']!=1:
        raise ValueError('This recorder is validated for DashScope JSON calls with one extraction worker')
    case,variant,source=resolve_case(cfg,args.variant)
    if bool(args.variant)!=bool(args.baseline_run): raise ValueError('Use --variant and --baseline-run together')
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid4().hex[:8]
    run=LAB/'runs'/run_id; run.mkdir(parents=True,exist_ok=False)
    for name in ('input','config','logs','official','tmp','trace','evaluation','execution'):
        (run/name).mkdir()
    start=time.monotonic(); before=manifest(root)
    status={'schema':'skill-lab-v3','run_id':run_id,'case_key':cfg['case_key'],'case_id':case['case_id'],
            'method_id':cfg['method_id'],'condition':variant['condition'],
            'started_at_utc':utc(),'status':'preflight',
            'pipeline_pass':False,'semantic_review':'pending','task_execution':'not_run','independent_judging':'not_run','overall_pass':None}
    exit_code=2; key=''; stage='prepare'
    def redact(text): return text.replace(key,'[REDACTED]') if key else text
    try:
        snapshot=run/'input'/source.name; shutil.copyfile(source,snapshot)
        if sha(snapshot)!=variant['input_sha256']: raise ValueError('Input changed while snapshotting')
        save(run/'config/config.json',cfg); save(run/'config/case_manifest.json',case)
        save(run/'case_ref.json',{'case_key':cfg['case_key'],'case_id':case['case_id'],
             'case_manifest':cfg['case_manifest'],'method_id':cfg['method_id'],
             'condition':variant['condition'],'repeat_id':variant['repeat_id'],
             'clean_sha256':case['clean_sha256'],'input_sha256':variant['input_sha256']})
        save(run/'config/variant.json',variant); save(run/'config/framework_before.json',before)
        shutil.copytree(LAB/'scripts',run/'config/lab_scripts',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        shutil.copytree(inside(case['evaluation_dir']),run/'evaluation',dirs_exist_ok=True)
        if manifest(run/'evaluation')!=case['evaluation_sha256']: raise ValueError('Evaluation changed while snapshotting')
        if args.variant:
            shutil.copyfile(inside(variant['degradation']['generator_file']),run/'config/degradation_generator.py')
            if sha(run/'config/degradation_generator.py')!=variant['degradation']['generator_sha256']: raise ValueError('Generator changed while snapshotting')
        sources=framework_sources(root)
        save(run/'config/framework_sources.json',sources)
        with zipfile.ZipFile(run/'config/framework_source.zip','x',zipfile.ZIP_DEFLATED) as z:
            for name in sources: z.write(root/name,name)
        save(run/'execution/status.json',{'status':'not_run','judge':'not_run','reason':'This runner generates skills only'})
        save(run/'status.json',status)
        key,key_source=load_credentials(Path(cfg['credential_file']))
        save(run/'config/credential_status.json',{'DASHSCOPE_API_KEY':bool(key),'source':key_source})
        env=os.environ.copy()
        # Remove model/provider overrides; preserve OS runtime and network setup.
        prefixes=('AUTOSKILL_','DASHSCOPE_','OPENAI_','ANTHROPIC_','BIGMODEL_','INTERNLM_','ZHIPUAI_')
        for k in list(env):
            if k.startswith(prefixes): env.pop(k)
        env.update({'PYTHONPATH':str(root),'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8',
                    'PYTHONUNBUFFERED':'1','PYTHONHASHSEED':'0','PYTHONNOUSERSITE':'1',
                    'DASHSCOPE_API_KEY':key,'DASHSCOPE_BASE_URL':cfg['llm_base_url'],
                    'DASHSCOPE_EMB_BASE_URL':cfg.get('embeddings_base_url',cfg['llm_base_url']),
                    'AUTOSKILL_TIMEOUT_S':str(cfg['timeout_s']),'DASHSCOPE_MAX_TOKENS':str(cfg['max_tokens']),
                    'TEMP':str(run/'tmp'),'TMP':str(run/'tmp'),'TMPDIR':str(run/'tmp'),
                    'SKILL_LAB_FRAMEWORK':str(root),'SKILL_LAB_TRACE':str(run/'trace')})
        python=cfg['python_executable']; stage='preflight'
        probe_code="import AutoSkill4Doc,autoskill,sys,json,platform,importlib.metadata as m;print(json.dumps({'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'AutoSkill4Doc':AutoSkill4Doc.__file__,'autoskill':autoskill.__file__,'packages':sorted((d.metadata['Name'],d.version) for d in m.distributions() if d.metadata['Name'])}))"
        probe=subprocess.run([python,'-B','-c',probe_code],cwd=run,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60,check=True)
        runtime=json.loads(probe.stdout); save(run/'config/runtime.json',runtime)
        for module in ('AutoSkill4Doc','autoskill'):
            if Path(runtime[module]).resolve()!=root/module/'__init__.py': raise ValueError('Unexpected import '+module)
        for suffix,cmdargs in [('main',['--help']),('build',['build','--help'])]:
            result=subprocess.run([python,'-B','-m','AutoSkill4Doc',*cmdargs],cwd=run,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60,check=True)
            (run/'logs'/('help_'+suffix+'.txt')).write_text(redact(result.stdout+result.stderr),encoding='utf-8')
        params={k:cfg[k] for k in CLI_KEYS}
        params.update({k:cfg[k] for k in ('timeout_s','max_tokens','run_timeout_s','method_id')})
        params['embeddings_base_url']=cfg.get('embeddings_base_url',cfg['llm_base_url'])
        contract={'case_id':case['case_id'],'clean_sha256':case['clean_sha256'],
                  'evaluation_sha256':case['evaluation_sha256'],'parameters':params,
                  'framework_source_hash':digest(sources),'lab_script_hash':digest(manifest(run/'config/lab_scripts')),
                  'runtime':{k:runtime[k] for k in ('python','platform','packages')},
                  'selection_policy':'all canonical task skills; no selection by successful output',
                  'model_seed':'not supported by official CLI; temperature=0 is not deterministic'}
        save(run/'config/comparison_contract.json',contract)
        save(run/'config/comparison_fingerprint.json',{'sha256':digest(contract),'repeat_id':variant['repeat_id']})
        if args.baseline_run:
            baseline=inside('runs/'+args.baseline_run)
            if not check_frozen(baseline)['valid']: raise ValueError('Baseline is missing or has changed since sealing')
            baseline_variant=read(baseline/'config/variant.json')
            if baseline_variant['condition']!='clean': raise ValueError('Baseline must be clean')
            if baseline_variant['repeat_id']!=variant['repeat_id']: raise ValueError('Baseline repeat_id differs')
            if read(baseline/'config/comparison_fingerprint.json')['sha256']!=digest(contract): raise ValueError('Baseline comparison settings differ; rerun a matched clean control')
            baseline_status=read(baseline/'status.json')
            if not baseline_status.get('pipeline_pass') or not baseline_status.get('evidence_capture_pass'): raise ValueError('Baseline generation/evidence is incomplete')
            save(run/'config/pair.json',{'baseline_run_id':args.baseline_run,'baseline_checksums_sha256':sha(baseline/'checksums.json'),'repeat_id':variant['repeat_id']})
        # Entry installs a recorder, then runpy executes the real official __main__.
        # The frozen copy of our scripts is used so mid-run edits cannot change this run.
        command=[python,'-B',str(run/'config/lab_scripts/official_entry.py'),'build','--file',str(snapshot),
                 '--store-path',str(run/'official/store'),'--registry-root',str(run/'official/registry')]
        for name in CLI_KEYS: command.extend(['--'+name.replace('_','-'),str(cfg[name])])
        command.extend(['--embeddings-base-url',params['embeddings_base_url'],'--fail-fast','--json'])
        save(run/'config/command.json',{'argv':command,'cwd':str(run),'entry':'runpy.run_module(AutoSkill4Doc, run_name=__main__)','official_source_unchanged':True,
             'env_overrides_without_credentials':{k:env[k] for k in ('PYTHONPATH','PYTHONHASHSEED','PYTHONNOUSERSITE','DASHSCOPE_BASE_URL','DASHSCOPE_EMB_BASE_URL','AUTOSKILL_TIMEOUT_S','DASHSCOPE_MAX_TOKENS')}})
        if args.preflight_only:
            status['status']='preflight_only'; exit_code=0
        else:
            if not key: raise RuntimeError('Missing DASHSCOPE_API_KEY; configure it in environment or credential_file')
            stage='build'; status['status']='running'; save(run/'status.json',status)
            print('RUN_DIR='+str(run),flush=True)
            print('CASE='+cfg['case_key']+' METHOD='+cfg['method_id'],flush=True)
            timed_out=threading.Event()
            with (run/'logs/build.log').open('x',encoding='utf-8') as log:
                process=subprocess.Popen(command,cwd=run,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
                def stop():
                    if process.poll() is None:
                        timed_out.set(); process.kill()
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
        after=manifest(root)
        save(run/'config/framework_after.json',after)
        delta={'changed':sorted(k for k in before.keys()&after.keys() if before[k]!=after[k]),'removed':sorted(before.keys()-after.keys()),'added':sorted(after.keys()-before.keys())}
        save(run/'framework_integrity.json',{'unchanged':before==after,'file_count':len(before),**delta})
        status.update(framework_unchanged=before==after,finished_at_utc=utc(),elapsed_s=time.monotonic()-start)
        if not args.preflight_only:
            try:
                audit=collect(run)
            except Exception as exc:
                audit={'pipeline_pass':False,'errors':['audit failure: '+redact(str(exc))],
                       'trace':{'available':False,'errors':['audit failed']},'rule_coverage':[]}
            save(run/'audit.json',audit)
            trace_ok=audit['trace']['available'] and not audit['trace']['errors']
            status['pipeline_pass']=status.get('official_exit_code')==0 and audit['pipeline_pass'] and before==after and status['status']=='completed_unreviewed'
            status['evidence_capture_pass']=trace_ok
            if exit_code==0 and not(status['pipeline_pass'] and trace_ok):
                status['status']='artifact_validation_failed'; exit_code=4
            save(run/'rule_review_template.json',{'run_id':run_id,'status':'pending','rules':audit['rule_coverage'],
                 'instructions':'Review all final task skill bodies; quote exact paths/lines. Do not score from keywords/references. Save review outside this sealed run.'})
        if before!=after: status['status']='framework_changed'; exit_code=3
        save(run/'official_artifacts_sha256.json',manifest(run/'official'))
        status['wrapper_exit_code']=exit_code
        save(run/'status.json',status); freeze(run)
        save(LAB/'reports'/(run_id+'_status.json'),status)
        print('RUN_DIR='+str(run)); print('STATUS='+status['status']+'; semantic_review=pending; task_execution=not_run')
    return exit_code

if __name__=='__main__': raise SystemExit(main())
