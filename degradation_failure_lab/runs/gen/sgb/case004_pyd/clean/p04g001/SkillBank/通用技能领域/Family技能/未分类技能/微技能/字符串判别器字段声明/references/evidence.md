# 字符串判别器字段声明 Evidence

- family: 未分类技能
- skill_id: dbee85ed-4cc4-53bf-a0b0-a1d98c51007a
- support_count: 1

## Evidence 1

- support_id: 9f372687-7a80-5ee3-b90e-37de244c8cb3
- relation_type: support
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 16129:19225
- confidence: 0.75
- quote: def model_x_discriminator(v: Any) -> str:
    if isinstance(v, int):
        return 'int'
    if isinstance(v, (dict, BaseModel)):
        return 'model'
    else:
        # return None if the discriminator value isn't found
        return None

class SpecialValue(BaseModel):
    value: int

class DiscriminatedModel(BaseModel):
    value: Annotated[
        Union[
            Annotated[int, Tag('int')],
            Annotated['SpecialValue', Tag('model')],
        ],
        Discriminator(model_x_discriminator),
    ]

model_data = {'value': {'value': 1}}
m = DiscriminatedModel.model_validate(model_data)
print(m)
#> value=SpecialValue(value=1)

int_data = {'value': 123}
m = DiscriminatedModel.model_validate(int_data)
print(m)
#> value=123

1. Notice the callable discriminator function returns `None` if a discriminator value is not found.
 When `None` is returned, this `union_tag_not_found` error is raised.

```
from typing import Annotated, Any

from pydantic import BaseModel, Discriminator, Tag, ValidationError

def model_x_discriminator(v: Any) -> str:
    if isinstance(v, int):
        return 'int'
    if isinstance(v, (dict, BaseModel)):
        return 'model'
    else:
        # return None if the discriminator value isn't found
        return None

class SpecialValue(BaseModel):
    value: int

class DiscriminatedModel(BaseModel):
    value: Annotated[
        (
            Annotated[int, Tag('int')] |
            Annotated['SpecialValue', Tag('model')]
        ),
        Discriminator(model_x_discriminator),
    ]

model_data = {'value': {'value': 1}}
m = DiscriminatedModel.model_validate(model_data)
print(m)
#> value=SpecialValue(value=1)

int_data = {'value': 123}
m = DiscriminatedModel.model_validate(int_data)
print(m)
#> value=123

1. Notice the callable discriminator function returns `None` if a discriminator value is not found.
 When `None` is returned, this `union_tag_not_found` error is raised.

Using the [annotated pattern](../fields/#the-annotated-pattern) can be handy to regroup
the `Union` and `discriminator` information. See the next example for more details.

There are a few ways to set a discriminator for a field, all varying slightly in syntax.

For `str` discriminators:

```
some_field: Union[...] = Field(discriminator='my_discriminator')
some_field: Annotated[Union[...], Field(discriminator='my_discriminator')]
```
