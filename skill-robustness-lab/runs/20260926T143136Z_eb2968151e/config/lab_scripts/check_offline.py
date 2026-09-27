"""Run meaningful offline checks and save their actual outputs, without API calls."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
from evidence import save
from data_contracts import utc

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--preflight',action='store_true'); a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    commands=[['scripts/validate_data.py'],['-m','unittest','discover','-s','tests','-v']]
    if a.preflight:
        commands.extend([['scripts/run_case.py','--case','case001','--method',method,'--preflight-only'] for method in ('chunk','strict')])
    commands.append(['scripts/validate_results.py'])
    result={'kind':'offline_engineering_verification','started_at_utc':utc(),'python':sys.executable,'steps':[],'model_calls':0}
    env=os.environ.copy(); env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
    for cmd in commands:
        proc=subprocess.run([sys.executable,'-B',*cmd],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=180)
        result['steps'].append({'argv':[sys.executable,'-B',*cmd],'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
        print('PASS' if proc.returncode==0 else 'FAIL',' '.join(cmd),flush=True)
        if proc.returncode: break
    result['passed']=len(result['steps'])==len(commands) and all(x['exit_code']==0 for x in result['steps'])
    result['finished_at_utc']=utc(); out=root/'reports'/('offline-'+uuid4().hex+'.json'); save(out,result); print(out)
    return 0 if result['passed'] else 4
if __name__=='__main__': raise SystemExit(main())
