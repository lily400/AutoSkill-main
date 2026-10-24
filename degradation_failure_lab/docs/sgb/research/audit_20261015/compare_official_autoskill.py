"""Compare a pinned public checkout with the historical local run fingerprint."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import subprocess

OUT = Path(__file__).parent
OFFICIAL = OUT / 'AutoSkill-official-94c47ca'
LOCAL = Path(r'D:\AS\AutoSkill-main\AutoSkill-main')
MANIFEST = Path(r'D:\AS\AutoSkill-main\degradation_failure_lab\runs\case001_qsv_select\clean\raecd75e08b34\upstream_before.json')
EXPECTED = '94c47ca488d4ba4117d20272e66d49b9877e68cf'

def git(*args):
    return subprocess.check_output(['git', '-C', str(OFFICIAL), *args], text=True).strip()

def sha(data):
    return hashlib.sha256(data).hexdigest()

head = git('rev-parse', 'HEAD')
if head != EXPECTED:
    raise SystemExit(f'Unexpected public checkout revision: {head}; expected {EXPECTED}')
historical = json.loads(MANIFEST.read_text('utf-8'))
files = []
patch = []
for relative, historic_hash in historical.items():
    local, official = LOCAL / relative, OFFICIAL / relative
    record = {'path': relative, 'historical_run_sha256': historic_hash,
              'local_exists': local.exists(), 'official_exists': official.exists()}
    if local.exists():
        a = local.read_bytes()
        record.update(local_sha256=sha(a), local_matches_historical=sha(a)==historic_hash)
    if official.exists():
        b = official.read_bytes()
        record['official_sha256'] = sha(b)
    if local.exists() and official.exists():
        al, bl = a.replace(b'\r\n', b'\n'), b.replace(b'\r\n', b'\n')
        record.update(byte_identical=a==b, lf_identical=al==bl,
                      local_lf_sha256=sha(al), official_lf_sha256=sha(bl))
        if relative.endswith('.py'):
            try:
                record['python_ast_identical'] = ast.dump(ast.parse(al.decode('utf-8-sig'))) == ast.dump(ast.parse(bl.decode('utf-8-sig')))
            except (SyntaxError, UnicodeError) as exc:
                record['python_ast_comparison_error'] = str(exc)
        if al != bl:
            patch.extend(difflib.unified_diff(al.decode('utf-8-sig').splitlines(True), bl.decode('utf-8-sig').splitlines(True), fromfile='local/'+relative, tofile='official/'+relative))
    files.append(record)

core_prefixes = ('AutoSkill4Doc/', 'autoskill/management/')
official_core = {str(p.relative_to(OFFICIAL)).replace('\\','/') for prefix in core_prefixes for p in (OFFICIAL/prefix).rglob('*') if p.is_file()}
local_core = {str(p.relative_to(LOCAL)).replace('\\','/') for prefix in core_prefixes for p in (LOCAL/prefix).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
output = {
    'audit_date': '2026-10-15',
    'official_url': 'https://github.com/ECNU-ICALK/AutoSkill',
    'official_revision': head, 'official_commit_datetime': git('show','-s','--format=%cI','HEAD'),
    'official_checkout': str(OFFICIAL), 'official_status_porcelain': git('status','--porcelain'),
    'local_upstream': str(LOCAL), 'historical_manifest': str(MANIFEST),
    'scope': 'All 164 files recorded by all five Clean runs; path/byte/LF/Python-AST comparisons, no downloaded code executed',
    'summary': {'historical_files':len(files),
                'local_matches_historical':sum(x.get('local_matches_historical',False) for x in files),
                'official_files_found':sum(x['official_exists'] for x in files),
                'byte_identical':sum(x.get('byte_identical',False) for x in files),
                'lf_identical':sum(x.get('lf_identical',False) for x in files),
                'python_files_checked':sum('python_ast_identical' in x for x in files),
                'python_ast_identical':sum(x.get('python_ast_identical',False) for x in files),
                'non_lf_identical_paths':[x['path'] for x in files if not x.get('lf_identical',False)]},
    'core_path_set': {'official_count':len(official_core),'local_count':len(local_core),
                      'official_only':sorted(official_core-local_core),'local_only':sorted(local_core-official_core),
                      'core_paths_not_in_historical_manifest':sorted((official_core|local_core)-set(historical))},
    'files':files,
}
(OUT/'official_autoskill_comparison.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),'utf-8')
(OUT/'official_autoskill_core_diffs.patch').write_text(''.join(patch),'utf-8')
print(json.dumps({k:output[k] for k in ['official_revision','official_commit_datetime','official_status_porcelain','summary','core_path_set']},ensure_ascii=False,indent=2))
