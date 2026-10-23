"""New Task-024 integration checks; no model or Windows Oracle execution."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

LAB=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(LAB),str(LAB/'src')]
from degradation_lab.io import read,sha256,inventory
from downstream_eval.integration.request_budget import Ledger,BudgetStop,MeteredTransport
from downstream_eval.integration.p1_observer import body_visible

OUT=LAB/'runs/downstream/scrapy-task-024/s24d001'
PRE=Path(r'C:\Users\lily\Documents\ChatGPT\回归解决退化文档\audit_2026-10-15\scrapy024_preflight')
ORDER=['NoSkill1','CleanSkill1','NoSkill2','CleanSkill2','NoSkill3','CleanSkill3']


class Scrapy024(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='s24test-',dir=LAB.parent if sys.platform=='win32' else None)
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        net=patch('socket.socket.connect',side_effect=AssertionError('No real network'))
        net.start();self.addCleanup(net.stop)

    def ledger(self):
        return Ledger.create(self.root/'budget.sqlite3',{'scope':'FIXTURE_ONLY','order':ORDER,
            'global_limit':36,'per_trial_limit':6,'trials':{a:'trial-'+a for a in ORDER},
            'files':{},'budget':{'max_input_tokens_per_request':20000,'max_input_tokens_total':100000}})

    def test_six_trials_have_exactly_36_slots_without_reset_or_transfer(self):
        ledger=self.ledger()
        for arm in ORDER:
            trial='trial-'+arm
            lease=ledger.begin(arm,trial);ledger.attach(arm,trial,lease)
            for _ in range(6):
                n=ledger.reserve(arm,trial,lease,1000)
                ledger.response(n,SimpleNamespace(prompt_tokens=900,cache_tokens=0,completion_tokens=10))
            with self.assertRaises(BudgetStop):ledger.reserve(arm,trial,lease,1000)
            # An ordinary task failure is data, not a gate for later calibration trials.
            self.assertTrue(ledger.finish(arm,trial,lease,{'infra_ok':True,'task_success':False,'skill_read':False}))
            with self.assertRaises(BudgetStop):ledger.begin(arm,trial)
        self.assertEqual(ledger.snapshot()['global_reserved_attempts'],36)
        self.assertEqual(ledger.snapshot()['counts'],dict.fromkeys(ORDER,6))
        with self.assertRaises(FileExistsError):self.ledger()

    def test_unknown_delivery_stops_all_further_dispatch(self):
        ledger=self.ledger();arm=ORDER[0];lease=ledger.begin(arm,'trial-'+arm);ledger.attach(arm,'trial-'+arm,lease)
        n=ledger.reserve(arm,'trial-'+arm,lease,1000);ledger.fail(n,'FAKE_TIMEOUT')
        with self.assertRaises(BudgetStop):ledger.reserve(arm,'trial-'+arm,lease,1000)
        with self.assertRaises(BudgetStop):ledger.begin(ORDER[1],'trial-'+ORDER[1])
        self.assertEqual(ledger.snapshot()['global_reserved_attempts'],1)

    def test_all_registered_canonical_packages_are_frozen_unchanged(self):
        manifest=read(OUT/'skills_manifest.json')
        self.assertEqual(len(manifest['packages']),15)
        self.assertEqual(set(manifest['packages']),set(manifest['registry_ids']))
        self.assertEqual(manifest['seed_final_skills'],0)
        for sid,p in manifest['packages'].items():
            self.assertEqual(inventory(OUT/'skills'/sid),p['files'])
            self.assertEqual(inventory(OUT/'staged/CleanSkill'/sid),p['files'])
            self.assertEqual(p['version'],'0.1.0')
        self.assertEqual(inventory(OUT/'staged/NoSkill'),{})

    def test_original_instruction_and_oracle_bytes_are_unchanged(self):
        task=LAB/'downstream_eval/tasks/scrapy_task024_v1'
        assets=read(OUT/'task_asset_manifest.json')
        frozen=read(task/'scorer/source_manifest.json')['frozen_inventory']
        self.assertEqual(sha256(task/'instruction.md'),assets['instruction_sha256'])
        self.assertEqual(sha256(task/'scorer/stages/scorer/oracle/eval.py'),assets['original_oracle_sha256'])
        for rel in ['preflight.py','runtime/oracle_bridge.py']:
            self.assertEqual(sha256(task/'scorer'/rel),frozen[rel])
        if PRE.exists():
            self.assertEqual(sha256(task/'instruction.md'),sha256(PRE/'stages/agent/instruction.md'))
            self.assertEqual(sha256(task/'scorer/stages/scorer/oracle/eval.py'),sha256(PRE/'stages/scorer/oracle/eval.py'))

    def test_fairness_profiles_share_model_permissions_and_budget(self):
        fairness=read(OUT/'fairness.json')
        self.assertEqual(fairness['status'],'PASS')
        self.assertEqual(len(set(fairness['shared_config_hashes'].values())),1)
        self.assertEqual(fairness['order'],ORDER)
        for label in ORDER:
            config=read(OUT/'configs'/(label+'.json'))
            self.assertEqual(config['agent']['kwargs']['max_turns'],6)
            self.assertEqual(config['agent']['kwargs']['llm_call_kwargs']['num_retries'],0)
            self.assertFalse(config['environment']['kwargs']['enable_environment_dir_upload'])

    def test_title_or_partial_output_does_not_prove_complete_body_exposure(self):
        manifest=read(OUT/'skills_manifest.json')
        sid=next(iter(manifest['packages']))
        text=(OUT/'skills'/sid/'SKILL.md').read_text(encoding='utf-8')
        self.assertFalse(body_visible(text,manifest['packages'][sid]['metadata']['name']))
        self.assertFalse(body_visible(text,text[:len(text)//2]))
        self.assertTrue(body_visible(text,text))


    @unittest.skipUnless(__import__('importlib.util',fromlist=['find_spec']).find_spec('harbor'), 'Requires the pinned Linux Harbor runtime')
    def test_scrapy_agent_sdk_uses_the_bounded_transport_without_real_network(self):
        import asyncio
        import os
        import httpx
        from openai import AsyncOpenAI
        from harbor.agents.factory import AgentFactory
        from harbor.models.trial.config import AgentConfig
        from downstream_eval.integration.request_budget import MeteredTransport
        profile=read(OUT/'profile.json')
        profile['approval_environment_variable']='SCRAPY_TEST_ONLY'
        (self.root/'profile.json').write_text(json.dumps(profile),encoding='utf-8')
        (self.root/'manifest.json').write_text(json.dumps({'arm':ORDER[0],'metadata':{},'files':{},'staged_root':str(self.root)}),encoding='utf-8')
        config=AgentConfig(import_path='downstream_eval.integration.scrapy_agent:ScrapyTerminus2',
            model_name=profile['model']['name'],model_base_url=profile['model']['base_url'],
            model_api_key_name='ZHIZENGZENG_API_KEY',model_api_format='openai_chat_completions',
            kwargs={'p1_mode':'paid','p1_profile':str(self.root/'profile.json'),'p1_manifest':str(self.root/'manifest.json'),
                    'max_turns':6,'temperature':0,'reasoning_effort':'none','enable_summarize':False})
        ledger=self.ledger();arm=ORDER[0];lease=ledger.begin(arm,'trial-'+arm)
        sent=[]
        def fake(request):
            sent.append(True)
            return httpx.Response(200,json={'id':'FIXTURE_ONLY','object':'chat.completion','created':0,
                'model':'gpt-5.4-mini-2026-03-17','choices':[{'index':0,'message':{'role':'assistant','content':'FIXTURE_ONLY'},'finish_reason':'stop'}],
                'usage':{'prompt_tokens':10,'completion_tokens':5,'total_tokens':15}})
        async def run():
            with patch.dict(os.environ,{'ZHIZENGZENG_API_KEY':'FIXTURE_ONLY','SCRAPY_TEST_ONLY':'1'}):
                agent=AgentFactory.create_agent_from_config(config,logs_dir=self.root/'trial/agent')
                ledger.attach(arm,'trial-'+arm,lease)
                agent._p1_budget=ledger
                agent._p1_transport=MeteredTransport(ledger,arm,'trial-'+arm,lease,httpx.MockTransport(fake))
                agent._p1_http_client=httpx.AsyncClient(transport=agent._p1_transport,trust_env=False,follow_redirects=False)
                sdk=AsyncOpenAI(api_key='FIXTURE_ONLY',base_url=profile['model']['base_url'],max_retries=0)
                with patch('litellm.llms.openai.openai.OpenAIChatCompletion._get_openai_client',return_value=sdk):
                    for _ in range(6):
                        await agent._llm.call(prompt='FIXTURE_ONLY',max_completion_tokens=2048,num_retries=0,timeout=45)
                    with self.assertRaisesRegex(RuntimeError,'budget'):
                        await agent._llm.call(prompt='blocked',max_completion_tokens=2048,num_retries=0,timeout=45)
                await sdk.close();await agent._p1_http_client.aclose()
        asyncio.run(run())
        self.assertEqual(len(sent),6)
        self.assertEqual(ledger.snapshot()['global_reserved_attempts'],6)


if __name__=='__main__':unittest.main()
