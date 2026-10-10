"""Call the upstream public API; observe HTTP without changing prompts/results."""
import argparse
from collections import Counter
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import threading
import time
import traceback
import uuid
from common import LAB, UPSTREAM, code_inventory, new_run, sha256, utc, write_json


def validate_config(cfg):
    if cfg['llm']['provider'] != 'openai':
        raise ValueError('This observation wrapper supports only the official OpenAI-compatible client; mock is forbidden')
    if any(k in cfg['llm'] for k in ('api_key', 'response', 'connector_factory', 'allow_mock')):
        raise ValueError('Config must not contain credentials, replacement connectors or mock responses')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default=str(LAB / 'configs/clean_qsv_select.json'))
    parser.add_argument('--manifest', help='Explicit clean or future degraded manifest; no transformations are performed')
    parser.add_argument('--run-id')
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding='utf-8'))
    validate_config(cfg)
    manifest_path = Path(args.manifest) if args.manifest else LAB / cfg['source_manifest']
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    source = (LAB / manifest['local_path']).resolve()
    if sha256(source) != manifest['sha256']:
        raise ValueError('Source hash mismatch')
    if manifest.get('variant') not in ('clean', 'degraded'):
        raise ValueError('Manifest must declare clean or degraded')
    key = os.environ.get(cfg['credential_env'])
    if not key:
        raise SystemExit('BLOCKED: set environment variable '+cfg['credential_env'])
    run_id = args.run_id or time.strftime('%Y%m%dT%H%M%S') + '_' + uuid.uuid4().hex[:8]
    if Path(run_id).name != run_id or run_id in ('.','..'):
        raise ValueError('run-id must be a single directory name')
    run = new_run(LAB / 'runs', run_id)
    store = run / 'SkillBank'
    write_json(run / 'config.json', cfg)
    write_json(run / 'source_manifest.json', manifest)
    before = code_inventory(Path(cfg['upstream_path']))
    write_json(run / 'upstream_before.json', before)
    write_json(run / 'invocation.json', {'started_at':utc(),'argv':[sys.executable,'-B',*sys.argv],
        'cwd':str(Path.cwd()),'python':sys.version,'run_id':run_id,'store_path':str(store),
        'initial_store_entries':list(store.iterdir()),'variant':manifest['variant'],
        'secret_env_name':cfg['credential_env'],'real_generation':True})
    sys.dont_write_bytecode = True
    sys.path.insert(0, cfg['upstream_path'])
    from autoskill import AutoSkill, AutoSkillConfig
    from AutoSkill4Doc import extract_from_doc
    from AutoSkill4Doc.document.file_loader import load_file_units
    from autoskill.llm.openai import OpenAIChatLLM
    units, actual_path = load_file_units(str(source), max_files=1)
    if len(units)!=1 or not units[0].get('text','').strip():
        raise RuntimeError('Official file loader did not return one nonempty document')
    write_json(run / 'parsed_text_units.json', {'source_file':actual_path,'units':units})
    llm = dict(cfg['llm'], api_key=key)  # Memory only; never serialize this dictionary.
    sdk = AutoSkill(AutoSkillConfig(llm=llm, embeddings=cfg['embeddings'],
        store={'provider':'local','path':str(store)}, maintenance_strategy='llm'))
    calls = []
    lock = threading.Lock()
    counts = Counter()
    upstream_resolved = str(Path(cfg['upstream_path']).resolve()).lower()
    secrets = [os.environ[k] for k in (cfg['credential_env'],'OPENAI_API_KEY','ARK_API_KEY','DASHSCOPE_API_KEY') if os.environ.get(k)]

    def redact(text):
        for secret in secrets:
            text = text.replace(secret, '[REDACTED]')
        return text

    def log(message):
        line = utc() + ' ' + redact(str(message))
        with (run / 'pipeline.log').open('a',encoding='utf-8') as f: f.write(line+'\n')
        print(line, flush=True)

    original = OpenAIChatLLM._post_json

    def observed(client, *, payload, stream):
        with lock:
            tokens = sum(c.get('usage',{}).get('total_tokens',0) for c in calls)
            if len(calls)>=cfg['max_http_calls'] or tokens>=cfg['max_observed_total_tokens']:
                raise RuntimeError('P0 external observation budget exhausted')
            n = len(calls)+1
            rec = {'number':n,'started_at':utc(),'model_requested':client.model,'endpoint':client._build_url(),
                   'official_client':inspect.getsourcefile(original),'stack':[]}
            frame = inspect.currentframe().f_back
            while frame:
                if frame.f_code.co_filename.lower().startswith(upstream_resolved):
                    rec['stack'].append({'file':frame.f_code.co_filename,'function':frame.f_code.co_name,'line':frame.f_lineno})
                frame = frame.f_back
            calls.append(rec)
        call_dir = run / 'http' / f'{n:03d}'
        # Only the body is logged. Authorization headers and SDK configuration are never serialized.
        write_json(call_dir / 'request.json', json.loads(redact(json.dumps(payload, ensure_ascii=False))))
        start = time.monotonic()
        try:
            body = original(client, payload=payload, stream=stream)
            (call_dir / 'response.json').write_text(redact(body),encoding='utf-8')
            parsed = json.loads(body)
            rec.update({'success':True,'response_id':parsed.get('id'),'model_returned':parsed.get('model'),
                'usage':parsed.get('usage',{}),'response_sha256':hashlib.sha256(body.encode()).hexdigest(),
                'finish_reasons':[c.get('finish_reason') for c in parsed.get('choices',[])],
                'returned_body_unchanged':True})
            return body
        except Exception as e:
            rec.update({'success':False,'exception_type':type(e).__name__,'error':redact(str(e))})
            raise
        finally:
            rec['seconds'] = round(time.monotonic()-start,3)
            write_json(call_dir / 'event.json', rec)
            write_json(run / 'model_calls.json', calls)
            log(f'HTTP call {n}: success={rec.get("success")} tokens={rec.get("usage",{}).get("total_tokens")}')

    def trace(frame, event, arg):
        if event=='call' and frame.f_code.co_filename.lower().startswith(upstream_resolved):
            name = frame.f_code.co_name
            if name in ('extract_from_doc','build','ingest_document','extract_skills','compile_skills','register_versions',
                        '_plan_unit_skills','_expand_planned_skill','_resume_or_stream_compile','_resume_or_stream_register',
                        'sync_visible_skill_tree','_upsert_store_skill','load_file_units'):
                counts[f'{frame.f_code.co_filename}:{frame.f_code.co_firstlineno}:{name}'] += 1

    OpenAIChatLLM._post_json = observed
    sys.setprofile(trace)
    threading.setprofile(trace)
    exit_code = 1
    try:
        log('Official public API starting: one document, empty independent SkillBank')
        result = extract_from_doc(sdk=sdk, file_path=str(source),
            registry_root=str(store / '.runtime/document_registry'),
            metadata={k:manifest[k] for k in ('source_id','source_url','source_commit','sha256','classification','variant')},
            continue_on_error=False, dry_run=False, logger=log, **cfg['pipeline'])
        write_json(run / 'official_result.json', result)
        exit_code = 0 if result.get('total_skill_specs',0)>0 and not result.get('errors') and result.get('status')=='completed' else 2
    except BaseException as e:
        write_json(run / 'exception.json', {'type':type(e).__name__,'message':redact(str(e)),
            'traceback':redact(traceback.format_exc())})
        log('Official build failed: '+redact(str(e)))
    finally:
        sys.setprofile(None)
        threading.setprofile(None)
        OpenAIChatLLM._post_json = original
        write_json(run / 'official_call_trace.json',dict(counts))
        after = code_inventory(Path(cfg['upstream_path']))
        write_json(run / 'upstream_after.json',after)
        write_json(run / 'execution.json',{'ended_at':utc(),'exit_code':exit_code,'upstream_unchanged':before==after,
            'http_attempts':len(calls),'http_successes':sum(c.get('success',False) for c in calls),
            'usage_totals':{k:sum(c.get('usage',{}).get(k,0) for c in calls) for k in ('prompt_tokens','completion_tokens','total_tokens')},
            'billed_cost':None,'cost_status':'NOT_PROVIDED_BY_API; no fabricated cost estimate',
            'budget_note':'Token threshold is checked before the next request; one response can exceed the threshold.',
            'missing_intermediates':[]})
        write_json(run / 'artifact_manifest.json', {p.relative_to(run).as_posix():sha256(p) for p in run.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'})
        print('RUN_DIRECTORY='+str(run),flush=True)
    raise SystemExit(exit_code)


if __name__=='__main__':
    main()
