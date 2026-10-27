import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
import sys

root=Path(r'D:\AS\AutoSkill-main\degradation_failure_lab' if os.name=='nt' else '/run/desktop/mnt/host/d/AS/AutoSkill-main/degradation_failure_lab');sys.path[:0]=[str(root),str(root/'src')]
from degradation_lab.evaluation import validate_evaluation
from downstream_eval.sgb.task_adapters.audited import sanctuary002 as task
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
run=root/'runs/gen/sgb/case003_san/clean/sn3r001'
output=root/'runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001'
upstream=root/'results/sgb/upstream/sn3r001'
audit=root/'results/sgb/audits/task003-execution-sn3g001'
review_path=root/'evaluations/case003_san/clean/sn3r001/pre_downstream.json'
review=read(review_path)
assert review['reviewer']=='pending' and all(r['status']=='unreviewed' for r in review['records'])
manifest=read(output/'skills_manifest.json');verification=read(upstream/'exports/verification.json')
expected_false={'fresh_skillbank','final_bodies_preserved','evidence_quotes','model_stage_extract','model_stage_compile','model_stage_ingest'}
assert {k for k,v in verification['checks'].items() if not v}==expected_false
assert {x['run_id'] for x in manifest['lineage']}=={'sn3r001','sn3g001'}
for item in manifest['lineage']:
    parent=root/'runs/gen/sgb/case003_san/clean'/item['run_id']
    assert digest(parent/'artifact_manifest.json')==item['manifest_sha256']
    assert all(digest(parent/name)==h for name,h in read(parent/'artifact_manifest.json').items())
assert digest(run/'config.json')==digest(root/'configs/generation/task003_sn3r001_resume.json')
sid='12088cea-5a72-5997-94e9-56794cb7b6dd';order_sid='562b0933-2527-56d9-bbd9-080210e1d2ff'
body=(output/'skills'/sid/'SKILL.md').read_text(encoding='utf-8').splitlines()
assert '4个保护目标' in body[57] and '10分' in body[60] and '5分' in body[62]
hash_rows=[]
for skill_id,package in manifest['packages'].items():
    for name,h in package['files'].items():
        path=output/'skills'/skill_id/name
        assert digest(path)==h
        hash_rows.append({'skill_id':skill_id,'path':path.relative_to(root).as_posix(),'sha256':h})
notes={
 'sanctuary-objectives-4':('correct',[31,58],'Source line 95 states four supported Conservation objectives; final body lines 31/58 explicitly retain four, not a keyword-only inference.'),
 'sanctuary-trigger-10':('correct',[31,61],'Source line 95 assigns 10 to the first condition-1/2 trigger; final body lines 31/61 retain both value and triggering-role condition.'),
 'sanctuary-last-turn-5':('correct',[31,63],'Source line 95 assigns 5 to another player meeting 1/2 on their final extra turn; final body lines 31/63 retain value, role and timing.'),
 'sanctuary-extra-turns':('uncertain',[31,61,62,70,71],'Other players receive exactly one turn, trigger excluded, and condition 3 alone ends immediately. Clockwise appears in ordinary non-trigger handoff Skill, but is not explicit for the extra-turn queue in the delivered endgame Skill. Treat complete scheduling-rule preservation as uncertain; do not invent a confirmed downstream effect.')}
report=upstream/'manual-quality-audit.md'
lines=['# Task003 source-grounded quality review','',
 'Reviewer: Codex assistant, explicitly not independent human sign-off. No extra classifier/model run was used.',
 'Scope: four predeclared target rules and observable package/lineage issues; this is not a full semantic certification of every rule in all 21 Skills.','',
 'Final generator: sn3r001, recovery of sn3g001. Original official status completed; cumulative 124 HTTP attempts, 514291 observed tokens. One original HTTP failure has no observed token usage; actual billing remains unknown.','',
 '## Findings','']
for record in review['records']:
    status,loc,reason=notes[record['rule_id']]
    record.update(status=status,skill_ids=[sid],generated_evidence=[{'skill_id':sid,'lines':loc}],
        trace_refs=[{'stage':'skill','entity_id':sid}],error_types=[],notes=reason)
    if record['rule_id']=='sanctuary-extra-turns':
        record['skill_ids'].append(order_sid)
        record['generated_evidence'].append({'skill_id':order_sid,'lines':[28,54]})
        record['trace_refs'].append({'stage':'skill','entity_id':order_sid})
    lines.append('- '+record['rule_id']+': '+status+' — '+reason)
