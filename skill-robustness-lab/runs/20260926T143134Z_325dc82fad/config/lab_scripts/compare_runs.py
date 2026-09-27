"""Validate complete clean/degraded pairing, retaining failures in both conditions."""
import argparse
from pathlib import Path
from uuid import uuid4
from evidence import read,save,sha,digest
from data_contracts import sealed_run,validate_object,VERSION,ContractError
LAB=Path(__file__).resolve().parents[1]

def compare(clean,degraded):
    clean=Path(clean).resolve(); degraded=Path(degraded).resolve(); reasons=[]
    if clean.parent!=degraded.parent or clean.parent.name!='runs': raise ContractError('Both runs must belong to the same lab')
    root=clean.parent.parent
    # Malformed/missing evidence is a validation error, never a measured failure.
    _,cr,cc=sealed_run(root,clean.name); _,dr,dc=sealed_run(root,degraded.name)
    cv=read(clean/'config/variant.json'); dv=read(degraded/'config/variant.json')
    validate_object('variant',cv); validate_object('variant',dv)
    for label,v,r in (('clean',cv,cr),('degraded',dv,dr)):
        if v['condition']!=label: reasons.append('Wrong '+label+' condition')
        for key in ('case_id','source_id','source_version','family_id','variant_id','input_sha256'):
            if v[key]!=r[key]: reasons.append(label+' variant/run differs: '+key)
    for key in ('case_id','source_id','source_version','family_id','split','method_id','generation_repeat','dataset_freeze_sha256'):
        if cr[key]!=dr[key]: reasons.append('Pair differs: '+key)
    if dv['clean_variant_id']!=cv['variant_id'] or dv['clean_sha256']!=cv['input_sha256']: reasons.append('Wrong clean pairing')
    if dv['input_sha256']==cv['input_sha256']: reasons.append('Degraded input equals clean')
    if digest(cc)!=digest(dc): reasons.append('Method/code/environment/standards differ')
    pair=read(degraded/'config/pair.json') if (degraded/'config/pair.json').exists() else {}
    if pair.get('baseline_run_id')!=clean.name or pair.get('baseline_checksums_sha256')!=sha(clean/'checksums.json'):
        reasons.append('Baseline binding missing or changed')
    cs=read(clean/'status.json'); ds=read(degraded/'status.json')
    result={'schema_version':VERSION,'comparison_id':'pair-'+uuid4().hex,'clean_run_id':clean.name,'degraded_run_id':degraded.name,
        **{k:cr[k] for k in ('case_id','source_id','family_id','method_id','generation_repeat')},
        'comparable':not reasons,'reasons':reasons,'clean_status':cr,'degraded_status':dr,
        'eligible_for_skill_quality_comparison':not reasons and cr['structural_pass'] is True and dr['structural_pass'] is True
            and bool(cs.get('evidence_capture_pass') and ds.get('evidence_capture_pass')),
        'semantic_score_delta':None,'task_success_delta':None,'metrics_status':'not_run',
        'metric_reason':'Pair eligibility retains clean/degraded failures. No independent task judgments were aggregated; deltas remain null.'}
    validate_object('comparison',result); return result

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('clean_run'); p.add_argument('degraded_run'); a=p.parse_args()
    for value in (a.clean_run,a.degraded_run):
        if (LAB/'runs'/value).resolve().parent!=(LAB/'runs').resolve(): p.error('Expected run ID')
    result=compare(LAB/'runs'/a.clean_run,LAB/'runs'/a.degraded_run)
    out=LAB/'comparisons'/(result['comparison_id']+'.json'); save(out,result); print(out)
    return 0 if result['comparable'] else 4
if __name__=='__main__': raise SystemExit(main())
