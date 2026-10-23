"""Reuse P0's unchanged official API invocation and transparent HTTP observer."""
from collections import Counter
import hashlib, inspect, json, os, sys, threading, time, traceback
import urllib.request, urllib.error
from urllib.parse import urlsplit
from pathlib import Path

from .io import read, sha256, utc, write as write_json, upstream_inventory as code_inventory


def execute(run):
    cfg = read(run/'config.json')
    key = os.environ[cfg['credential_env']]
    upstream = Path(read(run/'environment.json')['upstream_path'])
    before = read(run/'upstream_before.json')
    store = run/'SkillBank'
    resume = read(run/'resume.json') if (run/'resume.json').is_file() else None
    if resume:
        from .io import inventory
        from .resume import checked_finder, guard_request
        if inventory(store) != resume['seed_skillbank']:
            raise RuntimeError('Copied checkpoint changed before execution')
        parent = Path(resume['parent_path'])
        if sha256(parent/'artifact_manifest.json') != resume['parent_manifest_sha256'] or any(
                sha256(parent/p) != h for p,h in read(parent/'artifact_manifest.json').items()):
            raise RuntimeError('Parent run changed before recovery')
    elif list(store.iterdir()):
        raise RuntimeError('SkillBank must be empty before execution')
    input_manifest = read(run/'input_manifest.json')
    if resume and (code_inventory(upstream) != before or any(
            sha256(Path(i['execution_path'])) != i['sha256'] for i in input_manifest['inputs'])):
        raise RuntimeError('Frozen source or upstream changed before recovery')
    source = Path(resume['source_path']) if resume else run/'inputs'
    prior_attempts = resume['prior_http_attempts'] if resume else 0
    prior_usage = resume['prior_usage_totals'] if resume else {}
    invocation = read(run/'invocation.json')
    invocation.update(real_generation=True, argv=[sys.executable, '-B', *sys.argv], python=sys.version)
    write_json(run/'invocation.json', invocation)
    write_json(run/'status.json', {'state':'RUNNING', 'real_generation':True, 'updated_at':utc()})
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(upstream))
    from autoskill import AutoSkill, AutoSkillConfig
    from AutoSkill4Doc import extract_from_doc
    from AutoSkill4Doc.document.file_loader import load_file_units
    from autoskill.llm.openai import OpenAIChatLLM
    from .provider_adapter import ConfiguredOpenAIChatLLM, limited_transport_retry, retryable_transport_error
    units, actual_path = load_file_units(str(source), max_files=len(input_manifest['inputs']))
    if len(units)!=len(input_manifest['inputs']) or not all(u.get('text','').strip() for u in units):
        raise RuntimeError('Official file loader did not parse every nonempty input')
    write_json(run / 'parsed_text_units.json', {'source_file':actual_path,'units':units})
    llm = dict(cfg['llm'], api_key=key)  # Memory only; never serialize this dictionary.
    sdk = AutoSkill(AutoSkillConfig(llm=llm, embeddings=cfg['embeddings'],
        store={'provider':'local','path':str(store)}, maintenance_strategy='llm'))
    calls = []
    lock = threading.Lock()
    counts = Counter()
    upstream_resolved = str(upstream.resolve()).lower()
    secrets = [os.environ[k] for k in (cfg['credential_env'],'OPENAI_API_KEY','ARK_API_KEY','DASHSCOPE_API_KEY') if os.environ.get(k)]

    def redact(text):
        for secret in secrets:
            text = text.replace(secret, '[REDACTED]')
        return text

    def log(message):
        line = utc() + ' ' + redact(str(message))
        with (run / 'pipeline.log').open('a',encoding='utf-8') as f: f.write(line+'\n')
        print(line, flush=True)

    # Safe route diagnostics; no proxy credentials or URL parameters are persisted.
    try:
        system_proxy=urllib.request.getproxies().get('https')
        proxy=urlsplit(system_proxy if '://' in (system_proxy or '') else 'http://'+system_proxy) if system_proxy else None
        proxy_data={'proxy_mode':cfg['llm'].get('proxy_mode','system'),
                    'system_https_proxy_present':bool(system_proxy),
                    'system_https_proxy_host':proxy.hostname if proxy else None,
                    'system_https_proxy_port':proxy.port if proxy else None,
                    'transport_retries':cfg['llm'].get('transport_retries',0)}
    except (TypeError,ValueError):
        proxy_data={'proxy_mode':cfg['llm'].get('proxy_mode','system'), 'diagnostic_error':True}
    write_json(run/'network_diagnostics.json',proxy_data)
    original_base=OpenAIChatLLM._post_json
    original_custom=ConfiguredOpenAIChatLLM._post_json

    def observed(client, *, payload, stream):
        original=original_custom if isinstance(client,ConfiguredOpenAIChatLLM) else original_base
        logical_id=None
        def send_once(attempt_index):
            nonlocal logical_id
            with lock:
                tokens=prior_usage.get('total_tokens',0)+sum(c.get('usage',{}).get('total_tokens',0) for c in calls)
                if prior_attempts+len(calls)>=cfg['max_http_calls'] or tokens>=cfg['max_observed_total_tokens']:
                    raise RuntimeError('P0 external observation budget exhausted')
                n=len(calls)+1
                if logical_id is None: logical_id=n
                rec={'number':n,'logical_call_id':logical_id,'attempt_index':attempt_index,
                     'retry_of':logical_id if attempt_index>1 else None,
                     'started_at':utc(),'model_requested':client.model,
                     'endpoint':client._build_url(),
                     'official_client':inspect.getsourcefile(original),'stack':[]}
                frame=inspect.currentframe().f_back
                while frame:
                    if frame.f_code.co_filename.lower().startswith(upstream_resolved):
                        rec['stack'].append({'file':frame.f_code.co_filename,
                                             'function':frame.f_code.co_name,'line':frame.f_lineno})
                    frame=frame.f_back
                if resume:
                    guard_request(resume, payload, rec['stack'])
                calls.append(rec)
            call_dir=run/'http'/f'{n:03d}'
            write_json(call_dir/'request.json',json.loads(redact(json.dumps(payload,ensure_ascii=False))))
            start=time.monotonic()
            try:
                body=original(client,payload=payload,stream=stream)
                (call_dir/'response.json').write_text(redact(body),encoding='utf-8')
                parsed=json.loads(body)
                rec.update({'success':True,'response_id':parsed.get('id'),
                    'model_returned':parsed.get('model'),'usage':parsed.get('usage',{}),
                    'response_sha256':hashlib.sha256(body.encode()).hexdigest(),
                    'finish_reasons':[c.get('finish_reason') for c in parsed.get('choices',[])],
                    'returned_body_unchanged':True})
                return body
            except Exception as e:
                rec.update({'success':False,'exception_type':type(e).__name__,
                    'error':redact(str(e)),'transport_retry_eligible':retryable_transport_error(e),
                    'reason_type':type(e.reason).__name__ if isinstance(e,urllib.error.URLError) else None})
                raise
            finally:
                rec['seconds']=round(time.monotonic()-start,3)
                write_json(call_dir/'event.json',rec)
                write_json(run/'model_calls.json',calls)
                log(f'HTTP call {n}: success={rec.get("success")} tokens={rec.get("usage",{}).get("total_tokens")}')

        return limited_transport_retry(send_once,retries=cfg['llm'].get('transport_retries',0),
            backoff_s=cfg['llm'].get('transport_retry_backoff_s',1.0),
            on_retry=lambda idx,exc:log(f'Transport retry after failed attempt {idx}: {type(exc).__name__}; POST delivery or billing may be unknown'))

    def trace(frame, event, arg):
        if event=='call' and frame.f_code.co_filename.lower().startswith(upstream_resolved):
            name = frame.f_code.co_name
            if name in ('extract_from_doc','build','ingest_document','extract_skills','compile_skills','register_versions',
                        '_plan_unit_skills','_expand_planned_skill','_resume_or_stream_compile','_resume_or_stream_register',
                        'sync_visible_skill_tree','_upsert_store_skill','load_file_units'):
                counts[f'{frame.f_code.co_filename}:{frame.f_code.co_firstlineno}:{name}'] += 1

    if resume:
        import importlib
        pipeline_module = importlib.import_module('AutoSkill4Doc.pipeline')
        original_finder = pipeline_module.find_intermediate_run_by_resume_key
        pipeline_module.find_intermediate_run_by_resume_key = checked_finder(original_finder, resume)
    OpenAIChatLLM._post_json = observed
    ConfiguredOpenAIChatLLM._post_json = observed
    sys.setprofile(trace)
    threading.setprofile(trace)
    exit_code = 1
    try:
        log('Official public API starting: ' + ('resume copied checkpoint; completed windows must not be resent' if resume else
            'snapshotted inputs, empty independent SkillBank'))
        result = extract_from_doc(sdk=sdk, file_path=str(source),
            registry_root=str(store / '.runtime/document_registry'),
            metadata={'case_id': invocation['case_id'], 'condition_id':invocation['condition_id'], 'lab_run_id':resume['pipeline_run_id'] if resume else run.name, 'input_manifest':input_manifest},
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
        if resume:
            pipeline_module.find_intermediate_run_by_resume_key = original_finder
        OpenAIChatLLM._post_json = original_base
        ConfiguredOpenAIChatLLM._post_json = original_custom
        write_json(run / 'official_call_trace.json',dict(counts))
        after = code_inventory(upstream)
        write_json(run / 'upstream_after.json',after)
        write_json(run / 'execution.json',{'ended_at':utc(),'exit_code':exit_code,'upstream_unchanged':before==after,
            'http_attempts':len(calls),'http_successes':sum(c.get('success',False) for c in calls),
            'cumulative_http_attempts':prior_attempts+len(calls),
            'cumulative_usage_totals':{k:prior_usage.get(k,0)+sum(c.get('usage',{}).get(k,0) for c in calls)
                for k in ('prompt_tokens','completion_tokens','total_tokens')},
            'usage_totals':{k:sum(c.get('usage',{}).get(k,0) for c in calls) for k in ('prompt_tokens','completion_tokens','total_tokens')},
            'billed_cost':None,'cost_status':'NOT_PROVIDED_BY_API; no fabricated cost estimate',
            'budget_note':'Token threshold is checked before the next request; one response can exceed the threshold.',
            'missing_intermediates':[]})
        write_json(run/'status.json', {'state':'COMPLETED' if exit_code==0 else 'FAILED', 'real_generation':True, 'updated_at':utc()})
        write_json(run / 'artifact_manifest.json', {p.relative_to(run).as_posix():sha256(p) for p in run.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'})
        print('RUN_DIRECTORY='+str(run),flush=True)
    return exit_code

