"""Resolve dataset-scoped SGB cases and generation paths alongside other datasets."""
from pathlib import Path
import re

from .io import inside


def case_paths(root):
    root = Path(root).resolve()
    result = {}
    for pattern in ('*/case.json', 'sgb/*/case.json'):
        for path in sorted((root/'cases').glob(pattern)):
            directory = inside(root, path.parent.relative_to(root))
            if path.parent.name in result:
                raise ValueError('Duplicate case_id across layouts: ' + path.parent.name)
            result[path.parent.name] = directory
    return result


def case_path(root, case_id):
    paths = case_paths(root)
    if case_id not in paths:
        raise ValueError('Unknown case_id: ' + case_id)
    return paths[case_id]


def generation_path(root, case_id, condition_id, run_id):
    root = Path(root).resolve()
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',v) for v in (case_id,condition_id,run_id)):
        raise ValueError('Unsafe generation identifier')
    directory = case_path(root, case_id)
    # Windows' intermediate snapshots already consume most of MAX_PATH.
    prefix = 'runs/gen/sgb' if directory.parent == root/'cases/sgb' else 'runs'
    return inside(root, f'{prefix}/{case_id}/{condition_id}/{run_id}')
