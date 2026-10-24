"""Read-only upstream audit. Writes inventories only to --output (outside repo)."""
import argparse, ast, collections, csv, hashlib, json, re, statistics, tomllib
from pathlib import Path

def digest(data): return hashlib.sha256(data).hexdigest()
def reject_constants(value): raise ValueError('Non-standard JSON constant: '+value)
def strict_json(text): return json.loads(text, parse_constant=reject_constants)
def read(p): return p.read_text(encoding='utf-8-sig')
def write_json(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--repo',type=Path,required=True); parser.add_argument('--output',type=Path,required=True); a=parser.parse_args()
    root=a.repo.resolve(); out=a.output.resolve(); out.mkdir(parents=True,exist_ok=True)
    if out==root or root in out.parents: raise ValueError('Audit output must be outside upstream repository')
    rel=lambda p:p.relative_to(root).as_posix()
    errors=[]; formats=collections.Counter()
    for p in sorted(root.rglob('*')):
        if '.git' in p.parts or not p.is_file() or p.suffix not in ('.json','.toml','.py'): continue
        try:
            text=read(p)
            if p.suffix=='.json': strict_json(text)
            elif p.suffix=='.toml': tomllib.loads(text)
            else: ast.parse(text,filename=rel(p))
            formats[p.suffix+'_valid']+=1
        except Exception as e:
            formats[p.suffix+'_invalid']+=1; errors.append({'path':rel(p),'error':str(e),'type':type(e).__name__})
    rows=[]; docs=[]; source_map=collections.defaultdict(list)
    for taskfile in sorted((root/'skill_evaluation').rglob('task.toml')):
        ev=taskfile.parent; cfg=tomllib.loads(read(taskfile)); task=cfg['task']; source=task['source']; group=task['collection_slug']; tid=task['task_id']
        gen=root/'data_source'/source/group/'tasks'/tid
        docpaths=sorted((gen/'materials'/'docs').rglob('*')) if (gen/'materials'/'docs').exists() else []
        docpaths=[p for p in docpaths if p.is_file()]; narrative=[p for p in docpaths if p.suffix.lower() in ('.md','.txt','.rst','.html','.htm','.pdf')]
        dr=[]
        for p in docpaths:
            raw=p.read_bytes(); s=raw.decode('utf-8-sig',errors='replace'); d={'task_id':tid,'source_type':source,'source_group':group,'path':rel(p),'bytes':len(raw),'sha256':digest(raw),'chars':len(s),'whitespace_words':len(s.split()),'lines':len(s.splitlines()),'narrative_document':p in narrative,'nonascii_chars':sum(ord(c)>127 for c in s),'cjk_chars':len(re.findall(r'[\u3400-\u9fff]',s)),'headings':len(re.findall(r'^#{1,6}\s',s,re.M))}
            dr.append(d); docs.append(d)
        tests=sorted((ev/'tests').rglob('*')) if (ev/'tests').exists() else []; tests=[p for p in tests if p.is_file()]
        pyfiles=[p for p in tests if p.suffix=='.py']
        active_pyfiles=[ev/'tests'/'eval.py'] if source in ('code_doc','domain_knowledge_doc') and (ev/'tests'/'eval.py').exists() else pyfiles
        combined='\n'.join(read(p) for p in active_pyfiles)
        imports=[]; funcs=[]; asserts=[]
        for p in active_pyfiles:
            try: tree=ast.parse(read(p))
            except SyntaxError: continue
            imports += [n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
            imports += [x.name for n in ast.walk(tree) if isinstance(n,ast.Import) for x in n.names]
            funcs += [n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test')]
            asserts += [ast.unparse(n.test) for n in ast.walk(tree) if isinstance(n,ast.Assert)]
        casepath=ev/'tests'/'testcases.json'; cases=json.loads(read(casepath)) if casepath.exists() else None
        runner=ev/cfg.get('validation',{}).get('runner','tests/test.sh')
        risks=[]
        taskjson=gen/'task.json'; e=next((x for x in errors if x['path']==rel(taskjson)),None)
        if e: risks.append('OBSERVED: generation task.json fails strict JSON: '+e['error'])
        if not runner.exists(): risks.append('OBSERVED: declared verifier runner missing')
        if 'source' in combined and (' in source' in combined or 'source.count(' in combined): risks.append('OBSERVED: verifier includes source-text checks; semantically equivalent code may be rejected')
        if source=='domain_knowledge_doc': risks.append('OBSERVED: task metadata is colocated under materials/docs; filter by documented format contract rather than silently treating JSON as source prose')
        if not docpaths: risks.append('OBSERVED: no task-local materials/docs; inspect shared repository material separately')
        rule_candidate='UNVERIFIED: no published rule-to-task mapping; shared library alone is insufficient'
        suitability=('INFERRED: curated API excerpt(s); text/ordering/distractor perturbations possible; original visual layout not preserved' if source=='code_doc' else 'INFERRED: long synthetic/specialized textual context; rule perturbation possible after source sufficiency validation' if source=='domain_knowledge_doc' else 'UNVERIFIED: repository mixed code/docs, auxiliary source type')
        rows.append({'task_id':tid,'source_type':source,'source_group':group,'input_paths':[rel(p) for p in docpaths],'document_count':len(narrative),'document_lengths':dr,'instruction_visibility':'OBSERVED: instruction.md is public generation-task artifact; actual prompt inclusion depends on runner mode','skill_scope':cfg.get('skill',{}).get('scope'),'oracle_type':cfg.get('evaluation',{}),'oracle_files':[rel(p) for p in tests],'shared_rule_candidate':rule_candidate,'rule_dependency_tasks':[],'degradation_suitability':suitability,'compatibility_risks':risks,'verification_status':{'structure':'OBSERVED all tasks','strict_parse':'OBSERVED all JSON/TOML/Python files','oracle_static':'OBSERVED AST/import/assert inventory; semantic review tracked separately','oracle_execution':'UNVERIFIED (no official container or agent run)','source_sufficiency':'UNVERIFIED','rule_dependencies':'UNVERIFIED'},'task_toml':rel(taskfile),'generation_task_json':rel(taskjson),'generation_task_json_valid':e is None and taskjson.exists(),'instruction_file':rel(ev/'instruction.md'),'instruction_exists':(ev/'instruction.md').exists(),'runner_exists':runner.exists(),'oracle_python_files':[{'path':rel(p),'sha256':digest(p.read_bytes())} for p in pyfiles],'oracle_imports':sorted(set(imports)),'oracle_test_functions':funcs,'oracle_assertions':asserts,'oracle_case_count':len(cases.get('test_cases',[])) if cases else None,'oracle_setup_code':cases.get('setup_code') if cases else None,'oracle_function_name':cases.get('function_name') if cases else None,'runtime':cfg.get('runtime',{}),'task_status':task.get('status'),'document_set_hash':digest('\n'.join(sorted(d['sha256'] for d in dr if d['narrative_document'])).encode())})
        source_map[(source,group)].append(rows[-1])
    sources=[]
    for (stype,group), tasks in sorted(source_map.items()):
        sd=[d for t in tasks for d in t['document_lengths'] if d['narrative_document']]
        sources.append({'source_type':stype,'source_group':group,'task_count':len(tasks),'task_ids':[t['task_id'] for t in tasks],'narrative_document_path_count':len(sd),'unique_document_sha256_count':len({d['sha256'] for d in sd}),'unique_document_sets':len({t['document_set_hash'] for t in tasks}),'doc_chars_total':sum(d['chars'] for d in sd),'doc_words_total':sum(d['whitespace_words'] for d in sd),'group_independence':'UNVERIFIED: source/library or CLBench context group, not a proven statistically independent unit'})
    summaries={}
    for stype in sorted({t['source_type'] for t in rows}):
        subset=[t for t in rows if t['source_type']==stype]; sd=[d for d in docs if d['source_type']==stype and d['narrative_document']]; lens=[d['chars'] for d in sd]; sets=[sum(d['chars'] for d in t['document_lengths'] if d['narrative_document']) for t in subset]
        summaries[stype]={'tasks':len(subset),'source_groups':len({t['source_group'] for t in subset}),'narrative_document_paths':len(sd),'unique_document_sha256':len({d['sha256'] for d in sd}),'unique_document_sets':len({t['document_set_hash'] for t in subset}),'doc_chars':{'min':min(lens,default=0),'median':statistics.median(lens) if lens else 0,'max':max(lens,default=0),'sum':sum(lens)},'task_set_chars':{'min':min(sets,default=0),'median':statistics.median(sets) if sets else 0,'max':max(sets,default=0)},'strict_generation_task_json_valid':sum(t['generation_task_json_valid'] for t in subset),'runner_present':sum(t['runner_exists'] for t in subset),'case_count_total':sum(t['oracle_case_count'] or 0 for t in subset)}
    write_json(out/'sgb_data_summary.json',{'repo_root':str(root),'definitions':{'document':'task-local materials/docs narrative extensions; JSON descriptors counted separately','distinct_document':'SHA256 byte-distinct text, not a claim of independent original publication','collection':'set of narrative document hashes per task','source_group':'published collection_slug; statistical independence unverified','language':'CJK/nonASCII counts only; English classification reviewed separately','executable_oracle':'file presence and syntax only; runtime execution unverified'},'task_count':len(rows),'formats':dict(formats),'source_types':summaries,'parse_errors':errors})
    write_json(out/'sgb_source_groups.json',sources); write_json(out/'sgb_document_files.json',docs)
    (out/'sgb_task_inventory.jsonl').write_text(''.join(json.dumps(t,ensure_ascii=False)+'\n' for t in rows),encoding='utf-8')
    fields=list(rows[0]);
    with (out/'sgb_task_inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in t.items()} for t in rows)
    print(json.dumps({'tasks':len(rows),'formats':dict(formats),'source_types':summaries},indent=2))
if __name__=='__main__': main()
