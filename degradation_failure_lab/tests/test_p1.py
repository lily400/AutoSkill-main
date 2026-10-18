import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from unittest.mock import patch

LAB = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(LAB), str(LAB / 'src')]
from degradation_lab.io import read
from downstream_eval.p1 import fairness_identity, gold_check
from downstream_eval.checks import materialize_task
from downstream_eval.integration.p1_observer import accessed_skills, body_visible, PreModelStop, P1ObservationMixin


class P1Tests(unittest.TestCase):
    def test_fairness_detects_model_budget_task_and_tool_changes(self):
        base = {'task': {'path': '/same'}, 'environment': {'type': 'docker'},
                'agent': {'model_name': 'fixed', 'skills': ['a'], 'kwargs': {'max_turns': 8, 'p1_manifest': 'a'}}}
        other = json.loads(json.dumps(base))
        other['trial_name'] = 'Gold'
        other['agent']['skills'] = ['gold']
        other['agent']['kwargs']['p1_manifest'] = 'gold'
        self.assertEqual(fairness_identity(base), fairness_identity(other))
        for section, key, value in [('task', 'path', '/changed'), ('environment', 'type', 'other'),
                                    ('agent', 'model_name', 'changed')]:
            changed = json.loads(json.dumps(other))
            changed[section][key] = value
            self.assertNotEqual(fairness_identity(base), fairness_identity(changed))
        other['agent']['kwargs']['max_turns'] = 9
        self.assertNotEqual(fairness_identity(base), fairness_identity(other))

    def test_gold_rule_passes_raw_state_oracle_without_task_answer(self):
        path = LAB / 'downstream_eval/gold/SKILL.md'
        result = gold_check(path)
        self.assertEqual(result['engineering_check'], 'PASS')
        self.assertEqual(result['human_signoff'], 'PENDING_USER_REVIEW')
        text = path.read_text(encoding='utf-8')
        for answer in ('target.txt', 'sentinel.txt', 'V1:', 'reward.txt', 'oracle.py'):
            self.assertNotIn(answer, text)

    def test_p1_materialization_has_no_reference_solution(self):
        with tempfile.TemporaryDirectory() as directory:
            config = read(LAB / 'downstream_eval/configs/git_restore_pilot.json')
            task, fixture = materialize_task(LAB, config, Path(directory), oracle_solution=False)
            self.assertFalse((task / 'solution').exists())
            self.assertNotIn('--source', (task / 'instruction.md').read_text(encoding='utf-8'))
            self.assertIn(fixture['commit_a'], (task / 'instruction.md').read_text(encoding='utf-8'))
            self.assertNotIn('oracle.py', (task / 'environment/Dockerfile').read_text())

    def test_kernel_evidence_rejects_discovery_open_unknown_and_prefix_paths(self):
        lines = '\n'.join(['1|OPEN|/harbor/skills/id/SKILL.md',
                            '2|ACCESS|/harbor/skills/id/SKILL.md',
                            '3|ACCESS|/harbor/skills/unknown/SKILL.md',
                            '4|ACCESS|/harbor/skills-evil/id/SKILL.md'])
        events = accessed_skills(lines, {'id'})
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['timestamp'], '2')

    def test_body_visibility_distinguishes_soft_wrap_from_missing_content(self):
        body = '---\r\nname: 中文技能\r\n---\r\n完整规则内容\r\n'
        self.assertTrue(body_visible(body, '---\nname: 中文技\n能\n---\n完整规则内\n容'))
        self.assertFalse(body_visible(body, 'name: 中文技能\n完整...内容'))

    def test_no_skill_arm_accepts_native_empty_stdout_without_inventing_reads(self):
        dummy = SimpleNamespace(_p1_environment=SimpleNamespace(exec=AsyncMock(return_value=SimpleNamespace(return_code=0, stdout=None))),
                                _p1_manifest={'metadata': {}}, _p1_watch_lines=0, _p1_reads=[], _p1_kernel_prefix=[])
        self.assertEqual(asyncio.run(P1ObservationMixin._capture_reads(dummy)), [])
        self.assertEqual(dummy._p1_reads, [])

    def test_real_constructor_probe_and_paid_guards_never_reach_provider(self):
        try:
            from harbor.agents.factory import AgentFactory
            from harbor.models.trial.config import AgentConfig
        except ImportError:
            self.skipTest('Pinned Harbor is installed in the Linux control container')
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            profile = read(LAB / 'downstream_eval/configs/p1_smoke.json')
            (folder / 'profile.json').write_text(json.dumps(profile))
            (folder / 'manifest.json').write_text(json.dumps({'files': {}, 'metadata': {}, 'staged_root': directory}))
            kwargs = {'p1_mode': 'paid', 'p1_profile': str(folder / 'profile.json'),
                      'p1_manifest': str(folder / 'manifest.json'), 'max_turns': 8,
                      'temperature': 0, 'reasoning_effort': 'none', 'enable_summarize': False}
            config = AgentConfig(import_path='downstream_eval.integration.terminus_compat:CompatibleTerminus2',
                                 model_name=profile['model']['name'], kwargs=kwargs)
            agent = AgentFactory.create_agent_from_config(config, logs_dir=folder / 'agent')
            with patch.dict(os.environ, {'P1_ALLOW_PAID': ''}), \
                 patch('litellm.acompletion', side_effect=AssertionError('Provider must not be called')) as provider:
                with self.assertRaisesRegex(RuntimeError, 'approval'):
                    asyncio.run(agent._llm.call(prompt='probe'))
                self.assertEqual(provider.call_count, 0)

            with patch.dict(os.environ, {'P1_ALLOW_PAID': '1'}), \
                 patch('litellm.acompletion', side_effect=AssertionError('Provider must not be called')) as provider:
                with self.assertRaisesRegex(ValueError, 'controls'):
                    asyncio.run(agent._llm.call(prompt='probe', max_completion_tokens=999))
                agent._p1_calls = 8
                with self.assertRaisesRegex(RuntimeError, 'budget'):
                    asyncio.run(agent._llm.call(prompt='probe', max_completion_tokens=2048, num_retries=0, timeout=45))
                agent._p1_calls = 0
                provider.side_effect = RuntimeError('transient provider boundary')
                with self.assertRaisesRegex(RuntimeError, 'transient provider boundary'):
                    asyncio.run(agent._llm.call(prompt='probe', max_completion_tokens=2048, num_retries=0, timeout=45))
                self.assertEqual(provider.call_count, 1)
                self.assertEqual(agent._p1_calls, 1)
                provider.reset_mock()
                agent.options.p1_mode = 'probe'
                with self.assertRaises(PreModelStop):
                    asyncio.run(agent._llm.call(prompt='probe'))
                self.assertEqual(provider.call_count, 0)

    def test_observer_records_are_outside_agent_mount_and_kernel_log_is_append_only(self):
        with tempfile.TemporaryDirectory() as directory:
            private = Path(directory) / 'trial/p1-observer'
            dummy = SimpleNamespace(_p1_logs=private)
            P1ObservationMixin._event(dummy, 'test', status='PASS')
            self.assertTrue((private / 'p1-test.jsonl').is_file())
            self.assertFalse((private.parent / 'agent/p1-test.jsonl').exists())
        dummy = SimpleNamespace(_p1_environment=SimpleNamespace(exec=AsyncMock(return_value=SimpleNamespace(return_code=0, stdout=None))),
                                _p1_manifest={'metadata': {}}, _p1_watch_lines=1, _p1_reads=[], _p1_kernel_prefix=['1|ACCESS|old'])
        with self.assertRaisesRegex(RuntimeError, 'truncated or changed'):
            asyncio.run(P1ObservationMixin._capture_reads(dummy))

    def test_provider_validation_reaches_sdk_with_zero_retries_without_credentials(self):
        try:
            from harbor.llms.lite_llm import LiteLLM
        except ImportError:
            self.skipTest('Pinned Harbor is installed in the Linux control container')
        model = read(LAB / 'downstream_eval/configs/p1_smoke.json')['model']
        client = LiteLLM(model_name=model['name'], api_base=model['base_url'],
                         temperature=0, reasoning_effort='none')
        with patch('litellm.llms.openai.openai.OpenAIChatCompletion._get_openai_client', side_effect=PreModelStop) as sdk:
            with self.assertRaises(PreModelStop):
                asyncio.run(client.call(prompt='provider validation only', max_completion_tokens=2048, num_retries=0, timeout=45))
        self.assertEqual(sdk.call_count, 1)
        self.assertEqual(sdk.call_args.kwargs['max_retries'], 0)
        self.assertEqual(sdk.call_args.kwargs['api_base'], model['base_url'])
        self.assertTrue(sdk.call_args.kwargs['is_async'])

    def test_native_request_assembly_stops_before_provider_http(self):
        try:
            from harbor.llms.lite_llm import LiteLLM
        except ImportError:
            self.skipTest('Pinned Harbor is installed in the Linux control container')
        profile = read(LAB / 'downstream_eval/configs/p1_smoke.json')
        model = profile['model']
        client = LiteLLM(model_name=model['name'], api_base=model['base_url'],
                         temperature=model['temperature'], reasoning_effort=model['reasoning_effort'])
        with patch('litellm.acompletion', side_effect=PreModelStop) as boundary:
            with self.assertRaises(PreModelStop):
                asyncio.run(client.call(prompt='request wiring only', max_completion_tokens=2048, num_retries=0, timeout=45))
        request = boundary.call_args.kwargs
        self.assertEqual(request['model'], model['name'])
        self.assertEqual(request.get('api_base') or request.get('base_url'), model['base_url'])
        self.assertEqual(request['max_completion_tokens'], 2048)
        self.assertEqual(request['num_retries'], 0)
        self.assertEqual(request['reasoning_effort'], 'none')


if __name__ == '__main__':
    unittest.main()
