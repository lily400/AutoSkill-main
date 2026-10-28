# TypeAdapter 校验纯联合类型 Evidence

- family: 未分类技能
- skill_id: 2a47f56f-2ee0-5cb8-80c8-ed41f07d7ffc
- support_count: 1

## Evidence 1

- support_id: 52871143-3b70-5022-a1fd-af6ce48fbc55
- relation_type: support
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 19692:25009
- confidence: 0.80
- quote: Nested Discriminated Unions
Only one discriminator can be set for a field but sometimes you want to combine multiple discriminators.
You can do it by creating nested `Annotated` types, e.g.:

```
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, ValidationError

class BlackCat(BaseModel):
    pet_type: Literal['cat']
    color: Literal['black']
    black_name: str

class WhiteCat(BaseModel):
    pet_type: Literal['cat']
    color: Literal['white']
    white_name: str

Cat = Annotated[Union[BlackCat, WhiteCat], Field(discriminator='color')]

class Dog(BaseModel):
    pet_type: Literal['dog']
    name: str

Pet = Annotated[Union[Cat, Dog], Field(discriminator='pet_type')]

class Model(BaseModel):
    pet: Pet
    n: int

If you want to validate data against a union, and solely a union, you can use pydantic's [`TypeAdapter`](../type_adapter/) construct instead of inheriting from the standard `BaseModel`.

In the context of the previous example, we have the following:

```
type_adapter = TypeAdapter(Pet)

pet = type_adapter.validate_python(
    {'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'}
)
print(repr(pet))
#> BlackCat(pet_type='cat', color='black', black_name='felix')
```

You can also customize the error type, message, and context for a `Discriminator` by passing
these specifications as parameters to the `Discriminator` constructor, as seen in the example below.

```
from typing import Annotated, Union

from pydantic import BaseModel, Discriminator, Tag, ValidationError

# Errors are quite verbose with a normal Union:
class Model(BaseModel):
    x: Union[str, 'Model']

# Errors are much simpler with a discriminated union:
def model_x_discriminator(v):
    if isinstance(v, str):
        return 'str'
    if isinstance(v, (dict, BaseModel)):
        return 'model'

try:
    DiscriminatedModel.model_validate({'x': {'x': {'x': 1}}})
except ValidationError as e:
    print(e)
    """
    1 validation error for DiscriminatedModel
    x.model.x.model.x
      Invalid union member [type=invalid_union_member, input_value=1, input_type=int]
    """

try:
    DiscriminatedModel.model_validate({'x': {'x': {'x': {}}}})
except ValidationError as e:
    print(e)
    """
    1 validation error for DiscriminatedModel
    x.model.x.model.x.model.x
      Field required [type=missing, input_value={}, input_type=dict]
    """
