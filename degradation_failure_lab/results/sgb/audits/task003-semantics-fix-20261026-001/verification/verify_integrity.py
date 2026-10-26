"""Read-only release checks; write evidence only in the review workspace."""
import ast
import hashlib
import json
from pathlib import Path

root = Path(r'D:\AS\AutoSkill-main\degradation_failure_lab')
local = Path(__file__).resolve().parent
allowed = {
    'scripts/sgb/sanctuary002.py',
    'downstream_eval/sgb/task_adapters/audited/sanctuary002.py',
    'tests/test_sgb_sanctuary002.py',
    'tests/test_skill_freeze.py',
    'docs/sgb/task003-clean-runbook.md',
    'docs/sgb/task003-clean-admission.md',
}
before = json.loads((local/'before-hashes.json').read_text(encoding='utf-8-sig'))
digest = lambda path: hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()
changed, missing, current = [], [], {}
for name, expected in before.items():
    path = root/name
    if not path.is_file():
        missing.append(name)
        continue
    actual = digest(path)
    current[name] = actual
    if actual != expected:
        changed.append(name)
unexpected = sorted(set(changed)-allowed)
parsed = []
for name in sorted(allowed):
    if name.endswith('.py'):
        ast.parse((root/name).read_text(encoding='utf-8-sig'), filename=name)
        parsed.append(name)
historical = [n for n in before if n.split('/')[0] in ('runs','results','evaluations')]
protected = ['src/degradation_lab/evaluation.py','src/degradation_lab/schema.py',
    'scripts/lab.py','scripts/sgb/pilot.py','downstream_eval/sgb/pilot.py',
    'downstream_eval/sgb/attribution.py','downstream_eval/integration/skill_freeze.py']
# Find the actual budget module rather than assuming its location.
protected += [n for n in before if n.endswith('/request_budget.py')]
gate_name = 'data/manifests/sgb/gates/t-febd929cffec.json'
gate = json.loads((root/gate_name).read_text(encoding='utf-8'))
value = dict(success=not missing and not unexpected and set(changed)==allowed,
    baseline_files=len(before), changed_files=sorted(changed),missing_files=missing,
    unexpected_changes=unexpected, historical_files=len(historical),
    historical_changed=[n for n in historical if n in changed or n in missing],
    protected_shared_components={n:dict(sha256=current.get(n),unchanged=current.get(n)==before.get(n)) for n in protected},
    code_manifest={n:dict(before=before[n],after=current.get(n)) for n in sorted(allowed)},
    python_ast_parsed=parsed,
    gate=dict(path=gate_name,unchanged=current.get(gate_name)==before.get(gate_name),
              status=gate['status'],downstream_status=gate['downstream']['status']))
(local/'integrity.json').write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:value[k] for k in ('success','baseline_files','changed_files','historical_files','historical_changed','gate')},ensure_ascii=False))
if not value['success'] or value['historical_changed']:
    raise SystemExit(1)
