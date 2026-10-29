"""Lossless package copies with ID-set and per-file frozen hash verification."""
import asyncio
import base64
import json
import re
import shlex
import shutil
import tarfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

from degradation_lab.artifacts import load_run
from degradation_lab.io import inside, inventory, read, sha256
from .harbor_adapter import discover_local, official_probe_class, official_resolve_skills


def canonical_packages(root, config):
    if config.get('bank_binding_id'):
        from degradation_lab.skillbank import SkillBank
        bank = SkillBank(root)
        binding = bank.binding(config['bank_binding_id'], task_key=config['task_key'])
        if config.get('generator_run_id', binding['generator_run_id']) != binding['generator_run_id']:
            raise ValueError('Snapshot generator differs from requested origin')
        packages = bank.packages(binding['binding_id'], task_key=config['task_key'])
        if config.get('expected_skill_count', len(packages)) != len(packages):
            raise ValueError('Snapshot Skill count differs from requested count')
        return packages
    identity, run, result, stages = load_run(root, config['generator_run_id'])
    if identity['case_id'] != config['case_id'] or identity['condition_id'] != config['condition']:
        raise ValueError('Generator run identity differs from pilot config')
    saved = read(run / 'artifact_manifest.json')
    expected = {x['id'] for x in stages['register']['upserted_store_skills']}
    export = read(inside(root, config['skill_manifest']))
    if len(expected) != config['expected_skill_count'] or export['unique_program_skill_count'] != len(expected):
        raise ValueError('Missing expected registration IDs')
    exported_names = {Path(p.replace('\\', '/')).parent.name for p in export['canonical_program_skills']}
    parser = official_probe_class(root)
    packages = {}
    for path in (run / 'SkillBank/Users').rglob('SKILL.md'):
        content = path.read_bytes().decode('utf-8')
        match = re.search(r'^id: "([^"\r\n]+)"', content, re.M)
        if not match:
            continue
        sid = match[1]
        if sid in packages:
            raise ValueError('Duplicate canonical Skill ID: ' + sid)
        if not re.fullmatch(r'[0-9a-f-]{36}', sid):
            raise ValueError('Unsafe canonical ID')
        metadata = parser._parse_skill_frontmatter(content)
        if not metadata or any(not isinstance(metadata[k], str) or not metadata[k].strip() for k in ('name', 'description')):
            raise ValueError('Invalid frontmatter: ' + sid)
        files = inventory(path.parent)
        # inventory excludes Python caches; package validation must never silently drop files.
        all_files = [p for p in path.parent.rglob('*') if p.is_file()]
        if len(files) != len(all_files) or any(p.is_symlink() for p in path.parent.rglob('*')):
            raise ValueError('Unsupported package symlink/cache; explicit review required')
        for relative, digest in files.items():
            frozen_key = (path.parent / relative).relative_to(run).as_posix()
            if saved.get(frozen_key) != digest:
                raise ValueError('Frozen package hash missing or changed: ' + frozen_key)
        packages[sid] = {'path': path, 'metadata': metadata, 'files': files}
    if set(packages) != expected or {p['path'].parent.name for p in packages.values()} != exported_names:
        raise ValueError('Canonical/export/registration identity sets differ')
    return packages


