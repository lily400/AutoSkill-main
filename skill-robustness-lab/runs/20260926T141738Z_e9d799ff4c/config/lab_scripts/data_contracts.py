"""Offline strict schema, identity, provenance, split and integrity checks."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import math
import re
from evidence import read, save, sha, manifest, check_frozen, digest
from schema_defs import SCHEMAS, VERSION

class ContractError(ValueError): pass
def require(condition, message):
    if not condition: raise ContractError(message)
def utc(): return datetime.now(timezone.utc).isoformat()

def validate(value, spec, where='$'):
    """Validate only schema keywords used by schema_defs; reject unknown keywords."""
    allowed={'type','minLength','pattern','minimum','enum','anyOf','items','minItems','properties','required','additionalProperties'}
    require(not set(spec)-allowed, 'Unsupported schema keyword: '+str(set(spec)-allowed))
    if 'anyOf' in spec:
        for choice in spec['anyOf']:
            try: validate(value,choice,where); return
            except ContractError: pass
        raise ContractError(where+': no allowed type matched')
    if 'enum' in spec: require(value in spec['enum'], where+': invalid enum')
    kind=spec.get('type')
    checks={'string':lambda:isinstance(value,str), 'integer':lambda:type(value) is int,
        'number':lambda:type(value) in (float,int) and math.isfinite(value), 'boolean':lambda:type(value) is bool,
        'object':lambda:isinstance(value,dict), 'array':lambda:isinstance(value,list), 'null':lambda:value is None}
    if kind: require(checks[kind](),where+': expected '+kind)
    if isinstance(value,str):
        require(len(value)>=spec.get('minLength',0),where+': empty string')
        if 'pattern' in spec: require(re.fullmatch(spec['pattern'],value) is not None,where+': invalid pattern')
    if type(value) in (int,float) and 'minimum' in spec: require(value>=spec['minimum'],where+': below minimum')
    if isinstance(value,list):
        require(len(value)>=spec.get('minItems',0),where+': too few items')
        for i,item in enumerate(value): validate(item,spec.get('items',{}),f'{where}[{i}]')
    if isinstance(value,dict):
        props=spec.get('properties',{}); extra=spec.get('additionalProperties',True)
        require(set(spec.get('required',[]))<=value.keys(),where+': missing fields '+str(set(spec.get('required',[]))-value.keys()))
        if extra is False: require(not value.keys()-props.keys(),where+': unexpected fields '+str(value.keys()-props.keys()))
        for key,item in value.items():
            if key in props: validate(item,props[key],where+'.'+key)
            elif isinstance(extra,dict): validate(item,extra,where+'.'+key)

def validate_object(kind,value):
    validate(value,SCHEMAS[kind],kind)
    if kind=='program_ir':
        seen=set()
        for step in value['steps']:
            require(step['step_id'] not in seen,'IR duplicate step')
            require(set(step['depends_on'])<=seen,'IR dependency missing, forward or cyclic')
            seen.add(step['step_id'])
        for branch in value['branches']:
            require(set(branch['then_step_ids']+branch['else_step_ids'])<=seen,'IR branch references missing step')
        if value['status']=='validated': require(value['goal'] and seen and value['outputs'],'Validated IR must have content')
    if kind=='judgment':
        if value['status']=='not_run': require(value['passed'] is None and not value['checks'],'Unrun judgment cannot have a score')
        else:
            require(bool(value['checks']),'Judgment needs evidence checks')
            require(value['passed']==all(c['passed'] for c in value['checks']),'Judgment checks disagree')
            require(value['passed']==(value['status']=='passed'),'Judgment status disagrees')
    if kind=='comparison' and value['metrics_status']=='not_run':
        require(value['task_success_delta'] is None and value['semantic_score_delta'] is None,'Unrun metrics must be null')
    if kind=='execution':
        generated=value['mode']=='generated_skill'
        require((value['run_id'] is not None)==generated,'Only generated_skill execution references run')
        require((value['run_checksums_sha256'] is not None)==generated,'Generated execution needs sealed run hash')
        if value['status'] in ('not_run','blocked'):
            require(not value['actual_outputs'] and value['exit_code'] is None and value['error'] is None,
                    'Unrun execution cannot contain actual results')
        if value['status']=='completed': require(value['finished_at_utc'] is not None and value['exit_code'] is not None,'Completed execution lacks evidence')
    return value

def safe(root,value,base=None):
    root=Path(root).resolve()
    require(isinstance(value,str) and value and '\\' not in value and ':' not in value,'Invalid relative path')
    parts=PurePosixPath(value).parts
    require(not PurePosixPath(value).is_absolute() and '..' not in parts and '.' not in parts,'Path escape')
    p=root.joinpath(*parts)
    # Reject symlinks/junctions in the trusted data tree, even if they resolve inward.
    cursor=p
    while cursor!=root:
        require(not cursor.is_symlink() and not (getattr(cursor,'is_junction',lambda:False)()),'Linked data path forbidden')
        cursor=cursor.parent
    resolved=p.resolve()
    require(resolved.is_relative_to(root),'Path outside lab')
    if base: require(resolved.is_relative_to(Path(base).resolve()),'Cross-case path: '+value)
    return resolved

def filename(name):
    require(bool(name) and name not in ('.','..') and not any(c in name for c in '/\\:') and not name.endswith(('.', ' ')), 'Unsafe task filename')
    require(name.split('.')[0].upper() not in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]},'Reserved filename')
    return name

def unique(items,label): require(len(items)==len(set(items)),label+': duplicate IDs/paths')
def same(parent,child,fields):
    for key in fields: require(child[key]==parent[key],'Reference mismatch '+key)

def load_dataset(root, verify_seal=True):
    root=Path(root).resolve()
    index=read(root/'catalog/cases.json')
    require(set(index)=={'schema_version','case_files'} and index['schema_version']==VERSION,'Invalid cases index')
    require(isinstance(index['case_files'],list) and index['case_files'],'Empty case index')
    unique(index['case_files'],'case files')
    families=read(root/'catalog/families.json')
    require(isinstance(families,list) and families,'Empty family registry')
    for f in families: validate_object('family',f); unique(f['source_ids'],'family sources')
    unique([f['family_id'] for f in families],'families')
    family_by_id={f['family_id']:f for f in families}
    split=validate_object('split',read(root/'catalog/split.json'))
    assignments={a['case_id']:a for a in split['assignments']}
    require(len(assignments)==len(split['assignments']),'Duplicate split case')
    cases={}; variants={}; tasks={}; contracts={}; judges={}; registered=set(index['case_files'])
    source_splits={}; family_splits={}; hash_splits={}; source_defs={}; source_families={}
    def load(kind,path,base=None):
        p=safe(root,path,base); require(p.is_file(),'Missing '+path); registered.add(path)
        return validate_object(kind,read(p))
    for path in index['case_files']:
        c=load('case',path); key=c['case_key']; cr=root/'cases'/key; sr=root/'standards'/key
        require(path==f'cases/{key}/case.json','Case manifest not canonical')
        require(c['status']=='frozen','Case not frozen')
        require(c['case_id'] not in cases,'Duplicate case_id'); cases[c['case_id']]=c
        require(c['family_id'] in family_by_id,'Unknown family_id')
        require(assignments.get(c['case_id'])=={k:c[k] for k in ('case_id','source_id','family_id','split')},'Split assignment mismatch')
        if c['usage']=='development_only': require(c['split']=='development','Development case cannot be held out')
        if c['split']=='heldout_test':
            require(split['heldout_locked'] and family_by_id[c['family_id']]['review_status']=='reviewed','Heldout not independently grouped and locked')
        source=load('source',c['source_record'],cr)
        same(c,source,('case_id','source_id','source_version','family_id'))
        same({'document_file':c['source_file'],'document_sha256':c['source_sha256']},source,('document_file','document_sha256'))
        origin=source['origin']
        if any(origin[k] is None for k in ('uri','revision','license')): require(origin['unknown_reason'],'Unknown provenance needs reason')
        doc=safe(root,c['source_file'],cr/'clean'); require(doc.is_file() and sha(doc)==c['source_sha256'],'Clean hash mismatch')
        registered.add(c['source_file']); text=doc.read_bytes().decode('utf-8-sig')
        source_key=(c['source_id'],c['source_version'])
        require(source_defs.setdefault(source_key,c['source_sha256'])==c['source_sha256'],'Same source version has different bytes')
        require(source_families.setdefault(c['source_id'],c['family_id'])==c['family_id'],'One source assigned multiple families')
        for groups,item in ((source_splits,c['source_id']),(family_splits,c['family_id']),(hash_splits,c['source_sha256'])):
            require(groups.setdefault(item,c['split'])==c['split'],'Source/family/duplicate crosses splits')
        contract=load('contract',c['contract_file'],sr)
        same(c,contract,('case_id','source_id','source_version','source_sha256'))
        require(contract['contract_id'] not in contracts,'Duplicate contract_id'); contracts[contract['contract_id']]=contract
        unique([r['rule_id'] for r in contract['rules']],'rules')
        require(all(r['source_text'] in text for r in contract['rules']),'Contract quote absent from source')
        judge=load('judge',f'standards/{key}/judge.json',sr)
        same(c,judge,('case_id',)); require(judge['judge_id'] not in judges,'Duplicate judge_id'); judges[judge['judge_id']]=judge
        for f,h in (('implementation_file','implementation_sha256'),('reference_file','reference_sha256')):
            p=safe(root,judge[f],root/'scripts'); require(p.is_file() and sha(p)==judge[h],'Judge/reference code hash mismatch')
        local_tasks=[]
        unique(c['task_files'],'task paths')
        for path2 in c['task_files']:
            t=load('task',path2,sr/'tasks'); same(c,t,('case_id','source_id','family_id','split'))
            require(t['purpose']==c['split'],'Task purpose crosses dataset split')
            require(t['contract_id']==contract['contract_id'] and t['judge_id']==judge['judge_id'],'Task judge/contract reference mismatch')
            require(t['task_id'] not in tasks,'Duplicate task_id'); tasks[t['task_id']]=t; local_tasks.append(t)
            require(bool(t['inputs']),'Empty task input mapping')
            for files in (t['inputs'],t['expected']['outputs']):
                unique([k.lower() for k in files],'case-insensitive task files')
                for name in files: filename(name)
            require(not set(t['inputs']) & set(t['expected']['outputs']),'Expected output overwrites input')
            if t['expected']['outcome']=='error': require(not t['expected']['outputs'],'Expected error cannot produce outputs')
            require(set(t['covered_rule_ids'])<={r['rule_id'] for r in contract['rules']},'Unknown covered rule')
        fixture_path=sr/'fixtures.json'
        if fixture_path.exists():
            registered.add(fixture_path.relative_to(root).as_posix()); legacy=read(fixture_path)
            require(len(local_tasks)==len(legacy['cases']),'Fixture migration count mismatch')
            for old,t in zip(legacy['cases'],local_tasks):
                require(t['task_id'].endswith('.'+old['id']),'Fixture identity mismatch')
                expected={'outcome':old['expect'],'outputs':old['outputs'],'error_record':old.get('error_record'),'error_field':old.get('error_field')}
                require(t['inputs']=={'orders.csv':old['input']} and t['expected']==expected,'Fixture/task drift')
        local_variants=[]; unique(c['variant_files'],'variant paths')
        for path2 in c['variant_files']:
            v=load('variant',path2,cr/'variants'); same(c,v,('case_id','source_id','source_version','family_id'))
            require(v['variant_id'] not in variants,'Duplicate variant_id'); variants[v['variant_id']]=v; local_variants.append(v)
            require(v['contract_id']==contract['contract_id'],'Variant contract mismatch')
            p=safe(root,v['input_file'],cr); require(p.is_file() and sha(p)==v['input_sha256'],'Variant hash mismatch')
            registered.add(v['input_file'])
        clean=[v for v in local_variants if v['condition']=='clean']; require(len(clean)==1,'Exactly one clean variant required')
        clean=clean[0]
        require(clean['input_file']==c['source_file'] and clean['input_sha256']==c['source_sha256'],'Clean source mismatch')
        require(clean['degradation_file'] is None,'Clean has degradation metadata')
        for v in local_variants:
            require(v['clean_variant_id']==clean['variant_id'] and v['clean_sha256']==c['source_sha256'],'Wrong clean pairing')
            if v['condition']=='clean': continue
            require(v['input_sha256']!=c['source_sha256'],'Degraded input identical to clean')
            require(v['degradation_file'] is not None,'Missing degradation metadata')
            d=load('degradation',v['degradation_file'],cr/'degradation'); same(v,d,('case_id','variant_id'))
            gen=safe(root,d['generator']['file'],cr/'degradation/generators')
            require(gen.is_file() and sha(gen)==d['generator']['sha256'],'Degradation generator hash mismatch')
            registered.add(d['generator']['file'])
            cursor=0; pieces=[]
            for edit in d['edits']:
                a,b=edit['start'],edit['end']; require(cursor<=a<=b<=len(text),'Overlapping or invalid edit')
                require(text[a:b]==edit['before'],'Edit before-text mismatch')
                pieces.extend((text[cursor:a],edit['after'])); cursor=b
            pieces.append(text[cursor:])
            require(''.join(pieces)==safe(root,v['input_file']).read_bytes().decode('utf-8-sig'),'Edit replay mismatch')
            r=d['recoverability']
            require(set(r['rule_ids'])<={x['rule_id'] for x in contract['rules']},'Unknown recovery rule IDs')
            if r['status']=='recoverable':
                require(r['reviewer'] and set(r['rule_ids'])=={x['rule_id'] for x in contract['rules']},'Incomplete recovery audit')
    require(set(assignments)==set(cases),'Split has missing or unregistered cases')
    for f in families:
        require(set(f['source_ids'])=={c['source_id'] for c in cases.values() if c['family_id']==f['family_id']},'Family source membership mismatch')
    # An unregistered standards/case file must not silently enter the benchmark.
    actual={p.relative_to(root).as_posix() for part in ('cases','standards') for p in (root/part).rglob('*') if p.is_file()}
    require(actual=={p for p in registered if p.startswith(('cases/','standards/'))},'Unregistered data files: '+str(actual-registered))
    if split['formal_ready']:
        require(split['heldout_locked'] and any(c['split']=='heldout_test' for c in cases.values()),'Formal dataset missing heldout')
        require(all(f['review_status']=='reviewed' for f in families),'Formal family review pending')
        require(all(c['review_status']=='reviewed' for c in contracts.values()),'Formal contract review pending')
    if verify_seal: verify_dataset_seal(root)
    return {'cases':cases,'variants':variants,'tasks':tasks,'contracts':contracts,'judges':judges,'families':family_by_id,'split':split}

def data_manifest(root):
    root=Path(root); result={}
    for part in ('catalog','cases','standards'):
        for name,h in manifest(root/part).items():
            if part=='catalog' and name=='freeze.json': continue
            result[part+'/'+name]=h
    for path in (root/'standards').glob('*/judge.json'):
        j=read(path)
        for key in ('implementation_file','reference_file'): result[j[key]]=sha(safe(root,j[key]))
    return dict(sorted(result.items()))

def verify_dataset_seal(root):
    p=Path(root)/'catalog/freeze.json'; require(p.is_file(),'Dataset not frozen')
    seal=read(p); require(seal.get('schema_version')==VERSION,'Wrong freeze schema')
    require(seal['files']==data_manifest(root),'Frozen dataset changed, added or removed; create a new release')
    require(seal['content_sha256']==digest(seal['files']),'Freeze digest mismatch')
    return seal

def freeze_dataset(root):
    load_dataset(root,False); p=Path(root)/'catalog/freeze.json'
    if p.exists(): verify_dataset_seal(root); return p
    files=data_manifest(root)
    save(p,{'schema_version':VERSION,'frozen_at_utc':utc(),'files':files,'content_sha256':digest(files),
        'scope':'fixed documents/specifications/judge code; not scientific outcomes',
        'limitation':'Local integrity only. Keep an external immutable copy of this seal for published experiments.'})
    return p

def select(root,case_key,variant_id=None):
    ds=load_dataset(root); matches=[c for c in ds['cases'].values() if c['case_key']==case_key]
    require(len(matches)==1,'Unknown case'); c=matches[0]
    candidates=[v for v in ds['variants'].values() if v['case_id']==c['case_id'] and (v['variant_id']==variant_id if variant_id else v['condition']=='clean')]
    require(len(candidates)==1,'Unknown or cross-case variant'); v=candidates[0]
    if v['condition']=='degraded':
        d=read(safe(root,v['degradation_file']))
        require(d['recoverability']['status']=='recoverable','Main run requires reviewed recoverable variant')
    return ds,c,v

def sealed_run(root,run_id):
    validate(run_id,SCHEMAS['run']['properties']['run_id'],'run_id')
    p=safe(root,'runs/'+run_id)
    require(check_frozen(p)['valid'],'Run seal missing or changed')
    r=validate_object('run',read(p/'run.json')); require(r['run_id']==run_id,'Run directory ID mismatch')
    require(r['kind']=='generation' and r['finished_at_utc'] is not None,'Preflight/incomplete run is not experimental evidence')
    ct=read(p/'config/comparison_contract.json'); fp=read(p/'config/comparison_fingerprint.json')
    require(digest(ct)==fp['sha256']==r['comparison_fingerprint'],'Comparison fingerprint not derived from contract')
    return p,r,ct
