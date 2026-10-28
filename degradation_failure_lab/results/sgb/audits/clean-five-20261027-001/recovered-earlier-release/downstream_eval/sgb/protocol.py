"""One frozen Clean pair protocol; no model or environment execution."""
from degradation_lab.io import inside, read, sha256
from downstream_eval.p1 import fairness_identity

CONFIG = 'configs/sgb/clean_pair_protocol.json'


def apply(root, output, raw):
    profile = read(output / 'profile.json')
    if profile.get('protocol_id') == 'clean-pair-v1':
        protocol = read(inside(root, CONFIG))
        paths = raw.setdefault('extra_instruction_paths', [])
        note = str(inside(root, protocol['skill_read_instruction']))
        if note not in paths:
            paths.append(note)
    return raw


def validate(root, profile, configs):
    protocol = read(inside(root, CONFIG))
    if profile.get('protocol_id') != protocol['protocol_id']:
        raise ValueError('Formal pair requires the frozen Clean protocol')
    for key in ('conditions', 'model', 'budget', 'repeats_per_arm'):
        if profile.get(key) != protocol[key]:
            raise ValueError('Formal pair protocol differs: ' + key)
    if set(configs) != set(protocol['conditions']):
        raise ValueError('Formal pair requires exactly two conditions')
    identities = {label: fairness_identity(raw) for label, raw in configs.items()}
    if len(set(identities.values())) != 1:
        raise ValueError('Trial conditions differ beyond Skill treatment')
    required = inside(root, protocol['skill_read_instruction'])
    from downstream_eval.integration.network_isolation import environment_config
    for label, raw in configs.items():
        environment = raw.get('environment', {})
        if (any(environment.get(k) != v for k,v in environment_config().items())
                or environment.get('extra_allowed_hosts') not in (None, [])
                or raw.get('verifier',{}).get('disable') is not True):
            raise ValueError('Native isolation or independent Verifier protocol differs')
        agent = raw['agent']; kwargs = agent['kwargs']; budget = protocol['budget']; model = protocol['model']
        expected = {'model_name':model['name'], 'model_base_url':model['base_url'],
                    'model_api_format':model['api_format'], 'override_timeout_sec':budget['agent_timeout_sec'],
                    'override_setup_timeout_sec':budget['setup_timeout_sec']}
        if any(agent.get(k) != v for k,v in expected.items()):
            raise ValueError('Native model or timeout differs from protocol')
        if (kwargs.get('max_turns') != budget['max_requests'] or kwargs.get('temperature') != model['temperature']
                or kwargs.get('reasoning_effort') != model['reasoning_effort']
                or kwargs.get('enable_summarize') is not False
                or kwargs.get('llm_call_kwargs') != {'max_completion_tokens':budget['max_completion_tokens_per_request'],
                    'num_retries':budget['num_retries'], 'timeout':budget['request_timeout_sec']}):
            raise ValueError('Native sampling or budget differs from protocol')
        if label == 'NoSkill1' and agent.get('skills') != []:
            raise ValueError('NoSkill must have an empty Skill installation')
        if label == 'CleanSkill1' and len(agent.get('skills', [])) != 1:
            raise ValueError('CleanSkill requires one frozen package directory')
        if str(required) not in raw.get('extra_instruction_paths', []):
            raise ValueError('Formal pair lacks the common Skill reading instruction')
    return {'protocol_id': protocol['protocol_id'], 'configuration_hashes': identities,
            'protocol_sha256': sha256(inside(root, CONFIG)), 'reading_sha256': sha256(required)}
