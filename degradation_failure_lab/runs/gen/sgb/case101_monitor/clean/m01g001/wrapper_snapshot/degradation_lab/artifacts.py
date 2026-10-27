"""Read-only inspection and trace exports for current case/condition/run layouts."""
from pathlib import Path
import re
from .io import inside, read, sha256, upstream_inventory, write


def run_refs(root):
    root = Path(root)
    refs = []
    paths = [p for pattern in ('case*/*/*/invocation.json', 'gen/sgb/*/*/*/invocation.json')
             for p in (root/'runs').glob(pattern)]
    for p in sorted(paths):
        p = inside(root, p.relative_to(root))
        invocation = read(p)
        refs.append({k:invocation[k] for k in ('case_id', 'condition_id', 'run_id')})
        refs[-1]['path'] = p.parent.relative_to(root).as_posix()
    keys = [(r['case_id'], r['condition_id'], r['run_id']) for r in refs]
    if len(keys) != len(set(keys)): raise ValueError('Duplicate run identity')
    if len({r['run_id'] for r in refs}) != len(refs):
        raise ValueError('Globally unique run IDs required across layouts')
    return refs


def resolve_run(root, run_id):
    found = [r for r in run_refs(root) if r['run_id'] == run_id]
    if len(found) != 1: raise ValueError('Run id missing or ambiguous; globally unique run IDs required')
    return found[0], inside(root, found[0]['path'])


def load_run(root, run_id):
    identity, run = resolve_run(root, run_id)
    result = read(run/'official_result.json') if (run/'official_result.json').is_file() else {}
    mid = result.get('intermediate', {}).get('run_dir')
    stages = {}
    if mid:
        # Read from this run only. Do not follow arbitrary stored absolute paths.
        mid = inside(run, 'SkillBank/.runtime/intermediate_runs/' + Path(mid.replace('\\', '/')).name)
        for name in ('ingest', 'extract', 'compile', 'register'):
            path = mid/name/'result.json'
            stages[name] = read(path) if path.is_file() else {}
    return identity, run, result, stages


