"""Normalize task failures, resource limits and infrastructure failures separately."""
import json

TASK_FAILURES = {'submission_missing', 'invalid_submission', 'candidate_timeout',
                 'oracle_assertion_failure'}
INFRA_FAILURES = {'environment_error', 'scorer_timeout', 'candidate_protocol_error', 'scorer_protocol_error',
                  'scorer_integrity_error', 'submission_hash_mismatch', 'submission_ambiguous',
                  'submission_origin_unknown'}
BUDGET_MESSAGES = ('HTTP limit ', 'Persistent input Token budget reached',
                   'P1 request/input token budget exhausted')


def completion_state(native, max_turns):
    """Interpret the pinned Terminus-2 two-confirmation contract, without executing Agent code."""
    metadata = ((native or {}).get('agent_result') or {}).get('metadata') or {}
    episodes = metadata.get('n_episodes')
    replies = [m.get('content') for m in metadata.get('all_messages', []) if m.get('role') == 'assistant']
    flags = []
    for content in replies[-2:]:
        try:
            if isinstance(content,str) and content.lstrip().startswith('```'):
                content = '\n'.join(content.strip().splitlines()[1:-1])
            value = json.loads(content).get('task_complete')
            flags.append(value if type(value) is bool else None)
        except (ValueError,TypeError,AttributeError):flags.append(None)
    confirmed = len(flags) == 2 and flags == [True,True]
    capped = (type(max_turns) is int and type(episodes) is int and episodes >= max_turns
              and bool(flags) and (flags[-1] is False or flags == [False,True]))
    return {'status':'confirmed' if confirmed else 'turn_limit_unconfirmed' if capped else 'unknown',
            'n_episodes':episodes,'max_turns':max_turns,'last_completion_flags':flags,
            'confirmation_contract':'two consecutive task_complete=true responses'}


def failure_kind(score, native_exception=None, *, error=None, stage=None, attempts=(), native_result=None, max_turns=None):
    # A reserved or unknown model call cannot be relabelled as a free resource stop.
    if any(a.get('state') in ('UNKNOWN', 'RESERVED') or
           a.get('http_status') is not None and not 200 <= a['http_status'] < 300 for a in attempts):
        return 'infrastructure_failure'
    info = native_exception or {}
    name = type(error).__name__ if error is not None else info.get('exception_type', info.get('type', ''))
    message = str(error) if error is not None else str(info.get('exception_message', info.get('message', '')))
    if name == 'AgentTimeoutError' or any(part in message for part in BUDGET_MESSAGES):
        return 'budget_exhausted'
    if native_exception or error is not None:
        return 'infrastructure_failure'
    if completion_state(native_result,max_turns)['status'] == 'turn_limit_unconfirmed':
        return 'budget_exhausted'
    category = score.get('failure_category')
    if category in TASK_FAILURES:
        return 'task_failure'
    if category in INFRA_FAILURES or score.get('infra_ok') is False:
        return 'infrastructure_failure'
    return 'none' if score.get('task_success') else 'task_failure'


def trial_record(value, task_key, evidence):
    if value.get('run_kind') == 'runtime_smoke' or value.get('real_agent_outcome') is False:
        raise ValueError('Engineering smoke/receipt records are not observed Agent trials')
    success, infra = value.get('task_success'), value.get('infra_ok')
    if type(infra) is not bool or (infra and type(success) is not bool) or success not in (True, False, None):
        raise ValueError('Observed trials require explicit task_success and infra_ok booleans (unknown on infra failure)')
    return {'task_key':task_key, 'trial':value['label'], 'condition':value['condition'],
        'outcome':('passed' if success else 'failed') if infra else 'unscorable',
        'task_success':success, 'infra_ok':infra, 'failure_category':value.get('failure_category'),
        'failure_kind':value.get('failure_kind'),
        'task_result':value.get('oracle',{}).get('task_result'),
        'rule_result':value.get('oracle',{}).get('rule_result'),
        'model_body_exposed_ids':value.get('exposure',{}).get('model_body_exposed_ids',[]),
        'http_attempts':value.get('http_attempts'), 'token_usage':value.get('token_usage'),
        'evidence':evidence}


def summarize(rows):
    conditions = {}
    for row in rows:
        if row.get('run_kind') == 'runtime_smoke' or row.get('real_agent_outcome') is False:
            raise ValueError('Engineering smoke/receipt records cannot enter success-rate summaries')
        group = conditions.setdefault(row['condition'], {'observed':0,'passed':0,'failed':0,'unscorable':0,
                                                        'failure_kinds':{}})
        group['observed'] += 1; group[row['outcome']] += 1
        kind = row.get('failure_kind') or 'historical_unclassified'
        group['failure_kinds'][kind] = group['failure_kinds'].get(kind, 0) + 1
    for group in conditions.values():
        scorable = group['passed'] + group['failed']
        group['success_rate_among_scorable'] = group['passed']/scorable if scorable else None
    return {'conditions':conditions, 'aggregation':'Per-trial mean; never any-trial-pass',
            'caveat':'Observed counts are not planned counts; shared tasks/sources may be dependent.'}
