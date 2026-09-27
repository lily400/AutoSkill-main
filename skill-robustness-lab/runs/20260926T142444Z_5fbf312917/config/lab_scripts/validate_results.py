"""Validate actual result files, references, seals and local execution evidence."""
import argparse
from pathlib import Path
from data_contracts import load_dataset,validate_object,require,safe,sealed_run,VERSION
from evidence import read,sha,check_frozen,digest,manifest
from compare_runs import compare
import judge_csv

def validate_results(root):
    root=Path(root); ds=load_dataset(root); runs={}; executions={}; count={'runs':0,'executions':0,'judgments':0,'comparisons':0,'program_ir':0}
    for folder in sorted((root/'runs').glob('*')):
        if not folder.is_dir(): continue
        require(check_frozen(folder)['valid'],'Run seal changed: '+folder.name)
        r=validate_object('run',read(folder/'run.json')); require(r['run_id']==folder.name,'Run ID mismatch')
        require(r['case_id'] in ds['cases'] and r['variant_id'] in ds['variants'],'Unknown run case/variant')
        c=ds['cases'][r['case_id']]; v=ds['variants'][r['variant_id']]
        for key in ('case_id','source_id','source_version','family_id'):
            require(r[key]==c[key]==v[key],'Cross-case run '+key)
        require(r['split']==c['split'] and r['input_sha256']==v['input_sha256'],'Run input/split mismatch')
        require(r['dataset_freeze_sha256']==sha(root/'catalog/freeze.json'),'Run dataset seal differs; inspect original release')
        require(sha(folder/'input/source.md')==r['input_sha256'],'Run snapshot differs from variant')
        status=read(folder/'status.json')
        require(status['status']==r['status'] and status['structural_pass']==r['structural_pass'],'Status aliases disagree')
        if r['comparison_fingerprint'] is not None:
            ct=read(folder/'config/comparison_contract.json'); fp=read(folder/'config/comparison_fingerprint.json')
            require(digest(ct)==fp['sha256']==r['comparison_fingerprint'],'Run fingerprint mismatch')
        if r['kind']=='preflight': require(r['structural_pass'] is None and not list((folder/'trace').glob('*.json')),'Preflight contains model results')
        require(not (folder/'evaluation').exists(),'Standards copied into generation run')
        runs[r['run_id']]=r; count['runs']+=1
    for folder in sorted((root/'executions').glob('*')):
        if not folder.is_dir(): continue
        require(check_frozen(folder)['valid'],'Execution seal changed')
        e=validate_object('execution',read(folder/'execution.json')); require(e['execution_id']==folder.name,'Execution ID mismatch')
        require(e['task_id'] in ds['tasks'],'Unknown execution task'); t=ds['tasks'][e['task_id']]
        for key in ('case_id','source_id','family_id','task_id','contract_id','judge_id'): require(e[key]==t[key],'Cross-case execution '+key)
        require(e['dataset_freeze_sha256']==sha(root/'catalog/freeze.json'),'Execution dataset changed')
        for path,h in e['standard_hashes'].items(): require(sha(safe(root,path))==h,'Execution standard hash changed')
        if e['run_id'] is not None:
            rp,r,_=sealed_run(root,e['run_id']); require(r['case_id']==e['case_id'],'Cross-case execution run')
            require(sha(rp/'checksums.json')==e['run_checksums_sha256'],'Execution run seal changed')
        if e['status'] in ('completed','failed'):
            workspace=folder/'workspace'
            actual_inputs={name:sha(workspace/name) for name in t['inputs'] if (workspace/name).is_file()}
            require(actual_inputs==e['input_after'],'Execution input evidence differs')
            import hashlib
            require(e['input_before']=={name:hashlib.sha256(value.encode('utf-8')).hexdigest() for name,value in t['inputs'].items()},'Execution initial inputs differ from task')
            actual_outputs={p.relative_to(workspace/'outputs').as_posix():p.read_bytes().decode('utf-8') for p in (workspace/'outputs').rglob('*') if p.is_file()}
            require(actual_outputs==e['actual_outputs'],'Execution output evidence differs')
        executions[e['execution_id']]=e; count['executions']+=1
    for folder in sorted((root/'judgments').glob('*')):
        if not folder.is_dir(): continue
        require(check_frozen(folder)['valid'],'Judgment seal changed')
        j=validate_object('judgment',read(folder/'judgment.json')); require(j['judgment_id']==folder.name,'Judgment ID mismatch')
        require(j['execution_id'] in executions,'Unknown judgment execution'); e=executions[j['execution_id']]
        for key in ('case_id','task_id','judge_id'): require(j[key]==e[key],'Judgment cross-reference mismatch')
        require(j['execution_checksums_sha256']==sha(root/'executions'/e['execution_id']/'checksums.json'),'Judgment execution seal changed')
        require(j['judge_sha256']==ds['judges'][j['judge_id']]['implementation_sha256'],'Wrong judge version')
        verdict=judge_csv.judge(ds['tasks'][e['task_id']],e)
        for key in ('status','passed','checks','reason'): require(j[key]==verdict[key],'Judgment cannot be reproduced: '+key)
        count['judgments']+=1
    for path in sorted((root/'comparisons').glob('*.json')):
        c=validate_object('comparison',read(path)); require(path.stem==c['comparison_id'],'Comparison ID mismatch')
        require(c['metrics_status']=='not_run','Metric aggregation is not implemented; computed scores rejected')
        fresh=compare(root/'runs'/c['clean_run_id'],root/'runs'/c['degraded_run_id'])
        for key in fresh:
            if key!='comparison_id': require(fresh[key]==c[key],'Comparison differs from its run evidence')
        count['comparisons']+=1
    for path in sorted((root/'program_ir').glob('*/*.json')):
        ir=validate_object('program_ir',read(path)); require(ir['run_id'] in runs,'IR references unknown run')
        r=runs[ir['run_id']]
        require(r['program_ir_status']!='not_applicable','Official native baseline cannot silently become unified IR')
        for key in ('case_id','source_id','variant_id'): require(ir[key]==r[key],'IR cross-reference mismatch')
        count['program_ir']+=1
    return count

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--root',default=str(Path(__file__).resolve().parents[1])); a=p.parse_args()
    print(validate_results(a.root)); print('EVIDENCE_VALID; no new scientific score computed')
