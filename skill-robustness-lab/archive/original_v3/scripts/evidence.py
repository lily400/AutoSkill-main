"""Offline evidence collection. Never calls a model or edits official artifacts."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SCHEMA = 'skill-lab-evidence-v2'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def manifest(root, exclude=()):
    root = Path(root)
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob('*'))
            if p.is_file() and p.relative_to(root).as_posix() not in exclude}

def verify(root, expected):
    actual = manifest(root)
    return {'missing': sorted(expected.keys()-actual.keys()),
            'changed': sorted(k for k in expected.keys() & actual.keys() if expected[k] != actual[k]),
            'extra': sorted(actual.keys()-expected.keys())}

def freeze(run):
    """The manifest excludes only itself; reports/reviews belong outside sealed runs."""
    save(Path(run)/'checksums.json', manifest(run, exclude=('checksums.json',)))

def check_frozen(run):
    p = Path(run)/'checksums.json'
    if not p.is_file():
        return {'valid': False, 'reason': 'missing_checksums'}
    delta = verify(run, read(p))
    delta['extra'] = [x for x in delta['extra'] if x != 'checksums.json']
    return {'valid': not any(delta.values()), **delta}

def collect(run):
    run = Path(run)
    errors = []
    def load(p, default=None):
        if not p.is_file():
            errors.append('missing: '+p.relative_to(run).as_posix()); return default
        try: return read(p)
        except (ValueError, OSError) as e:
            errors.append('unreadable: '+p.relative_to(run).as_posix()+': '+type(e).__name__); return default
    dirs = sorted((run/'official/store/.runtime/intermediate_runs').glob('*'))
    dirs = [d for d in dirs if d.is_dir()]
    summary, state, ingest, extract, compiled, registered = {}, {}, {}, {}, {}, {}
    if len(dirs) != 1:
        errors.append('expected exactly one official intermediate run')
    else:
        d=dirs[0]
        summary=load(d/'final/summary.json', {})
        state=load(d/'status.json', {})
        ingest=load(d/'ingest/result.json', {})
        extract=load(d/'extract/result.json', {})
        compiled=load(d/'compile/result.json', {})
        registered=load(d/'register/result.json', {})
    for stage, obj in [('summary',summary),('ingest',ingest),('extract',extract),('compile',compiled),('register',registered)]:
        if obj.get('errors'): errors.append(stage+': '+str(obj['errors']))
    if state.get('status') != 'completed' or state.get('unresolved_doc_ids') or state.get('unresolved_nodes'):
        errors.append('official stages incomplete or unresolved')
    skills=[]
    for p in sorted((run/'official/store/Users').glob('*/*/SKILL.md')):
        text=p.read_text(encoding='utf-8-sig')
        body=text.split('---',2)[-1].strip() if text.startswith('---') else text.strip()
        skills.append({'path':p.relative_to(run).as_posix(), 'sha256':sha(p), 'body_chars':len(body)})
    counts={k:summary.get(k,0) for k in ('documents','windows','support_records','skill_drafts','skill_specs','store_upserts','visible_children')}
    for k,v in counts.items():
        if not isinstance(v,int) or v<=0: errors.append('zero or missing '+k)
    if counts['documents'] != 1: errors.append('expected one document')
    if not skills or any(s['body_chars']==0 for s in skills): errors.append('missing or empty canonical task skill')
    if len(skills)!=counts['store_upserts'] or len(skills)!=counts['visible_children']:
        errors.append('canonical count disagrees with official output')
    for obj, field in [(ingest,'documents'),(ingest,'windows'),(extract,'support_records'),(extract,'skill_drafts'),(compiled,'skill_specs')]:
        records=obj.get(field,[])
        if not records or not all(isinstance(v,dict) and v for v in records): errors.append('empty actual '+field)
        if len(records)!=counts.get(field,len(records)): errors.append('actual count mismatch '+field)
    for draft in extract.get('skill_drafts',[]):
        if not any(draft.get(k) for k in ('workflow_steps','constraints','intervention_moves','output_contract')):
            errors.append('draft has no substantive steps/constraints/output contract')
    for spec in compiled.get('skill_specs',[]):
        if not str(spec.get('skill_body','')).strip(): errors.append('compiled skill body empty')
    windows=ingest.get('windows',[])
    docs=ingest.get('documents',[])
    coverage=[]
    for doc in docs:
        text=doc.get('raw_text','')
        spans=[]; flags=[False]*len(text)
        for w in windows:
            if w.get('doc_id')!=doc.get('doc_id'): continue
            s=w.get('span',{}); a=s.get('start',-1); b=s.get('end',-1)
            valid=isinstance(a,int) and isinstance(b,int) and 0<=a<=b<=len(text) and text[a:b]==w.get('text','')
            exact=w.get('text','')
            resolved=(a,b) if valid else None
            # Upstream spans can be offset by stripped whitespace. Only recover
            # a unique literal match; never silently trust approximate offsets.
            if not valid and exact:
                pos=text.find(exact)
                if pos>=0 and text.find(exact,pos+1)<0: resolved=(pos,pos+len(exact))
            spans.append({'window_id':w.get('window_id'),'start':a,'end':b,'span_matches_text':valid,
                          'resolved_by':'official_span' if valid else 'unique_exact_text' if resolved else 'unresolved',
                          'resolved_span':list(resolved) if resolved else None})
            if resolved:
                a2,b2=resolved; flags[a2:b2]=[True]*(b2-a2)
        missing=[]; start=None
        for j in range(len(text)+1):
            omitted=j<len(text) and not flags[j]
            if omitted and start is None: start=j
            if not omitted and start is not None:
                fragment=text[start:j]
                if fragment.strip(): missing.append({'start':start,'end':j,'text':fragment})
                start=None
        meaningful=sum(not c.isspace() for c in text)
        covered=sum(not c.isspace() and flags[j] for j,c in enumerate(text))
        coverage.append({'doc_id':doc.get('doc_id'),'raw_chars':len(text),'covered_nonspace_ratio':covered/max(1,meaningful),'coverage_is_lower_bound':any(s['resolved_span'] is None for s in spans),'unresolved_note':'Unresolved windows make unproven ranges uncertain, not confirmed omissions.','spans':spans,'omitted_ranges':missing})
    snapshots=list((run/'input').glob('*'))
    if len(snapshots)==1 and len(docs)==1:
        if snapshots[0].read_text(encoding='utf-8-sig').rstrip()!=docs[0].get('raw_text','').rstrip():
            errors.append('snapshot differs from official raw_text')
    else: errors.append('expected exactly one input snapshot and official document')
    rules=[]
    contract_path=run/'evaluation/contract.json'
    if contract_path.exists():
        contract=load(contract_path,{})
        for rule in contract.get('rules',[]):
            quote=rule['source_text']
            # Exact source matching is coverage evidence, never semantic scoring.
            rules.append({'id':rule['id'],'source_text':quote,
                          'present_in_variant':any(quote in d.get('raw_text','') for d in docs),
                          'window_ids':[w.get('window_id') for w in windows if quote in w.get('text','')],
                          'semantic_verdict':'pending'})
    trace_files=sorted((run/'trace').glob('*.json'))
    calls=[]; trace_errors=[]
    for p in trace_files:
        if p.name=='session.json': continue
        try: call=read(p)
        except ValueError: trace_errors.append(p.name+': invalid JSON'); continue
        if 'call_id' in call:
            calls.append(call)
            if call.get('state')=='started': trace_errors.append(p.name+': incomplete response')
    return {'schema':SCHEMA, 'pipeline_pass':not errors,'errors':errors,'counts':counts,
            'canonical_skills':skills,'official_summary':summary,'window_coverage':coverage,'rule_coverage':rules,
            'trace':{'calls':len(calls),'completed':sum(c.get('state')=='completed' for c in calls),
                     'failed':sum(c.get('state')=='failed' for c in calls),'errors':trace_errors,
                     'available':bool(calls),'reported_models':sorted({str(c.get('response_json',{}).get('model')) for c in calls if isinstance(c.get('response_json'),dict) and c['response_json'].get('model')} )},
            'semantic_review':'pending','task_execution':'not_run','independent_judging':'not_run',
            'note':'Window coverage and structural generation checks are not semantic or execution success.'}
