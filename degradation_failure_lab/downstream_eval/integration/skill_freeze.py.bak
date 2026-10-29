"""Freeze final document-generated Skills without changing their contents."""
from pathlib import Path
import re

from degradation_lab.artifacts import load_run
from degradation_lab.io import inside, inventory, read, sha256, write
from .skill_install import canonical_packages, copy_packages


def freeze_generation(root, generator_run_id, destination, *, case_id=None, condition='clean'):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    if not destination.is_relative_to(root):
        raise ValueError('Freeze destination must be inside the lab')
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError('Freeze output must be new and empty')
    identity, run, result, stages = load_run(root, generator_run_id)
    case_id = case_id or identity['case_id']
    if (identity['case_id'] != case_id or identity['condition_id'] != condition
            or result.get('status') != 'completed' or result.get('errors')):
        raise ValueError('Completed matching generation required')
    lineage, seen = [], set()
    current = run
    while True:
        if current.name in seen:
            raise ValueError('Cyclic generation lineage')
        seen.add(current.name)
        saved = read(current / 'artifact_manifest.json')
        if not saved or any(sha256(inside(current, name)) != digest for name, digest in saved.items()):
            raise ValueError('Generator history changed: ' + current.name)
        invocation = read(current / 'invocation.json')
        if not invocation.get('real_generation') or invocation.get('execution_kind') != 'official':
            raise ValueError('Fixture generation is not a Clean Skill source')
        lineage.append({'run_id': current.name, 'manifest_sha256': sha256(current / 'artifact_manifest.json'),
                        'execution': read(current / 'execution.json')})
        if not (current / 'resume.json').is_file():
            break
        parent = read(current / 'resume.json')['parent_run_id']
        parent_identity, current, _, _ = load_run(root, parent)
        if (parent_identity['case_id'], parent_identity['condition_id']) != (case_id, condition):
            raise ValueError('Generation lineage crosses case/condition')
    registry = run / 'SkillBank/.runtime/document_registry'
    active = {x['skill_id']: x for p in (registry / 'skills').glob('*.json')
              if (x := read(p))['status'] == 'active'}
    expected = {x['id'] for x in stages['register']['upserted_store_skills']}
    if not active or set(active) != expected:
        raise ValueError('Final live registry and exported registration identities differ; explicit review required')
    destination.mkdir(parents=True, exist_ok=True)
    write(destination / 'canonical_files.json', {
        'unique_program_skill_count': len(active),
        'canonical_program_skills': [str(p) for p in (run / 'SkillBank/Users').rglob('SKILL.md')]})
    packages = canonical_packages(root, {
        'generator_run_id': generator_run_id, 'case_id': case_id, 'condition': condition,
        'expected_skill_count': len(active),
        'skill_manifest': (destination / 'canonical_files.json').relative_to(root).as_posix()})
    supports = {x['support_id']: x for p in (registry / 'supports').glob('*.json') if (x := read(p))}
    provenance = {x['entity_id']: x for p in (registry / 'provenance_links').glob('*.json')
                  if (x := read(p)).get('entity_type') == 'skill'}
    docs = {d['doc_id'] for d in stages['ingest']['documents']}
    entries = {}
    for sid, package in packages.items():
        body = package['path'].read_text(encoding='utf-8')
        version = re.search(r'^version: "([^"\r\n]+)"', body, re.M)
        if not version or version[1] != active[sid]['version']:
            raise ValueError('Canonical file and live registry version differ: ' + sid)
        evidence = [supports[s] for s in active[sid]['support_ids']]
        if not evidence or any(x['doc_id'] not in docs for x in evidence):
            raise ValueError('Missing or foreign source evidence: ' + sid)
        entries[sid] = {
            'source_path': package['path'].relative_to(root).as_posix(),
            'files': package['files'], 'metadata': package['metadata'],
            'version': active[sid]['version'], 'support_ids': active[sid]['support_ids'],
            'evidence': evidence, 'provenance': provenance.get(sid, {}), 'sha256': sha256(package['path'])}
    copy_packages(packages, destination / 'skills')
    write(destination / 'skills_manifest.json', {
        'schema_version': 1, 'generator_run_id': generator_run_id, 'case_id': case_id,
        'condition': condition, 'packages': entries, 'lineage': lineage,
        'source_inputs': read(run / 'input_manifest.json'),
        'source_artifact_manifest_sha256': sha256(run / 'artifact_manifest.json'),
        'registry_authority': 'Final live document_registry'})
    write(destination / 'skill_freeze.json', {
        'generator_run_id': generator_run_id, 'files': inventory(destination / 'skills'),
        'manifest_sha256': sha256(destination / 'skills_manifest.json'), 'skill_count': len(entries)})
    return entries
