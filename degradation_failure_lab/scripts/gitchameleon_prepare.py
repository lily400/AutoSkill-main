"""Prepare official documentation and materialize paragraph-deletion conditions. No LLM."""
import ast,datetime,difflib,hashlib,inspect,itertools,json,pathlib,re

VERSION='gch-doc-projection-v1'
FLASK='735a4701d6d5e848241e7d7535db898efb62d400'
NUMPY='609c5399d0c2ca284ccc4b84d606727ed5640469'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode() if not isinstance(x,str) else x.encode()
    if p.exists() and p.read_bytes()!=data:raise FileExistsError('Refuse to overwrite changed asset: '+str(p))
    p.write_bytes(data)

def prepare(lab):
    raw=lab/'.external/gitchameleon/doc_sources'
    outputs=lab/'data/raw_sources/gitchameleon'
    blocks=[]
    def add(key,relative,node,signature=''):
        text=inspect.cleandoc(node.value.value)
        blocks.append({'key':key,'raw_file':relative,'raw_sha256':sha(raw/relative),'source_lines':[node.lineno,node.end_lineno],'signature':signature,'body':text})
    def signature(node,source):
        return '\n'.join(source.splitlines()[node.lineno-1:node.body[0].lineno-1])
    def doc_node(node):
        return node.body[0] if node.body and isinstance(node.body[0],ast.Expr) and isinstance(node.body[0].value,ast.Constant) and isinstance(node.body[0].value.value,str) else None
    p='flask-3.0.0/src/flask/json/provider.py';source=(raw/p).read_text(encoding='utf-8');tree=ast.parse(source)
    classes=[n for n in tree.body if isinstance(n,ast.ClassDef)]
    for cls in classes:
        if cls.name not in ['JSONProvider','DefaultJSONProvider']:continue
        add(cls.name,p,doc_node(cls),signature(cls,source))
        for index,node in enumerate(cls.body):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and doc_node(node):add(cls.name+'.'+node.name,p,doc_node(node),signature(node,source))
            if isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str) and index and isinstance(cls.body[index-1],(ast.Assign,ast.AnnAssign)):
                prev=cls.body[index-1];target=prev.target if isinstance(prev,ast.AnnAssign) else prev.targets[0];key=target.id
                declaration=ast.get_source_segment(source,prev).split('=')[0].strip() if isinstance(prev.value,ast.Call) else ast.get_source_segment(source,prev).strip()
                add(cls.name+'.'+key,p,node,declaration)
    p='flask-3.0.0/src/flask/sansio/app.py';source=(raw/p).read_text(encoding='utf-8');tree=ast.parse(source)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='App')
    for index,node in enumerate(cls.body):
        if isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name) and node.target.id=='json_provider_class':add('App.json_provider_class',p,cls.body[index+1],ast.get_source_segment(source,node).strip())
    init=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    for index,node in enumerate(init.body):
        if isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Attribute) and node.target.attr=='json':add('App.json',p,init.body[index+1],ast.get_source_segment(source,node).split('=')[0].strip())
    p='flask-3.0.0/src/flask/json/__init__.py';source=(raw/p).read_text(encoding='utf-8');node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='jsonify');add('flask.json.jsonify',p,doc_node(node),signature(node,source))
    flask_blocks=list(blocks)
    p='numpy-v1.25.1/numpy/lib/arraysetops.py';source=(raw/p).read_text(encoding='utf-8');node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='unique');add('numpy.unique',p,doc_node(node),signature(node,source))
    p='numpy-v1.25.1/numpy/core/_add_newdocs.py';tree=ast.parse((raw/p).read_text(encoding='utf-8'))
    for n in tree.body:
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='add_newdoc':
            args=n.value.args
            if len(args)==3 and isinstance(args[1],ast.Constant) and args[1].value=='ndarray' and isinstance(args[2],ast.Tuple) and isinstance(args[2].elts[0],ast.Constant) and args[2].elts[0].value=='tolist':
                string=args[2].elts[1]
                add('numpy.ndarray.tolist',p,ast.Expr(value=string,lineno=string.lineno,end_lineno=string.end_lineno));break
    numpy_blocks=[b for b in blocks if b not in flask_blocks]
    def render(title,items):
        doc='# '+title+'\n\n';mapping=[]
        for b in items:
            start=len(doc.splitlines())+1
            doc+='## '+b['key']+'\n\n'
            if b['signature']:doc+='```python\n'+b['signature']+'\n```\n\n'
            body_start=len(doc.splitlines())+1;doc+=b['body']+'\n\n'
            mapping.append({**b,'input_heading_line':start,'input_body_start_line':body_start,'input_body_end_line':len(doc.splitlines())-1})
        return doc,mapping
    flask,fmap=render('Flask 3.0.0 official API documentation',flask_blocks)
    numpy,nmap=render('NumPy 1.25.1 official API documentation',numpy_blocks)
    assert 'equal_nan=True' in numpy and 'If True, collapses multiple NaN values' in numpy
    assert ':attr:`app.json <flask.Flask.json>` to an instance of the class.' in flask and 'attribute afterwards.' in flask
    allmap=fmap+nmap
    for b in allmap:
        source=(raw/b['raw_file']).read_text(encoding='utf-8')
        assert b['body'] in (flask if b in fmap else numpy)
        assert b['body']==inspect.cleandoc(ast.literal_eval(ast.get_source_segment(source,next(n.value for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str) and n.lineno==b['source_lines'][0])))) if b['key']!='numpy.ndarray.tolist' else True
    prepared={'flask_json.md':flask,'numpy_unique.md':numpy}
    for name,text in prepared.items():write(outputs/'prepared'/name,text)
    preparation={'version':VERSION,'converter_sha256':sha(pathlib.Path(__file__)),'conversion':'AST docs + exact API signatures + static add_newdoc string; no module execution, no rendered HTML input, no Skill extraction','blocks':allmap,'source_scope':'Complete selected official documentation blocks; entire upstream source files preserved separately; no full-site claim','known_limits':['RST cross-reference markup retained, not rewritten','Raw source line ranges are authoritative; whitespace dedent is recorded','Dynamic decorators are not executed; current selected APIs have statically located required text']}
    write(lab/'data/manifests/gitchameleon_preparation.json',preparation)
    paragraphs=[]
    for key,prefix in [('JSONProvider','To use a different provider'),('App.json_provider_class','A subclass of'),('App.json','An instance of')]:
        b=next(b for b in fmap if b['key']==key);paragraph=next(p for p in b['body'].split('\n\n') if p.startswith(prefix));paragraphs.append(paragraph+'\n\n')
    irrelevant=[next(b for b in fmap if b['key']=='DefaultJSONProvider.'+key)['body']+'\n\n' for key in ['ensure_ascii','sort_keys','compact']]
    wanted=sum(len(x) for x in paragraphs)
    options=[c for n in range(1,len(irrelevant)+1) for c in itertools.combinations(irrelevant,n)]
    irrelevant=min(options,key=lambda c:abs(sum(len(x) for x in c)-wanted))
    unique=next(b for b in nmap if b['key']=='numpy.unique')['body']
    relevant_nan=re.search(r'(?ms)^equal_nan :.*?(?=^Returns\n)',unique).group()
    irrelevant_nan=re.search(r'(?ms)^return_counts :.*?(?=^axis :)',unique).group()
    deltas=[]
    def degrade(task,condition,filename,text,spans,target):
        removed=[]
        for s in spans:
            assert text.count(s)==1,(task,filename,s)
            offset=text.index(s);removed.append({'clean_start_line':text[:offset].count('\n')+1,'chars':len(s),'text':s});text=text.replace(s,'',1)
        destination=lab/f'data/condition_inputs/gitchameleon/{task}/{condition}/{filename}';write(destination,text)
        clean=prepared[filename]
        diff=''.join(difflib.unified_diff(clean.splitlines(True),text.splitlines(True),fromfile=filename,tofile=filename))
        diffpath=lab/f'data/condition_inputs/gitchameleon/{task}/{condition}/{filename}.diff';write(diffpath,diff)
        deltas.append({'task_id':task,'condition_id':condition,'semantic_label':'Relevant Degradation' if condition=='c01' else 'Irrelevant Degradation','operator':'paragraph_delete_v1','file':str(destination.relative_to(lab)).replace('\\','/'),'clean_sha256':hashlib.sha256(clean.encode()).hexdigest(),'sha256':sha(destination),'target':target,'deletions':removed,'deleted_chars':sum(r['chars'] for r in removed),'diff_file':str(diffpath.relative_to(lab)).replace('\\','/')})
    degrade('144','c01','flask_json.md',flask,paragraphs,'F-JSON-INSTALL')
    degrade('144','c02','flask_json.md',flask,irrelevant,'ensure_ascii/sort_keys/compact documentation; not required for numeric sets')
    degrade('164','c01','numpy_unique.md',numpy,[relevant_nan],'N-UNIQUE-NAN')
    degrade('164','c02','numpy_unique.md',numpy,[irrelevant_nan],'return_counts optional output; task requests only unique values')
    for c in ['c01','c02']:
        write(lab/f'data/condition_inputs/gitchameleon/164/{c}/flask_json.md',flask)
    fidelity={'status':'PASS','version':VERSION,'blocks':len(allmap),'assertions':{'all_blocks_equal_official_doc_strings_after_standard_dedent':True,'exact_unique_signature_with_default':True,'static_add_newdoc_tolist_preserved':True,'flask_app_initialization_and_instance_condition_preserved':True,'source_implementation_statements_excluded':True,'no_problem_solution_or_tests_in_conversion':True},'clean_inputs':{n:{'sha256':sha(outputs/'prepared'/n),'bytes':len(t.encode())} for n,t in prepared.items()},'degradations':deltas,'residual_information':['164/c01 retains equal_nan=True in the unchanged API signature and historical NaN notes; this is parameter-description deletion, not all NaN knowledge removal','144/c01 deletes three provider-installation paragraphs; default handling, jsonify description and class names remain'],'size_match':{t:{'relevant_chars':next(d['deleted_chars'] for d in deltas if d['task_id']==t and d['condition_id']=='c01'),'irrelevant_chars':next(d['deleted_chars'] for d in deltas if d['task_id']==t and d['condition_id']=='c02')} for t in ['144','164']}}
    write(lab/'data/manifests/gitchameleon_fidelity.json',fidelity)
    return fidelity

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--lab',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]);args=parser.parse_args()
    print(json.dumps(prepare(args.lab.resolve()),ensure_ascii=False,indent=2))
