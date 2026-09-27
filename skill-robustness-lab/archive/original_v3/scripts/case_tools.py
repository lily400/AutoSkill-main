"""Create an empty case, then freeze its user-authored input/evaluation assets."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
from evidence import read, save, sha, manifest

LAB=Path(__file__).resolve().parents[1]

def case_path(key):
    if not re.fullmatch(r'case[0-9]+(?:_[A-Za-z0-9-]+)?',key):
        raise ValueError('Use a case name such as case002')
    root=(LAB/'cases'/key).resolve()
    if root.parent!=(LAB/'cases').resolve(): raise ValueError('Invalid case path')
    return root

def init_case(key,title):
    root=case_path(key)
    root.mkdir(parents=True,exist_ok=False)
    for name in ('clean','evaluation','degradation/variants','degradation/recipes'):
        (root/name).mkdir(parents=True,exist_ok=True)
    (root/'clean/source.md').write_text('# TODO: Replace with this case complete source document.\n',encoding='utf-8')
    case_id=key+'-dev-v1'
    save(root/'case.json',{'case_key':key,'case_id':case_id,'title':title,'status':'draft',
         'split':'development','clean_file':f'cases/{key}/clean/source.md','clean_sha256':None,
         'evaluation_dir':f'cases/{key}/evaluation','evaluation_sha256':{},
         'task':{'domain':'general','domain_type':'default','family_name':title}})
    save(root/'evaluation/contract.json',{'case_id':case_id,'version':1,'split':'development',
         'rules':[],'instructions':'Add rules with unique id and source_text copied from THIS case source; no scores.'})
    save(root/'evaluation/fixtures.json',{'version':1,'split':'development','cases':[],
         'instructions':'Add actual test cases with unique id, input, expect and expected outputs. This is test design, not run output.'})
    return root

def freeze_case(key):
    root=case_path(key); case=read(root/'case.json')
    if case.get('case_key')!=key: raise ValueError('case_key mismatch')
    for field in ('clean_file','evaluation_dir'):
        if not (LAB/case[field]).resolve().is_relative_to(root):
            raise ValueError(field+' points outside this case')
    source=LAB/case['clean_file']; evaluation=LAB/case['evaluation_dir']
    source_hash=sha(source)
    if case.get('status')=='ready':
        if case['clean_sha256']==source_hash and case['evaluation_sha256']==manifest(evaluation):
            return root
        raise ValueError('Ready case was changed. Keep it and create a new case/version; do not overwrite its frozen hashes.')
    text=source.read_text(encoding='utf-8-sig')
    if not text.strip() or text.startswith('# TODO:'): raise ValueError('Write the actual clean source first')
    contract=read(evaluation/'contract.json'); fixtures=read(evaluation/'fixtures.json')
    if contract.get('case_id')!=case['case_id']: raise ValueError('Contract case_id mismatch')
    rules=contract.get('rules',[]); tests=fixtures.get('cases',[])
    for records,label in ((rules,'rules'),(tests,'fixtures')):
        ids=[item.get('id') for item in records]
        if not ids or not all(ids) or len(ids)!=len(set(ids)):
            raise ValueError(label+' must have unique nonempty IDs and at least one item')
    if any(not r.get('source_text') or r['source_text'] not in text for r in rules):
        raise ValueError('Every source_text must occur in this case clean source')
    if any('input' not in t or t.get('expect') not in ('success','error') or 'outputs' not in t for t in tests):
        raise ValueError('Each fixture needs input, expect=success/error and outputs')
    contract['source_sha256']=source_hash
    save(evaluation/'contract.json',contract)
    case.update(status='ready',clean_sha256=source_hash,evaluation_sha256=manifest(evaluation))
    save(root/'case.json',case)
    return root

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('init','freeze'));p.add_argument('case_key')
    p.add_argument('--title',help='Task name for a new case')
    a=p.parse_args(argv)
    if a.action=='init' and not a.title: p.error('init requires --title')
    root=init_case(a.case_key,a.title) if a.action=='init' else freeze_case(a.case_key)
    print(root)
    print('This creates/freezes input files only. No model was called and no result was generated.')

if __name__=='__main__': raise SystemExit(main())
