"""Fail-closed network admission tests. No containers, Agent or model calls."""
import copy
from pathlib import Path
import sys
import unittest

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
from downstream_eval.integration.network_isolation import evaluate, environment_config, DEFAULT_TARGETS


class NetworkIsolation(unittest.TestCase):
    def setUp(self):
        self.inspected = {
            'Id':'fixture', 'Image':'fixture',
            'HostConfig':{'NetworkMode':'none', 'Privileged':False, 'CapAdd':None,
                          'CapDrop':['NET_ADMIN','NET_RAW','SYS_ADMIN'],
                          'SecurityOpt':['no-new-privileges'], 'Dns':['127.0.0.1']},
            'NetworkSettings':{'Networks':{'none':{}}}}
        self.observed = {
            'interfaces':['lo'], 'ipv4_routes':'Iface Destination\n',
            'ipv6_routes':'', 'resolver':'nameserver 127.0.0.1\n',
            'capabilities':{'CapEff':'0','CapPrm':'0','CapBnd':'0','NoNewPrivs':'1'},
            'loopback_control':True, 'probes':{
                label+'/'+channel:{'outcome':'blocked','errno':101}
                for label in DEFAULT_TARGETS for channel in ('tcp','dns_tcp','dns_udp','udp','icmp','raw')}}
        for addr in ('127.0.0.1','127.0.0.11'):
            for kind in ('tcp','udp'):
                self.observed['probes']['resolver/'+addr+'/'+kind] = {'outcome':'timeout'}
        for family in ('packet','vsock'):
            self.observed['probes']['socket/'+family] = {'outcome':'blocked','errno':1}

    def verdict(self):
        return evaluate(self.inspected, self.observed, DEFAULT_TARGETS)['status']

    def test_complete_kernel_denials_pass(self):
        self.assertEqual(self.verdict(), 'PASS')

    def test_docker_cap_prefix_is_normalized_but_kernel_caps_still_checked(self):
        self.inspected['HostConfig']['CapDrop'] = ['CAP_NET_ADMIN','CAP_NET_RAW','CAP_SYS_ADMIN']
        self.assertEqual(self.verdict(), 'PASS')
        self.observed['capabilities']['CapBnd'] = '2000'
        self.assertEqual(self.verdict(), 'FAIL')

    def test_sidecar_or_host_or_bridge_namespace_is_rejected_even_if_tcp_fails(self):
        for mode in ('container:old-sidecar','host','bridge'):
            with self.subTest(mode=mode):
                self.inspected['HostConfig']['NetworkMode'] = mode
                self.assertEqual(self.verdict(), 'FAIL')

    def test_dns_icmp_udp_ipv6_and_raw_escape_are_each_rejected(self):
        for name in self.observed['probes']:
            with self.subTest(channel=name):
                previous = self.observed['probes'][name]
                self.observed['probes'][name] = {'outcome':'reachable'}
                self.assertEqual(self.verdict(), 'FAIL')
                self.observed['probes'][name] = previous

    def test_timeout_is_not_proof_of_external_kernel_denial(self):
        self.observed['probes']['ipv4/tcp'] = {'outcome':'timeout'}
        self.assertEqual(self.verdict(), 'FAIL')

    def test_missing_channel_or_failed_probe_is_rejected(self):
        del self.observed['probes']['ipv6/icmp']
        self.assertEqual(self.verdict(), 'FAIL')
        self.observed['probes']['ipv6/icmp'] = {'outcome':'error','errno':22}
        self.assertEqual(self.verdict(), 'FAIL')

    def test_actual_interfaces_routes_resolver_and_privilege_are_checked(self):
        original = copy.deepcopy(self.observed)
        mutations = [
            ('interfaces',['lo','eth0']),
            ('ipv4_routes','Iface Destination\neth0 00000000'),
            ('ipv6_routes','00000000 eth0'),
            ('resolver','nameserver 127.0.0.11\n'),
            ('loopback_control',False)]
        for key, value in mutations:
            with self.subTest(field=key):
                self.observed = copy.deepcopy(original)
                self.observed[key] = value
                self.assertEqual(self.verdict(), 'FAIL')
        for key in ('CapEff','CapPrm','CapBnd'):
            self.observed = copy.deepcopy(original)
            self.observed['capabilities'][key] = '2000'
            self.assertEqual(self.verdict(), 'FAIL')
        self.observed = copy.deepcopy(original)
        self.observed['capabilities']['NoNewPrivs'] = '0'
        self.assertEqual(self.verdict(), 'FAIL')

    def test_privileged_cap_add_dns_and_gateway_are_rejected(self):
        for key,value in [('Privileged',True),('CapAdd',['SYS_ADMIN']),('CapDrop',[]),
                          ('SecurityOpt',[]),('Dns',['8.8.8.8'])]:
            original = copy.deepcopy(self.inspected)
            self.inspected['HostConfig'][key] = value
            self.assertEqual(self.verdict(), 'FAIL')
            self.inspected = original
        self.inspected['NetworkSettings']['Networks']['none']['Gateway'] = '172.17.0.1'
        self.assertEqual(self.verdict(), 'FAIL')

    def test_shared_observer_refuses_native_setup_until_admission_passes(self):
        import asyncio
        from unittest.mock import AsyncMock, patch
        from downstream_eval.integration.p1_observer import P1ObservationMixin
        from downstream_eval.integration.network_isolation import NetworkIsolationError
        events = []

        class NativeSentinel:
            async def setup(self, environment):
                events.append('native_setup')
                raise RuntimeError('native setup sentinel')

        class Harness(P1ObservationMixin, NativeSentinel):
            def _event(self, *args, **kwargs):
                events.append(kwargs['status'])

        # This is only a mixin harness; no Harbor Agent is imported or constructed.
        harness = object.__new__(Harness)
        harness._p1 = True
        failure = {'status':'FAIL','failures':['fixture denial']}
        with patch('downstream_eval.integration.p1_observer.verify_environment_network',
                   AsyncMock(side_effect=NetworkIsolationError(failure))):
            with self.assertRaises(NetworkIsolationError):
                asyncio.run(harness.setup(None))
        self.assertEqual(events, ['FAIL'])
        events.clear()
        with patch('downstream_eval.integration.p1_observer.verify_environment_network',
                   AsyncMock(return_value={'status':'PASS'})):
            with self.assertRaisesRegex(RuntimeError, 'native setup sentinel'):
                asyncio.run(harness.setup(None))
        self.assertEqual(events, ['PASS','native_setup'])

    def test_public_config_supplies_the_strict_overlay(self):
        config = environment_config()
        self.assertTrue(Path(config['extra_docker_compose'][0]).is_file())
        self.assertFalse(config['kwargs']['enable_environment_dir_upload'])


if __name__ == '__main__':
    unittest.main()
