# Pydantic 校验错误抛出与校验器顺序控制 Evidence

- family: 未分类技能
- skill_id: 6f6dd4cb-79fc-53a5-a853-3cf312474f21
- support_count: 1

## Evidence 1

- support_id: d5ee8998-95c2-5be0-990d-a3a218461c30
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 23781:24361
- confidence: 0.65
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
