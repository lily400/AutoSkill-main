"""Public official-native generation entry; validate fixed data before calls."""
import argparse
from pathlib import Path
import tempfile
from evidence import read, save
from data_contracts import select, require
import run_one
LAB=Path(__file__).resolve().parents[1]

def load_config(case_key,method,environment=None,repeat_id=1,variant_id=None):
    require(method in ('chunk','strict') and type(repeat_id) is int and repeat_id>=1,'Invalid method/repeat')
    _,case,_=select(LAB,case_key,variant_id)
    env=read(environment or LAB/'configs/environment.json')
    require(set(env)=={'framework_root','python_executable','credential_file'},'Environment must contain exactly three paths')
    exe=Path(env['python_executable'])
    if exe.is_dir(): exe=exe/'python.exe'
    require(exe.is_file(),'Python executable missing: '+str(exe)); env['python_executable']=str(exe.resolve())
    method_cfg=read(LAB/'configs/methods'/(method+'.json'))
    expected=(set(run_one.CLI_KEYS)-set(case['official'])) | {'method_id','embeddings_base_url','timeout_s','max_tokens','run_timeout_s'}
    require(set(method_cfg)==expected,'Method configuration differs from supported official CLI')
    return {**env,**method_cfg,**case['official'],'case_key':case_key,
        'case_manifest':f'cases/{case_key}/case.json','repeat_id':repeat_id,'variant_id':variant_id}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--case',required=True)
    p.add_argument('--method',choices=('chunk','strict'),default='chunk'); p.add_argument('--environment')
    p.add_argument('--repeat-id',type=int,default=1); p.add_argument('--variant-id')
    p.add_argument('--baseline-run'); p.add_argument('--preflight-only',action='store_true'); a=p.parse_args(argv)
    cfg=load_config(a.case,a.method,a.environment,a.repeat_id,a.variant_id)
    forwarded=[]
    if a.baseline_run: forwarded+=['--baseline-run',a.baseline_run]
    if a.preflight_only: forwarded+=['--preflight-only']
    with tempfile.TemporaryDirectory(prefix='skill-lab-config-') as tmp:
        file=Path(tmp)/'resolved.json'; save(file,cfg)
        return run_one.main(['--config',str(file),*forwarded])
if __name__=='__main__': raise SystemExit(main())
