"""Fail-closed admission for a Linux Docker workload with no egress namespace."""
import asyncio
import json
from pathlib import Path
import shlex
import subprocess

COMPOSE = Path(__file__).with_name('network-none.yaml')
PROBE = Path(__file__).with_name('network_probe.py')
DEFAULT_TARGETS = {'ipv4':'198.18.0.1', 'ipv6':'2001:db8::1'}
FORBIDDEN_CAPS = (1 << 12) | (1 << 13) | (1 << 21)  # NET_ADMIN, NET_RAW, SYS_ADMIN


class NetworkIsolationError(RuntimeError):
    def __init__(self, report):
        super().__init__('Network isolation admission failed: ' + '; '.join(report['failures']))
        self.report = report


def environment_config():
    return {'type':'docker', 'delete':False,
            'extra_docker_compose':[str(COMPOSE)],
            'kwargs':{'enable_environment_dir_upload':False}}


def evaluate(inspected, observed, targets):
    failures = []
    host = inspected['HostConfig']
    networks = inspected['NetworkSettings']['Networks']
    if host.get('NetworkMode') != 'none' or set(networks) != {'none'}:
        failures.append('workload is not in the Docker none network')
    if any(item.get(key) for item in networks.values()
           for key in ('IPAddress','GlobalIPv6Address','Gateway','IPv6Gateway')):
        failures.append('workload has an external address or gateway')
    if host.get('Privileged') or host.get('CapAdd'):
        failures.append('privileged workload or added capabilities')
    if not {'NET_ADMIN','NET_RAW','SYS_ADMIN'} <= {name.removeprefix('CAP_') for name in host.get('CapDrop') or []}:
        failures.append('network/namespace capabilities not dropped')
    if not any(value in ('no-new-privileges', 'no-new-privileges:true')
               for value in host.get('SecurityOpt') or []):
        failures.append('no-new-privileges missing')
    if host.get('Dns') != ['127.0.0.1']:
        failures.append('resolver is not explicitly local')
    if set(observed['interfaces']) != {'lo'}:
        failures.append('non-loopback interface exists')
    if any(line.split()[0] != 'lo' for line in observed['ipv4_routes'].splitlines()[1:] if line.strip()):
        failures.append('non-loopback IPv4 route')
    if any(line.split()[-1] != 'lo' for line in observed['ipv6_routes'].splitlines() if line.strip()):
        failures.append('non-loopback IPv6 route')
    nameservers = [line.split()[1] for line in observed['resolver'].splitlines()
                   if line.startswith('nameserver ')]
    if nameservers != ['127.0.0.1']:
        failures.append('effective resolver is not local')
    caps = observed['capabilities']
    if any(int(caps[key], 16) & FORBIDDEN_CAPS for key in ('CapEff','CapPrm','CapBnd')):
        failures.append('forbidden capability remains available')
    if caps['NoNewPrivs'] != '1':
        failures.append('effective NoNewPrivs is not set')
    if not observed['loopback_control']:
        failures.append('local positive socket control failed')
    expected = {label + '/' + channel for label in targets
                for channel in ('tcp','dns_tcp','dns_udp','udp','icmp','raw')}
    expected |= {'resolver/' + address + '/' + kind for address in ('127.0.0.1','127.0.0.11')
                 for kind in ('tcp','udp')}
    expected |= {'socket/packet','socket/vsock'}
    if set(observed['probes']) != expected:
        failures.append('connectivity evidence incomplete')
    for name in expected:
        value = observed['probes'].get(name, {})
        if name.startswith('resolver/'):
            # Timeout/refusal is accepted only together with the kernel topology checks above.
            if value.get('outcome') not in ('blocked','timeout','error') or (
                    value.get('outcome') == 'error' and value.get('errno') != 111):
                failures.append(name + ' resolver reachable or probe failed')
        elif value.get('outcome') != 'blocked':
            failures.append(name + ' did not produce a kernel denial')
    return {'status':'FAIL' if failures else 'PASS', 'failures':failures,
            'policy':'docker-none-v1', 'container_id':inspected['Id'],
            'image_id':inspected['Image'], 'host_config':{
                key:host.get(key) for key in ('NetworkMode','Dns','CapAdd','CapDrop','Privileged','SecurityOpt')},
            'networks':networks, 'targets':targets, 'observations':observed}


async def verify_environment_network(environment, targets=None):
    targets = targets or DEFAULT_TARGETS
    result = await environment._run_docker_compose_command(['ps','-q','main'])
    cid = result.stdout.strip()
    if not cid or '\n' in cid:
        raise RuntimeError('Expected one running main container')
    proc = await asyncio.to_thread(subprocess.run, ['docker','inspect',cid],
                                  capture_output=True, text=True, check=True, timeout=15)
    inspected = json.loads(proc.stdout)[0]
    command = 'python -B -c ' + shlex.quote(PROBE.read_text()) + ' ' + shlex.quote(json.dumps(targets))
    probe = await environment.exec(command, timeout_sec=20)
    if probe.return_code:
        raise RuntimeError('Network probe execution failed: ' + str(probe.stderr))
    report = evaluate(inspected, json.loads(probe.stdout), targets)
    if report['status'] != 'PASS':
        raise NetworkIsolationError(report)
    return report
