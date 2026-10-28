# Pydantic 模型级校验器与 ValidationInfo 使用 Evidence

- family: 未分类技能
- skill_id: 4641701b-2dc0-5429-a380-d65c1c0ec55d
- support_count: 1

## Evidence 1

- support_id: c0482437-45c1-56f1-a73c-a15764b64f88
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 23781:24361
- confidence: 0.70
- quote: class Basket(BaseModel):
    fruits: list[InstanceOf[Fruit]]

print(Basket(fruits=[Banana(), Apple()]))
#> fruits=[Banana, Apple]
try:
    Basket(fruits=[Banana(), 'Apple'])
except ValidationError as e:
    print(e)
    """
    1 validation error for Basket
    fruits.1
      Input should be an instance of Fruit [type=is_instance_of, input_value='Apple', input_type=str]
    """
```
- [`SkipValidation`](../../api/functional_validators/#pydantic.functional_validators.SkipValidation) can be used to skip validation on a field.

```
from pydantic import BaseModel, SkipValidation
