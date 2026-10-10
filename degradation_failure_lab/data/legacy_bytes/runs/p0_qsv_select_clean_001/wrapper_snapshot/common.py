"""Experiment bookkeeping only; no skill extraction logic."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
UPSTREAM = Path(r'D:\Baseline-anthing2skill\AutoSkill-main\AutoSkill-main')


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def code_inventory(root=UPSTREAM):
    """Hash algorithm, prompts, configuration and tests, excluding mutable stores."""
    entries = {}
    for rel in ('AutoSkill4Doc', 'autoskill', 'tests', 'pyproject.toml'):
        p = root / rel
        files = p.rglob('*') if p.is_dir() else [p]
        for f in files:
            if f.is_file() and '__pycache__' not in f.parts and f.suffix != '.pyc':
                entries[f.relative_to(root).as_posix()] = sha256(f)
    return dict(sorted(entries.items()))


def new_run(root, name):
    target = Path(root) / name
    target.mkdir(parents=True, exist_ok=False)
    (target / 'SkillBank').mkdir()
    return target
