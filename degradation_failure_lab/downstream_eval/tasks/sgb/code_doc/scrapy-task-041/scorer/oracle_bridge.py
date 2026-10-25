"""Execute unchanged Oracle assertions over data from separately isolated candidates."""
import hashlib
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys
import scrapy

DATA = json.loads(Path('/observations/envelope.json').read_text())
if DATA['protocol'] != 'scrapy041-object-observation-v1':
    raise ValueError('Unexpected observation protocol')
for path, key in [('/submission/agent_output.py','candidate_sha256'),('/oracle/eval.py','oracle_sha256')]:
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != DATA[key]:
        raise ValueError('Oracle/candidate binding mismatch')
CURRENT = None
LOADS = []


def unpack(value):
    kind = value['kind']
    if kind == 'scalar':
        if value['value'] is not None and type(value['value']) not in (bool,int,float,str):
            raise ValueError('Invalid scalar')
        return value['value']
    if kind in ('list','tuple'):
        items = [unpack(v) for v in value['value']]
        return tuple(items) if kind == 'tuple' else items
    if kind == 'dict':
        return {k:unpack(v) for k,v in value['value'].items()}
    if kind == 'opaque':
        return object()
    raise ValueError('Unknown observation type')


def fail(error):
    # Candidate exceptions are data. They never select arbitrary Python code to execute.
    raise RuntimeError('Isolated candidate: ' + error['type'] + ': ' + error['message'])


def proxy_class(record):
    def init(self):
        if 'constructor_error' in record:
            fail(record['constructor_error'])
    def start_requests(self):
        return iter(SimpleNamespace(**{k:unpack(v) for k,v in item.items()})
                    for item in record.get('requests', []))
    attrs = {'__init__':init, 'start_requests':start_requests}
    if 'allowed_domains' in record:
        attrs['allowed_domains'] = unpack(record['allowed_domains'])
    return type(record['name'], (scrapy.Spider,), attrs)


def load_proxy():
    response = DATA['loads'][CURRENT]
    LOADS.append(CURRENT)
    if not response['ok']:
        fail(response['error'])
    module = ModuleType('isolated_candidate_proxy')
    for record in response['spiders']:
        setattr(module, record['name'], proxy_class(record))
    return module


def pytest_collection_modifyitems(items):
    if len(items) != 10 or {item.name for item in items} != set(DATA['test_names']):
        raise ValueError('Original test inventory changed')
    for item in items:
        if Path(item.module.__file__).resolve() != Path('/oracle/eval.py'):
            raise ValueError('Unexpected test module')
        item.module.load_agent_module = load_proxy


def pytest_runtest_setup(item):
    global CURRENT
    CURRENT = item.name


def pytest_sessionfinish(session, exitstatus):
    executed = any(getattr(module, '__file__', None) == '/submission/agent_output.py'
                   for module in list(sys.modules.values()))
    marker = Path('/tmp/scrapy041-candidate-marker').exists()
    Path('/results/bridge.json').write_text(json.dumps({
        'candidate_code_imported':executed, 'candidate_marker_visible':marker,
        'loads':LOADS, 'candidate_sha256':DATA['candidate_sha256'],
        'oracle_sha256':DATA['oracle_sha256'], 'original_test_count':len(session.items)}))
    if executed or marker:
        session.exitstatus = 4
