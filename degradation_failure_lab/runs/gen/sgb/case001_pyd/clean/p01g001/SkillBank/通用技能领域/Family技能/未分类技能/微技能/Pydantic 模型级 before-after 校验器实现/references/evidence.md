# Pydantic 模型级 before/after 校验器实现 Evidence

- family: 未分类技能
- skill_id: 688b17b0-4bcf-5eb2-879a-50609da68fe0
- support_count: 1

## Evidence 1

- support_id: cd88700d-ce2b-5523-a900-392c03194c0e
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 14817:15985
- confidence: 0.80
- quote: class UserModel(BaseModel):
    username: str

@model_validator(mode='before')
    @classmethod
    def check_card_number_not_present(cls, data: Any) -> Any:  # (1)!
        if isinstance(data, dict):  # (2)!
            if 'card_number' in data:
                raise ValueError("'card_number' should not be included")
        return data
```
  1. Notice the use of [`Any`](https://docs.python.org/3/library/typing.html#typing.Any) as a type hint for `data`. *Before* validators take the raw input, which
 can be anything.
  2. Most of the time, the input data will be a dictionary (e.g. when calling `UserModel(username='...')`). However,
 this is not always the case. For instance, if the [`from_attributes`](../../api/config/#pydantic.config.ConfigDict.from_attributes)
 configuration value is set, you might receive an arbitrary class instance for the `data` argument.
- ***Wrap* validators**: are the most flexible of all. You can run code before or after Pydantic and
 other validators process the input data, or you can terminate validation immediately, either by returning
 the data early or by raising an error.

```
import logging
from typing import Any