def inspect_run(root, run_id):
    identity, run, result, stages = load_run(root, run_id)
    cfg = read(run/'config.json')
    invocation = read(run/'invocation.json')
    execution = read(run/'execution.json') if (run/'execution.json').is_file() else {}
    calls = read(run/'model_calls.json') if (run/'model_calls.json').is_file() else []
    sources = read(run/'sources.json')
    inputs = read(run/'input_manifest.json')['inputs']
    source_map = {s['source_id']:s for s in sources}
    input_map = {str(Path(i['execution_path']).resolve()).lower():i for i in inputs}
    ing, ext, comp, reg = [stages.get(k, {}) for k in ('ingest', 'extract', 'compile', 'register')]
    docs = {x['doc_id']:x for x in ing.get('documents', [])}
    windows = {x['window_id']:x for x in ing.get('windows', [])}
    supports = {x['support_id']:x for x in comp.get('support_records', ext.get('support_records', []))}
    drafts = {x['draft_id']:x for x in ext.get('skill_drafts', [])}
    specs = {x['skill_id']:x for x in comp.get('skill_specs', [])}
    final_ids = {x['id'] for x in reg.get('upserted_store_skills', [])}
    canonical = {}
    for p in (run/'SkillBank/Users').rglob('SKILL.md'):
        match = re.search(r'^id: "([^"\n]+)"', p.read_text(encoding='utf-8'), re.M)
        if match:
            if match[1] in canonical: raise ValueError('Duplicate canonical skill ID')
            canonical[match[1]] = p
    evidence = {}
    for p in (run/'SkillBank').rglob('evidence_manifest.json'):
        ev = read(p)
        evidence[ev['skill_id']] = (p, ev)
    def input_for_source_path(path):
        return input_map.get(str(Path(path).resolve()).lower())
    chains = []
    for sid, spec in specs.items():
        sids = spec.get('support_ids', [])
        linked = [supports[x] for x in sids if x in supports]
        origin = [input_for_source_path(s.get('source_file', '')) for s in linked]
        chains.append({'skill_id':sid, 'name':spec['name'], 'registered':sid in final_ids,
            'canonical_file':str(canonical[sid]) if sid in canonical else None,
            'source_draft_ids':spec.get('metadata', {}).get('source_draft_ids', []),
            'support_ids':sids, 'window_ids':sorted({s.get('metadata', {}).get('window_id', '') for s in linked}),
            'doc_ids':sorted({s['doc_id'] for s in linked}),
            'sources':[{'source_id':i['source_id'], 'input_sha256':i['sha256'],
                        'source_sha256':source_map[i['source_id']]['sha256']} for i in origin if i],
            'workflow_steps':spec.get('workflow_steps', [])})
    alignments = []
    for wid, w in windows.items():
        doc = docs.get(w.get('doc_id'), {})
        path = doc.get('metadata', {}).get('source_file', '')
        item = input_for_source_path(path)
        if not item:
            item = next((input_for_source_path(s.get('source_file', '')) for s in supports.values()
                         if s.get('metadata', {}).get('window_id') == wid), None)
        if not item and len(inputs) == 1: item = inputs[0]
        matches, unmatched, cursor = [], [], 0
        actual_input = inside(run, item['path']) if item else None
        lines = actual_input.read_text(encoding='utf-8').splitlines() if actual_input else []
        for line in w.get('text', '').splitlines():
            if not line.strip(): continue
            found = next((i for i in range(cursor, len(lines)) if lines[i].strip() == line.strip()), None)
            if found is None: unmatched.append(line)
            else: matches.append({'input_line':found+1, 'text':line}); cursor = found+1
        alignments.append({'window_id':wid, 'source_id':item['source_id'] if item else None,
            'input_sha256':item['sha256'] if item else None, 'official_span':w.get('span'),
            'exact_line_matches':matches, 'unmatched_normalized_lines':unmatched,
            'coordinate_note':'Input-file line matches; upstream spans address normalized text. Degraded positions are not original-source positions.'})
    before = read(run/'upstream_before.json')
    after = read(run/'upstream_after.json') if (run/'upstream_after.json').is_file() else None
    environment = read(run/'environment.json') if (run/'environment.json').is_file() else cfg
    fixture = invocation.get('execution_kind') == 'fixture'
    trace = read(run/'official_call_trace.json') if (run/'official_call_trace.json').is_file() else {}
    saved = read(run/'artifact_manifest.json') if (run/'artifact_manifest.json').is_file() else {}
    checks = {
        'original_source_hashes':all(sha256(inside(root,s['local_path']))==s['sha256'] for s in sources),
        'input_hashes':bool(inputs) and all(sha256(inside(run,i['path']))==i['sha256'] for i in inputs),
        'real_model_calls':not fixture and invocation.get('real_generation') is True and bool(calls)
            and any(c.get('success') and c.get('response_id') for c in calls),
        'configured_model_observed':bool(calls) and all(c['model_requested'] == cfg['llm']['model'] for c in calls),
        'no_mock':cfg['llm']['provider'] == 'openai' and not any(k in cfg['llm'] for k in ('response','allow_mock')),
        'upstream_unchanged':before == after == upstream_inventory(Path(environment['upstream_path'])),
        'saved_artifact_hashes':bool(saved) and all(inside(run,p).is_file() and
            sha256(inside(run,p))==h for p,h in saved.items()),
        'completed_without_errors':execution.get('exit_code') == 0 and result.get('status') == 'completed' and not result.get('errors'),
        'all_inputs_parsed':len(docs) == len(inputs) == len(ing.get('text_units',[])) and bool(docs)
            and all(x.get('text','').strip() for x in ing.get('text_units', [])),
        'fresh_skillbank':invocation.get('initial_store_entries') == [] and result.get('skipped_documents') == 0 and not result.get('reused_nodes'),
        'public_api_traced':any(k.endswith(':extract_from_doc') for k in trace),
        'canonical_program_skills':bool(final_ids) and set(canonical) == final_ids and final_ids.issubset(evidence),
        'final_bodies_preserved':bool(final_ids) and all(sid in specs and sid in canonical and
            specs[sid]['skill_body'] in canonical[sid].read_text(encoding='utf-8') for sid in final_ids),
        'support_links':bool(supports) and all(s['doc_id'] in docs and s.get('metadata', {}).get('window_id') in windows
            and input_for_source_path(s.get('source_file', '')) is not None for s in supports.values()),
        'draft_links':bool(drafts) and all(d['doc_id'] in docs and d['support_ids'] and set(d['support_ids']).issubset(supports) for d in drafts.values()),
        'spec_links':bool(specs) and all(s.get('metadata', {}).get('source_draft_ids') and
            set(s['metadata']['source_draft_ids']).issubset(drafts) and set(s['support_ids']).issubset(supports) for s in specs.values()),
        'final_provenance':bool(final_ids) and all(any(p['entity_id']==sid and p.get('support_added') and
            set(p['doc_ids']).issubset(docs) for p in reg.get('provenance_links', [])) for sid in final_ids),
        'evidence_quotes':bool(final_ids) and all(set(evidence[sid][1]['support_ids']) == set(specs[sid]['support_ids'])
            if 'support_ids' in evidence[sid][1] else
            set(e['support_id'] for e in evidence[sid][1]['supports']) == set(specs[sid]['support_ids']) for sid in final_ids if sid in evidence and sid in specs),
        'responses_unchanged':bool(calls) and all(c.get('returned_body_unchanged') and
            sha256(run/'http'/f"{c['number']:03d}"/'response.json') == c['response_sha256'] for c in calls if c.get('success')),
    }
    checks['evidence_excerpts_preserved'] = bool(final_ids) and all(
        e['support_id'] in supports and e['quote'] == supports[e['support_id']]['excerpt']
        for sid in final_ids if sid in evidence for e in evidence[sid][1].get('supports', []))
    for stage,function in [('extract','_plan_unit_skills'),('compile','_compile_group'),('register','classify_change')]:
        checks['model_stage_'+stage]=any(c.get('success') and any(f['function']==function for f in c.get('stack',[])) for c in calls)
    if cfg['pipeline'].get('section_outline_mode')=='llm':
        checks['model_stage_ingest']=any(c.get('success') and any(f['function']=='_outline_matches_from_llm'
            for f in c.get('stack',[])) for c in calls)
    missing = [k for k in ('ingest','extract','compile','register') if not stages.get(k)]
    counts = {'documents':len(docs), 'windows':len(windows), 'supports':len(supports),
              'drafts':len(drafts), 'compiled_specs':len(specs), 'registered_skills':len(final_ids)}
    report = dict(identity, status='FIXTURE' if fixture else ('PASS' if all(checks.values()) else 'PARTIAL'),
        recorded_official_status=result.get('status', 'not_executed'), checks=checks, counts=counts,
        missing_states=missing, input_snapshot='run-local byte snapshot',
        quality_status='SEPARATE_RULE_EVALUATION_REQUIRED', errors=result.get('errors', []),
        execution_kind='fixture' if fixture else 'official', usage_totals=execution.get('usage_totals', {}),
        historical_checkout_differences={})
    all_files = list((run/'SkillBank').rglob('SKILL.md'))
    exports = {'documents':list(docs.values()), 'text_units':ing.get('text_units', []),
        'windows':list(windows.values()), 'support_records':list(supports.values()),
        'skill_drafts':list(drafts.values()), 'skill_specs':list(specs.values()), 'registration':reg,
        'traceability':chains, 'window_source_alignment':alignments,
        'skill_files':{'canonical_program_skills':[str(p) for p in canonical.values()],
                       'navigation_skills':[str(p) for p in all_files if p.parent.name=='总技能'],
                       'physical_skill_md_count':len(all_files), 'unique_program_skill_count':len(final_ids)}}
    return report, exports


def export_run(root, run_id, output):
    _, run = resolve_run(root, run_id)
    output = Path(output).resolve()
    if output.is_relative_to(run): raise ValueError('Exports must be outside immutable run directory')
    report, exports = inspect_run(root, run_id)
    write(output/'verification.json', report)
    for name, data in exports.items(): write(output/(name+'.json'), data)
    return report
