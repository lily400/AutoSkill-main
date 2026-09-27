"""Observe the official urllib JSON transport, without rewriting requests/results."""
from __future__ import annotations
import hashlib
import io
import json
import os
from pathlib import Path
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from uuid import uuid4
from evidence import save

class Recorder:
    def __init__(self, root, secrets=()):
        self.root=Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self.secrets=sorted(set(s for s in secrets if s),key=len,reverse=True)
    def redact(self, text):
        for secret in self.secrets: text=text.replace(secret,'[REDACTED]')
        return text
    def persist(self, obj):
        # No HTTP headers are recorded. Redact known secrets even if echoed in a body/error.
        def scrub(value):
            if isinstance(value,str): return self.redact(value)
            if isinstance(value,list): return [scrub(x) for x in value]
            if isinstance(value,dict): return {self.redact(str(k)):scrub(v) for k,v in value.items()}
            return value
        obj=scrub(obj)
        save(self.root/(obj['call_id']+'.json'),obj)
    def wrap(self, original):
        def traced(request, *args, **kwargs):
            url=request.full_url if isinstance(request,urllib.request.Request) else str(request)
            parsed=urllib.parse.urlsplit(url)
            if not parsed.path.endswith(('/chat/completions','/embeddings')):
                return original(request,*args,**kwargs)
            data=getattr(request,'data',None) or b''
            body=data.decode('utf-8',errors='replace')
            try: payload=json.loads(body)
            except ValueError: payload=None
            record={'call_id':str(time.time_ns())+'_'+uuid4().hex[:8], 'thread':threading.current_thread().name,
                    'endpoint':urllib.parse.urlunsplit((parsed.scheme,parsed.netloc,parsed.path,'','')),
                    'started_at_unix':time.time(),'state':'started','request_body':body,'request_json':payload,
                    'request_sha256_before_redaction':hashlib.sha256(data).hexdigest(),
                    'call_stack':[{'file':Path(x.filename).name,'function':x.name,'line':x.lineno} for x in traceback.extract_stack(limit=18)[:-1]]}
            self.persist(record)
            start=time.monotonic()
            try:
                response=original(request,*args,**kwargs)
                # Official DashScope clients consume the whole JSON response with read().
                # Buffer once and return identical bytes to preserve client parsing/errors.
                with response:
                    raw=response.read()
                    status=getattr(response,'status',None)
                    headers=response.headers
                    response_url=response.geturl()
                record.update(state='completed',http_status=status,elapsed_s=time.monotonic()-start,
                              response_body=raw.decode('utf-8',errors='replace'),
                              response_sha256_before_redaction=hashlib.sha256(raw).hexdigest())
                try: record['response_json']=json.loads(record['response_body'])
                except ValueError: record['response_json']=None
                self.persist(record)
                return BufferedResponse(raw,status,headers,response_url)
            except urllib.error.HTTPError as e:
                raw=e.read()
                record.update(state='failed',http_status=e.code,elapsed_s=time.monotonic()-start,
                              error_type=type(e).__name__,response_body=raw.decode('utf-8',errors='replace'))
                self.persist(record)
                # Restore consumed bytes so the official error handler receives the same body.
                e.fp=io.BytesIO(raw)
                e.read=e.fp.read
                raise
            except BaseException as e:
                record.update(state='failed',elapsed_s=time.monotonic()-start,error_type=type(e).__name__,error=str(e))
                self.persist(record); raise
        return traced

class BufferedResponse(io.BytesIO):
    def __init__(self,raw,status,headers,url):
        super().__init__(raw); self.status=status; self.code=status; self.headers=headers; self.url=url
    def geturl(self): return self.url
    def getcode(self): return self.status
    def info(self): return self.headers

def install(root):
    secrets=[v for k,v in os.environ.items() if any(s in k.upper() for s in ('KEY','TOKEN','SECRET','PASSWORD')) and len(v)>=8]
    recorder=Recorder(root,secrets)
    urllib.request.urlopen=recorder.wrap(urllib.request.urlopen)
    save(Path(root)/'session.json',{'transport':'urllib.request.urlopen','capture':'JSON chat/completions and embeddings; headers omitted; known secrets redacted',
                                 'limitations':'Not packet capture; records server-reported model/usage only when returned. Streaming is not supported by this lab configuration.'})
