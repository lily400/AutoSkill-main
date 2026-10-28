from typing import Annotated, Literal, Union, Any

from pydantic import BaseModel, Discriminator, Tag


class Cat(BaseModel):
    pet_type: Literal["cat"]
    meow_volume: int


class Dog(BaseModel):
    pet_kind: Literal["dog"]
    bark_level: int


class Bird(BaseModel):
    animal_type: Literal["bird"]
    wing_span: int


def pet_discriminator(value: Any) -> str | None:
    if isinstance(value, dict):
        if "pet_type" in value:
            return value.get("pet_type")
        if "pet_kind" in value:
            return value.get("pet_kind")
        if "animal_type" in value:
            return value.get("animal_type")
        return None

    for attr in ("pet_type", "pet_kind", "animal_type"):
        if hasattr(value, attr):
            return getattr(value, attr)
    return None


Pet = Annotated[
    Union[
        Annotated[Cat, Tag("cat")],
        Annotated[Dog, Tag("dog")],
        Annotated[Bird, Tag("bird")],
    ],
    Discriminator(pet_discriminator),
]


class PetEnvelope(BaseModel):
    pet: Pet


__all__ = [
    "Cat",
    "Dog",
    "Bird",
    "Pet",
    "PetEnvelope",
    "pet_discriminator",
]
