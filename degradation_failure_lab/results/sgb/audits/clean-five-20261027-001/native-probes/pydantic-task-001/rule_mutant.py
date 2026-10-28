"""Researcher-written positive fixture; never a generated Skill or Agent result."""
from typing import Annotated
from pydantic import AfterValidator,BaseModel,BeforeValidator,WrapValidator

VALIDATION_LOG=[]

def before(value):
    VALIDATION_LOG.append({'event':'before','value':value})
    return value*2

def wrap(value,handler):
    VALIDATION_LOG.append({'event':'wrap_start','value':value})
    result=handler(value)
    VALIDATION_LOG.append({'event':'wrap_end','value':result})
    return result

def after(value):
    VALIDATION_LOG.append({'event':'after','value':value})
    return value+10

class MyModel(BaseModel):
    value:Annotated[int,AfterValidator(after),WrapValidator(wrap),BeforeValidator(before)]
