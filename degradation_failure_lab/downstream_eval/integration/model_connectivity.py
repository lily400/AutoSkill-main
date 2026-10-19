"""One bounded connectivity request in the existing Harbor control environment."""
import argparse
import asyncio
import contextlib
import importlib
import io
import json
import logging
import os
import re
import sys
from pathlib import Path
from unittest.mock import patch


class RequestLimit(BaseException):
    """A second request must bypass retry handlers and stop immediately."""


def already_attempted(output):
    if not (output / 'request.started').exists():
        return None
    saved = output / 'result.json'
    status = json.loads(saved.read_text(encoding='utf-8')).get('status') if saved.exists() else 'UNREPORTED'
    return {'status': 'ALREADY_ATTEMPTED', 'saved_result_status': status,
            'new_request_attempts': 0, 'reason': 'Single-use request lock exists; do not enter the credential or resend'}


def settings(profile):
    model = profile['model']
    if (model['name'] != 'openai/gpt-5.4-mini-2026-03-17' or
        model['base_url'] != 'https://api.zhizengzeng.com/v1' or
        model['api_format'] != 'openai_chat_completions' or
        model['api_key_environment_variable'] != 'ZHIZENGZENG_API_KEY' or
        model['temperature'] != 0 or model['reasoning_effort'] != 'none'):
        raise ValueError('Unexpected connectivity configuration')
    return model


class OneRequest:
    def __init__(self, sender, max_completion_tokens=16):
        self.sender = sender
        self.max_completion_tokens = max_completion_tokens
        self.attempts = 0
        self.http_attempts = 0
        self.http_status = None
        self.response = None

    async def before_http(self, request):
        if self.http_attempts:
            raise RequestLimit()
        if str(request.url) != 'https://api.zhizengzeng.com/v1/chat/completions':
            raise ValueError('Unexpected HTTP destination')
        self.http_attempts += 1

    async def after_http(self, response):
        self.http_status = response.status_code

    async def send(self, *args, **kwargs):
        if self.attempts:
            raise RequestLimit()
        client, data = kwargs['openai_aclient'], kwargs['data']
        if (client.max_retries != 0 or
            str(client.base_url).rstrip('/') != 'https://api.zhizengzeng.com/v1' or
            data.get('model') != 'gpt-5.4-mini-2026-03-17' or
            data.get('max_completion_tokens') != self.max_completion_tokens or
            data.get('temperature') != 0 or data.get('reasoning_effort') != 'none'):
            raise ValueError('Wire parameters differ from the approved request')
        self.attempts += 1
        http_client = client._client
        previous_hooks = http_client.event_hooks
        try:
            http_client.event_hooks = {'request': [self.before_http], 'response': [self.after_http]}
            result = await self.sender(*args, **kwargs)
        finally:
            http_client.event_hooks = previous_hooks
        response = result[1]
        usage = response.usage
        self.response = {'returned_model': response.model,
                         'reply': response.choices[0].message.content,
                         'usage': {name: getattr(usage, name, None) for name in
                                   ('prompt_tokens', 'completion_tokens', 'total_tokens')} if usage else None}
        return result


