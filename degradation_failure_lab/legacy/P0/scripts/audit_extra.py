"""Bounded public-data audit and qsv binary-version readiness checks."""
import ast
from collections import Counter
import json
from pathlib import Path
import re
import shutil
from common import LAB, UPSTREAM, write_json
from prepare_sources import AUDIT, AUTO_COMMIT, QSV_COMMIT, api, get


def main():
    tree=json.loads((AUDIT/'official_tree.json').read_text(encoding='utf-8'))['tree']
    files=[x for x in tree if x['type']=='blob']
    data=[x['path'] for x in files if x['path'].startswith('data/')]
    info={'official_commit':AUTO_COMMIT,'official_blob_count':len(files),
        'top_level_file_counts':dict(Counter(x['path'].split('/')[0] for x in files)),
        'data_subtrees':dict(Counter('/'.join(x.split('/')[:2]) for x in data)),
        'qsv_named_files':[x['path'] for x in files if 'qsv' in x['path'].lower()],
        'local_directories_present':{k:(UPSTREAM/k).exists() for k in ['data','examples','tests','SkillBank']},
        'local_test_doc_classification':'CUSTOM_TEST_DATA; local test_doc.md is not included in official Git tree',
        'paper_data_status':'No verified original qsv document snapshot found in inspected public sources',
        'limitations':'Public repository and cited pages inspected; private author files and undocumented external archives cannot be ruled out.'}
    samples=[]
    for prefix in ('data/eval/','data/', 'examples/', 'SkillBank/DocSkill/'):
        candidates=[x['path'] for x in files if x['path'].startswith(prefix) and (x['path'].endswith('.json') or x['path'].endswith('.md') or x['path'].endswith('.py'))]
        if candidates:
            rel=candidates[0]
            try:
                raw=get(f'https://raw.githubusercontent.com/ECNU-ICALK/AutoSkill/{AUTO_COMMIT}/{rel}')
                (AUDIT/('sample_'+str(len(samples))+Path(rel).suffix)).write_bytes(raw)
                samples.append({'source_path':rel,'bytes':len(raw),'saved_as':'sample_'+str(len(samples))+Path(rel).suffix})
            except Exception as e: samples.append({'source_path':rel,'error':str(e)})
    info['samples']=samples
    branches=json.loads((AUDIT/'official_branches.json').read_text(encoding='utf-8'))
    for b in branches:
        if b['name']=='main':continue
        try:
            t=api('repos/ECNU-ICALK/AutoSkill','git/trees/'+b['commit']['sha']+'?recursive=1','alternate_branch_tree')
            info['alternate_branch']={'name':b['name'],'commit':b['commit']['sha'],'truncated':t.get('truncated'),
                'qsv_paths':[x['path'] for x in t['tree'] if 'qsv' in x['path'].lower()],
                'data_top_levels':sorted(set('/'.join(x['path'].split('/')[:2]) for x in t['tree'] if x['path'].startswith('data/')))}
        except Exception as e: info['alternate_branch_error']=str(e)
    for name,url in [('SkillGym_README.md','https://raw.githubusercontent.com/ECNU-ICALK/SkillGym/main/README.md'),
                     ('SkillGym_dataset_card.md','https://huggingface.co/datasets/ecnu-icalk/SkillGym/raw/main/README.md')]:
        try: (AUDIT/name).write_bytes(get(url))
        except Exception as e: info[name+'_error']=str(e)
    write_json(AUDIT/'data_audit.json',info)
    release=json.loads((AUDIT/'qsv_latest_release.json').read_text(encoding='utf-8'))
    readiness={'source_commit':QSV_COMMIT,'source_cargo_version':'24.0.0','source_rust_requirement':'1.99',
        'release_tag':release['tag_name'],'release_published_at':release.get('published_at'),
        'local_tools':{x:shutil.which(x) for x in ['qsv','rustc','cargo']},
        'windows_x64_assets':[{'name':x['name'],'url':x['browser_download_url'],'size':x['size'],'digest':x.get('digest')} for x in release['assets'] if 'x86_64-pc-windows' in x['name']],
        'installed_or_executed':False}
    for rel in ('docs/help/select.md','src/cmd/select.rs'):
        try:
            a=api('repos/dathere/qsv','contents/'+rel+'?ref='+QSV_COMMIT,'qsv_pinned_'+Path(rel).name.replace('.','_'))
            b=api('repos/dathere/qsv','contents/'+rel+'?ref='+release['tag_name'],'qsv_release_'+Path(rel).name.replace('.','_'))
            readiness[rel]={'pinned_git_blob':a['sha'],'release_git_blob':b['sha'],'identical':a['sha']==b['sha']}
        except Exception as e:readiness[rel]={'error':str(e)}
    write_json(AUDIT/'qsv_binary_readiness.json',readiness)
    locations={}
    for path in (UPSTREAM/'AutoSkill4Doc').rglob('*.py'):
        parsed=ast.parse(path.read_text(encoding='utf-8'))
        locations[path.relative_to(UPSTREAM).as_posix()]=[
            {'name':n.name,'line':n.lineno,'kind':type(n).__name__}
            for n in ast.walk(parsed) if isinstance(n,(ast.FunctionDef,ast.ClassDef))]
    write_json(AUDIT/'code_symbol_locations.json',locations)
    print('Supplementary audit saved')


if __name__=='__main__':main()
