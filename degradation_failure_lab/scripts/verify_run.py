"""Read-only evidence checks and exports; never changes generated skills."""
import argparse
import json
from pathlib import Path
import re
import sys
from common import LAB, code_inventory, sha256, write_json


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify(run):
    result=read(run/'official_result.json')
    execution=read(run/'execution.json')
    manifest=read(run/'source_manifest.json')
    invocation=read(run/'invocation.json')
    source=LAB/manifest['local_path']
    mid=Path(result['intermediate']['run_dir'])
    stages={name:read(mid/name/'result.json') for name in ('ingest','extract','compile','register')}
    ing,ext,comp,reg=(stages[k] for k in ('ingest','extract','compile','register'))
    docs={x['doc_id']:x for x in ing['documents']}
    windows={x['window_id']:x for x in ing['windows']}
    supports={x['support_id']:x for x in comp['support_records']}
    drafts={x['draft_id']:x for x in ext['skill_drafts']}
    specs={x['skill_id']:x for x in comp['skill_specs']}
    final_ids={x['id'] for x in reg['upserted_store_skills']}
    calls=read(run/'model_calls.json')
    canonical=list((run/'SkillBank/Users/docskill').glob('*/SKILL.md'))
    evidence=list((run/'SkillBank').rglob('evidence_manifest.json'))
    evidence_by_id={read(p)['skill_id']:(p,read(p)) for p in evidence}
    canonical_by_id={re.search(r'^id: "([^"]+)"',p.read_text(encoding='utf-8'),re.M).group(1):p for p in canonical}
    checks={
        'source_hash':sha256(source)==manifest['sha256'],
        'official_source_reconstruction':manifest['classification']=='RECONSTRUCTED_OFFICIAL_SOURCE' and not manifest['paper_snapshot_verified'],
        'real_http_calls':len(calls)>0 and all(c.get('response_id') for c in calls if c.get('success')),
        'no_mock':read(run/'config.json')['llm']['provider']=='openai' and all(c['model_requested']=='deepseek-flash' for c in calls),
        'upstream_unchanged':read(run/'upstream_before.json')==read(run/'upstream_after.json')==code_inventory(),
        'completed_without_stage_errors':execution['exit_code']==0 and result['status']=='completed' and not result['errors'],
        'single_document_parsed':len(docs)==1 and len(ing['text_units'])==1 and bool(ing['text_units'][0]['text']),
        'fresh_skillbank':invocation['initial_store_entries']==[] and result['skipped_documents']==0 and not result['reused_nodes'],
        'nonempty_canonical_skills':bool(canonical) and all(p.stat().st_size>0 for p in canonical),
        'final_ids_match':set(canonical_by_id)==final_ids and final_ids.issubset(evidence_by_id),
        'final_compiled_body_preserved':all(specs[sid]['skill_body'] in canonical_by_id[sid].read_text(encoding='utf-8') for sid in final_ids),
        'evidence_quotes_preserved':all(entry['quote']==supports[entry['support_id']]['excerpt'] for _,ev in evidence_by_id.values() for entry in ev['supports']),
        'all_drafts_grounded':all(d['doc_id'] in docs and d['support_ids'] and set(d['support_ids']).issubset(supports) for d in drafts.values()),
        'compiled_draft_links':all(s['metadata'].get('source_draft_ids') and set(s['metadata']['source_draft_ids']).issubset(drafts) for s in specs.values()),
        'support_window_links':all(s['doc_id'] in docs and s['metadata'].get('window_id') in windows for s in supports.values()),
        'source_paths':all(Path(s['source_file']).resolve()==source.resolve() for s in supports.values()),
        'registered_provenance':all(any(p['entity_id']==sid and set(p['doc_ids']).issubset(docs) and p['support_added'] for p in reg['provenance_links']) for sid in final_ids),
    }
    for stage, function in [('ingest','_outline_matches_from_llm'),('extract','_plan_unit_skills'),('compile','_compile_group'),('register','classify_change')]:
        checks['real_model_'+stage]=any(c.get('success') and any(f['function']==function for f in c['stack']) for c in calls)
    trace=read(run/'official_call_trace.json')
    checks['public_api_traced']=any(k.endswith(':extract_from_doc') for k in trace)
    checks['unchanged_http_responses']=all(c.get('returned_body_unchanged') and sha256(run/'http'/f"{c['number']:03d}"/'response.json')==c['response_sha256'] for c in calls if c.get('success'))
    # Official HeuristicDocumentIngestor._build_text_unit applies .strip().
    # The original file itself is byte-preserved and checked separately above.
    checks['text_unit_matches_official_strip']=ing['text_units'][0]['text']==read(run/'parsed_text_units.json')['units'][0]['text'].strip()
    # Explicit source-line alignment. Official spans can address normalized text;
    # these are never falsely presented as raw-file character offsets.
    source_lines=source.read_text(encoding='utf-8').splitlines()
    alignments=[]
    for wid,w in windows.items():
        cursor=0; matched=[]; unmatched=[]
        for line in w['text'].splitlines():
            if not line.strip():continue
            found=next((i for i in range(cursor,len(source_lines)) if source_lines[i].strip()==line.strip()),None)
            if found is None:unmatched.append(line)
            else:matched.append({'source_line':found+1,'text':line});cursor=found+1
        alignments.append({'window_id':wid,'official_span':w['span'],'exact_line_matches':matched,
            'unmatched_normalized_lines':unmatched,'coordinate_note':'Line positions are wrapper exact-line matches, separate from upstream normalized-text spans.'})
    chain=[]
    for sid in sorted(final_ids):
        spec=specs[sid]
        ep,ev=evidence_by_id[sid]
        checks['evidence_'+sid]=set(x['support_id'] for x in ev['supports'])==set(spec['support_ids'])
        chain.append({'skill_id':sid,'name':spec['name'],'canonical_file':str(canonical_by_id[sid]),
            'visible_file':str(ep.parent.parent/'SKILL.md'),'evidence_manifest':str(ep),
            'source_draft_ids':spec['metadata']['source_draft_ids'],'support_ids':spec['support_ids'],
            'window_ids':[supports[x]['metadata']['window_id'] for x in spec['support_ids']],
            'doc_ids':[supports[x]['doc_id'] for x in spec['support_ids']],
            'source_id':manifest['source_id'],'source_sha256':manifest['sha256'],
            'workflow_steps':spec['workflow_steps']})
    all_skills=list((run/'SkillBank').rglob('SKILL.md'))
    exports=run/'exports'
    for name, data in [('text_units',ing['text_units']),('documents',ing['documents']),('windows',ing['windows']),
                       ('support_records',list(supports.values())),('skill_drafts',list(drafts.values())),
                       ('skill_specs',list(specs.values())),('registration',reg),('traceability',chain),('window_source_alignment',alignments)]:
        write_json(exports/(name+'.json'),data)
    paths={'canonical_program_skills':[str(p) for p in canonical],
        'visible_program_copies':[x['visible_file'] for x in chain],
        'navigation_skills':[str(p) for p in all_skills if p.parent.name=='总技能'],
        'physical_skill_md_count':len(all_skills),'unique_program_skill_count':len(final_ids)}
    write_json(exports/'skill_files.json',paths)
    report={'status':'PASS' if all(checks.values()) else 'PARTIAL','checks':checks,'counts':{
        'documents':len(docs),'text_units':len(ing['text_units']),'windows':len(windows),'supports':len(supports),
        'drafts':len(drafts),'compiled_specs':len(specs),'registered_skills':len(final_ids)},
        'quality_scope':'Evidence and execution verification only; see separate rule review. No qsv commands executed.',
        'missing_states':[], 'non_bitwise_reproducibility':'Remote model sampling and alias version may change across future runs.'}
    write_json(run/'verification.json',report)
    write_json(run/'artifact_manifest.json',{p.relative_to(run).as_posix():sha256(p) for p in run.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'})
    return report


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);args=p.parse_args()
    result=verify(Path(args.run));print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)
