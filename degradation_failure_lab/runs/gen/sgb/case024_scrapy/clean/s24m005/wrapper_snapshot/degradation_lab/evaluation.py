import csv
import json
from pathlib import Path
from .artifacts import inspect_run, resolve_run, run_refs
from .catalog import CaseManager
from .io import inside, read, sha256, utc, write
from .schema import check, unique


def validate_evaluation(root, value):
    check('evaluation', value)
    manager = CaseManager(root)
    bundle = manager.load(value['case_id'])
    manager.condition(bundle, value['condition_id'])
    identity, _ = resolve_run(root, value['run_id'])
    if (identity['case_id'], identity['condition_id']) != (value['case_id'], value['condition_id']):
        raise ValueError('Evaluation/run identifiers disagree')
    report, exports = inspect_run(root, value['run_id'])
    skills = {s['skill_id'] for s in exports['traceability'] if s['registered']}
    refs = {'window':{w['window_id'] for w in exports['windows']},
            'support':{s['support_id'] for s in exports['support_records']},
            'draft':{d['draft_id'] for d in exports['skill_drafts']},
            'spec':{s['skill_id'] for s in exports['skill_specs']}, 'skill':skills}
    rules = {r['rule_id'] for r in bundle['rules']['rules']}
    unique(value['records'], 'record_id')
    for r in value['records']:
        if r['rule_id'] not in rules: raise ValueError('Unknown evaluation rule')
        manager.evidence(bundle['case'], r['source_evidence'])
        if not set(r['skill_ids']).issubset(skills): raise ValueError('Unknown final skill in evaluation')
        for ref in r['trace_refs']:
            if ref['entity_id'] not in refs[ref['stage']]: raise ValueError('Unknown trace entity')
        if r['skill_ids']:
            linked=set()
            for skill in exports['traceability']:
                if skill['skill_id'] not in r['skill_ids']: continue
                linked.update(('window',v) for v in skill['window_ids'])
                linked.update(('support',v) for v in skill['support_ids'])
                linked.update(('draft',v) for v in skill['source_draft_ids'])
                linked.update([('spec',skill['skill_id']),('skill',skill['skill_id'])])
            if any((ref['stage'],ref['entity_id']) not in linked for ref in r['trace_refs']):
                raise ValueError('Trace reference does not belong to mapped skills')
        for evidence in r['generated_evidence']:
            if evidence['skill_id'] not in r['skill_ids']: raise ValueError('Generated evidence skill is not mapped')
            _, run = resolve_run(root, value['run_id'])
            skill = next(s for s in exports['traceability'] if s['skill_id']==evidence['skill_id'])
            if max(evidence['lines']) > len(Path(skill['canonical_file']).read_text(encoding='utf-8').splitlines()):
                raise ValueError('Generated evidence line outside SKILL.md')
    p = value['provenance']
    if bool(p.get('file')) != bool(p.get('sha256')): raise ValueError('Incomplete review provenance')
    if p and sha256(inside(root,p['file'])) != p['sha256']:
        raise ValueError('Evaluation provenance changed')
    return value


def init_evaluation(root, run_id, evaluation_id='initial_review'):
    identity, _ = resolve_run(root, run_id)
    bundle = CaseManager(root).load(identity['case_id'])
    records = [dict(record_id=r['rule_id']+'_preservation', rule_id=r['rule_id'],
        judgment_scope='rule_preservation', status='unreviewed', source_evidence=r['source_evidence'],
        skill_ids=[], trace_refs=[], generated_evidence=[], error_types=[], notes='No quality judgment yet')
        for r in bundle['rules']['rules']]
    value = dict(schema_version=1, evaluation_id=evaluation_id, **{k:identity[k] for k in ('case_id','condition_id','run_id')},
                 created_at=utc(), method='manual', reviewer='pending', provenance={}, records=records)
    validate_evaluation(root, value)
    target = inside(root, f"evaluations/{identity['case_id']}/{identity['condition_id']}/{run_id}/{evaluation_id}.json")
    if target.exists(): raise FileExistsError(target)
    write(target, value)
    return target


def aggregate(root, output, case_ids=None):
    root, output = Path(root), Path(output)
    manager = CaseManager(root)
    rows, runs = [], []
    for identity in run_refs(root):
        if case_ids and identity['case_id'] not in case_ids: continue
        report, _ = inspect_run(root, identity['run_id'])
        if report['execution_kind'] == 'fixture': continue
        runs.append(report)
        pattern = f"evaluations/{identity['case_id']}/{identity['condition_id']}/{identity['run_id']}/*.json"
        reviews = [validate_evaluation(root, read(p)) for p in sorted(root.glob(pattern))]
        bundle = manager.load(identity['case_id'])
        for rule in bundle['rules']['rules']:
            found = [(v,r) for v in reviews for r in v['records'] if r['rule_id']==rule['rule_id']]
            if not found:
                found = [(None, {'record_id':None, 'judgment_scope':'rule_preservation', 'status':'unreviewed',
                                  'skill_ids':[], 'error_types':[], 'notes':'No review record'})]
            for review, record in found:
                rows.append({**{k:identity[k] for k in ('case_id','condition_id','run_id')},
                    'rule_id':rule['rule_id'], 'evaluation_id':review['evaluation_id'] if review else None,
                    'record_id':record['record_id'], 'judgment_scope':record['judgment_scope'], 'status':record['status'],
                    'skill_ids':record['skill_ids'], 'error_types':record['error_types'],
                    'source_evidence':record.get('source_evidence',rule['source_evidence']),
                    'trace_refs':record.get('trace_refs',[]), 'generated_evidence':record.get('generated_evidence',[]),
                    'method':review['method'] if review else None, 'reviewer':review['reviewer'] if review else None,
                    'engineering_status':report['status'], 'notes':record['notes']})
    output.mkdir(parents=True, exist_ok=True)
    write(output/'runs.json', runs)
    write(output/'rule_results.json', rows)
    with (output/'rule_results.csv').open('w', encoding='utf-8-sig', newline='') as f:
        fields = ['case_id','condition_id','run_id','rule_id','evaluation_id','record_id','judgment_scope',
                  'status','skill_ids','error_types','source_evidence','trace_refs','generated_evidence',
                  'method','reviewer','engineering_status','notes']
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for r in rows: writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in r.items()})
    # Multiple reviews/addition records are not collapsed into a fabricated accuracy rate.
    return {'runs':len(runs), 'rule_review_rows':len(rows), 'output':str(output),
            'quality_metric':'No automatic correctness score; review scopes and revisions retained'}
