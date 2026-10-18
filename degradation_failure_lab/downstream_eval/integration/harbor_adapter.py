"""Pinned official method probes, not a second Agent runner."""
import ast
import asyncio
import hashlib
import importlib.metadata
import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import SimpleNamespace

from degradation_lab.io import inside, read, sha256


def verify_sources(root):
    lock = read(root / 'downstream_eval/configs/runner.lock.json')
    source = inside(root, lock['external_source'])
    for relative, item in lock['source_files'].items():
        data = inside(source, relative).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != item['git_blob_sha1'] or sha256(source / relative) != item['sha256']:
            raise ValueError('Changed official dependency: ' + relative)
    return source, lock


def crlf_compat(terminus):
    """Only normalize the memory input; retain the upstream parser and every file."""
    original = terminus._parse_skill_frontmatter
    terminus._parse_skill_frontmatter = staticmethod(
        lambda content: original(content.replace('\r\n', '\n').replace('\r', '\n')))
    return original


def official_probe_class(root, patched=True):
    source, _ = verify_sources(root)
    path = source / 'src/harbor/agents/terminus_2/terminus_2.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Terminus2')
    names = {'_parse_skill_frontmatter', '_build_skills_section'}
    methods = [x for x in cls.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.name in names]
    assert {x.name for x in methods} == names
    # Execute the exact official method AST without importing the model stack.
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0),
                             ast.ClassDef(name='Terminus2', bases=[], keywords=[], body=methods, decorator_list=[])], type_ignores=[])
    namespace = {'shlex': shlex}
    exec(compile(ast.fix_missing_locations(module), str(path), 'exec'), namespace)
    terminus = namespace['Terminus2']
    if patched:
        crlf_compat(terminus)
    return terminus


def official_resolve_skills(root, paths):
    source, _ = verify_sources(root)
    tree = ast.parse((source / 'src/harbor/skills.py').read_text(encoding='utf-8'))
    names = {'ResolvedSkill', 'resolve_skills', '_find_skill_dirs'}
    nodes = [x for x in tree.body if getattr(x, 'name', None) in names]
    namespace = {'Path': Path, 'dataclass': dataclass, 'SKILL_FILE_NAME': 'SKILL.md'}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), '<official skills.py>', 'exec'), namespace)
    return namespace['resolve_skills'](paths)


def validate_task_network_modes(root, task):
    """Small static contract check; never claim full TaskConfig validation."""
    import tomllib
    source, _ = verify_sources(root)
    tree = ast.parse((source / 'src/harbor/models/task/config.py').read_text(encoding='utf-8'))
    node = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'NetworkMode')
    namespace = {'Enum': Enum}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), '<official NetworkMode>', 'exec'), namespace)
    data = tomllib.loads((Path(task) / 'task.toml').read_text(encoding='utf-8'))
    for env in (data['environment'], data['verifier']['environment']):
        namespace['NetworkMode'](env['network_mode'])
    if data['verifier']['environment_mode'] != 'separate':
        raise ValueError('Task must use separate verifier')
    return {'status': 'PASS', 'scope': 'TOML syntax and exact official NetworkMode enum only'}


def bash_path():
    if os.name == 'nt':
        git = shutil.which('git')
        candidate = Path(git).parent.parent / 'bin/bash.exe' if git else Path('missing')
        if candidate.is_file():
            return str(candidate)
    shell = shutil.which('bash')
    if not shell:
        raise RuntimeError('BLOCKED: Bash required for official find/cat probe')
    return shell


def shell_path(path):
    path = Path(path).resolve()
    if os.name == 'nt':
        return '/' + path.drive[0].lower() + path.as_posix()[2:]
    return path.as_posix()


class LocalShellEnvironment:
    """Real host shell I/O for the official method; no fake find or cat replies."""
    async def exec(self, command, timeout_sec=10):
        result = await asyncio.to_thread(subprocess.run, [bash_path(), '-c', command],
                                         capture_output=True, timeout=timeout_sec)
        return SimpleNamespace(return_code=result.returncode, stdout=result.stdout.decode('utf-8'),
                               stderr=result.stderr.decode('utf-8'))

    async def is_dir(self, path):
        return (await self.exec('test -d ' + shlex.quote(path))).return_code == 0


def discover_local(root, installed):
    terminus = official_probe_class(root)
    agent = terminus()
    agent.skills_dir = shell_path(installed)
    return asyncio.run(agent._build_skills_section(LocalShellEnvironment()))


def preflight(root):
    checks = []
    source = None
    lock = read(root / 'downstream_eval/configs/runner.lock.json')
    def record(name, status, reason):
        checks.append({'name': name, 'status': status, 'reason': reason})
    import sys
    record('python', 'PASS' if sys.version_info >= (3, 12) else 'BLOCKED', sys.version)
    for name in ('git', 'docker', 'harbor'):
        executable = shutil.which(name)
        if executable:
            result = subprocess.run([executable, '--version'], capture_output=True, timeout=30)
            record(name, 'PASS' if result.returncode == 0 else 'BLOCKED',
                   result.stdout.decode('utf-8', errors='replace').strip())
        else:
            record(name, 'BLOCKED', 'Executable not found on host PATH')
    if shutil.which('docker'):
        r = subprocess.run(['docker', 'info', '--format', '{{.OSType}}'], capture_output=True, timeout=30)
        record('docker_linux_daemon', 'PASS' if r.returncode == 0 and r.stdout.strip() == b'linux' else 'BLOCKED',
               r.stdout.decode(errors='replace') + r.stderr.decode(errors='replace'))
    else:
        record('docker_linux_daemon', 'BLOCKED', 'Docker absent; containers not executed')
    try:
        source, lock = verify_sources(root)
        record('pinned_source_subset', 'PASS', str(source) + '; verified source bytes; installation checked separately')
        for name, version in lock['offline_dependencies'].items():
            observed = importlib.metadata.version(name)
            record(name, 'PASS' if observed == version else 'BLOCKED', observed + '; expected ' + version)
    except (OSError, ValueError, importlib.metadata.PackageNotFoundError) as error:
        record('pinned_source_subset', 'BLOCKED', str(error))
    try:
        observed = importlib.metadata.version('harbor')
        distribution = importlib.metadata.distribution('harbor')
        direct = distribution.read_text('direct_url.json')
        direct = json.loads(direct) if direct else {}
        commit = direct.get('vcs_info', {}).get('commit_id')
        if not commit and source is not None and (source / '.git').exists():
            probe = subprocess.run(['git', '-C', str(source), 'rev-parse', 'HEAD'], capture_output=True, timeout=10)
            commit = probe.stdout.decode().strip() if probe.returncode == 0 else None
            editable = direct.get('dir_info', {}).get('editable')
            if not editable or direct.get('url') != source.as_uri():
                commit = None
        record('installed_harbor_identity', 'PASS' if observed == lock['harbor_version'] and commit == lock['harbor_commit'] else 'BLOCKED',
               observed + '; commit=' + str(commit))
    except importlib.metadata.PackageNotFoundError:
        record('installed_harbor_identity', 'BLOCKED', 'No installed Harbor distribution')
    record('host_platform', 'PASS', sys.platform + '; Docker runtime checked separately')
    return {'status': 'BLOCKED' if any(c['status'] == 'BLOCKED' for c in checks) else 'PASS', 'checks': checks}
