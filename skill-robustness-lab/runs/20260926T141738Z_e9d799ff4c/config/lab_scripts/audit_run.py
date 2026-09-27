"""Read-only run audit; output is written under reports, never into the run."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from evidence import collect, read, save, verify, check_frozen
LAB=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('run_id'); a=p.parse_args()
    run=(LAB/'runs'/a.run_id).resolve()
    if run.parent!=LAB/'runs' or not run.is_dir(): p.error('Expected an existing run ID')
    result=collect(run)
    result['run_id']=a.run_id
    result['sealed_integrity']=check_frozen(run)
    old=run/'official_artifacts_sha256.json'
    result['official_integrity']=verify(run/'official',read(old)) if old.exists() else {'missing_manifest':True}
    result['historical_status']=read(run/'status.json') if (run/'status.json').exists() else None
    if (run/'rule_review.json').exists(): result['existing_semantic_review']=read(run/'rule_review.json')
    path=LAB/'reports'/(a.run_id+'_audit_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid4().hex[:6]+'.json')
    save(path,result); print(path)
    return 0 if result['pipeline_pass'] and result['sealed_integrity']['valid'] and not any(result['official_integrity'].values()) else 4
if __name__=='__main__': raise SystemExit(main())
