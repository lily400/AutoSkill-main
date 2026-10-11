"""Read-only upstream audit and one pinned, byte-preserved qsv source download."""
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from common import LAB, UPSTREAM, code_inventory, sha256, utc, write_json

QSV_COMMIT = '257ae7b38738688138dc430c2ccb4eef8766f3fc'
AUTO_COMMIT = '94c47ca488d4ba4117d20272e66d49b9877e68cf'
AUDIT = LAB / 'reports' / 'audit'


def get(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'degradation-failure-lab-P0'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)


def api(repo, endpoint, name):
    url = 'https://api.github.com/' + repo + '/' + endpoint
    cached = AUDIT / (name + '.json')
    if cached.exists():
        return json.loads(cached.read_text(encoding='utf-8'))
    raw = get(url)
    (AUDIT / (name + '.json')).write_bytes(raw)
    return json.loads(raw)


def git(*args):
    return subprocess.check_output(['git', '-C', str(UPSTREAM), *args], text=True, encoding='utf-8').strip()


def main():
    for folder in ('configs', 'data/sources', 'data/manifests', 'runs', 'tests', 'reports/audit'):
        (LAB / folder).mkdir(parents=True, exist_ok=True)
    if not (AUDIT / 'upstream_before.json').exists():
        write_json(AUDIT / 'upstream_before.json', code_inventory())
    environment = {
        'checked_at': utc(), 'python': sys.version, 'executable': sys.executable,
        'platform': platform.platform(), 'git_root': git('rev-parse', '--show-toplevel'),
        'local_commit': git('rev-parse', 'HEAD'), 'local_commit_subject': git('log', '-1', '--format=%s'),
        'status_before': git('status', '--short'),
        'dependencies_declared': [],
        'modules': {m: importlib.util.find_spec(m) is not None for m in ('pytest','yaml','requests','dotenv')},
        'credential_presence_only': {k: bool(os.environ.get(k)) for k in ('DEEPSEEK_API_KEY','ARK_API_KEY','OPENAI_API_KEY','DASHSCOPE_API_KEY')}
    }
    if not (AUDIT / 'local_environment.json').exists():
        write_json(AUDIT / 'local_environment.json', environment)
    tasks = [
        ('repos/ECNU-ICALK/AutoSkill','branches?per_page=100','official_branches'),
        ('repos/ECNU-ICALK/AutoSkill','releases?per_page=100','official_releases'),
        ('repos/ECNU-ICALK/AutoSkill','tags?per_page=100','official_tags'),
        ('repos/ECNU-ICALK/AutoSkill','commits/main','official_main'),
        ('repos/ECNU-ICALK/AutoSkill','git/trees/'+AUTO_COMMIT+'?recursive=1','official_tree'),
        ('orgs/ECNU-ICALK','repos?per_page=100','author_org_repositories'),
        ('repos/dathere/qsv','commits/'+QSV_COMMIT,'qsv_commit'),
        ('repos/dathere/qsv','releases/latest','qsv_latest_release'),
    ]
    errors = []
    for repo, endpoint, name in tasks:
        try:
            d = api(repo, endpoint, name)
            print('saved', name, flush=True)
        except Exception as e:
            errors.append({'name':name,'error':str(e)})
            print('unavailable', name, type(e).__name__, flush=True)
    tree_file = AUDIT / 'official_tree.json'
    if tree_file.exists():
        tree = json.loads(tree_file.read_text(encoding='utf-8'))
        comparison = {'against_commit': AUTO_COMMIT, 'tree_truncated': tree.get('truncated'), 'identical':[], 'lf_equivalent':[], 'different':[], 'missing_local':[]}
        remote_paths = set()
        for e in tree['tree']:
            if e['type'] != 'blob':
                continue
            rel = e['path']
            remote_paths.add(rel)
            f = UPSTREAM / rel
            if not f.is_file():
                comparison['missing_local'].append(rel)
                continue
            data = f.read_bytes()
            def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
            key = 'identical' if blob(data)==e['sha'] else ('lf_equivalent' if blob(data.replace(b'\r\n',b'\n'))==e['sha'] else 'different')
            comparison[key].append(rel)
        comparison['local_code_not_in_remote'] = [p for p in code_inventory() if p not in remote_paths]
        write_json(AUDIT / 'official_comparison.json', comparison)
        print('comparison', {k:len(v) for k,v in comparison.items() if isinstance(v,list)}, flush=True)
    # The source is a current pinned reconstruction, not a verified paper snapshot.
    dest = LAB / 'data' / 'sources' / 'qsv' / QSV_COMMIT
    dest.mkdir(parents=True, exist_ok=True)
    for rel in ('docs/help/select.md', 'LICENSE-MIT', 'Cargo.toml'):
        url = f'https://raw.githubusercontent.com/dathere/qsv/{QSV_COMMIT}/{rel}'
        raw = get(url)
        p = dest / Path(rel).name
        if p.exists() and p.read_bytes()!=raw:
            raise RuntimeError('Pinned source changed: '+str(p))
        p.write_bytes(raw)
        if rel.endswith('select.md'):
            write_json(LAB / 'data/manifests/qsv_select.json', {
                'source_id':'qsv-select-'+QSV_COMMIT[:12], 'source_url':url,
                'source_repository':'https://github.com/dathere/qsv', 'source_commit':QSV_COMMIT,
                'source_path':rel, 'license':'MIT (see pinned LICENSE-MIT and Cargo.toml)',
                'downloaded_at':utc(), 'sha256':sha256(p), 'bytes':len(raw),
                'document_type':'official_cli_help_markdown', 'corresponding_cli_command':'qsv select',
                'classification':'RECONSTRUCTED_OFFICIAL_SOURCE',
                'paper_snapshot_verified':False, 'local_path':p.relative_to(LAB).as_posix(),
                'variant':'clean', 'transform':None
            })
    for name,url in [('paper_v3.html','https://arxiv.org/html/2606.09316v3'),('upstream_README.md',f'https://raw.githubusercontent.com/ECNU-ICALK/AutoSkill/{AUTO_COMMIT}/README.md')]:
        try: (AUDIT / name).write_bytes(get(url))
        except Exception as e: errors.append({'name':name,'error':str(e)})
    write_json(AUDIT / 'acquisition_errors.json', errors)
    print('source', str(dest / 'select.md'), sha256(dest / 'select.md'), flush=True)


if __name__ == '__main__':
    main()
