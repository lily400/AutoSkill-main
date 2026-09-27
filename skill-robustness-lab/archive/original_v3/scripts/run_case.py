"""Public entry: select one case and one method; delegate to the existing runner."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import tempfile
import run_one
from evidence import read, save

LAB = Path(__file__).resolve().parents[1]

def load_config(case_key, method, environment=None, repeat_id=1):
    if not re.fullmatch(r'case[0-9]+(?:_[A-Za-z0-9-]+)?', case_key):
        raise ValueError('Use a case folder name such as case001 or case002')
    if method not in ('strict', 'chunk') or repeat_id < 1:
        raise ValueError('Choose strict/chunk and a positive repeat_id')
    case_root = (LAB/'cases'/case_key).resolve()
    if case_root.parent != (LAB/'cases').resolve():
        raise ValueError('Case path escapes cases directory')
    case_path = case_root/'case.json'
    case = read(case_path)
    if case.get('case_key') != case_key or case.get('status') != 'ready':
        raise ValueError('Case is not ready; fill its files and run case_tools.py freeze')
    # A case cannot point to another case's clean document or evaluation assets.
    for field in ('clean_file', 'evaluation_dir'):
        target = (LAB/case[field]).resolve()
        if not target.is_relative_to(case_root):
            raise ValueError(field+' must remain inside the selected case')
    env = read(environment or LAB/'configs/environment.json')
    expected_env = {'framework_root', 'python_executable', 'credential_file'}
    if set(env) != expected_env:
        raise ValueError('environment.json must contain only framework/Python/credential paths')
    method_cfg = read(LAB/'configs/methods'/(method+'.json'))
    task = case.get('task', {})
    if set(task) != {'domain', 'domain_type', 'family_name'} or not all(task.values()):
        raise ValueError('Fill the case-specific domain/domain_type/family_name')
    if set(method_cfg) & (expected_env | set(task) | {'case_manifest','repeat_id','case_key'}):
        raise ValueError('Method configuration cannot override environment or case fields')
    return {**env, **method_cfg, **task, 'case_key':case_key,
            'case_manifest':case_path.relative_to(LAB).as_posix(), 'repeat_id':repeat_id}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', required=True, help='Folder name under cases, e.g. case001')
    parser.add_argument('--method', choices=('chunk','strict'), default='chunk')
    parser.add_argument('--environment', help='Optional alternate environment.json')
    parser.add_argument('--repeat-id', type=int, default=1)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--variant', help='Recipe path relative to the selected case folder')
    parser.add_argument('--baseline-run', help='Clean run ID for a degraded run')
    args = parser.parse_args(argv)
    cfg = load_config(args.case, args.method, args.environment, args.repeat_id)
    forwarded = []
    if bool(args.variant) != bool(args.baseline_run):
        parser.error('--variant and --baseline-run must be used together')
    if args.variant:
        case_root=(LAB/'cases'/args.case).resolve()
        recipe=(case_root/args.variant).resolve()
        if not recipe.is_relative_to(case_root/'degradation/recipes'):
            parser.error('Variant recipe must stay in this case degradation/recipes')
        forwarded += ['--variant', str(recipe), '--baseline-run', args.baseline_run]
    if args.preflight_only:
        forwarded += ['--preflight-only']
    # This temporary file is only a bridge. The runner saves the resolved config
    # in the run before execution; no stale global config or old result is reused.
    with tempfile.TemporaryDirectory(prefix='skill-lab-config-') as tmp:
        path=Path(tmp)/'resolved.json'; save(path, cfg)
        return run_one.main(['--config', str(path), *forwarded])

if __name__ == '__main__':
    raise SystemExit(main())
