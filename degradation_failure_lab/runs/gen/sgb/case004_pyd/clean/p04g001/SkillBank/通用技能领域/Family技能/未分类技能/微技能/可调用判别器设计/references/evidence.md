# 可调用判别器设计 Evidence

- family: 未分类技能
- skill_id: f2ee54d4-9dd0-5a47-9012-d0e239e70e9a
- support_count: 1

## Evidence 1

- support_id: 119de05c-37c6-55ca-8414-1aa8724e07e1
- relation_type: support
- document: input002\unions.md
- doc_id: 1d31929f-7c28-5538-8026-89e5fc796f73
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case004_pyd\clean\p04g001\inputs\input002\unions.md
- section: # Unions
- span: 10151:13211
- confidence: 0.85
- quote: To validate models based on that information you can set the same field - let's call it `my_discriminator` -
in each of the models with a discriminated value, which is one (or many) `Literal` value(s).
For your `Union`, you can set the discriminator in its value: `Field(discriminator='my_discriminator')`.

Python 3.9 and abovePython 3.10 and above

```
from typing import Literal, Union

from pydantic import BaseModel, Field, ValidationError

class Cat(BaseModel):
    pet_type: Literal['cat']
    meows: int

class Dog(BaseModel):
    pet_type: Literal['dog']
    barks: float

class Lizard(BaseModel):
    pet_type: Literal['reptile', 'lizard']
    scales: bool

class Model(BaseModel):
    pet: Union[Cat, Dog, Lizard] = Field(discriminator='pet_type')
    n: int

```
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

class Cat(BaseModel):
    pet_type: Literal['cat']
    meows: int

class Dog(BaseModel):
    pet_type: Literal['dog']
    barks: float

class Lizard(BaseModel):
    pet_type: Literal['reptile', 'lizard']
    scales: bool

class Model(BaseModel):
    pet: Cat | Dog | Lizard = Field(discriminator='pet_type')
    n: int

Discriminated Unions with callable `Discriminator`
API Documentation

[`pydantic.types.Discriminator`](../../api/types/#pydantic.types.Discriminator)

In the case of a `Union` with multiple models, sometimes there isn't a single uniform field
across all models that you can use as a discriminator.
This is the perfect use case for a callable `Discriminator`.

When you're designing callable discriminators, remember that you might have to account
for both `dict` and model type inputs. This pattern is similar to that of `mode='before'` validators,
where you have to anticipate various forms of input.

But wait! You ask, I only anticipate passing in `dict` types, why do I need to account for models?
Pydantic uses callable discriminators for serialization as well, at which point the input to your callable is
very likely to be a model instance.

In the following examples, you'll see that the callable discriminators are designed to handle both `dict` and model inputs.
If you don't follow this practice, it's likely that you'll, in the best case, get warnings during serialization,
and in the worst case, get runtime errors during validation.

Python 3.9 and abovePython 3.10 and above
