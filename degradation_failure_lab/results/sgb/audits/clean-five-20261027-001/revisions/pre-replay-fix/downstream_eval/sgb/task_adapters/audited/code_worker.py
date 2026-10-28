"""Candidate-only object observations. No assertions, expected outputs or Oracle mount."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
from typing import get_args, get_origin, get_type_hints, Annotated

sys.path.insert(0, '/opt/sgb/site')
CANDIDATE = Path('/submission/agent_output.py')


def error(value):
    item = {'type':type(value).__name__, 'message':str(value)[:2000]}
    if type(value).__name__ == 'ValidationError':
        item['validation_errors'] = json.loads(value.json(include_url=False))
    return item


def observe(request):
    spec = importlib.util.spec_from_file_location('agent_output', CANDIDATE)
    module = importlib.util.module_from_spec(spec)
    sys.modules['agent_output'] = module
    spec.loader.exec_module(module)
    family = request['family']
    names = ('MyModel',) if family == 'pydantic001' else ('Cat','Dog','Bird','PetEnvelope','Pet','pet_discriminator')
    if family == 'scrapy050':
        names = ('DepthLimitZeroSpider','get_depth_limit_zero_finding')
    exports = {}
    for name in names:
        if not hasattr(module, name):
            continue
        obj = getattr(module, name)
        item = {'callable':callable(obj), 'class':isinstance(obj,type)}
        if family.startswith('pydantic'):
            from pydantic import BaseModel
            item['base_model'] = isinstance(obj,type) and issubclass(obj,BaseModel)
            if item['base_model']:
                item['fields'] = list(obj.model_fields)
        elif name == 'DepthLimitZeroSpider':
            import scrapy
            item['spider'] = isinstance(obj,type) and issubclass(obj,scrapy.Spider)
            item['custom_settings'] = getattr(obj,'custom_settings',None)
        exports[name] = item
    annotation = {'present':False,'annotated':False,'metadata':[]}
    if family == 'pydantic001' and hasattr(module,'MyModel'):
        try:
            hints = get_type_hints(module.MyModel,include_extras=True)
            annotation['present'] = 'value' in hints
            if 'value' in hints:
                annotation['annotated'] = get_origin(hints['value']) is Annotated
                annotation['metadata'] = [type(m).__name__ for m in get_args(hints['value'])[1:]]
        except Exception as exc:
            annotation['error'] = error(exc)
    classes = {name:getattr(module,name) for name in names
               if hasattr(module,name) and isinstance(getattr(module,name),type)}

    def pack(value, depth=0):
        if depth > 10:
            raise ValueError('Object observation nesting limit')
        if value is None or type(value) in (bool,int,float,str):
            return {'kind':'scalar','value':value}
        if type(value) in (list,tuple):
            if len(value)>256:raise ValueError('Sequence limit')
            return {'kind':'list','value':[pack(x,depth+1) for x in value]}
        if type(value) is dict:
            if len(value)>256 or not all(type(k) is str for k in value):raise ValueError('Dictionary limit')
            return {'kind':'dict','value':{k:pack(v,depth+1) for k,v in value.items()}}
        for name,cls in classes.items():
            if type(value) is cls:
                attrs = {k:pack(getattr(value,k),depth+1) for k in getattr(cls,'model_fields',{})}
                if hasattr(value,'validation_log'):attrs['validation_log']=pack(value.validation_log,depth+1)
                dump = pack(value.model_dump(),depth+1) if hasattr(value,'model_dump') else None
                return {'kind':'model','symbol':name,'attributes':attrs,'dump':dump}
        return {'kind':'opaque'}

    def unpack(value):
        if type(value) is dict and set(value)=={'object','kwargs'}:
            return getattr(module,value['object'])(**value['kwargs'])
        return value

    results = {}
    for operation in request['operations']:
        key = json.dumps(operation,sort_keys=True)
        try:
            op, symbol = operation['op'], operation['symbol']
            if family == 'pydantic001' and hasattr(module,'VALIDATION_LOG') and isinstance(module.VALIDATION_LOG,list):
                module.VALIDATION_LOG.clear()
            target = getattr(module,symbol)
            if op == 'construct':value=target(**operation['value'])
            elif op == 'model_validate':value=target.model_validate(unpack(operation['value']))
            elif op == 'validate_python':
                from pydantic import TypeAdapter
                value=TypeAdapter(target).validate_python(unpack(operation['value']))
            elif op == 'call':value=target(unpack(operation['value']))
            elif op == 'finding':value=target()
            else:raise ValueError('Unknown observation operation')
            record = {'ok':True,'value':pack(value)}
            if family == 'pydantic001':
                record['module_log'] = pack(getattr(module,'VALIDATION_LOG',None))
            results[key] = record
        except Exception as exc:
            results[key] = {'ok':False,'error':error(exc)}
    return {'exports':exports,'annotation':annotation,'results':results}


if __name__ == '__main__':
    request = json.loads(sys.stdin.read())
    digest = hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()
    capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(capture),contextlib.redirect_stderr(capture):
            response = {'ok':True,**observe(request)}
    except BaseException as exc:
        response = {'ok':False,'error':error(exc)}
    response.update(candidate_sha256=digest,schema_version=1,candidate_output=capture.getvalue()[:2000])
    print(json.dumps(response,allow_nan=False))
