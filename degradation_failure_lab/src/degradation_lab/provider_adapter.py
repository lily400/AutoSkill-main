"""Audited DeepSeek adapter: preserve payloads and isolate optional proxy transport."""
import http.client
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, fields

from autoskill.llm.factory import build_llm
from autoskill.llm.openai import OpenAIChatLLM


def retryable_transport_error(exc):
    """Retry a small whitelist of connection failures, never auth/cert/HTTP errors."""
    if isinstance(exc, urllib.error.HTTPError):
        return False
    reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(reason, ssl.SSLCertVerificationError):
        return False
    return isinstance(reason, (
        ssl.SSLEOFError,
        TimeoutError,
        ConnectionResetError,
        ConnectionAbortedError,
        BrokenPipeError,
        http.client.RemoteDisconnected,
    ))


def limited_transport_retry(send_once, *, retries=0, backoff_s=1.0, on_retry=None, sleep=time.sleep):
    """Every callback invocation must be individually budgeted and logged by caller."""
    for attempt_index in range(1, retries + 2):
        try:
            return send_once(attempt_index)
        except Exception as exc:
            if attempt_index > retries or not retryable_transport_error(exc):
                raise
            if on_retry is not None:
                on_retry(attempt_index, exc)
            sleep(min(8.0, backoff_s * (2 ** (attempt_index - 1))))


@dataclass
class ConfiguredOpenAIChatLLM(OpenAIChatLLM):
    thinking_mode: str = 'disabled'
    proxy_mode: str = 'system'

    def _build_payload(self, **kwargs):
        payload = super()._build_payload(**kwargs)
        payload['thinking'] = {'type': self.thinking_mode}
        return payload

    def _post_json(self, *, payload, stream):
        """The direct opener ignores both env and Windows registry proxy settings."""
        req = self._build_request(payload=payload, stream=stream)
        try:
            if self.proxy_mode == 'direct':
                opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                with opener.open(req, timeout=self.timeout_s) as resp:
                    return resp.read().decode('utf-8')
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                return resp.read().decode('utf-8')
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode('utf-8', errors='replace')
            raise RuntimeError(f'OpenAI-compatible HTTP {exc.code}: {raw}') from exc


def build(config):
    # Keep upstream parameters/prompt/response exactly; only configure the
    # thinking field and explicit transport route on the subclass.
    non_upstream = {'connector_factory', 'proxy_mode', 'transport_retries', 'transport_retry_backoff_s'}
    base = build_llm({k: v for k, v in config.items() if k not in non_upstream})
    if type(base) is not OpenAIChatLLM:
        raise ValueError('Expected the upstream OpenAI client')
    mode = config.get('thinking_mode', 'disabled')
    if mode not in ('disabled', 'enabled'):
        raise ValueError('Invalid thinking_mode')
    proxy_mode = config.get('proxy_mode', 'system')
    if proxy_mode not in ('direct', 'system'):
        raise ValueError('Invalid proxy_mode')
    return ConfiguredOpenAIChatLLM(
        **{f.name: getattr(base, f.name) for f in fields(OpenAIChatLLM)},
        thinking_mode=mode, proxy_mode=proxy_mode,
    )
