from typing import Annotated, Union, Literal, Any
from pydantic import BaseModel, Discriminator, Tag

class Cat(BaseModel):
    pet_type: Literal['cat']
    meow_volume: int

class Dog(BaseModel):
    pet_kind: Literal['dog']
    bark_level: int

class Bird(BaseModel):
    animal_type: Literal['bird']
    wing_span: int

def pet_discriminator(value: Any):
    for key in ('pet_type', 'pet_kind', 'animal_type'):
        result = value.get(key) if isinstance(value, dict) else getattr(value, key, None)
        if result is not None:
            return result
    return None

Pet = Annotated[Union[Annotated[Cat, Tag('cat')], Annotated[Dog, Tag('dog')], Annotated[Bird, Tag('bird')]], Discriminator(pet_discriminator)]

class PetEnvelope(BaseModel):
    pet: Pet
