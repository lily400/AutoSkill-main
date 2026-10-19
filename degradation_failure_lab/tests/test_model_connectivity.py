import asyncio
import importlib
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB))
from downstream_eval.integration.model_connectivity import OneRequest, RequestLimit, settings, probe, already_attempted


class ConnectivityTests(unittest.TestCase):
    def test_http_status_and_redirect_limit_without_network(self):
        import httpx
        async def scenario(status, output_limit=16):
            calls = []
            def transport(request):
                calls.append(request)
                return httpx.Response(status, headers={'location': 'https://api.zhizengzeng.com/v1/redirect'} if status == 302 else {})
            async with httpx.AsyncClient(transport=httpx.MockTransport(transport), follow_redirects=True) as http:
                client = SimpleNamespace(max_retries=0, base_url='https://api.zhizengzeng.com/v1/', _client=http)
                response = SimpleNamespace(model='gpt-5.4-mini-2026-03-17',
                    choices=[SimpleNamespace(message=SimpleNamespace(content='API_OK'))],
                    usage=SimpleNamespace(prompt_tokens=13, completion_tokens=3, total_tokens=16))
                async def sender(**kwargs):
                    await http.post('https://api.zhizengzeng.com/v1/chat/completions')
                    return {}, response
                observed = OneRequest(sender, max_completion_tokens=output_limit)
                kwargs = {'openai_aclient': client, 'data': {'model': 'gpt-5.4-mini-2026-03-17',
                          'max_completion_tokens': output_limit, 'temperature': 0, 'reasoning_effort': 'none'}}
                if status == 302:
                    with self.assertRaises(RequestLimit):
                        await observed.send(**kwargs)
                else:
                    await observed.send(**kwargs)
                self.assertEqual(observed.http_status, status)
                self.assertEqual(observed.http_attempts, 1)
                self.assertEqual(len(calls), 1)
        asyncio.run(scenario(200))
        asyncio.run(scenario(302))
        asyncio.run(scenario(200, 2048))
        asyncio.run(scenario(302, 2048))

    def test_existing_request_lock_blocks_before_credential_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            self.assertIsNone(already_attempted(path))
            (path / 'request.started').write_text('unit fixture')
            (path / 'result.json').write_text('{"status":"FAIL"}')
            result = already_attempted(path)
            self.assertEqual(result['status'], 'ALREADY_ATTEMPTED')
            self.assertEqual(result['new_request_attempts'], 0)
    def test_actual_module_entry_validates_sources_without_key_or_request(self):
        try:
            import harbor
        except ImportError:
            self.skipTest('Use the fixed Linux control environment')
        env = dict(os.environ)
        env.pop('ZHIZENGZENG_API_KEY', None)
        result = subprocess.run([sys.executable, '-B', '-m', 'downstream_eval.integration.model_connectivity',
                                 '--run-id', 'p1-connectivity-entry-check'], cwd=LAB,
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['request_attempts'], 0)
        self.assertFalse(report['credential_present'])
        self.assertEqual(report['pinned_harbor_source_check'], 'PASS')
        self.assertFalse((LAB / 'runs/downstream/git-restore-explicit-source-both-v1/p1-connectivity-entry-check/request.started').exists())

    def test_profile_targets_only_the_requested_provider_snapshot_and_key_variable(self):
        profile = json.loads((LAB / 'downstream_eval/configs/p1_smoke.json').read_text(encoding='utf-8'))
        self.assertEqual(settings(profile)['api_key_environment_variable'], 'ZHIZENGZENG_API_KEY')
        self.assertIsNone(profile['price_usd_per_million_tokens'])
        self.assertEqual(profile['reference_price_usd_per_million_tokens']['input'], 0.75)
        self.assertIn('UNVERIFIED', profile['pricing_status'])
        profile['model']['base_url'] = 'https://example.invalid/v1'
        with self.assertRaises(ValueError):
            settings(profile)

    def test_second_send_is_blocked_before_transport(self):
        response = SimpleNamespace(model='gpt-5.4-mini-2026-03-17',
            choices=[SimpleNamespace(message=SimpleNamespace(content='API_OK'))],
            usage=SimpleNamespace(prompt_tokens=13, completion_tokens=3, total_tokens=16))
        sender = AsyncMock(return_value=(None, response))
        probe = OneRequest(sender)
        kwargs = {'openai_aclient': SimpleNamespace(max_retries=0, base_url='https://api.zhizengzeng.com/v1/', _client=SimpleNamespace(event_hooks={})),
                  'data': {'model': 'gpt-5.4-mini-2026-03-17', 'max_completion_tokens': 16,
                           'temperature': 0, 'reasoning_effort': 'none'}}
        asyncio.run(probe.send(**kwargs))
        with self.assertRaises(RequestLimit):
            asyncio.run(probe.send(**kwargs))
        self.assertEqual(sender.await_count, 1)
        self.assertEqual(probe.response['usage']['total_tokens'], 16)

    def test_sdk_retry_setting_mismatch_prevents_any_send(self):
        sender = AsyncMock()
        probe = OneRequest(sender)
        with self.assertRaises(ValueError):
            asyncio.run(probe.send(openai_aclient=SimpleNamespace(max_retries=2), data={}))
        sender.assert_not_awaited()
        self.assertEqual(probe.attempts, 0)

    def test_real_harbor_parameter_transformation_stops_before_http(self):
        try:
            import harbor
        except ImportError:
            self.skipTest('Use the fixed Linux control environment')
        class BeforeHTTP(BaseException):
            pass
        profile = json.loads((LAB / 'downstream_eval/configs/p1_smoke.json').read_text(encoding='utf-8'))
        adapter = importlib.import_module('litellm.main').openai_chat_completions
        client = SimpleNamespace(max_retries=0, base_url='https://api.zhizengzeng.com/v1/', api_key='', _client=SimpleNamespace(event_hooks={}),
                                 _base_url=SimpleNamespace(_uri_reference='https://api.zhizengzeng.com/v1/'))
        boundary = AsyncMock(side_effect=BeforeHTTP)
        with patch.object(adapter, '_get_openai_client', return_value=client) as factory, \
             patch.object(adapter, 'make_openai_chat_completion_request', new=boundary):
            with self.assertRaises(BeforeHTTP):
                asyncio.run(probe(profile, 'offline-fixture-not-a-key'))
        self.assertEqual(boundary.await_count, 1)
        self.assertEqual(factory.call_args.kwargs['api_key'], 'offline-fixture-not-a-key')


if __name__ == '__main__':
    unittest.main()
