"""Deterministic, local-only Git task construction. Never run on an existing repo."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

TARGET = 'target.txt'
OTHER = 'unrelated.txt'
SENTINEL = 'sentinel.txt'
VERSIONS = (b'V1: old committed content\n', b'V2: current HEAD content\n',
            b'V3: staged content\n', b'V4: working content\n')


def git(repo, *args, data=None):
    # Whitelist the process environment, so inherited GIT_DIR/config/filter state cannot enter.
    env = {k: v for k, v in os.environ.items() if k.upper() in
           {'PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'TMPDIR', 'COMSPEC'}}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM='1',
               GIT_NO_REPLACE_OBJECTS='1', GIT_TERMINAL_PROMPT='0', LC_ALL='C', TZ='UTC',
               GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
               GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid',
               GIT_AUTHOR_DATE='2000-01-01T00:00:00+0000', GIT_COMMITTER_DATE='2000-01-01T00:00:00+0000')
    command = ['git', '-c', 'core.hooksPath=' + os.devnull, '-c', 'core.attributesFile=' + os.devnull,
               '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false', '-C', str(repo), *args]
    result = subprocess.run(command, input=data, capture_output=True, env=env, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace'))
    return result.stdout


def build(repo):
    repo = Path(repo)
    repo.mkdir(parents=True, exist_ok=False)
    git(repo, 'init', '--quiet', '--template=', '--object-format=sha1', '--initial-branch=main')
    for key, value in [('core.autocrlf', 'false'), ('core.eol', 'lf'), ('core.filemode', 'true'),
                       ('core.ignorecase', 'false'), ('core.logAllRefUpdates', 'false'),
                       ('core.hooksPath', 'disabled-hooks'), ('core.attributesFile', 'disabled-attributes'),
                       ('core.fsmonitor', 'false'), ('core.untrackedCache', 'false'), ('index.version', '2')]:
        git(repo, 'config', key, value)
    # Create commits with plumbing: no inherited hooks, commit signing or external filters.
    other_bytes = b'unrelated committed content\n'
    other_blob = git(repo, 'hash-object', '-w', '--stdin', data=other_bytes).strip().decode()
    blobs = [git(repo, 'hash-object', '-w', '--stdin', data=v).strip().decode() for v in VERSIONS[:3]]
    commits = []
    for n, blob in enumerate(blobs[:2]):
        tree_data = f'100644 blob {blob}\t{TARGET}\n100644 blob {other_blob}\t{OTHER}\n'.encode()
        tree = git(repo, 'mktree', data=tree_data).strip().decode()
        parent = ['-p', commits[-1]] if commits else []
        commits.append(git(repo, 'commit-tree', tree, *parent, data=f'Fixture {n}\n'.encode()).strip().decode())
    git(repo, 'update-ref', 'refs/heads/main', commits[1])
    git(repo, 'update-index', '--add', '--cacheinfo', '100644,' + blobs[2] + ',' + TARGET)
    git(repo, 'update-index', '--add', '--cacheinfo', '100644,' + other_blob + ',' + OTHER)
    (repo / TARGET).write_bytes(VERSIONS[3])
    (repo / OTHER).write_bytes(b'unrelated working change must survive\n')
    (repo / SENTINEL).write_bytes(b'untracked sentinel must survive\n')
    for p in repo.glob('*.txt'):
        p.chmod(0o644)
    observed = [git(repo, 'show', commits[0] + ':' + TARGET), git(repo, 'show', 'HEAD:' + TARGET),
                git(repo, 'show', ':' + TARGET), (repo / TARGET).read_bytes()]
    if observed != list(VERSIONS) or len(set(observed)) != 4:
        raise ValueError('Fixture does not contain four distinct target versions')
    return {'commit_a': commits[0], 'head': commits[1], 'target_blob': blobs[0],
            'target_mode': 0o100644, 'target': TARGET,
            'versions_sha256': [hashlib.sha256(x).hexdigest() for x in observed]}


if __name__ == '__main__':
    import sys
    print(json.dumps(build(Path(sys.argv[1])), sort_keys=True))
