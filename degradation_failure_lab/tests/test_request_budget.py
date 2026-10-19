import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from downstream_eval.integration.request_budget import Ledger, MeteredTransport, BudgetStop
from downstream_eval.integration.request_budget import trial_evidence

DATA = {'model': 'gpt-5.4-mini-2026-03-17', 'temperature': 0,
        'reasoning_effort': 'none', 'max_completion_tokens': 2048}
USAGE = SimpleNamespace(prompt_tokens=10, cache_tokens=0, completion_tokens=5)
GOOD = {'infra_ok': True, 'task_success': True, 'skill_read': True}


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.policy = {'trials': {a: 'case-' + a for a in ('Gold', 'A0', 'A1')}, 'files': {},
                       'budget': {'max_input_tokens_per_request': 20000, 'max_input_tokens_total': 100000}}
        self.ledger = Ledger.create(self.root / 'budget.sqlite3', self.policy)

    def admit(self, arm):
        lease = self.ledger.begin(arm, 'case-' + arm)
        self.ledger.attach(arm, 'case-' + arm, lease)
        return lease

    def test_transport_1_to_6_allowed_7_blocked_18_allowed_19_blocked(self):
        sent = []
        async def run():
            for arm in ('Gold', 'A0', 'A1'):
                lease = self.admit(arm)
                def fake(request):
                    snapshot = self.ledger.snapshot()
                    self.assertEqual(snapshot['global_reserved_attempts'], len(sent) + 1)
                    sent.append(True)
                    return httpx.Response(200, json={})
                transport = MeteredTransport(self.ledger, arm, 'case-' + arm, lease, httpx.MockTransport(fake))
                transport.input_estimate = 100
                async with httpx.AsyncClient(transport=transport, trust_env=False, follow_redirects=False) as client:
                    for _ in range(6):
                        await client.post('https://api.zhizengzeng.com/v1/chat/completions', json=DATA)
                        self.ledger.response(transport.last_number, USAGE)
                    message = 'Global' if arm == 'A1' else 'Arm'
                    with self.assertRaisesRegex(BudgetStop, message):
                        await client.post('https://api.zhizengzeng.com/v1/chat/completions', json=DATA)
                self.ledger.finish(arm, 'case-' + arm, lease, GOOD)
        asyncio.run(run())
        self.assertEqual(len(sent), 18)
        self.assertEqual(self.ledger.snapshot()['counts'], {'Gold': 6, 'A0': 6, 'A1': 6})

    def test_restart_crash_and_duplicate_trial_never_reset_reservations(self):
        lease = self.ledger.begin('Gold', 'case-Gold')
        code = """import os,sys
from downstream_eval.integration.request_budget import Ledger
ledger=Ledger(sys.argv[1]); ledger.attach('Gold','case-Gold',sys.argv[2])
ledger.reserve('Gold','case-Gold',sys.argv[2],100)
os._exit(17)
"""
        child = subprocess.run([sys.executable, '-B', '-c', code, str(self.ledger.path), lease], cwd=LAB, capture_output=True)
        self.assertEqual(child.returncode, 17)
        reopened = Ledger(self.ledger.path)
        self.assertEqual(reopened.snapshot()['global_reserved_attempts'], 1)
        self.assertEqual(reopened.snapshot()['attempts'][0]['state'], 'RESERVED')
        with self.assertRaises(BudgetStop):
            reopened.begin('Gold', 'case-Gold')
        with self.assertRaises(BudgetStop):
            reopened.attach('Gold', 'case-Gold', lease)
        with self.assertRaises(BudgetStop):
            reopened.begin('A0', 'case-A0')
        with self.assertRaises(FileExistsError):
            Ledger.create(self.ledger.path, self.policy)

    def test_timeout_unknown_is_consumed_and_stops_further_dispatch(self):
        lease = self.admit('Gold')
        def timeout(request):
            raise httpx.ReadTimeout('fake transport timeout')
        transport = MeteredTransport(self.ledger, 'Gold', 'case-Gold', lease, httpx.MockTransport(timeout))
        async def run():
            async with httpx.AsyncClient(transport=transport, trust_env=False) as client:
                with self.assertRaises(BudgetStop):
                    await client.post('https://api.zhizengzeng.com/v1/chat/completions', json=DATA)
        asyncio.run(run())
        snapshot = self.ledger.snapshot()
        self.assertEqual(snapshot['global_reserved_attempts'], 1)
        self.assertEqual(snapshot['attempts'][0]['state'], 'UNKNOWN')
        with self.assertRaises(BudgetStop):
            self.ledger.reserve('Gold', 'case-Gold', lease, 100)

    def test_failed_http_redirect_and_wrong_destination_cannot_retry(self):
        lease = self.admit('Gold')
        calls = []
        def fake(request):
            calls.append(True)
            return httpx.Response(302, headers={'location': 'https://api.zhizengzeng.com/v1/other'})
        transport = MeteredTransport(self.ledger, 'Gold', 'case-Gold', lease, httpx.MockTransport(fake))
        async def run():
            async with httpx.AsyncClient(transport=transport, follow_redirects=False, trust_env=False) as client:
                response = await client.post('https://api.zhizengzeng.com/v1/chat/completions', json=DATA)
                self.assertEqual(response.status_code, 302)
                with self.assertRaises(BudgetStop):
                    await client.post('https://api.zhizengzeng.com/v1/chat/completions', json=DATA)
                with self.assertRaises(BudgetStop):
                    await client.post('https://example.invalid/chat/completions', json=DATA)
        asyncio.run(run())
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.ledger.snapshot()['global_reserved_attempts'], 1)

    def test_serial_admission_no_transfer_and_input_limit(self):
        lease = self.admit('Gold')
        with self.assertRaises(BudgetStop):
            self.ledger.begin('A0', 'case-A0')
        with self.assertRaises(BudgetStop):
            self.ledger.reserve('A0', 'case-A0', lease, 100)
        with self.assertRaises(BudgetStop):
            self.ledger.reserve('Gold', 'case-Gold', lease, 20001)
        number = self.ledger.reserve('Gold', 'case-Gold', lease, 100)
        with self.assertRaises(BudgetStop):
            self.ledger.reserve('Gold', 'case-Gold', lease, 100)
        self.ledger.response(number, USAGE)
        self.ledger.finish('Gold', 'case-Gold', lease, GOOD)
        a0 = self.admit('A0')
        for _ in range(6):
            self.ledger.response(self.ledger.reserve('A0', 'case-A0', a0, 100), USAGE)
        with self.assertRaises(BudgetStop):
            self.ledger.reserve('A0', 'case-A0', a0, 100)

    def test_gold_failure_or_missing_read_blocks_A0_and_A1(self):
        lease = self.admit('Gold')
        self.assertFalse(self.ledger.finish('Gold', 'case-Gold', lease, dict(GOOD, task_success=False)))
        for arm in ('A0', 'A1'):
            with self.assertRaises(BudgetStop):
                self.ledger.begin(arm, 'case-' + arm)
        other = Ledger.create(self.root / 'other.sqlite3', self.policy)
        lease = other.begin('Gold', 'case-Gold')
        other.attach('Gold', 'case-Gold', lease)
        self.assertFalse(other.finish('Gold', 'case-Gold', lease, dict(GOOD, skill_read=False)))
        with self.assertRaises(BudgetStop):
            other.begin('A0', 'case-A0')

    def test_A0_task_failure_can_continue_but_infrastructure_failure_cannot(self):
        gold = self.admit('Gold')
        self.ledger.finish('Gold', 'case-Gold', gold, GOOD)
        a0 = self.admit('A0')
        self.assertTrue(self.ledger.finish('A0', 'case-A0', a0, dict(GOOD, task_success=False, skill_read=False)))
        self.admit('A1')
        other = Ledger.create(self.root / 'infra.sqlite3', self.policy)
        lease = other.begin('Gold', 'case-Gold')
        other.attach('Gold', 'case-Gold', lease)
        other.finish('Gold', 'case-Gold', lease, dict(GOOD, infra_ok=False))
        with self.assertRaises(BudgetStop):
            other.begin('A0', 'case-A0')

    def test_A0_no_tool_action_is_task_failure_not_infrastructure_failure(self):
        trial = self.root / 'paid/case-A0'
        (trial / 'p1-observer').mkdir(parents=True)
        (trial / 'verifier').mkdir()
        (trial / 'result.json').write_text(json.dumps({'exception_info': None, 'verifier_environment_mode': 'separate',
            'verifier_result': {'rewards': {'reward': 0.0}}}))
        (trial / 'p1-observer/p1-summary.json').write_text(json.dumps({'stopped_before_model': False, 'model_read_ids': []}))
        (trial / 'verifier/assertions.json').write_text(json.dumps({'reason': None, 'assertion_results': {str(i): False for i in range(9)}}))
        evidence = trial_evidence({'trials_dir': str(self.root / 'paid'), 'trial_name': 'case-A0'}, self.root, 'A0')
        self.assertTrue(evidence['infra_ok'])
        self.assertFalse(evidence['task_success'])

    def test_actual_agent_SDK_path_uses_metered_client_with_fake_transport(self):
        from openai import AsyncOpenAI
        from harbor.agents.factory import AgentFactory
        from harbor.models.trial.config import AgentConfig
        profile = json.loads((LAB / 'downstream_eval/configs/p1_smoke.json').read_text())
        (self.root / 'profile.json').write_text(json.dumps(profile))
        (self.root / 'manifest.json').write_text(json.dumps({'arm': 'Gold', 'metadata': {}, 'files': {}, 'staged_root': str(self.root)}))
        config = AgentConfig(import_path='downstream_eval.integration.terminus_compat:CompatibleTerminus2',
            model_name=profile['model']['name'], model_base_url=profile['model']['base_url'],
            model_api_key_name='ZHIZENGZENG_API_KEY', model_api_format='openai_chat_completions',
            kwargs={'p1_mode': 'paid', 'p1_profile': str(self.root / 'profile.json'), 'p1_manifest': str(self.root / 'manifest.json'),
                    'max_turns': 6, 'temperature': 0, 'reasoning_effort': 'none', 'enable_summarize': False})
        calls = []
        def fake(request):
            calls.append(True)
            return httpx.Response(200, json={'id': 'fake-only', 'object': 'chat.completion', 'created': 0,
                'model': DATA['model'], 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'FAKE_ONLY'}, 'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}})
        async def run():
            with patch.dict(os.environ, {'ZHIZENGZENG_API_KEY': 'FAKE_ONLY_SDK_PATH', 'P1_ALLOW_PAID': '1'}), \
                 patch('socket.socket.connect', side_effect=AssertionError('Real network forbidden')):
                agent = AgentFactory.create_agent_from_config(config, logs_dir=self.root / 'case-Gold/agent')
                lease = self.admit('Gold')
                agent._p1_budget = self.ledger
                agent._p1_transport = MeteredTransport(self.ledger, 'Gold', 'case-Gold', lease, httpx.MockTransport(fake))
                agent._p1_http_client = httpx.AsyncClient(transport=agent._p1_transport, trust_env=False, follow_redirects=False)
                sdk = AsyncOpenAI(api_key='FAKE_ONLY_SDK_PATH', base_url='https://api.zhizengzeng.com/v1', max_retries=0)
                with patch('litellm.llms.openai.openai.OpenAIChatCompletion._get_openai_client', return_value=sdk):
                    for _ in range(6):
                        await agent._llm.call(prompt='fake request', max_completion_tokens=2048, num_retries=0, timeout=45)
                    with self.assertRaisesRegex(RuntimeError, 'budget'):
                        await agent._llm.call(prompt='blocked seventh', max_completion_tokens=2048, num_retries=0, timeout=45)
                await sdk.close()
                await agent._p1_http_client.aclose()
        asyncio.run(run())
        self.assertEqual(len(calls), 6)
        self.assertEqual(self.ledger.snapshot()['counts']['Gold'], 6)
        self.assertEqual(sum(row['input_tokens'] for row in self.ledger.snapshot()['attempts']), 60)


if __name__ == '__main__':
    unittest.main()
