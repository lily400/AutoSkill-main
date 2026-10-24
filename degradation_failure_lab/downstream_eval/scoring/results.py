"""Normalize observed trials without treating infrastructure failures as answers."""


def trial_record(value, task_key, evidence):
    success = value.get('task_success')
    infra = value.get('infra_ok')
    if type(success) is not bool or type(infra) is not bool:
        raise ValueError('Observed trials require explicit task_success and infra_ok booleans')
    return {'task_key':task_key, 'trial':value['label'], 'condition':value['condition'],
        'outcome':('passed' if success else 'failed') if infra else 'unscorable',
        'task_success':success, 'infra_ok':infra, 'failure_category':value.get('failure_category'),
        'task_result':value.get('oracle',{}).get('task_result'),
        'rule_result':value.get('oracle',{}).get('rule_result'),
        'model_body_exposed_ids':value.get('exposure',{}).get('model_body_exposed_ids',[]),
        'http_attempts':value.get('http_attempts'), 'token_usage':value.get('token_usage'),
        'evidence':evidence}


def summarize(rows):
    conditions = {}
    for row in rows:
        group = conditions.setdefault(row['condition'], {'observed':0,'passed':0,'failed':0,'unscorable':0})
        group['observed'] += 1; group[row['outcome']] += 1
    for group in conditions.values():
        scorable = group['passed']+group['failed']
        group['success_rate_among_scorable'] = group['passed']/scorable if scorable else None
    return {'conditions':conditions, 'aggregation':'Per-trial mean; never any-trial-pass',
            'caveat':'Observed counts are not planned counts; shared tasks/sources may be dependent.'}
