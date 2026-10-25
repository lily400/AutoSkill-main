"""Task-local checks; keep the public Agent loop, network guard and metered transport."""
from pathlib import Path

from downstream_eval.integration.terminus_compat import CompatibleTerminus2
from downstream_eval.integration.request_budget import Ledger, BudgetStop
from downstream_eval.integration.skill_install import remote_hashes


class Scrapy041Terminus2(CompatibleTerminus2):
    def _budget_ledger(self):
        profile = self._p1
        if profile['task_id'] != 'scrapy-task-041':
            raise BudgetStop('Wrong task budget')
        scope = '/'.join((profile['task_id'], profile['generator_run_id'], profile['experiment_id']))
        ledger = Ledger(Path(profile['hard_http_budget']['database']))
        with ledger.transaction() as db:
            policy = ledger.policy(db)
            if policy['scope'] != scope or policy['budget'] != profile['budget']:
                raise BudgetStop('Scrapy041 budget binding mismatch')
        return ledger

    async def setup(self, environment):
        await super().setup(environment)
        result = await environment.exec(
            "python -B -c \"import importlib.util,pathlib; "
            "assert importlib.util.find_spec('scrapy') is None; "
            "assert not any(pathlib.Path('/workspace/docs').iterdir()); "
            "assert all(not pathlib.Path(p).exists() for p in "
            "('/oracle','/bridge','/observations','/tests','/solution','/workspace/tests','/var/run/docker.sock')); "
            "print('PASS')\"", timeout_sec=10)
        if result.return_code:
            raise RuntimeError('Scrapy041 task/Oracle isolation failed')
        self._event('scrapy041-isolation', status='PASS', source_and_oracle_absent=True,
                    dependency_source_absent=True)

    async def run(self, instruction, environment, context):
        try:
            return await super().run(instruction, environment, context)
        finally:
            if await remote_hashes(environment, '/harbor/skills') != self._p1_manifest['files']:
                raise RuntimeError('Scrapy041 installed Skill bytes changed')
