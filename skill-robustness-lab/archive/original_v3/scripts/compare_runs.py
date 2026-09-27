"""Validate a clean/degraded pair; no fabricated semantic or execution score."""
import argparse
from pathlib import Path
from uuid import uuid4
from evidence import read, save, check_frozen, sha
LAB=Path(__file__).resolve().parents[1]
def compare(clean,degraded):
    clean=Path(clean); degraded=Path(degraded); reasons=[]
    for label,run in [('clean',clean),('degraded',degraded)]:
        if not check_frozen(run)['valid']: reasons.append(label+': missing or changed sealed evidence')
    paths=['config/comparison_fingerprint.json','config/variant.json','status.json']
    if any(not (r/p).is_file() for r in (clean,degraded) for p in paths):
        return {'comparable':False,'reasons':reasons+['missing v2 metadata; legacy runs cannot be silently upgraded']}
    cv=read(clean/'config/variant.json'); dv=read(degraded/'config/variant.json')
    if cv['condition']!='clean' or dv['condition']!='degraded': reasons.append('conditions are not clean/degraded')
    if cv['case_id']!=dv['case_id'] or cv['clean_sha256']!=dv['clean_sha256']: reasons.append('different source case')
    if cv['repeat_id']!=dv['repeat_id']: reasons.append('repeat_id mismatch')
    if read(clean/'config/comparison_fingerprint.json')['sha256']!=read(degraded/'config/comparison_fingerprint.json')['sha256']:
        reasons.append('model/method/source/runtime/evaluation differs')
    pair=read(degraded/'config/pair.json') if (degraded/'config/pair.json').exists() else {}
    if pair.get('baseline_run_id')!=clean.name: reasons.append('degraded run points to another/no baseline')
    if (clean/'checksums.json').exists() and pair.get('baseline_checksums_sha256')!=sha(clean/'checksums.json'):
        reasons.append('baseline manifest changed')
    cs=read(clean/'status.json'); ds=read(degraded/'status.json')
    if not cs.get('pipeline_pass'): reasons.append('clean generation did not pass structural checks')
    if ds.get('status') in ('preflight_only','preflight','running'):
        reasons.append('degraded generation has not completed or failed')
    # Failed degraded builds stay in the denominator; expose their status, do not delete them.
    return {'comparable':not reasons,'reasons':reasons,'clean_run_id':clean.name,'degraded_run_id':degraded.name,
            'clean_status':cs,'degraded_status':ds,
            'eligible_for_skill_quality_comparison':not reasons and bool(cs.get('pipeline_pass') and ds.get('pipeline_pass') and cs.get('evidence_capture_pass') and ds.get('evidence_capture_pass')),
            'failed_build_interpretation':'Retained; classify provider/network/infrastructure failures separately from skill quality.',
            'semantic_score_delta':None,'task_success_delta':None,
            'note':'Comparable configuration is not proof of semantic correctness. Missing execution/judging cannot be scored as success or zero.'}
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('clean_run');p.add_argument('degraded_run');a=p.parse_args()
    runs=[]
    for value in (a.clean_run,a.degraded_run):
        r=(LAB/'runs'/value).resolve()
        if r.parent!=LAB/'runs' or not r.is_dir(): p.error('Expected existing run IDs')
        runs.append(r)
    result=compare(*runs)
    out=LAB/'comparisons'/('pair_'+uuid4().hex[:10]+'.json');save(out,result);print(out)
    return 0 if result['comparable'] else 4
if __name__=='__main__': raise SystemExit(main())
