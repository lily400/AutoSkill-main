"""Read raw artifact bytes only. Never invoke Git inside an Agent-owned repo."""
import hashlib
import os
import stat
import struct
from pathlib import Path

if __package__:
    from .fixture import OTHER, SENTINEL, TARGET, VERSIONS
else:
    from fixture import OTHER, SENTINEL, TARGET, VERSIONS


def snapshot(directory, exclude=()):
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('Expected a real artifact directory')
    files = {}
    total_bytes = 0
    for current, dirs, names in os.walk(directory, followlinks=False):
        for name in dirs + names:
            path = Path(current) / name
            relative = path.relative_to(directory).as_posix()
            if relative in exclude or any(relative.startswith(x + '/') for x in exclude):
                if name in dirs:
                    dirs.remove(name)
                continue
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError('Unsafe artifact type: ' + relative)
            if stat.S_ISREG(mode):
                total_bytes += path.stat().st_size
                if path.stat().st_size > 8_000_000 or total_bytes > 32_000_000 or len(files) >= 1000:
                    raise ValueError('Artifact size limit exceeded')
                files[relative] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                   'executable': bool(mode & 0o111) if os.name != 'nt' else False}
    return files


def index_entries(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_000_000:
        raise ValueError('Missing or unsafe Git index')
    data = path.read_bytes()
    if len(data) < 32 or hashlib.sha1(data[:-20]).digest() != data[-20:]:
        raise ValueError('Invalid Git index checksum')
    signature, version, count = struct.unpack('>4sII', data[:12])
    if signature != b'DIRC' or version != 2 or count > 100:
        raise ValueError('Expected bounded Git index v2')
    entries, offset = {}, 12
    for _ in range(count):
        start = offset
        if offset + 62 > len(data) - 20:
            raise ValueError('Truncated Git index')
        mode = struct.unpack('>I', data[offset + 24:offset + 28])[0]
        blob = data[offset + 40:offset + 60].hex()
        flags = struct.unpack('>H', data[offset + 60:offset + 62])[0]
        end = data.find(b'\0', offset + 62, len(data) - 20)
        if end < 0 or flags & 0xC000:
            raise ValueError('Unsupported extended/assume-valid index entry')
        name_bytes = data[offset + 62:end]
        name = name_bytes.decode('utf-8')
        if flags & 0xFFF != min(len(name_bytes), 0xFFF):
            raise ValueError('Index pathname length disagrees with flags')
        if not name or name in entries or name.startswith('/') or '..' in name.split('/'):
            raise ValueError('Invalid or duplicate index path')
        entries[name] = {'blob': blob, 'mode': mode, 'stage': (flags >> 12) & 3}
        offset = start + ((end + 1 - start + 7) // 8) * 8
        if offset > len(data) - 20 or any(data[end:offset]):
            raise ValueError('Invalid index padding')
    while offset < len(data) - 20:
        if offset + 8 > len(data) - 20:
            raise ValueError('Truncated index extension')
        name, size = struct.unpack('>4sI', data[offset:offset + 8])
        if name != b'TREE' or offset + 8 + size > len(data) - 20:
            raise ValueError('Unsupported mandatory or truncated index extension')
        offset += 8 + size
    if offset != len(data) - 20:
        raise ValueError('Index has invalid trailing bytes')
    return entries


def trusted_state(repo, fixture):
    """Called by trusted builder BEFORE handing the fixture to any actor."""
    return {'fixture': fixture, 'worktree': snapshot(repo, exclude=('.git',)),
            'git_metadata': snapshot(Path(repo) / '.git', exclude=('index',)),
            'index': index_entries(Path(repo) / '.git/index')}


def evaluate(repo, trusted):
    assertions = {}
    try:
        repo = Path(repo)
        worktree = snapshot(repo, exclude=('.git',))
        metadata = snapshot(repo / '.git', exclude=('index',))
        index = index_entries(repo / '.git/index')
        expected_worktree = dict(trusted['worktree'])
        expected_worktree[TARGET] = dict(expected_worktree[TARGET], sha256=hashlib.sha256(VERSIONS[0]).hexdigest())
        expected_index = dict(trusted['index'])
        expected_index[TARGET] = {'blob': trusted['fixture']['target_blob'],
                                  'mode': trusted['fixture']['target_mode'], 'stage': 0}
        assertions['target_worktree_bytes_and_mode'] = worktree.get(TARGET) == expected_worktree[TARGET]
        assertions['target_index_blob_and_mode'] = index.get(TARGET) == expected_index[TARGET]
        refs = lambda m: {k: v for k, v in m.items() if k == 'HEAD' or k.startswith('refs/') or k == 'packed-refs'}
        assertions['head_and_all_refs_unchanged'] = refs(metadata) == refs(trusted['git_metadata'])
        assertions['unrelated_tracked_worktree'] = worktree.get(OTHER) == trusted['worktree'][OTHER]
        assertions['unrelated_tracked_index'] = index.get(OTHER) == trusted['index'][OTHER]
        assertions['untracked_sentinel_preserved'] = worktree.get(SENTINEL) == trusted['worktree'][SENTINEL]
        assertions['no_other_worktree_changes'] = worktree == expected_worktree
        assertions['complete_index_matches'] = index == expected_index
        assertions['no_extra_commits_objects_or_git_metadata_changes'] = metadata == trusted['git_metadata']
        reason = None
    except (OSError, ValueError, struct.error, UnicodeError) as error:
        assertions['artifact_structurally_safe_and_readable'] = False
        reason = type(error).__name__ + ': ' + str(error)
    success = bool(assertions) and all(assertions.values())
    return {'status': 'PASS' if success else 'FAIL', 'success': success,
            'assertion_results': assertions, 'reason': reason, 'verifier_version': 'git-state-v1'}
