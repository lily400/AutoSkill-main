import concurrent.futures
import csv
import hashlib
import io
import json
import urllib.request
from pathlib import Path

BASE=Path(__file__).resolve().parent
REV='4e23915c65f0f1e7c8bacea00feb33974d936ef9'
files=['README.md','data/task_manifest.csv',
'data_source/doc2skill/scikitimage/tasks/scikitimage-task-001/task.json',
'data_source/doc2skill/scikitimage/tasks/scikitimage-task-002/task.json',
'data_source/doc2skill/scikitimage/tasks/scikitimage-task-001/materials/docs/match_template.md',
'skill_evaluation/doc2skill/scikitimage/scikitimage-task-001/tests/eval.py',
'skill_evaluation/doc2skill/scikitimage/scikitimage-task-001/task.toml',
'data_source/cl_tasks/clbench_Domain_Knowledge_Reasoning_Finance/tasks/lockdate_compliance_gate_001/materials/docs/context.md',
'data_source/cl_tasks/clbench_Domain_Knowledge_Reasoning_Finance/tasks/lockdate_compliance_gate_001/materials/docs/task.json',
'skill_evaluation/cl_tasks/clbench_Domain_Knowledge_Reasoning_Finance/lockdate_compliance_gate_001/tests/testcases.json']

def fetch(rel):
    target=BASE/'hf_snapshot_samples'/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    url=f'https://huggingface.co/datasets/anonymous-skillgenbench/SkillGenBench/raw/{REV}/{rel}'
    try:
        if target.exists():
            data=target.read_bytes()
        else:
            with urllib.request.urlopen(url,timeout=30) as response:
                data=response.read()
        target.write_bytes(data)
    except Exception as exc:
        return {'path':rel,'error':str(exc)}
    normalized=rel.replace('/doc2skill/','/code_doc/').replace('/cl_tasks/','/domain_knowledge_doc/').replace('/repo2skill/','/code_repo/')
    gh=BASE/'SkillGenBench'/normalized
    row={'path':rel,'mapped_github_path':normalized,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'github_path_exists':gh.exists()}
    if gh.exists():
        b=gh.read_bytes()
        row.update(byte_identical=data==b,lf_identical=data.replace(b'\r\n',b'\n')==b.replace(b'\r\n',b'\n'))
    if rel.endswith('task.json'):
        try:
            json.loads(data)
            row['strict_json']='PASS'
        except Exception as exc:
            row['strict_json']=str(exc)
    return row

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    rows=list(pool.map(fetch,files))
manifest=BASE/'hf_snapshot_samples/data/task_manifest.csv'
counts={}
if manifest.exists():
    records=list(csv.DictReader(io.StringIO(manifest.read_text(encoding='utf-8-sig'))))
    for r in records: counts[r['source']]=counts.get(r['source'],0)+1
else: records=[]
report={'hf_revision':REV,'github_revision':'5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d','manifest_rows':len(records),'source_counts':counts,'sample_comparison':rows,'scope':('HF manifest fully read; ' if records else 'HF manifest retrieval failed; ')+'byte comparison limited to named samples; no claim that all HF/GitHub files match'}
(BASE/'hf_github_comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