lines += ['', '## Scope and engineering reconciliation','',
 'The source and generated Skills describe recycling when the pile empties after the trigger. The task narrows pile_recycled to the trigger turn. Preserve this source-versus-task scope distinction; no Skill or Oracle was repaired.',
 'The generic single-run verify remains PARTIAL: inherited stages do not make new ingest/extract/compile calls and the resumed SkillBank is populated. It also compares pre-register specs/support sets against final live output: the official duplicate consolidation changed only non-target skill 7a0ec69e-c238-58af-8d93-d7372f0f0e45 and added support 940b95cc-1863-58d3-8e51-3d48b721b83a. Do not rewrite the raw checks.',
 'The unchanged freeze_generation validator accepted the actual final live registry and full parent/child hash chain. No fabricated package, reset counter, source edit or core algorithm change.',
 'The generated English template heading Example Therapist Responses is an observed formatting residue; not evidence that a target constant is wrong.',
 '', '## Complete inspected final package inventory','']
lines += ['- `'+x['path']+'` SHA256 `'+x['sha256']+'`' for x in hash_rows]
report_text='\n'.join(lines)+'\n'
if report.exists():
    assert report.read_text(encoding='utf-8')==report_text
else:
    report.write_text(report_text,encoding='utf-8')
review.update(reviewer='Codex assistant (not independent human sign-off)',method='manual',
              provenance={'file':report.relative_to(root).as_posix(),'sha256':digest(report)})
validate_evaluation(root,review);write(review_path,review)
task.check_review('sn3r001')
write(audit/'generation-lineage-validation.json',dict(status='FROZEN_LIVE_PACKAGE_AND_LINEAGE_VALIDATED',
    raw_single_run_verify=verification['status'],raw_false_checks=sorted(expected_false),
    explanation='Resumed stages and one official non-target duplicate consolidation; original verify is not rewritten.',
    skill_count=len(manifest['packages']),lineage=manifest['lineage'],frozen_file_count=len(hash_rows),
    source_sha256=task.verify_assets()['source_document']['sha256'],
    semantic_findings=task.review_findings(review)))
gate_path=task.GATE;gate=read(gate_path)
approval=root/'results/sgb/authorizations/task003-downstream-sn3e001.md'
if approval.exists():raise FileExistsError(approval)
(audit/'gate-before-downstream-binding.json').write_bytes(gate_path.read_bytes())
profile=root/gate['downstream']['profile_template'];template=read(profile)
approval.write_text('''# Task003 exact paired downstream approval binding

User explicitly approved: “批准上述门禁变更和完整真实执行”. The question explicitly covered a real NoSkill/CleanSkill pair after binding actual review evidence.

Task: sanctuary_endgame_scheduler_002. Batch: sn3e001. Final generator: sn3r001, the authorized recovery of sn3g001. One NoSkill1 then one CleanSkill1, same model/environment/input/Oracle/tools/budget and the existing conditional full-body-read instruction. NoSkill receives no source document or Skill body. Initial budget: 6 HTTP attempts per arm, 12 total, 100000 estimated input tokens total per arm, 2048 completion tokens per request, no transport retries. Actual task failure is an outcome, not a reason to silently repeat. Necessary execution-limit recovery requires cumulative accounting and preserved prior ledgers.

Quality is reviewed with three correct target rules and one uncertain ordering expression. This authorizes measuring that package without repairing it, not a claim of semantic perfection or human review.
'''+f'\nRecorded UTC: {datetime.now(timezone.utc).isoformat()}\nProfile: {profile.relative_to(root).as_posix()}\nProfile SHA256: {digest(profile)}\nQuality review SHA256: {digest(review_path)}\nFrozen package manifest SHA256: {digest(output/"skills_manifest.json")}\n',encoding='utf-8')
gate['downstream'].update(status='PASS',authorization_status='AUTHORIZED',generator_run_id='sn3r001',
    profile_sha256=digest(profile),quality_review_sha256=digest(review_path),
    approval_evidence={'file':approval.relative_to(root).as_posix(),'sha256':digest(approval)})
write(gate_path,gate)
print(json.dumps({'quality':'reviewed','findings':task.review_findings(review),
                  'downstream_authorization':task.check_authorization('downstream','sn3r001','sn3e001')},ensure_ascii=False))
