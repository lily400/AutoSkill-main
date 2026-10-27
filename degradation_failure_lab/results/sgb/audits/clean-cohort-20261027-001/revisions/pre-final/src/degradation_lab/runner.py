import os
import re
import shutil
import uuid
from pathlib import Path
from .catalog import CaseManager
from .layout import case_path, generation_path
from .io import check_windows_run_path, inside, inventory, read, resolve_upstream, sha256, upstream_inventory, utc, write


def validate_config(cfg):
    # Observation supports the unchanged official OpenAI-compatible transport.
    # No service or model name is special-cased.
    llm = cfg.get('llm', {})
    if llm.get('provider') != 'openai': raise ValueError('Official OpenAI-compatible provider required; mock forbidden')
    allowed = {'provider', 'base_url', 'model', 'timeout_s', 'max_tokens', 'max_input_chars',
               'connector_factory', 'thinking_mode', 'proxy_mode', 'transport_retries', 'transport_retry_backoff_s', 'extra_headers', 'extra_body'}
    if set(llm) - allowed: raise ValueError('Unsupported or credential-bearing LLM config field')
    if llm.get('connector_factory') not in (None, 'degradation_lab.provider_adapter:build'):
        raise ValueError('Only the audited optional thinking adapter is allowed')
    if 'extra_headers' in llm or 'extra_body' in llm:
        raise ValueError('Request overrides are not supported by this audited baseline')
    if 'thinking_mode' in llm and llm.get('connector_factory') is None:
        raise ValueError('thinking_mode requires the audited connector')
    if any(k in llm for k in ('proxy_mode','transport_retries','transport_retry_backoff_s')) and llm.get('connector_factory') is None:
        raise ValueError('Transport settings require the audited connector')
    if llm.get('proxy_mode','system') not in ('system','direct'):
        raise ValueError('proxy_mode must be direct or system')
    retries=llm.get('transport_retries',0)
    if type(retries) is not int or not 0 <= retries <= 2:
        raise ValueError('transport_retries must be integer 0..2')
    delay=llm.get('transport_retry_backoff_s',1.0)
    if type(delay) not in (float,int) or not 0 <= delay <= 10:
        raise ValueError('transport_retry_backoff_s must be number 0..10')
    def credentials(value):
        if isinstance(value, dict):
            for k,v in value.items():
                if k.lower() in ('api_key', 'authorization', 'response', 'allow_mock', 'allow_mock_provider'):
                    raise ValueError('Credentials/mock overrides forbidden in persisted configuration')
                credentials(v)
        elif isinstance(value, list):
            for v in value: credentials(v)
    credentials(cfg)
    if cfg.get('embeddings', {}).get('provider') != 'hashing':
        raise ValueError('Current audited baseline uses official local hashing embeddings')
    for key in ('max_http_calls', 'max_observed_total_tokens'):
        if type(cfg.get(key)) is not int or cfg[key] < 1: raise ValueError('Positive budget required: ' + key)
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', cfg.get('credential_env', '')):
        raise ValueError('Invalid credential environment variable name')
    if not llm.get('model') or not llm.get('base_url'): raise ValueError('Explicit model and endpoint required')
    if not isinstance(cfg.get('pipeline'), dict): raise ValueError('Pipeline settings required')


