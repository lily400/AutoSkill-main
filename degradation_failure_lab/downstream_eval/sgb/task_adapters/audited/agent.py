"""Budget binding for admitted screening pilots."""
from pathlib import Path

from downstream_eval.sgb.task_adapters.scrapy041.agent import Scrapy041Terminus2
from downstream_eval.integration.request_budget import Ledger, BudgetStop
from degradation_lab.io import read, sha256


class AuditedTerminus2(Scrapy041Terminus2):
    def _budget_ledger(self):
        profile = self._p1
        if profile['task_id'] not in ('scrapy-task-024', 'fla_packet_cadence_scope_validator_002',
                                      'sanctuary_endgame_scheduler_002'):
            binding = Path(self.options.p1_profile).parent / 'task_config.json'
            if (profile.get('protocol_id') != 'clean-pair-v1' or not binding.is_file()
                    or sha256(binding) != profile.get('task_config_sha256')
                    or read(binding).get('adapter') != 'downstream_eval.sgb.task_adapters.audited.json_task'
                    or read(binding).get('task_id') != profile['task_id']):
                raise BudgetStop('Task is outside the audited pilot')
        scope = '/'.join((profile['task_id'], profile['generator_run_id'], profile['experiment_id']))
        ledger = Ledger(Path(profile['hard_http_budget']['database']))
        with ledger.transaction() as db:
            policy = ledger.policy(db)
            if policy['scope'] != scope or policy['budget'] != profile['budget']:
                raise BudgetStop('Audited pilot budget binding mismatch')
        return ledger
