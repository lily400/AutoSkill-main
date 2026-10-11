import hashlib
import json
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
    return target


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
