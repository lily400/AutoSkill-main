"""Opt-in observation around the official agent; no replacement agent loop."""
import asyncio
import json
import os
import re
import shlex
import subprocess
import time
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree

from .skill_install import remote_hashes


class PreModelStop(BaseException):
    """Deliberate zero-model stop, outside the upstream request retry decorator."""


def accessed_skills(lines, expected_ids):
    result = []
    for line in lines.splitlines():
        fields = line.split('|', 2)
        if len(fields) != 3 or 'ACCESS' not in fields[1].split(','):
            continue
        path = PurePosixPath(fields[2])
        if path.parent.parent == PurePosixPath('/harbor/skills') and path.name == 'SKILL.md' and path.parent.name in expected_ids:
            result.append({'skill_id': path.parent.name, 'path': str(path), 'kernel_event': fields[1], 'timestamp': fields[0]})
    return result


def body_visible(body, observation):
    # tmux soft wraps and CRLF change whitespace; disk integrity is checked separately.
    compact = lambda text: re.sub(r'\s+', '', re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text))
    return bool(body) and compact(body) in compact(observation)


class P1ObservationMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._p1 = None
        if self.options.p1_mode is None:
            return
        self._p1 = json.loads(Path(self.options.p1_profile).read_text(encoding='utf-8'))
        self._p1_logs = self.logs_dir.parent / 'p1-observer'
        self._p1_manifest = json.loads(Path(self.options.p1_manifest).read_text(encoding='utf-8'))
        if self.model_name != self._p1['model']['name']:
            raise ValueError('P1 model differs from frozen profile')
        if (self.options.temperature != self._p1['model']['temperature'] or
            self.options.reasoning_effort != self._p1['model']['reasoning_effort'] or
            self.options.max_turns != self._p1['budget']['max_requests'] or self.options.enable_summarize):
            raise ValueError('P1 sampling, turn or summarization settings differ from frozen profile')
        self._p1_actor = 'zero_model_probe' if self.options.p1_mode == 'probe' else 'model_tool'
        self._p1_calls = self._p1_input = self._p1_watch_lines = 0
        self._p1_pid = None
        self._p1_reads = []
        self._p1_kernel_prefix = []
        self._p1_tool_events = []
        # P1's zero-retry budget also disables the pinned method's outer Tenacity retries.
        original_call = self._llm.call.__wrapped__.__get__(self._llm, type(self._llm))

        async def bounded_call(prompt, message_history=None, **call_kwargs):
            from litellm import token_counter
            messages = list(message_history or []) + [{'role': 'user', 'content': prompt}]
            estimated = token_counter(model=self.model_name, messages=messages) + 256
            self._event('model-requests', mode=self.options.p1_mode, messages=messages,
                        dispatched=False, estimated_input_tokens_with_reserve=estimated, parameters=call_kwargs)
            if self.options.p1_mode == 'probe':
                raise PreModelStop()
            if os.environ.get(self._p1['approval_environment_variable']) != '1':
                raise RuntimeError('Paid inference awaits explicit user approval; P1_ALLOW_PAID is unset')
            budget = self._p1['budget']
            expected = {'max_completion_tokens': budget['max_completion_tokens_per_request'],
                        'num_retries': budget['num_retries'], 'timeout': budget['request_timeout_sec']}
            if any(call_kwargs.get(key) != value for key, value in expected.items()):
                raise ValueError('P1 output/retry/timeout controls differ from frozen profile')
            if (self._p1_calls >= budget['max_requests'] or
                estimated > budget['max_input_tokens_per_request'] or
                self._p1_input + estimated > budget['max_input_tokens_total']):
                self._event('budget', status='exhausted_before_request')
                raise RuntimeError('P1 request/input token budget exhausted')
            self._p1_calls += 1
            self._p1_input += estimated
            self._event('model-dispatch', request_number=self._p1_calls, dispatched=True,
                        estimated_input_tokens_with_reserve=estimated)
            try:
                response = await original_call(prompt=prompt, message_history=message_history or [], **call_kwargs)
            except Exception as error:
                self._event('model-errors', error_type=type(error).__name__, usage='unreported; not zero cost')
                raise
            usage = response.usage
            rates = self._p1['price_usd_per_million_tokens']
            fixed_rate_cost = ((usage.prompt_tokens - usage.cache_tokens) * rates['input'] +
                               usage.cache_tokens * rates['cached_input'] + usage.completion_tokens * rates['output']) / 1_000_000 if usage else None
            self._event('model-responses', content=response.content, model=response.model_name,
                        fixed_rate_cost_estimate_usd=fixed_rate_cost,
                        usage=({key: getattr(usage, key) for key in
                                ('prompt_tokens', 'completion_tokens', 'cache_tokens', 'cost_usd')} if usage else None))
            return response

        self._llm.call = bounded_call

    def _event(self, name, **data):
        # The agent mounts logs_dir; its sibling is private to the Harbor control process.
        self._p1_logs.mkdir(parents=True, exist_ok=True)
        with (self._p1_logs / ('p1-' + name + '.jsonl')).open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'time': time.time(), **data}, ensure_ascii=False) + '\n')

    async def setup(self, environment):
        await super().setup(environment)
        if not self._p1:
            return
        self._p1_environment = environment
        result = await environment.exec('mkdir -p /harbor/skills; test ! -e /tests && test ! -e /solution && test ! -e /environment && test ! -e /tmp/build-fixture.py && test ! -S /var/run/docker.sock', timeout_sec=10)
        if result.return_code:
            raise RuntimeError('P1 answer-isolation filesystem check failed')
        container = await environment._run_docker_compose_command(['ps', '-q', 'main'])
        probe = await asyncio.to_thread(subprocess.run, ['docker', 'inspect', container.stdout.strip(), '--format', '{"mounts":{{json .Mounts}},"image_id":{{json .Image}}}'], capture_output=True, check=True)
        inspected = json.loads(probe.stdout)
        mounts = inspected['mounts']
        image_id = inspected['image_id']
        expected_image = self._p1.get('frozen_agent_image_id')
        if expected_image and image_id != expected_image:
            raise RuntimeError('P1 image differs from the zero-model validated image')
        if self.options.p1_mode == 'paid' and not expected_image:
            raise RuntimeError('P1 paid trial requires a zero-model validated image')
        frozen_image = 'harbor-p1-task:sha256-' + image_id.split(':')[-1]
        if self.options.p1_mode == 'probe':
            await asyncio.to_thread(subprocess.run, ['docker', 'tag', image_id, frozen_image], capture_output=True, check=True)
        allowed = {'/logs/agent': environment.trial_paths.agent_dir,
                   '/logs/verifier': environment.trial_paths.verifier_dir,
                   '/logs/artifacts': environment.trial_paths.host_artifact_path('main', '/logs/artifacts')}
        self._event('isolation', status='CHECKING', mounts=mounts)
        if any(m['Destination'] not in allowed or str(allowed[m['Destination']].resolve()) != m['Source'] for m in mounts):
            raise RuntimeError('P1 agent has an unexpected host mount')
        self._event('isolation', status='PASS', mounts=mounts, environment_image_id=image_id,
                    frozen_image=frozen_image, fixture_source_visible=False,
                    oracle_visible=False, reference_solution_visible=False, api_key_forwarded=bool(self._extra_env))
        await self._session.send_keys("export PS1='p1$ '; clear\n", min_timeout_sec=0.1)

    async def _build_skills_section(self, environment):
        xml = await super()._build_skills_section(environment)
        if not getattr(self, '_p1', None):
            return xml
        actual = await remote_hashes(environment, '/harbor/skills')
        if actual != self._p1_manifest['files']:
            raise ValueError('Native Harbor injection changed the Skill file/ID/hash set')
        entries = list(ElementTree.fromstring(xml)) if xml else []
        by_id = {PurePosixPath(e.findtext('location')).parent.name: e for e in entries}
        expected = self._p1_manifest['metadata']
        if len(entries) != len(expected) or set(by_id) != set(expected):
            raise ValueError('P1 index is incomplete or duplicated')
        for sid, metadata in expected.items():
            if any(by_id[sid].findtext(key) != metadata[key] for key in ('name', 'description')):
                raise ValueError('P1 index metadata differs from canonical Skill')
        self._p1_logs.mkdir(parents=True, exist_ok=True)
        (self._p1_logs / 'p1-skill-index.xml').write_text(xml or '', encoding='utf-8')
        self._event('installation', status='PASS', installed_ids=sorted(expected),
                    discovered_ids=sorted(by_id), file_hashes=actual)
        result = await environment.exec("nohup stdbuf -oL inotifywait -m -r -e open,access,close_nowrite --timefmt '%s' --format '%T|%e|%w%f' /harbor/skills >/logs/agent/p1-kernel-reads.log 2>/logs/agent/p1-kernel-watch.stderr </dev/null & echo $!", timeout_sec=10)
        self._p1_pid = int(result.stdout.strip())
        ready = await environment.exec("for i in $(seq 1 100); do grep -q 'Watches established' /logs/agent/p1-kernel-watch.stderr && exit 0; sleep 0.02; done; exit 1", timeout_sec=10)
        if ready.return_code:
            raise RuntimeError('P1 file-access monitor did not start')
        return xml

    def _limit_output_length(self, output, max_bytes=10000):
        limited = super()._limit_output_length(output, max_bytes)
        if getattr(self, '_p1', None):
            self._event('terminal-frames', actor=self._p1_actor, full_output=output,
                        model_visible_output=limited, truncated=limited != output,
                        full_utf8_bytes=len(output.encode('utf-8')), visible_utf8_bytes=len(limited.encode('utf-8')))
        return limited

    async def _capture_reads(self):
        result = await self._p1_environment.exec('cat /logs/agent/p1-kernel-reads.log', timeout_sec=10)
        if result.return_code:
            raise RuntimeError('P1 file-access evidence unavailable')
        lines = (result.stdout or '').splitlines()
        if lines[:self._p1_watch_lines] != self._p1_kernel_prefix:
            raise RuntimeError('P1 kernel read log was truncated or changed')
        events = accessed_skills('\n'.join(lines[self._p1_watch_lines:]), self._p1_manifest['metadata'])
        self._p1_watch_lines = len(lines)
        self._p1_kernel_prefix = lines
        for event in events:
            event['actor'] = self._p1_actor
            self._p1_reads.append(event)
            self._event('skill-reads', **event)
        return events

    async def _execute_commands(self, commands, session):
        if not getattr(self, '_p1', None):
            return await super()._execute_commands(commands, session)
        self._event('tool-actions', actor=self._p1_actor, stage='submitted', episode=self._n_episodes,
                    commands=[{'keystrokes': c.keystrokes, 'duration_sec': c.duration_sec} for c in commands])
        result = await super()._execute_commands(commands, session)
        reads = await self._capture_reads()
        visible = {}
        for event in reads:
            sid = event['skill_id']
            body = (Path(self._p1_manifest['staged_root']) / sid / 'SKILL.md').read_bytes().decode('utf-8')
            visible[sid] = body_visible(body, result[1])
        event = {'actor': self._p1_actor, 'stage': 'observed', 'timeout': result[0],
                 'observation': result[1], 'read_events': reads,
                 'full_body_visible_ignoring_terminal_whitespace': visible,
                 'truncated': '[... output limited to ' in result[1]}
        self._p1_tool_events.append(event)
        self._event('tool-actions', **event)
        return result

    async def run(self, instruction, environment, context):
        if not getattr(self, '_p1', None):
            return await super().run(instruction, environment, context)
        stopped = False
        try:
            try:
                await super().run(instruction, environment, context)
            except PreModelStop:
                stopped = True
                self._event('execution', status='STOPPED_BEFORE_MODEL', paid_requests=0)
                # Controlled terminal probes are kept separate from model-generated actions.
                from harbor.agents.terminus_2.terminus_2 import Command
                paths = ['/harbor/skills/' + sid + '/SKILL.md' for sid in sorted(self._p1_manifest['metadata'])]
                for path in paths:
                    await self._execute_commands([Command('cat ' + shlex.quote(path) + '\n', 0.2)], self._session)
                if not paths:
                    await self._execute_commands([Command('pwd\n', 0.2)], self._session)
        finally:
            if self._p1_pid:
                await environment.exec('kill ' + str(self._p1_pid), timeout_sec=10)
                await self._capture_reads()
            visible_ids = sorted({sid for e in self._p1_tool_events for sid, match in e['full_body_visible_ignoring_terminal_whitespace'].items() if match})
            summary = {'mode': self.options.p1_mode, 'stopped_before_model': stopped,
                       'paid_requests': self._p1_calls, 'estimated_input_reserved': self._p1_input,
                       'model_read_ids': sorted({e['skill_id'] for e in self._p1_reads if e['actor'] == 'model_tool'}),
                       'controlled_probe_read_ids': sorted({e['skill_id'] for e in self._p1_reads if e['actor'] == 'zero_model_probe'}),
                       'full_body_visible_ids_ignoring_terminal_whitespace': visible_ids,
                       'rule_following': 'requires action and Oracle review; not inferred from model self-report'}
            (self._p1_logs / 'p1-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
