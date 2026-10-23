"""Observation and request limits around the unchanged official Terminus-2 loop."""
import importlib,json,pathlib,re,shlex,subprocess,time
from typing import Literal
from unittest.mock import patch
from xml.etree import ElementTree
from harbor.agents.terminus_2.terminus_2 import Terminus2,Terminus2Options
from .model_connectivity import OneRequest
from .p1_observer import redact_credentials,accessed_skills
from .skill_install import remote_hashes

class StopBeforeModel(BaseException):pass
class GChOptions(Terminus2Options):
    gch_profile:str
    gch_manifest:str
    gch_mode:Literal['probe','paid']='probe'

class GitChameleonTerminus2(Terminus2):
    options_model=GChOptions
    @staticmethod
    def _parse_skill_frontmatter(content):
        return Terminus2._parse_skill_frontmatter(content.replace('\r\n','\n').replace('\r','\n'))

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._gch=json.loads(pathlib.Path(self.options.gch_profile).read_text())
        self._manifest=json.loads(pathlib.Path(self.options.gch_manifest).read_text())
        self._out=self.logs_dir.parent/'gch-observer';self._out.mkdir(parents=True,exist_ok=True)
        self._calls=self._http=0;self._pid=None;self._reads=[];self._events=[]
        self._secret=self._llm._llm_kwargs.get('api_key')
        factory=self._llm._init_logger_fn
        def logger(path):
            native=factory(path)
            return lambda data:native(redact_credentials(self._llm._clean_value(data),self._secret))
        self._llm._init_logger_fn=logger
        native=self._llm.call.__wrapped__.__get__(self._llm,type(self._llm))
        async def observed(prompt,message_history=None,**call_kwargs):
            budget=self._gch['budget'];messages=list(message_history or [])+[{'role':'user','content':prompt}]
            self.event('model-request',messages=messages,parameters=call_kwargs)
            if self.options.gch_mode=='probe':raise StopBeforeModel()
            if self._calls>=budget['max_requests']:raise RuntimeError('GCh request budget exhausted')
            if call_kwargs.get('num_retries')!=0 or call_kwargs.get('max_completion_tokens')!=2048:raise RuntimeError('GCh model configuration changed')
            import litellm
            estimate=litellm.token_counter(model=self.model_name,messages=messages)+256
            if estimate>budget['max_input_tokens_per_request']:raise RuntimeError('GCh input budget exceeded')
            consumed=sum(e['tokens'] for e in self._events if e.get('kind')=='reserved')
            if consumed+estimate>budget['max_input_tokens_total']:raise RuntimeError('GCh total input budget exceeded')
            self._events.append({'kind':'reserved','tokens':estimate});self._calls+=1
            adapter=importlib.import_module('litellm.main').openai_chat_completions
            request=OneRequest(adapter.make_openai_chat_completion_request,max_completion_tokens=2048)
            original_after=request.after_http
            async def response_hook(response):
                await original_after(response);body=await response.aread()
                self.event('http-response',status=response.status_code,body=body.decode('utf-8',errors='replace'))
            request.after_http=response_hook
            async def wire(*a,**kw):
                self.event('http-request',payload=kw.get('data'))
                return await request.send(*a,**kw)
            start=time.monotonic()
            try:
                with patch.object(adapter,'make_openai_chat_completion_request',wire):
                    result=await native(prompt=prompt,message_history=message_history or [],**call_kwargs)
                usage={k:getattr(result.usage,k) for k in ('prompt_tokens','completion_tokens','cache_tokens','cost_usd')} if result.usage else None
                self.event('model-response',content=result.content,model=result.model_name,usage=usage,seconds=time.monotonic()-start)
                return result
            except BaseException as e:
                self.event('model-error',error_type=type(e).__name__,seconds=time.monotonic()-start)
                raise RuntimeError('GCh model request stopped: '+type(e).__name__) from None
            finally:self._http+=request.http_attempts
        self._llm.call=observed

    def event(self,kind,**data):
        with (self._out/(kind+'.jsonl')).open('a',encoding='utf-8') as f:f.write(json.dumps(redact_credentials({'time':time.time(),**data},self._secret),ensure_ascii=False)+'\n')

    async def setup(self,environment):
        await super().setup(environment)
        probe=await environment.exec("test ! -e /app && test ! -e /tests && test ! -e /solution && test ! -e /audit/upstream && test ! -S /var/run/docker.sock && test -z \"$ZHIZENGZENG_API_KEY$DEEPSEEK_API_KEY\"",timeout_sec=10)
        if probe.return_code:raise RuntimeError('GCh hidden-resource or credential isolation failed')
        cid=await environment._run_docker_compose_command(['ps','-q','main'])
        inspected=subprocess.run(['docker','inspect',cid.stdout.strip(),'--format','{"image":{{json .Image}},"mounts":{{json .Mounts}},"network":{{json .HostConfig.NetworkMode}}}'],capture_output=True,check=True)
        info=json.loads(inspected.stdout)
        self.event('isolation-check',**info)
        allowed={'/logs/agent':environment.trial_paths.agent_dir,
                 '/logs/verifier':environment.trial_paths.verifier_dir,
                 '/logs/artifacts':environment.trial_paths.host_artifact_path('main','/logs/artifacts')}
        if any(m['Destination']not in allowed or m['Source']!=str(allowed[m['Destination']].resolve()) for m in info['mounts']):raise RuntimeError('GCh unexpected host mount')
        sidecar=await environment._run_docker_compose_command(['ps','-q',environment._EGRESS_CONTROL_SERVICE_NAME])
        if info['network']!='container:'+sidecar.stdout.strip() or environment.network_policy.network_mode.value!='no-network':raise RuntimeError('GCh unexpected network policy')
        # The transparent sidecar accepts a TCP handshake before rejecting the payload.
        network=await environment.exec("python -c "+shlex.quote("import urllib.request,urllib.error\ntry:\n urllib.request.urlopen('https://example.com/',timeout=3).read(1)\nexcept urllib.error.HTTPError:\n raise RuntimeError('External HTTP response was reachable')\nexcept OSError as e:\n print(type(e).__name__)\nelse:\n raise RuntimeError('External content was reachable')"),timeout_sec=10)
        self.event('network-probe',return_code=network.return_code,stdout=network.stdout,stderr=network.stderr)
        if network.return_code:raise RuntimeError('GCh network denial check failed')
        rules=await environment._run_docker_compose_command(['exec','--no-TTY',environment._EGRESS_CONTROL_SERVICE_NAME,'network-policy','show'])
        if 'mode: controlled egress' not in rules.stdout or '(empty: deny all controlled TCP egress)' not in rules.stdout:raise RuntimeError('GCh sidecar does not deny egress')
        info.update(network_policy='no-network',blocked_tcp_result=network.stdout,sidecar_policy=rules.stdout)
        expected=self._manifest.get('frozen_environment_image_id')
        if expected and info['image']!=expected:raise RuntimeError('GCh environment image changed')
        if self.options.gch_mode=='paid' and not expected:raise RuntimeError('GCh paid run requires zero-model frozen image')
        self.event('isolation',status='PASS',**info)

    async def _build_skills_section(self,environment):
        xml=await super()._build_skills_section(environment);actual=await remote_hashes(environment,'/harbor/skills')
        if actual!=self._manifest['files']:raise RuntimeError('GCh Skill bytes changed')
        entries=list(ElementTree.fromstring(xml)) if xml else []
        ids={pathlib.PurePosixPath(e.findtext('location')).parent.name for e in entries}
        if ids!=set(self._manifest['metadata']) or len(entries)!=len(ids):raise RuntimeError('GCh Skill discovery mismatch')
        (self._out/'skill-index.xml').write_text(xml,encoding='utf-8');self.event('installation',status='PASS',files=actual,ids=sorted(ids))
        watch=await environment.exec("nohup stdbuf -oL inotifywait -m -r -e open,access,close_nowrite --timefmt '%s' --format '%T|%e|%w%f' /harbor/skills >/logs/agent/gch-kernel-reads.log 2>/logs/agent/gch-watch.stderr </dev/null & echo $!",timeout_sec=10)
        self._pid=int(watch.stdout.strip())
        ready=await environment.exec("for i in $(seq 1 100); do grep -q 'Watches established' /logs/agent/gch-watch.stderr && exit 0; sleep 0.02; done; exit 1",timeout_sec=10)
        if ready.return_code:raise RuntimeError('GCh file-access monitor did not start')
        return xml

    async def _execute_commands(self,commands,session):
        self.event('tool-actions',commands=[{'keystrokes':c.keystrokes,'duration_sec':c.duration_sec} for c in commands])
        return await super()._execute_commands(commands,session)

    def _limit_output_length(self,output,max_bytes=10000):
        result=super()._limit_output_length(output,max_bytes);self.event('terminal-frames',full_output=output,model_visible_output=result);return result

    async def run(self,instruction,environment,context):
        stopped=False
        try:
            try:await super().run(instruction,environment,context)
            except StopBeforeModel:
                stopped=True
                if self._manifest.get('probe_read_skill',True):
                    for sid in self._manifest['metadata']:await environment.exec('cat /harbor/skills/'+sid+'/SKILL.md >/dev/null',timeout_sec=10)
        finally:
            if self._pid:
                await environment.exec('kill '+str(self._pid),timeout_sec=10)
                lines=await environment.exec('cat /logs/agent/gch-kernel-reads.log',timeout_sec=10)
                if lines.return_code:raise RuntimeError('GCh read monitor log unavailable')
                self._reads=accessed_skills(lines.stdout or '',self._manifest['metadata'])
            actor='controlled_probe' if self.options.gch_mode=='probe' else 'model_tool'
            (self._out/'summary.json').write_text(json.dumps({'mode':self.options.gch_mode,'stopped_before_model':stopped,'logical_requests':self._calls,'actual_http_attempts':self._http,'skill_reads':[{**e,'actor':actor} for e in self._reads],'cost_invoice':None},indent=2))
