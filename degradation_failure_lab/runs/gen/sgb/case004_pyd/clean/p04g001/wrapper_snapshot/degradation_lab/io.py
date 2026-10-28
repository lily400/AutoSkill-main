import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def inside(root, relative):
    root = Path(root).resolve()
    value = Path(relative)
    if value.is_absolute():
        raise ValueError('Expected a project-relative path: ' + str(relative))
    target = (root / value).resolve()
    if not target.is_relative_to(root):
        raise ValueError('Path escapes project: ' + str(relative))
    from .relocations import relocated
    return relocated(root,target)


def resolve_upstream(root):
    """Resolve the official source relative to the lab root, not the shell CWD.

    ANYTHING2SKILL_SOURCE may override the portable, project-relative config.
    The resolved absolute path is written only to each run's provenance snapshot.
    """
    root = Path(root).resolve()
    config = read(root / 'configs/environment.json')
    value = os.environ.get('ANYTHING2SKILL_SOURCE') or config.get('upstream_path')
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Missing upstream_path in configs/environment.json')
    source = Path(value.strip()).expanduser()
    if not source.is_absolute():
        source = root / source
    source = source.resolve()
    required = ('AutoSkill4Doc/pipeline.py', 'autoskill/__init__.py')
    missing = [name for name in required if not (source / name).is_file()]
    if missing:
        raise ValueError(
            'Official Anything2Skill source not found at ' + str(source) +
            '; missing ' + ', '.join(missing) +
            '. Move the repository with both sibling folders intact or set '
            'ANYTHING2SKILL_SOURCE to the official source directory.'
        )
    return source


def check_windows_run_path(target, *, windows=None):
    """Prevent expensive model calls when standard Windows file APIs hit MAX_PATH.

    Forecast the upstream Extract/window snapshot; this is a conservative guard,
    not a guarantee for every eventual skill filename.
    """
    if windows is None:
        windows = os.name == 'nt'
    if not windows:
        return
    sample = (Path(target) / 'SkillBank/.runtime/intermediate_runs' /
              ('0' * 24) / 'extract/windows' / ('0' * 36) /
              (('0' * 36) + '.json'))
    if len(str(sample)) >= 250:
        raise ValueError(
            f'BLOCKED: Windows intermediate path may be too long ({len(str(sample))} characters). '
            'Use a shorter checkout location (for example D:\\AS), or a shorter --run-id. '
            'No model request has been made.'
        )


def inventory(root):
    root = Path(root)
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


def upstream_inventory(root):
    root = Path(root)
    result = {}
    for rel in ('AutoSkill4Doc', 'autoskill', 'tests', 'pyproject.toml'):
        path = root / rel
        files = path.rglob('*') if path.is_dir() else [path]
        for p in files:
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
                result[p.relative_to(root).as_posix()] = sha256(p)
    if not result:
        raise ValueError('Official code inventory is empty')
    return dict(sorted(result.items()))
