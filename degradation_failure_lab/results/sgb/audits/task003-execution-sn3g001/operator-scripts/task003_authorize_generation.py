"""Record the user's explicit approval; retain all normal execution checks."""
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

root=Path(r'D:\AS\AutoSkill-main\degradation_failure_lab')
sys.path[:0]=[str(root),str(root/'src')]
gate_path=root/'data/manifests/sgb/gates/t-febd929cffec.json'
gate=json.loads(gate_path.read_text(encoding='utf-8'))
request=gate['requested_generation']
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert request['run_id']=='sn3g001' and request['case_id']=='case003_san'
assert request['configuration_sha256']==digest(root/request['configuration'])
assert gate['status']=='BLOCKED'
assert not (root/'runs/gen/sgb/case003_san/clean/sn3g001').exists()
approval=root/'results/sgb/authorizations/task003-generation-sn3g001.md'
audit=root/'results/sgb/audits/task003-execution-sn3g001'
if approval.exists() or audit.exists():raise FileExistsError('Preserve existing approval/audit')
spec=importlib.util.spec_from_file_location('task003_cli',root/'scripts/sgb/sanctuary002.py')
cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
print(json.dumps(cli.history('task003-preflight-sn3g001',create=True)))
audit.mkdir(parents=True)
(audit/'gate-before.json').write_bytes(gate_path.read_bytes())
approval.parent.mkdir(parents=True,exist_ok=True)
approval.write_text('''# Task003 generation and complete-flow approval

Authorizer: human user in this chat. Recorder: Codex. This is a record of an explicit user reply, not a fabricated signature.

Approval question: “请明确授权这项持久变更：为 Task003 保存你本次批准的原文记录，将 t-febd929cffec.json 的生成 gate 改为 PASS，运行 sn3g001（初始 150 次 HTTP、450000 观测 token），随后绑定真实审核结果并运行一对 NoSkill/CleanSkill；必要额度调整保留累计消耗，不重置账本。是否批准？”

User answer: “批准上述门禁变更和完整真实执行”

Scope: case003_san / clean / sn3g001, one initial official Anything2Skill generation using configs/generation/deepseek_flash.json. Initial authorized ceilings: 150 HTTP attempts / 450000 observed tokens. The complete flow includes one NoSkill/CleanSkill pair (sn3e001); exact profile and actual upstream review hash must be bound before downstream prepare. Necessary budget increases are authorized, with revised ceilings and cumulative consumption recorded separately; no reset of existing ledgers or overwrite of previous runs. Source/integrity, package safety, isolation and original Oracle checks remain required.
'''+f'\nRecorded UTC: {datetime.now(timezone.utc).isoformat()}\nConfiguration SHA256: {digest(root/request["configuration"])}\n',encoding='utf-8')
request['authorization_status']='AUTHORIZED'
request['approval_evidence']={'file':approval.relative_to(root).as_posix(),'sha256':digest(approval)}
gate['status']='PASS'
gate['reason']='User explicitly approved persistent Task003 gate change and complete real execution; generation approval source is hash-bound.'
gate['note']='Initial ceilings are authorized. Preserve cumulative consumption for any explicitly recorded increase. Bind actual quality-review/profile hashes before downstream prepare.'
gate_path.write_text(json.dumps(gate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'generation_authorization':'AUTHORIZED','run':'sn3g001','approval_sha256':digest(approval)}))