async def probe(profile, key):
    import litellm
    from harbor.llms.lite_llm import LiteLLM
    model = settings(profile)
    adapter = importlib.import_module('litellm.main').openai_chat_completions
    request = OneRequest(adapter.make_openai_chat_completion_request)
    client = LiteLLM(model_name=model['name'], api_base=model['base_url'],
                     model_api_format=model['api_format'], temperature=0,
                     reasoning_effort='none', api_key=key)
    # Use the fixed official function body, excluding its outer Tenacity retries.
    native_call = client.call.__wrapped__.__get__(client, type(client))
    previous_logging = logging.root.manager.disable
    litellm.suppress_debug_info = True
    logging.disable(logging.CRITICAL)
    error = None
    try:
        with patch.object(adapter, 'make_openai_chat_completion_request', new=request.send), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            await native_call(prompt='Reply only API_OK', max_completion_tokens=16, num_retries=0, timeout=45)
    except (Exception, RequestLimit) as failure:
        # Provider exception strings and HTTP headers can contain credentials.
        code = getattr(failure, 'status_code', None)
        error = {'type': type(failure).__name__, 'http_status': code if isinstance(code, int) else None}
    finally:
        logging.disable(previous_logging)
    response = request.response or {}
    passed = (error is None and request.attempts == 1 and request.http_attempts == 1 and
              request.http_status is not None and 200 <= request.http_status < 300 and
              (response.get('reply') or '').strip() == 'API_OK' and
              response.get('returned_model') == model['name'].split('/', 1)[1] and
              isinstance((response.get('usage') or {}).get('total_tokens'), int))
    # Record the response while removing any credential or authorization text echoed remotely.
    for field in ('reply', 'returned_model'):
        value = response.get(field)
        if isinstance(value, str):
            value = value.replace(key, '[REDACTED]') if key else value
            value = re.sub(r'(?im)^.*\bAuthorization\b.*$', '[REDACTED]', value)
            value = re.sub(r'(?i)\bBearer\s+[^\s\"\x27<>]+', '[REDACTED]', value)
        response[field] = value
    return {'status': 'PASS' if passed else 'FAIL', 'request_attempts': request.attempts,
            'http_request_attempts': request.http_attempts, 'http_status': request.http_status,
            'request': {'model': model['name'], 'wire_model': model['name'].split('/', 1)[1],
                        'base_url': model['base_url'], 'api_format': model['api_format'],
                        'messages': [{'role': 'user', 'content': 'Reply only API_OK'}],
                        'temperature': 0, 'reasoning_effort': 'none', 'max_completion_tokens': 16,
                        'timeout_sec': 45, 'sdk_retries': 0, 'outer_retries': 0},
            **response, 'error': error, 'actual_billed_cost': None,
            'billing_status': 'Zhizengzeng account tariff and invoice not verified',
            'terminus_tasks_started': 0, 'experiment_arms_started': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--send-once', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'p1-connectivity-[A-Za-z0-9_-]+', args.run_id):
        parser.error('Use a unique p1-connectivity- run ID')
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / 'src'))
    output = root / 'runs/downstream/git-restore-explicit-source-both-v1' / args.run_id
    output.mkdir(parents=True, exist_ok=True)
    previous = already_attempted(output)
    if previous:
        print(json.dumps(previous))
        return 3
    profile = json.loads((root / 'downstream_eval/configs/p1_smoke.json').read_text(encoding='utf-8'))
    model = settings(profile)
    from .harbor_adapter import verify_sources
    import importlib.metadata
    _, lock = verify_sources(root)
    if importlib.metadata.version('harbor') != lock['harbor_version']:
        raise ValueError('Pinned Harbor installation required')
    gate = os.environ.get('P1_ALLOW_PAID')
    key = os.environ.get(model['api_key_environment_variable'])
    if not args.send_once or not key:
        result = {'status': 'READY' if not args.send_once or key else 'BLOCKED', 'request_attempts': 0,
                  'credential_present': bool(key), 'reason': 'No request without --send-once and environment credential',
                  'pinned_harbor_source_check': 'PASS', 'harbor_version': lock['harbor_version'],
                  'P1_ALLOW_PAID_changed': False}
        target = output / 'preflight.json'
    else:
        # Durable single-use lock: a failed or interrupted request is never retried on rerun.
        with (output / 'request.started').open('x', encoding='utf-8') as stream:
            stream.write('Single authorized connectivity attempt; not P1 task authorization.\n')
        result = asyncio.run(probe(profile, key))
        result.update({'harbor_version': lock['harbor_version'], 'harbor_commit': lock['harbor_commit'],
                       'P1_ALLOW_PAID_changed': os.environ.get('P1_ALLOW_PAID') != gate,
                       'authorization_profile_unchanged': profile['authorization'] == 'AWAITING_USER_APPROVAL'})
        target = output / 'result.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] in ('PASS', 'READY') else 2


if __name__ == '__main__':
    raise SystemExit(main())
