"""Replay bounded object data for unchanged released assertions; never import candidate code."""
import hashlib
import json
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Annotated
import sys

DATA = json.loads(Path('/observations/envelope.json').read_text())
for path,key in [('/submission/agent_output.py','candidate_sha256'),('/oracle/eval.py','oracle_sha256')]:
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==DATA[key]
OBS = DATA['observation']
MODULE = ModuleType('agent_output')
MODULE.__file__ = '/submission/agent_output.py'
CLASSES = {}


def raise_error(value):
    if value['type']=='ValidationError':
        from pydantic import ValidationError
        records = value['validation_errors']
        for record in records:
            record.pop('msg',None);record.pop('url',None)
            if record.get('type')=='value_error':
                record.setdefault('ctx',{})['error']=ValueError(str(record.get('ctx',{}).get('error','candidate validation')))
        raise ValidationError.from_exception_data('Isolated candidate',records)
    raise RuntimeError('Isolated candidate: '+value['type']+': '+value['message'])


def unpack(value):
    kind=value['kind']
    if kind=='scalar':
        assert value['value'] is None or type(value['value']) in (bool,int,float,str)
        return value['value']
    if kind=='list':return [unpack(x) for x in value['value']]
    if kind=='dict':return {k:unpack(x) for k,x in value['value'].items()}
    if kind=='opaque':return object()
    if kind=='model':
        cls=CLASSES.get(value['symbol'],SimpleNamespace)
        result=object.__new__(cls)
        for k,v in value['attributes'].items():object.__setattr__(result,k,unpack(v))
        object.__setattr__(result,'_observed_dump',value['dump'])
        return result
    raise ValueError('Unknown bounded data type')


def input_value(value):
    if hasattr(value,'_observed_request'):return value._observed_request
    return value


def replay(op,symbol,value):
    key=json.dumps({'op':op,'symbol':symbol,'value':input_value(value)},sort_keys=True)
    row=OBS['results'][key]
    if not row['ok']:raise_error(row['error'])
    if 'module_log' in row:MODULE.VALIDATION_LOG=unpack(row['module_log'])
    return unpack(row['value'])


def model_class(name,record):
    from pydantic import BaseModel
    def init(self,**kwargs):
        value=replay('construct',name,kwargs)
        for key,item in vars(value).items():object.__setattr__(self,key,item)
        object.__setattr__(self,'_observed_request',{'object':name,'kwargs':kwargs})
    def validate(cls,value):return replay('model_validate',name,value)
    attrs={'__init__':init,'model_validate':classmethod(validate),
           'model_dump':lambda self:unpack(self._observed_dump),'__module__':'agent_output'}
    cls=type(name,(BaseModel,) if record.get('base_model') else (object,),attrs)
    if 'fields' in record:cls.__pydantic_fields__={key:None for key in record['fields']}
    return cls


if DATA['family'].startswith('pydantic'):
    for name,record in OBS.get('exports',{}).items():
        if name in ('MyModel','Cat','Dog','Bird','PetEnvelope') and record['class']:
            CLASSES[name]=model_class(name,record);setattr(MODULE,name,CLASSES[name])
        elif name=='Pet':MODULE.Pet=object()
        elif name=='pet_discriminator':
            MODULE.pet_discriminator=(lambda value:replay('call','pet_discriminator',value)) if record['callable'] else None
    if DATA['family']=='pydantic001' and 'MyModel' in CLASSES:
        import pydantic
        ann=OBS['annotation'];cls=CLASSES['MyModel']
        if ann['present']:
            metadata=[]
            for name in ann['metadata']:
                if name in ('BeforeValidator','WrapValidator','AfterValidator'):
                    metadata.append(getattr(pydantic,name)(lambda *args:None))
                else:metadata.append(type(name,(),{})())
            cls.__annotations__={'value':Annotated[int,*metadata] if ann['annotated'] and metadata else int}
        MODULE.VALIDATION_LOG=[]
else:
    import scrapy
    record=OBS.get('exports',{}).get('DepthLimitZeroSpider')
    if record:
        MODULE.DepthLimitZeroSpider=type('DepthLimitZeroSpider',(scrapy.Spider,) if record.get('spider') else (object,),
            {'custom_settings':record.get('custom_settings'),'__module__':'agent_output'}) if record['class'] else None
    record=OBS.get('exports',{}).get('get_depth_limit_zero_finding')
    if record:
        MODULE.get_depth_limit_zero_finding=(lambda:replay('finding','get_depth_limit_zero_finding',None)) if record['callable'] else None

# The released Oracle imports this data proxy at collection, before it can load submission code.
sys.modules['agent_output']=MODULE


class UnionAdapter:
    def __init__(self,value):assert value is MODULE.Pet
    def validate_python(self,value):return replay('validate_python','Pet',value)


def crawl(*args,**kwargs):
    import subprocess
    value=DATA['crawl']
    if value['returncode'] and kwargs.get('check'):
        raise subprocess.CalledProcessError(value['returncode'],args[0],value['stdout'],value['stderr'])
    return subprocess.CompletedProcess(args[0],value['returncode'],value['stdout'],value['stderr'])


def pytest_collection_modifyitems(items):
    assert [x.name for x in items]==DATA['test_names']
    for item in items:
        assert Path(item.module.__file__).resolve()==Path('/oracle/eval.py')
        if DATA['family']=='pydantic004':item.module.TypeAdapter=UnionAdapter
        if DATA['family']=='scrapy050':item.module.subprocess=SimpleNamespace(run=crawl)


def pytest_sessionfinish(session,exitstatus):
    imported=any(getattr(v,'__file__',None)=='/submission/agent_output.py' and v is not MODULE
                 for v in list(sys.modules.values()))
    Path('/results/bridge.json').write_text(json.dumps({'candidate_code_imported':imported,
        'candidate_sha256':DATA['candidate_sha256'],'oracle_sha256':DATA['oracle_sha256'],
        'original_test_count':len(session.items)}))
    if imported:session.exitstatus=4
