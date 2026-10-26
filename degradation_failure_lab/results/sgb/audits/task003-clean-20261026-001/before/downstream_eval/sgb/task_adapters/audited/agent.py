"""Budget binding for the two admitted screening pilots."""
from pathlib import Path

from downstream_eval.sgb.task_adapters.scrapy041.agent import Scrapy041Terminus2
from downstream_eval.integration.request_budget import Ledger, BudgetStop


class AuditedTerminus2(Scrapy041Terminus2):
    def _budget_ledger(self):
        profile = self._p1
        if profile['task_id'] not in ('scrapy-task-024', 'fla_packet_cadence_scope_validator_002'):
            raise BudgetStop('Task is outside the audited pilot')
        scope = '/'.join((profile['task_id'], profile['generator_run_id'], profile['experiment_id']))
        ledger = Ledger(Path(profile['hard_http_budget']['database']))
        with ledger.transaction() as db:
            policy = ledger.policy(db)
            if policy['scope'] != scope or policy['budget'] != profile['budget']:
                raise BudgetStop('Audited pilot budget binding mismatch')
        return ledger
