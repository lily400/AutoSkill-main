"""Zero-model Docker/Harbor acceptance. Creates only disposable probe environments."""
import argparse
import asyncio
import hashlib
import importlib.abc
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
import uuid

LAB = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(LAB), str(LAB / 'src')]


class NoAgentOrModel(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if any(fullname == prefix or fullname.startswith(prefix + '.')
               for prefix in ('harbor.agents', 'harbor.trial.trial', 'openai', 'litellm')):
            raise RuntimeError('Zero-model acceptance forbids import: ' + fullname)


sys.meta_path.insert(0, NoAgentOrModel())
from downstream_eval.integration.network_isolation import (
    PROBE, COMPOSE, environment_config, verify_environment_network, evaluate)
from harbor.environments.factory import EnvironmentFactory
from harbor.models.task.config import TaskConfig, NetworkPolicy
from harbor.models.trial.config import EnvironmentConfig
from harbor.models.trial.paths import TrialPaths

SERVER = """
import selectors,socket
sel=selectors.DefaultSelector()
for family,address in [(socket.AF_INET,'0.0.0.0'),(socket.AF_INET6,'::')]:
 for kind,ports in [(socket.SOCK_STREAM,[53,8080]),(socket.SOCK_DGRAM,[53,33434])]:
  for port in ports:
   s=socket.socket(family,kind)
   if family==socket.AF_INET6:s.setsockopt(socket.IPPROTO_IPV6,socket.IPV6_V6ONLY,1)
   s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
   s.bind((address,port))
   if kind==socket.SOCK_STREAM:s.listen()
   sel.register(s,selectors.EVENT_READ,kind)
print('READY',flush=True)
while True:
 for key,_ in sel.select():
  if key.data==socket.SOCK_STREAM:
   c,_=key.fileobj.accept()
   with c:c.sendall(c.recv(512))
  else:
   data,peer=key.fileobj.recvfrom(512);key.fileobj.sendto(data,peer)
"""


def save(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def command(args, *, check=True):
    result = subprocess.run(['docker', *args], capture_output=True, text=True, timeout=60)
    if check and result.returncode:
        raise RuntimeError('Docker command failed: ' + ' '.join(args[:4]) + '\n' + result.stderr)
    return result


async def main(output):
    output.mkdir(parents=True, exist_ok=False)
    if any(os.environ.get(name) for name in ('OPENAI_API_KEY','ZHIZENGZENG_API_KEY','DEEPSEEK_API_KEY')):
        raise RuntimeError('Acceptance controller must not receive model credentials')
    task_path = LAB / 'downstream_eval/tasks/sgb/code_doc/scrapy-task-024'
    task = TaskConfig.model_validate(tomllib.loads((task_path / 'task.toml').read_text()))
    token = 'net-audit-' + uuid.uuid4().hex[:10]
    network, server, control = token + '-net', token + '-echo', token + '-control'
    targets = {'ipv4':'198.18.25.2', 'ipv6':'fd7b:abc:25::2'}
    environment = None
    created = []
    report = {'status':'FAIL', 'agent_started':False, 'model_calls':0, 'targets':targets}
    try:
        command(['network','create','--internal','--ipv6','--subnet','198.18.25.0/24',
                 '--subnet','fd7b:abc:25::/64',network]); created.append(('network',network))
        command(['run','-d','--pull=never','--name',server,'--network',network,
                 '--ip',targets['ipv4'],'--ip6',targets['ipv6'],
                 task.environment.docker_image,'python','-B','-u','-c',SERVER])
        created.append(('container',server))
        for _ in range(30):
            if 'READY' in command(['logs',server]).stdout:
                break
            await asyncio.sleep(0.1)
        else:
            raise RuntimeError('Controlled TCP/UDP echo server did not become ready')
        command(['create','--pull=never','--name',control,'--network',network,
                 '--cap-drop','NET_ADMIN','--cap-drop','NET_RAW','--cap-drop','SYS_ADMIN',
                 '--security-opt','no-new-privileges','--dns','127.0.0.1',
                 task.environment.docker_image,'python','-B','-c',PROBE.read_text(),json.dumps(targets)])
        created.append(('container',control))
        positive = command(['start','-a',control])
        observations = json.loads(positive.stdout)
        save(output / 'positive-control.json', observations)
        channels = [label+'/'+channel for label in targets
                    for channel in ('tcp','dns_tcp','dns_udp','udp','icmp')]
        if any(observations['probes'][key]['outcome'] != 'reachable' for key in channels):
            raise RuntimeError('Controlled same-probe IPv4/IPv6 positive control failed')
        inspected = json.loads(command(['inspect',control]).stdout)[0]
        rejected = evaluate(inspected, observations, targets)
        save(output / 'connected-control-rejection.json', rejected)
        if rejected['status'] != 'FAIL':
            raise RuntimeError('Admission accepted an attached network')

        paths = TrialPaths(trial_dir=output / 'environment-only')
        config = EnvironmentConfig.model_validate(environment_config())
        save(output / 'environment-config.json', config.model_dump(mode='json'))
        policy = NetworkPolicy(network_mode='no-network')
        environment = EnvironmentFactory.create_environment_from_config(
            config=config, environment_dir=task_path / 'environment',
            environment_name='network-acceptance', session_id=token,
            trial_paths=paths, task_env_config=task.environment,
            network_policy=policy, phase_network_policies=[policy])
        await environment.start(force_build=False)
        effective = await environment._run_docker_compose_command(['config','--format','json'])
        # Only non-secret workload networking fields are retained.
        services = json.loads(effective.stdout)['services']
        save(output / 'effective-compose-network.json', {name:{
            k:service.get(k) for k in ('image','network_mode','networks','dns','cap_add','cap_drop','security_opt')}
            for name,service in services.items()})
        isolated = await verify_environment_network(environment, targets)
        save(output / 'isolated-network.json', isolated)
        # Even a sidecar phase-policy change must not attach the workload to that namespace.
        await environment.set_network_policy(NetworkPolicy(network_mode='public'))
        save(output / 'after-sidecar-public.json', await verify_environment_network(environment, targets))
        await environment.set_network_policy(policy)
        save(output / 'after-sidecar-restore.json', await verify_environment_network(environment, targets))
        report.update(status='PASS', positive_channels=channels,
                      negative_channels=list(isolated['observations']['probes']),
                      container_id=isolated['container_id'], image_id=isolated['image_id'],
                      sidecar_phase_change_cannot_reconnect=True,
                      imported_agent_or_model_modules=[n for n in sys.modules if n.startswith(
                          ('harbor.agents','harbor.trial.trial','openai','litellm'))])
        if report['imported_agent_or_model_modules']:
            raise RuntimeError('Unexpected Agent/model import')
    except BaseException as error:
        report.update(status='FAIL', error_type=type(error).__name__, error=str(error))
        if hasattr(error, 'report'):
            save(output / 'failed-network.json', error.report)
        raise
    finally:
        cleanup = []
        if environment is not None:
            try:
                await environment.stop(delete=True)
                cleanup.append({'environment':'removed'})
            except Exception as error:
                cleanup.append({'environment':'cleanup_failed','error':str(error)})
                report['status'] = 'FAIL'
        for kind,name in reversed(created):
            args = ['rm','-f',name] if kind == 'container' else ['network','rm',name]
            result = command(args, check=False)
            cleanup.append({'kind':kind,'name':name,'returncode':result.returncode})
            if result.returncode:
                report['status'] = 'FAIL'
        report['cleanup'] = cleanup
        report['code_hashes'] = {str(p.relative_to(LAB)):hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (Path(__file__),PROBE,COMPOSE,COMPOSE.with_name('network_isolation.py'))}
        save(output / 'result.json', report)
        print(json.dumps(report))
    return 0 if report['status'] == 'PASS' else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.output)))
