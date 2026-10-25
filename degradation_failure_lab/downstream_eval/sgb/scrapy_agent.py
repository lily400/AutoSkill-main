"""Task-024 policy checks around the existing Terminus-2 agent and observer."""
from pathlib import Path

from ..integration.terminus_compat import CompatibleTerminus2
from ..integration.request_budget import Ledger, BudgetStop
from ..integration.skill_install import remote_hashes


class ScrapyTerminus2(CompatibleTerminus2):
    def _budget_ledger(self):
        path = Path(self._p1['hard_http_budget']['database'])
        ledger = Ledger(path)
        with ledger.transaction() as db:
            policy = ledger.policy(db)
            if policy.get('scope') != 'scrapy-task-024/s24r005/initial-calibration' or policy['budget'] != self._p1['budget']:
                raise BudgetStop('Wrong Scrapy calibration ledger')
        return ledger

    async def setup(self, environment):
        await super().setup(environment)
        check = await environment.exec(
            "python -c \"import importlib.util,pathlib; "
            "assert importlib.util.find_spec('scrapy') is None; "
            "assert not any(pathlib.Path('/workspace/docs').iterdir()); "
            "assert not pathlib.Path('/oracle').exists(); "
            "assert not pathlib.Path('/responses').exists(); "
            "assert not pathlib.Path('/audit').exists(); print('PASS')\"",
            timeout_sec=10)
        if check.return_code:
            raise RuntimeError('Scrapy source/Oracle/runtime isolation failed')
        # Shared observer admits the real Docker namespace before native Agent setup.
        self._event('scrapy-isolation', status='PASS', no_scrapy=True, docs_empty=True,
                    oracle_absent=True, source_absent=True)

    async def run(self, instruction, environment, context):
        try:
            return await super().run(instruction, environment, context)
        finally:
            actual = await remote_hashes(environment, '/harbor/skills')
            if actual != self._p1_manifest['files']:
                self._event('skill-integrity-after', status='FAIL', file_hashes=actual)
                raise RuntimeError('Installed Skill package changed during the trial')
            self._event('skill-integrity-after', status='PASS', file_hashes=actual)
