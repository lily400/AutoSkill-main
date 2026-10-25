"""Untrusted candidate worker. No Oracle, expected values, source docs or scores here."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import scrapy

CANDIDATE = Path('/submission/agent_output.py')


def pack(value, depth=0):
    if depth > 8:
        raise ValueError('Observation exceeds nesting limit')
    if value is None or type(value) in (bool, int, float, str):
        return {'kind':'scalar', 'value':value}
    if type(value) in (list, tuple):
        if len(value) > 256:
            raise ValueError('Observation exceeds sequence limit')
        return {'kind':type(value).__name__, 'value':[pack(v, depth+1) for v in value]}
    if type(value) is dict:
        if len(value) > 256 or not all(type(k) is str for k in value):
            raise ValueError('Only bounded string-key dictionaries are supported')
        return {'kind':'dict', 'value':{k:pack(v, depth+1) for k,v in value.items()}}
    # Never pickle, repr-evaluate or execute returned objects in the trusted scorer.
    return {'kind':'opaque'}


def error_record(error):
    return {'type':type(error).__name__, 'message':str(error)[:1000]}


def observe(mode):
    spec = importlib.util.spec_from_file_location('agent_output', CANDIDATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if mode == 'import':
        return {'spiders':[]}
    spiders = []
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, scrapy.Spider) and obj != scrapy.Spider:
            spiders.append((name, obj))
    if len(spiders) > 64:
        raise ValueError('Too many Spider classes')
    records = []
    for name, cls in spiders:
        record = {'name':name}
        records.append(record)
        if mode == 'domains':
            record['allowed_domains'] = pack(getattr(cls, 'allowed_domains', None))
        if mode == 'requests':
            try:
                instance = cls()
            except Exception as error:
                record['constructor_error'] = error_record(error)
                break
            requests = []
            if hasattr(instance, 'start_requests'):
                try:
                    # Original Oracle discards a partially yielded list if iteration raises.
                    requests.extend(list(instance.start_requests()))
                except Exception:
                    pass
            if len(requests) > 256:
                raise ValueError('Too many yielded objects')
            record['requests'] = []
            for request in requests:
                item = {}
                for attr in ('url','meta'):
                    try:
                        item[attr] = pack(getattr(request, attr))
                    except AttributeError:
                        pass
                record['requests'].append(item)
    return {'spiders':records}


if __name__ == '__main__':
    request = json.loads(sys.stdin.read())
    digest = hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()
    capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
            response = {'ok':True, **observe(request['mode'])}
    except BaseException as error:
        response = {'ok':False, 'error':error_record(error)}
    response.update(schema_version=1, candidate_sha256=digest, candidate_output=capture.getvalue()[:2000])
    print(json.dumps(response, allow_nan=False))
