"""Read-only inventory of existing Clean runs; writes only to this audit folder."""
from pathlib import Path
import collections
import hashlib
import json
import re

OUT = Path(__file__).parent
ROOT = Path(r'D:\AS\AutoSkill-main')
UP = ROOT / 'AutoSkill-main'
LAB = ROOT / 'degradation_failure_lab'
RUNS = [('case001_qsv_select', 'raecd75e08b34'),
        ('case002_qsv_sort', 'rd9ced750fa54'),
        ('case003_docker_cp', 'rab9a070dfa59'),
        ('case004_git_restore', 'r18307cee4f4c'),
        ('case005_ripgrep_guide', 'r64cee24fae18')]

def read(p):
    return json.loads(p.read_text('utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def manifest_check(root, mapping):
    bad = []
    for rel, expected in mapping.items():
        p = root / rel
        if not p.exists():
            bad.append({'path': rel, 'status': 'missing'})
        elif sha(p) != expected:
            bad.append({'path': rel, 'status': 'hash_mismatch'})
    return {'checked': len(mapping), 'failures': bad}

inventory = []
texts = []
for case, run in RUNS:
    base = LAB / 'runs' / case / 'clean' / run
    result = read(base / 'official_result.json')
    inter = Path(result['intermediate']['run_dir'])
    stages = {s: read(inter / s / 'result.json') for s in ['ingest', 'extract', 'compile', 'register']}
    skills = []
    for f in sorted((base / 'SkillBank' / 'Users' / 'docskill').rglob('SKILL.md')):
        raw = f.read_text('utf-8')
        match = re.search(r'^name:\s*(.*)$', raw, re.M)
        skills.append({'path': str(f), 'sha256': sha(f), 'bytes': f.stat().st_size,
                       'chars': len(raw), 'name_line': match.group(1) if match else None,
                       'frontmatter': raw.startswith('---\n'),
                       'has_prompt_heading': '## Prompt' in raw,
                       'therapist_template': 'Example Therapist Responses' in raw,
                       'line_count': len(raw.splitlines())})
        texts.append('\n# ' + str(f) + '\n\n' + '\n'.join(f'{i}: {l}' for i,l in enumerate(raw.splitlines(),1)))
    decisions = [read(p) for p in sorted((inter/'register'/'decisions').glob('*.json'))]
    inputs = []
    for item in read(base/'input_manifest.json')['inputs']:
        p = base / item['path']
        original = LAB / item['original_path']
        inputs.append({**item, 'actual_sha256': sha(p), 'original_actual_sha256': sha(original),
                       'bytes': p.stat().st_size, 'chars': len(p.read_text('utf-8')),
                       'hashes_match': sha(p)==sha(original)==item['sha256']==item['source_sha256']})
    before = read(base/'upstream_before.json')
    docs = {d['doc_id']: d for d in stages['ingest']['documents']}
    support_checks = []
    for support in stages['extract']['support_records']:
        doc = docs.get(support['doc_id'], {})
        span = support.get('span', {})
        raw = doc.get('raw_text','')
        excerpt = support.get('excerpt','')
        start, end = span.get('start',0), span.get('end',0)
        support_checks.append({'support_id':support['support_id'], 'span':span,
                               'excerpt_in_document':excerpt in raw,
                               'excerpt_equals_span_trimmed':excerpt.strip()==raw[start:end].strip(),
                               'confidence':support.get('confidence')})
    entry = {'case_id':case,'run_id':run,'run_path':str(base),'verification_status':'ACTUALLY_CHECKED_STATIC',
             'official_status':result.get('status'),'errors':result.get('errors'),
             'execution':read(base/'execution.json'),
             'intermediate_dir':str(inter),
             'counts':{'documents':len(stages['ingest']['documents']),
                       'sections':sum(len(d['sections']) for d in stages['ingest']['documents']),
                       'windows':len(stages['ingest']['windows']),
                       'supports':len(stages['extract']['support_records']),
                       'drafts':len(stages['extract']['skill_drafts']),
                       'specs':len(stages['compile']['skill_specs']),
                       'canonical_skills':len(skills),
                       'actions':dict(collections.Counter(d['action'] for d in decisions)),
                       'source_draft_count_distribution':dict(collections.Counter(len(s.get('metadata',{}).get('source_draft_ids',[])) for s in stages['compile']['skill_specs']))},
             'inputs':inputs,'skills':skills,'support_checks':support_checks,
             'upstream_before_after_equal':before==read(base/'upstream_after.json'),
             'upstream_current_hash_check':manifest_check(UP,before),
             'artifact_manifest_check':manifest_check(base,read(base/'artifact_manifest.json')),
             'decisions':[{'skill_id':d['skill_id'],'action':d['action'],'reason':d.get('reason'),'hits':d.get('hits'),'branch':d.get('branch')} for d in decisions],
             'downstream_execution_evidence':'NONE_IDENTIFIED; generation exit code is not task success'}
    inventory.append(entry)

exports = []
first = LAB/'results'/'exports'/RUNS[0][1]
for case,run in RUNS:
    folder = LAB/'results'/'exports'/run
    check = read(folder/'verification.json') if (folder/'verification.json').exists() else None
    exports.append({'requested_case_id':case,'requested_run_id':run,'verification':check,
                    'json_count':len(list(folder.glob('*.json'))),
                    'files_equal_case001':[f.name for f in folder.glob('*.json') if (first/f.name).exists() and sha(f)==sha(first/f.name)]})

result={'audit_date':'2026-10-15','local_head':(ROOT/'.git/refs/heads/master').read_text().strip(),
        'runs':inventory,'export_identity_audit':exports,
        'totals':{'canonical_skills':sum(len(x['skills']) for x in inventory),
                  'therapist_template_skills':sum(s['therapist_template'] for x in inventory for s in x['skills'])}}
(OUT/'clean5_inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
(OUT/'clean5_canonical_texts.md').write_text('\n'.join(texts),'utf-8')
print(json.dumps({'totals':result['totals'],'runs':[{k:x[k] for k in ['case_id','counts','upstream_current_hash_check','artifact_manifest_check']} for x in inventory]},ensure_ascii=False,indent=2))
