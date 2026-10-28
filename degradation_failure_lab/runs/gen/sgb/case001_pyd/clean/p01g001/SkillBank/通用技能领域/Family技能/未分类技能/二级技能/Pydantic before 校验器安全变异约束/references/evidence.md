# Pydantic before 校验器安全变异约束 Evidence

- family: 未分类技能
- skill_id: 9eb16e27-a3e6-5b09-a407-854038ca54a2
- support_count: 1

## Evidence 1

- support_id: 43d03a28-6070-5e7c-a6c6-78da780d4613
- relation_type: constraint
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 14017:14766
- confidence: 0.75
- quote: class UserModel(BaseModel):
    username: str
    password: str
    password_repeat: str

@model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError('Passwords do not match')
        return self
```
- ***Before* validators**: are run before the model is instantiated. These are more flexible than *after* validators,
 but they also have to deal with the raw input, which in theory could be any arbitrary object. You should also avoid
 mutating the value directly if you are raising a validation error later in your validator
 function, as the mutated value may be passed to other validators if using [unions](../unions/).

```
from typing import Any
