import hashlib,json
from datetime import datetime,timezone
from pathlib import Path

root=Path(r'D:\AS\AutoSkill-main\degradation_failure_lab')
parent=root/'runs/gen/sgb/case003_san/clean/sn3g001'
gate_path=root/'data/manifests/sgb/gates/t-febd929cffec.json'
gate=json.loads(gate_path.read_text(encoding='utf-8'))
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert gate['requested_generation']['run_id']=='sn3g001'
assert not (root/'runs/gen/sgb/case003_san/clean/sn3r001').exists()
approval=root/'results/sgb/authorizations/task003-generation-sn3r001-resume.md'
config_path=root/'configs/generation/task003_sn3r001_resume.json'
if approval.exists() or config_path.exists():raise FileExistsError('Do not replace recovery evidence')
audit=root/'results/sgb/audits/task003-execution-sn3g001'
(audit/'gate-generation-sn3g001.json').write_bytes(gate_path.read_bytes())
execution=json.loads((parent/'execution.json').read_text(encoding='utf-8'))
config=json.loads((parent/'config.json').read_text(encoding='utf-8'))
config.update(max_http_calls=300,max_observed_total_tokens=1000000)
config_path.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
approval.write_text('''# Task003 authorized cumulative-budget recovery

User explicitly approved: “批准上述门禁变更和完整真实执行”. The approved question expressly included necessary limit adjustment with cumulative consumption retained and no ledger reset.

sn3g001 stopped on the existing observer token threshold during registration after completing ingest, extract and compile. Preserve it unchanged. The supported recovery sn3r001 resumes that exact parent, reusing completed stages and cached registration decisions. New cumulative ceilings across parent + recovery: 300 HTTP attempts / 1000000 observed tokens. These are not fresh counters or an additional replicate. Model, source, prompts and core algorithm remain unchanged.
'''+f'\nRecorded UTC: {datetime.now(timezone.utc).isoformat()}\nParent manifest SHA256: {digest(parent/"artifact_manifest.json")}\nParent actual execution: {json.dumps(execution)}\nExpected resumed configuration SHA256: {digest(config_path)}\nOriginal approval: results/sgb/authorizations/task003-generation-sn3g001.md\n',encoding='utf-8')
request=gate['requested_generation']
request.update(run_id='sn3r001',configuration=config_path.relative_to(root).as_posix(),
               configuration_sha256=digest(config_path),max_http_calls=300,
               max_observed_total_tokens=1000000,authorization_status='AUTHORIZED',
               approval_evidence={'file':approval.relative_to(root).as_posix(),'sha256':digest(approval)})
gate['downstream']['generator_run_id']='sn3r001'
gate['reason']='User-authorized cumulative-limit increase and safe registration recovery from sn3g001; original run retained.'
gate_path.write_text(json.dumps(gate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'recovery':'sn3r001','parent':'sn3g001','cumulative_limits':{'http':300,'observed_tokens':1000000}}))
