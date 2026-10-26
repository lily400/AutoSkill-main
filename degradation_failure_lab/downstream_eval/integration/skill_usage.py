"""Evidence-based Skill delivery reports; no model or framework initialization."""
import json
from pathlib import Path, PurePosixPath
import re
from xml.etree import ElementTree

from degradation_lab.io import inventory, read, sha256, write


def _events(path):
    if not path.is_file():
        return None
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def _compact(text):
    return re.sub(r'\s+', '', re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text))


def audit_skill_usage(output, label, trial_dir):
    """Distinguish provision, body access, context delivery and unproven behavioral use."""
    output, trial_dir = Path(output), Path(trial_dir)
    manifest = read(output / 'manifests' / (label + '.json'))
    expected = manifest['metadata']
    # Stored paths may be Linux paths while an old run is analyzed on Windows.
    stage_name = PurePosixPath(str(manifest['staged_root']).replace('\\', '/')).name
    if stage_name in ('', '.', '..') or any('/' in sid or '\\' in sid or sid in ('', '.', '..') for sid in expected):
        raise ValueError('Unsafe Skill evidence path')
    stage = output / 'staged' / stage_name
    if inventory(stage) != manifest['files']:
        raise ValueError('Skill usage analysis requires unchanged staged files')
    observer = trial_dir / 'p1-observer'
    paths = {name: observer / ('p1-' + name + '.jsonl')
             for name in ('installation', 'model-requests', 'model-http', 'tool-actions', 'skill-reads')}
    installation = _events(paths['installation'])
    requests = _events(paths['model-requests'])
    http = _events(paths['model-http'])
    summary_path = observer / 'p1-summary.json'
    summary = read(summary_path) if summary_path.is_file() else None
    installed = next((x for x in installation or [] if x.get('status') == 'PASS'), None)
    if installed is not None and installed.get('file_hashes') != manifest['files']:
        raise ValueError('Installation evidence differs from frozen Skill manifest')
    successful = {x['logical_request_number'] for x in http or []
                  if x.get('http_status') is not None and 200 <= x['http_status'] < 300}
    contexts = []
    index_ids = set()
    for number, request in enumerate(requests or [], 1):
        if number not in successful:
            continue
        text = '\n'.join(m['content'] for m in request['messages'] if isinstance(m.get('content'), str))
        contexts.append(_compact(text))
        for block in re.findall(r'<available_skills>.*?</available_skills>', text, re.S):
            for entry in ElementTree.fromstring(block):
                sid = PurePosixPath(entry.findtext('location', '')).parent.name
                if sid in expected:
                    if any(entry.findtext(k) != expected[sid][k] for k in ('name', 'description')):
                        raise ValueError('Delivered index metadata differs from frozen Skill')
                    index_ids.add(sid)
    delivery_observed = bool(contexts)
    paid = summary is not None and summary.get('mode') == 'paid'
    model_reads = set(summary.get('model_read_ids', [])) if paid else set()
    probe_reads = set(summary.get('controlled_probe_read_ids', [])) if summary else set()
    rows = []
    for sid, metadata in sorted(expected.items()):
        path = stage / sid / 'SKILL.md'
        body = path.read_text(encoding='utf-8')
        full_body = any(_compact(body) in context for context in contexts) if body else False
        rows.append({
            'skill_id': sid, 'name': metadata['name'], 'sha256': sha256(path),
            'installed': sid in installed.get('installed_ids', []) if installed else None,
            'discovered': sid in installed.get('discovered_ids', []) if installed else None,
            'index_in_successful_model_request': sid in index_ids if delivery_observed else None,
            'model_file_access_observed': sid in model_reads if summary is not None else None,
            'full_body_in_successful_model_request': full_body if delivery_observed else None,
            'controlled_probe_file_access_observed': sid in probe_reads,
            'behavioral_use': 'UNKNOWN',
        })
    evidence = {str(p): sha256(p) for p in [*paths.values(), summary_path] if p.is_file()}
    counts = {key: sum(row[key] is True for row in rows) for key in (
        'installed', 'discovered', 'index_in_successful_model_request',
        'model_file_access_observed', 'full_body_in_successful_model_request')}
    if not expected:
        status = 'NO_SKILL_CONDITION'
    elif not delivery_observed or summary is None or installed is None:
        status = 'INCOMPLETE_EVIDENCE'
    elif counts['full_body_in_successful_model_request']:
        status = 'BODY_CONTEXT_CONFIRMED'
    elif counts['model_file_access_observed']:
        status = 'FILE_ACCESSED_BODY_CONTEXT_NOT_FULLY_CONFIRMED'
    elif counts['index_in_successful_model_request']:
        status = 'INDEX_ONLY_OBSERVED'
    else:
        status = 'NO_SKILL_CONTEXT_CONFIRMED'
    return {
        'schema_version': 1, 'label': label, 'generator_run_id': manifest['generator_run_id'],
        'status': status, 'expected_skill_count': len(expected), 'counts': counts,
        'successful_model_requests': len(successful), 'per_skill': rows, 'evidence_files': evidence,
        'behavioral_use': {'status': 'UNKNOWN', 'reason': 'Reading or matching text does not prove reliance on its rules.'},
        'limits': [
            'Framework startup reads and controlled zero-model probes are not model-directed reading.',
            'Only complete body matches in successful requests are confirmed here; partial or paged coverage is not inferred from a negative full-body match.',
            'Missing observation logs produce unknown fields, not evidence of no access.',
        ],
    }


def save_skill_usage(output, label, trial_dir, destination):
    report = audit_skill_usage(output, label, trial_dir)
    write(destination, report)
    return report
