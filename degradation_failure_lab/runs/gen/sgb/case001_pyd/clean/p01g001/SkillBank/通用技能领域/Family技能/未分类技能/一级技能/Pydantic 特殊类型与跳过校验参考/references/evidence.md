# Pydantic 特殊类型与跳过校验参考 Evidence

- family: 未分类技能
- skill_id: 81c5fe93-c4e0-53ad-bc12-ac8fea6d8888
- support_count: 1

## Evidence 1

- support_id: 77c14e6e-dd36-58da-8ee6-ddabd63ab096
- relation_type: support
- document: input001\validators.md
- doc_id: a60f9661-6cba-5f16-be41-fbe06bc00bca
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case001_pyd\clean\p01g001\inputs\input001\validators.md
- section: # Validators
- span: 23781:24361
- confidence: 0.60
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
