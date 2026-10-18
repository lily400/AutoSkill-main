"""Offline consistency probe of published pure-function reference solutions.

Does not run official shell/container/agent, modify a task, or access model APIs.
Source calls/imports were reviewed before execution. Limited imports/builtins are
additional guardrails, not a general untrusted-code sandbox.
"""
import ast, builtins, json, math, platform, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT/'SkillGenBench'
ALLOWED={'math','numpy','re','collections','datetime','typing','csv','io','random','itertools','_strptime'}
DENIED={'open','exec','eval','compile','getattr','setattr','delattr','globals','locals','vars','input','breakpoint','__import__'}
BAD_ATTRIBUTES={'open','read','write','load','save','loadtxt','savetxt','fromfile','tofile','load_library','__dict__','__subclasses__','__globals__'}

def check(code):
    tree=ast.parse(code)
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): assert all(x.name.split('.')[0] in ALLOWED for x in n.names)
        if isinstance(n,ast.ImportFrom): assert n.module and n.module.split('.')[0] in ALLOWED
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name): assert n.func.id not in DENIED
        if isinstance(n,ast.Attribute): assert n.attr not in BAD_ATTRIBUTES and not (n.attr.startswith('__') and n.attr!='__init__')
    return tree

def guarded_import(name,globals=None,locals=None,fromlist=(),level=0):
    if name.split('.')[0] not in ALLOWED: raise ImportError(name)
    return builtins.__import__(name,globals,locals,fromlist,level)

def main():
    paths=sorted((REPO/'skill_evaluation/domain_knowledge_doc').rglob('testcases.json'))
    # Compile the unchanged comparator definitions after reading their source.
    oracle=ast.parse(paths[0].with_name('eval.py').read_text(encoding='utf-8-sig'))
    selected=[x for x in oracle.body if isinstance(x,ast.FunctionDef) and x.name in ('normalize_value','assert_close')]
    comparison={'math':math}; exec(compile(ast.Module(body=selected,type_ignores=[]),'<published comparator>','exec'),comparison)
    results=[]
    safe_builtins={k:v for k,v in vars(builtins).items() if k not in DENIED};safe_builtins['__import__']=guarded_import
    for p in paths:
        b=json.loads(p.read_text(encoding='utf-8-sig')); code=b.get('setup_code','')+'\n'+b['solution_code']; check(code)
        cases=[]
        for i,c in enumerate(b['test_cases'],1):
            ns={'__builtins__':safe_builtins,'__name__':'audit_reference'}
            try:
                exec(compile(code,str(p)+'#solution_code','exec'),ns)
                got=ns[b.get('function_name','solve')](c['input'])
                comparison['assert_close'](got,c['expected_output'])
                cases.append({'case':i,'passed':True})
            except Exception as e:
                cases.append({'case':i,'passed':False,'exception':type(e).__name__,'message':str(e)})
        results.append({'task_id':p.parent.parent.name,'testcase_file':p.relative_to(REPO).as_posix(),'case_count':len(cases),'passed':sum(c['passed'] for c in cases),'cases':cases})
    import numpy
    output={'scope':'Offline published reference/helper consistency; official container/Agent/runner NOT executed','environment':{'python':sys.version,'platform':platform.platform(),'numpy':numpy.__version__},'tasks':len(results),'cases':sum(r['case_count'] for r in results),'passed':sum(r['passed'] for r in results),'all_case_pass_tasks':sum(r['passed']==r['case_count'] for r in results),'results':results}
    (ROOT/'domain_reference_probe_results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k!='results'},indent=2))
    for r in results:
        if r['passed']!=r['case_count']: print(r['task_id'],r['passed'],r['case_count'],[c for c in r['cases'] if not c['passed']])
if __name__=='__main__':main()
