"""Observe upstream truncation without changing its return values or official files."""
from uuid import uuid4
from trace_http import Recorder
import os

def observe_chat(original,recorder):
    def wrapped(*,system,user,max_units):
        result=original(system=system,user=user,max_units=max_units)
        recorder.persist({'call_id':'runtime-'+uuid4().hex,'kind':'chat_input_truncation',
            'max_units':max_units,'units_definition':'official mixed CJK characters / ASCII words; not tokenizer tokens',
            'before':{'system':system,'user':user},'after':{'system':result[0],'user':result[1]},
            'changed':(system or '',user or '')!=(result[0] or '',result[1] or '')})
        return result
    return wrapped

def observe_embedding(original,recorder):
    def wrapped(text,*,max_units,**kwargs):
        result=original(text,max_units=max_units,**kwargs)
        recorder.persist({'call_id':'runtime-'+uuid4().hex,'kind':'embedding_input_truncation',
            'max_units':max_units,'before':text,'after':result,'changed':text!=result})
        return result
    return wrapped

def install(root):
    import autoskill.llm.openai as chat
    import autoskill.embeddings.generic as embedding
    secrets=[v for k,v in os.environ.items() if any(s in k.upper() for s in ('KEY','TOKEN','SECRET','PASSWORD')) and len(v)>=8]
    recorder=Recorder(root,secrets)
    chat.truncate_system_user=observe_chat(chat.truncate_system_user,recorder)
    embedding.truncate_keep_head_tail=observe_embedding(embedding.truncate_keep_head_tail,recorder)