class ExperimentRunner:
    def __init__(self, root, cases=None):
        self.root = Path(root).resolve()
        self.cases = cases or CaseManager(root)

    def resolve(self, case_id, condition_id):
        bundle = self.cases.load(case_id)
        condition, manifest = self.cases.condition(bundle, condition_id)
        config = read(inside(self.root, bundle['case']['generation_config']))
        validate_config(config)
        config['pipeline'] = dict(config['pipeline'], **bundle['case']['pipeline_overrides'])
        # This is the official file-count limit, not a change to extraction.
        config['pipeline']['max_documents'] = len(manifest['inputs'])
        return bundle, condition, manifest, config

    def plan(self, case_id, condition_id, repeat=1):
        if type(repeat) is not int or repeat < 1: raise ValueError('repeat must be a positive integer')
        _, _, manifest, config = self.resolve(case_id, condition_id)
        upstream = resolve_upstream(self.root)
        width = 10 if case_path(self.root,case_id).parent == self.root/'cases/sgb' else 12
        target = generation_path(self.root, case_id, condition_id, 'r' + '0'*width)
        check_windows_run_path(target)
        return {'case_id':case_id, 'condition_id':condition_id, 'repeat':repeat,
                'input_count':len(manifest['inputs']), 'model':config['llm']['model'],
                'upstream_path':str(upstream),
                'output_pattern':target.parent.relative_to(self.root).as_posix()+'/<run_id>/'}

    def prepare(self, case_id, condition_id, run_id=None, fixture=False):
        bundle, condition, manifest, config = self.resolve(case_id, condition_id)
        width = 10 if case_path(self.root,case_id).parent == self.root/'cases/sgb' else 12
        run_id = run_id or 'r' + uuid.uuid4().hex[:width]
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', run_id): raise ValueError('Unsafe run_id')
        upstream = resolve_upstream(self.root)
        target = generation_path(self.root, case_id, condition_id, run_id)
        check_windows_run_path(target)
        from .artifacts import run_refs
        if any(r['run_id']==run_id for r in run_refs(self.root)):
            raise FileExistsError('Globally unique run_id already exists: ' + run_id)
        target.mkdir(parents=True, exist_ok=False)
        (target/'SkillBank').mkdir()
        (target/'inputs').mkdir()
        normalized = []
        for item in manifest['inputs']:
            src = inside(self.root, item['path'])
            dst = target/'inputs'/item['input_id']/src.name
            dst.parent.mkdir()
            shutil.copyfile(src, dst)
            if sha256(dst) != item['sha256']: raise ValueError('Input changed while snapshotting')
            normalized.append(dict(item, original_path=item['path'], path=dst.relative_to(target).as_posix(),
                                   execution_path=str(dst)))
        write(target/'input_manifest.json', dict(manifest, inputs=normalized))
        write(target/'sources.json', [self.cases.sources.sources[s] for s in bundle['case']['source_ids']])
        for name in ('case', 'rules', 'conditions'): write(target/(name+'.json'), bundle[name])
        write(target/'condition.json', condition)
        write(target/'config.json', config)
        # Store environment paths separately from reusable generation parameters.
        write(target/'environment.json', {'upstream_path':str(upstream)})
        write(target/'upstream_before.json', upstream_inventory(upstream))
        package = self.root/'src/degradation_lab'
        if package.is_dir(): shutil.copytree(package, target/'wrapper_snapshot/degradation_lab',
                                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        write(target/'wrapper_manifest.json', inventory(target/'wrapper_snapshot'))
        write(target/'invocation.json', {'started_at':utc(), 'case_id':case_id, 'condition_id':condition_id,
            'run_id':run_id, 'store_path':str(target/'SkillBank'), 'initial_store_entries':[],
            'real_generation':False, 'execution_kind':'fixture' if fixture else 'official'})
        write(target/'status.json', {'state':'PREPARED', 'real_generation':False, 'updated_at':utc()})
        return target

    def run(self, case_id, condition_id, run_id=None, resume_from=None, resume_budget=None):
        if resume_from:
            from .artifacts import resolve_run
            identity, parent = resolve_run(self.root, resume_from)
            if (identity['case_id'], identity['condition_id']) != (case_id, condition_id):
                raise ValueError('Resume case/condition mismatch')
            bundle, config = {'case':read(parent/'case.json')}, read(parent/'config.json')
            validate_config(config)
        else:
            bundle, _, _, config = self.resolve(case_id, condition_id)
        gate_path = bundle['case'].get('execution_gate')
        if gate_path:
            gate = read(inside(self.root, gate_path))
            if gate.get('status') != 'PASS':
                raise RuntimeError('BLOCKED: execution gate has not passed: ' + gate_path)
            if gate.get('authorization_contract') == 'exact-generation-v1':
                request = gate.get('requested_generation', {})
                configuration = bundle['case']['generation_config']
                if (request.get('authorization_status') != 'AUTHORIZED'
                        or request.get('run_id') != run_id or request.get('case_id') != case_id
                        or request.get('condition_id') != condition_id
                        or request.get('configuration') != configuration
                        or request.get('configuration_sha256') != sha256(inside(self.root, configuration))
                        or any(request.get(k) != config[k] for k in ('max_http_calls','max_observed_total_tokens'))
                        or resume_from is not None):
                    raise RuntimeError('BLOCKED: exact generation identity/configuration/budget is not authorized')
        if not os.environ.get(config['credential_env']):
            raise RuntimeError('BLOCKED: set environment variable ' + config['credential_env'])
        if resume_from:
            from .resume import prepare_resume
            target = prepare_resume(self.root, resume_from, run_id, budget_overrides=resume_budget)
        else:
            target = self.prepare(case_id, condition_id, run_id)
        from .adapter import execute
        try:
            code = execute(target)
        except Exception as e:
            # Setup failures precede the observer's finally block; retain them too.
            import traceback
            message = str(e).replace(os.environ[config['credential_env']], '[REDACTED]')
            write(target/'exception.json', {'type':type(e).__name__, 'message':message,
                'traceback':traceback.format_exc().replace(os.environ[config['credential_env']], '[REDACTED]')})
            write(target/'status.json', {'state':'FAILED', 'real_generation':False, 'updated_at':utc()})
            write(target/'upstream_after.json',upstream_inventory(Path(read(target/'environment.json')['upstream_path'])))
            write(target/'execution.json', {'exit_code':1, 'http_attempts':0, 'usage_totals':{},
                'missing_intermediates':['ingest','extract','compile','register'], 'setup_failed':True})
            write(target/'artifact_manifest.json',{p:h for p,h in inventory(target).items() if p!='artifact_manifest.json'})
            code=1
        # Small ledger; artifacts stay isolated and untracked by default.
        index = self.root/'results/run_index.jsonl'
        index.parent.mkdir(exist_ok=True)
        import json
        with index.open('a', encoding='utf-8') as f:
            f.write(json.dumps({'case_id':case_id, 'condition_id':condition_id, 'run_id':target.name,
                                'path':target.relative_to(self.root).as_posix(), 'exit_code':code,
                                'ended_at':utc()}, ensure_ascii=False)+'\n')
        return target, code
