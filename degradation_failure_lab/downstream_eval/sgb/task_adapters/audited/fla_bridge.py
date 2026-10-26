"""Supply isolated observations to the byte-identical released pytest assertions."""
import hashlib
import json
from pathlib import Path


def pytest_collection_modifyitems(items):
    envelope = json.loads(Path('/observations/envelope.json').read_text())
    candidate = hashlib.sha256(Path('/submission/agent_output.py').read_bytes()).hexdigest()
    oracle = hashlib.sha256(Path('/oracle/eval.py').read_bytes()).hexdigest()
    assert envelope['candidate_sha256'] == candidate
    assert envelope['oracle_sha256'] == oracle
    module = items[0].module
    original_inputs = module.load_bundle()['test_cases']
    assert len(items) == len(envelope['observations']) == len(original_inputs)
    keys = [json.dumps(case['input'], sort_keys=True) for case in original_inputs]
    assert len(set(keys)) == len(keys)
    observations = dict(zip(keys, envelope['observations']))

    def run_case(bundle, case):
        value = observations[json.dumps(case['input'], sort_keys=True)]
        assert value['ok'], value.get('error', 'candidate failed')
        return value['value']

    module.run_case = run_case
    Path('/results/bridge.json').write_text(json.dumps({
        'candidate_sha256': candidate, 'oracle_sha256': oracle,
        'candidate_code_imported': False, 'observations': len(observations)}))