def copy_packages(packages, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for sid, package in sorted(packages.items()):
        target = destination / sid
        shutil.copytree(package['path'].parent, target)
        if inventory(target) != package['files']:
            raise ValueError('Package bytes changed: ' + sid)


def check_skills(root, config, output, environment=None):
    packages = canonical_packages(root, config)
    stage, installed = output / 'staged_skills', output / 'installed_skills'
    copy_packages(packages, stage)
    staged_packages = {sid: dict(p, path=stage / sid / 'SKILL.md') for sid, p in packages.items()}
    copy_packages(staged_packages, installed)
    resolved = official_resolve_skills(root, [stage])
    if {p.name for p in resolved} != set(packages):
        raise ValueError('Official source resolver dropped Skill IDs')
    xml = discover_local(root, installed)
    entries = list(ElementTree.fromstring(xml)) if xml else []
    discovered = {Path(x.findtext('location')).parent.name for x in entries}
    if len(entries) != len(packages) or discovered != set(packages):
        raise ValueError('Official discovery missing or duplicated Skill IDs')
    by_id = {Path(x.findtext('location')).parent.name: x for x in entries}
    original_parser = official_probe_class(root, patched=False)
    records = []
    for sid, item in sorted(packages.items()):
        path = item['path']; data = path.read_bytes()
        for field in ('name', 'description'):
            if by_id[sid].findtext(field) != item['metadata'][field]:
                raise ValueError('Index metadata changed')
        record = dict(source_id=read(inside(root, config['source_manifest']))['source_id'], skill_id=sid,
                      original_path=path.relative_to(root).as_posix(), staged_path=(stage / sid).relative_to(root).as_posix(),
                      installed_path=(installed / sid).relative_to(root).as_posix(), original_sha256=sha256(path),
                      installed_sha256=sha256(installed / sid / 'SKILL.md'), frontmatter_status='PASS', discovery_status='PASS',
                      unpatched_parser_status='PASS' if original_parser._parse_skill_frontmatter(data.decode('utf-8')) else 'FAIL',
                      newline_counts={'CRCRLF': data.count(b'\r\r\n'), 'CRLF_including_CRCRLF': data.count(b'\r\n'),
                                      'LF_total': data.count(b'\n')}, assets=item['files'], metadata=item['metadata'])
        if record['original_sha256'] != record['installed_sha256']:
            raise ValueError('SKILL.md changed during installation')
        records.append(record)
    (output / 'available_skills.xml').write_text(xml, encoding='utf-8')
    report = {'status': 'PASS', 'scope': 'host lossless install + exact official methods + real Bash find/cat',
            'container_install_status': 'BLOCKED', 'agent_prompt_delivery_status': 'not_run_by_scope',
            'model_body_read_status': 'not_run', 'model_rule_following_status': 'not_run',
            'expected_ids': sorted(packages), 'discovered_ids': sorted(discovered), 'records': records}
    if environment and environment['status'] == 'PASS':
        report['container'] = asyncio.run(check_container_skills(root, config, output, packages, stage))
        report['container_install_status'] = report['container']['status']
        report['scope'] += '; installed Harbor + native DockerEnvironment + imported Terminus-2 discovery'
        for record in records:
            sid = record['skill_id']
            record['container_path'] = report['container']['skills_dir'] + '/' + sid + '/SKILL.md'
            record['container_sha256'] = report['container']['file_hashes'][sid + '/SKILL.md']
    return report


async def check_container_skills(root, config, output, packages, staged):
    """Invoke imported Terminus methods with native Harbor Docker I/O, without an LLM."""
    import tomllib
    from harbor.environments.docker.docker import DockerEnvironment
    from harbor.models.task.config import EnvironmentConfig, NetworkMode, NetworkPolicy
    from harbor.models.trial.paths import TrialPaths
    from harbor.skills import resolve_skills
    from .terminus_compat import CompatibleTerminus2

    resolved = resolve_skills([staged])
    if {p.name for p in resolved} != set(packages):
        raise ValueError('Installed Harbor resolver dropped Skill IDs')
    template = inside(root, config['task_template'])
    environment_dir = output / 'skill_environment'
    shutil.copytree(template / 'environment', environment_dir)
    shutil.copyfile(template / 'fixture.py', environment_dir / 'fixture.py')
    task_config = tomllib.loads((template / 'task.toml').read_text(encoding='utf-8'))
    paths = TrialPaths(output / 'skills_container')
    paths.mkdir()
    env = DockerEnvironment(environment_dir=environment_dir, environment_name=config['task_id'],
                            session_id=output.name + '-skills__env', trial_paths=paths,
                            task_env_config=EnvironmentConfig.model_validate(task_config['environment']),
                            network_policy=NetworkPolicy(network_mode=NetworkMode.NO_NETWORK))
    skills_dir = read(root / 'downstream_eval/configs/runner.lock.json')['agent_skills_dir']
    try:
        await env.start(force_build=False)
        runtime = await env.exec('uname -s; python3 --version; git --version', timeout_sec=30)
        if runtime.return_code:
            raise RuntimeError('Container runtime version check failed')
        hashes = await install_remote(env, staged, skills_dir, output / 'skills.tar')
        # __init__ creates the model client; discovery only needs skills_dir and the parser.
        agent = object.__new__(CompatibleTerminus2)
        agent.skills_dir = skills_dir
        xml = await agent._build_skills_section(env)
        entries = list(ElementTree.fromstring(xml)) if xml else []
        discovered = {PurePosixPath(e.findtext('location')).parent.name: e for e in entries}
        if len(entries) != len(packages) or set(discovered) != set(packages):
            raise ValueError('Container discovery missing or duplicated Skill IDs')
        for sid, item in packages.items():
            for field in ('name', 'description'):
                if discovered[sid].findtext(field) != item['metadata'][field]:
                    raise ValueError('Container discovery metadata changed: ' + sid)
        (output / 'container_available_skills.xml').write_text(xml, encoding='utf-8')
        return {'status': 'PASS', 'skills_dir': skills_dir, 'runtime': runtime.stdout,
                'installed_ids': sorted(packages), 'discovered_ids': sorted(discovered),
                'file_hashes': hashes, 'frontmatter_status': 'PASS', 'discovery_status': 'PASS',
                'agent_initialization': 'not_run', 'model_calls': 0,
                'method': 'CompatibleTerminus2 inherits installed official _build_skills_section'}
    finally:
        await env.stop(delete=True)


async def install_remote(environment, staged, remote_root, archive):
    """Use native upload_file + tar to avoid Windows upload_dir rewriting scripts."""
    staged = Path(staged)
    if any(p.is_symlink() for p in staged.rglob('*')):
        raise ValueError('Skill archive must not contain symlinks')
    expected = inventory(staged)
    with tarfile.open(archive, 'w') as stream:
        for child in sorted(staged.iterdir()):
            if child.is_symlink() or not child.is_dir():
                raise ValueError('Only validated Skill directories may be installed')
            stream.add(child, arcname=child.name)
    remote_archive = remote_root + '.tar'
    await environment.upload_file(source_path=archive, target_path=remote_archive)
    command = f'mkdir -p {shlex.quote(remote_root)} && test -z "$(ls -A {shlex.quote(remote_root)})" && tar -xf {shlex.quote(remote_archive)} -C {shlex.quote(remote_root)}'
    result = await environment.exec(command, timeout_sec=30)
    if result.return_code:
        raise RuntimeError('Remote Skill install failed or destination was nonempty')
    observed = await remote_hashes(environment, remote_root)
    if observed != expected:
        raise ValueError('Remote package ID/file/hash set mismatch')
    return observed


async def remote_hashes(environment, remote_root):
    code = ('import pathlib,hashlib,json; r=pathlib.Path(' + repr(remote_root) + '); '
            'print(json.dumps({p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() '
            'for p in r.rglob("*") if p.is_file()},sort_keys=True))')
    encoded = base64.b64encode(code.encode()).decode()
    result = await environment.exec('python3 -c ' + shlex.quote('import base64;exec(base64.b64decode(' + repr(encoded) + '))'), timeout_sec=30)
    if result.return_code:
        raise ValueError('Remote package hash inspection failed')
    return json.loads(result.stdout)
