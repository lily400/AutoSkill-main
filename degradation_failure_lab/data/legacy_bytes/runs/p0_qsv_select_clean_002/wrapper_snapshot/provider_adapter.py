"""Official connector extension: model parameter only, no prompt/result changes."""
from dataclasses import dataclass, fields
from autoskill.llm.factory import build_llm
from autoskill.llm.openai import OpenAIChatLLM


@dataclass
class ConfiguredOpenAIChatLLM(OpenAIChatLLM):
    thinking_mode: str = 'disabled'

    def _build_payload(self, **kwargs):
        payload = super()._build_payload(**kwargs)
        payload['thinking'] = {'type': self.thinking_mode}
        return payload


def build(config):
    # Use the upstream factory for every standard parameter, including its
    # per-stage 256/768/128-token budgets. Add only the requested model setting.
    base = build_llm({k:v for k,v in config.items() if k!='connector_factory'})
    if type(base) is not OpenAIChatLLM:
        raise ValueError('Expected the upstream OpenAI client')
    mode = config.get('thinking_mode','disabled')
    if mode not in ('disabled','enabled'):
        raise ValueError('Invalid thinking_mode')
    return ConfiguredOpenAIChatLLM(**{f.name:getattr(base,f.name) for f in fields(OpenAIChatLLM)}, thinking_mode=mode)
