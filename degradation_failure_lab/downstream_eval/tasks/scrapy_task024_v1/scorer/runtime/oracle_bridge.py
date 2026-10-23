"""Keep original assertions; substitute isolated, hash-bound candidate responses."""
import builtins
import hashlib
import json
from pathlib import Path
from types import ModuleType

DATA = json.loads(Path('/responses/responses.json').read_text())
if hashlib.sha256(Path('/submission/agent_output.py').read_bytes()).hexdigest() != DATA['candidate_sha256']:
    raise ValueError('Candidate/response version mismatch')
if hashlib.sha256(Path('/oracle/eval.py').read_bytes()).hexdigest() != DATA['oracle_sha256']:
    raise ValueError('Original oracle changed')


def unwrap(response):
    if response.get('ok'):
        return object() if 'unsupported_type' in response else response.get('value')
    kind = next(iter(response.get('builtin_exception_bases',[])), response.get('exception_type'))
    cls = getattr(builtins, kind, RuntimeError)
    if not isinstance(cls, type) or not issubclass(cls, Exception):
        cls = RuntimeError
    raise cls(response.get('message', 'candidate error'))


def key(value):
    return json.dumps([type(value).__name__, value], sort_keys=True)


def default_feed_overwrite(value):
    return unwrap(DATA['calls'][key(value)])


def load_proxy():
    unwrap(DATA['metadata'])
    module = ModuleType('agent_output')
    module.default_feed_overwrite = default_feed_overwrite
    return module


def pytest_collection_modifyitems(items):
    for item in items:
        if Path(item.module.__file__).resolve() != Path('/oracle/eval.py'):
            raise ValueError('Unexpected test module')
        item.module.load_agent_module = load_proxy
