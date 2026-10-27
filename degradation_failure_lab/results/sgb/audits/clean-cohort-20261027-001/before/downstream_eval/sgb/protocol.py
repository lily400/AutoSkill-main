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
    for raw in configs.values():
        if str(required) not in raw.get('extra_instruction_paths', []):
            raise ValueError('Formal pair lacks the common Skill reading instruction')
    return {'protocol_id': protocol['protocol_id'], 'configuration_hashes': identities,
            'protocol_sha256': sha256(inside(root, CONFIG)), 'reading_sha256': sha256(required)}
