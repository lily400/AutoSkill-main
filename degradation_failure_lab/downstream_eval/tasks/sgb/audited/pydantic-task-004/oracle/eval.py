"""Test cases for pydantic_task_004: Nested Discriminator with Different Field Names

This test file supports both local testing and Docker testing via the TEST_ROOT_DIR
environment variable. By default, it uses /root (Docker mode).

Local testing:
    TEST_ROOT_DIR=/path/to/solution pytest tests/eval.py

Docker testing:
    pytest tests/eval.py
"""

import ast
import os
import sys
from typing import get_args, get_origin

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

# Support both local and Docker testing
ROOT_DIR = os.getenv("TEST_ROOT_DIR", "/root")
OUTPUT_FILE = os.path.join(ROOT_DIR, "agent_output.py")

# Import the agent's solution
sys.path.insert(0, ROOT_DIR)
import agent_output


def _read_source():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def _pet_adapter():
    return TypeAdapter(agent_output.Pet)


class TestNestedDiscriminatorDifferentFieldNames:
    """Test discriminated union with different discriminator field names."""

    def test_required_exports_exist(self):
        """Required symbols should be exported."""
        required = ["Cat", "Dog", "Bird", "Pet", "PetEnvelope", "pet_discriminator"]
        for name in required:
            assert hasattr(agent_output, name), f"Missing required export: {name}"

    def test_models_are_pydantic_models(self):
        """Cat/Dog/Bird/PetEnvelope should be BaseModel subclasses."""
        assert issubclass(agent_output.Cat, BaseModel)
        assert issubclass(agent_output.Dog, BaseModel)
        assert issubclass(agent_output.Bird, BaseModel)
        assert issubclass(agent_output.PetEnvelope, BaseModel)

    def test_source_mentions_annotated_discriminator_and_tag(self):
        """Implementation should use Pydantic's documented discriminated-union constructs."""
        source = _read_source()
        assert "Annotated" in source, "Expected use of typing.Annotated"
        assert "Discriminator" in source, "Expected use of pydantic.Discriminator"
        assert "Tag" in source, "Expected use of pydantic.Tag"

    def test_source_defines_named_discriminator_function(self):
        """Implementation should define a callable discriminator function named pet_discriminator."""
        source = _read_source()
        tree = ast.parse(source)

        function_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        assert "pet_discriminator" in function_names, "Expected a function named pet_discriminator"
        assert callable(agent_output.pet_discriminator)

    def test_dict_input_cat_validates_correctly_direct_union(self):
        """Direct union validation should accept Cat dict input."""
        data = {"pet_type": "cat", "meow_volume": 5}
        result = _pet_adapter().validate_python(data)

        assert isinstance(result, agent_output.Cat)
        assert result.pet_type == "cat"
        assert result.meow_volume == 5

    def test_dict_input_dog_validates_correctly_direct_union(self):
        """Direct union validation should accept Dog dict input."""
        data = {"pet_kind": "dog", "bark_level": 8}
        result = _pet_adapter().validate_python(data)

        assert isinstance(result, agent_output.Dog)
        assert result.pet_kind == "dog"
        assert result.bark_level == 8

    def test_dict_input_bird_validates_correctly_direct_union(self):
        """Direct union validation should accept Bird dict input."""
        data = {"animal_type": "bird", "wing_span": 12}
        result = _pet_adapter().validate_python(data)

        assert isinstance(result, agent_output.Bird)
        assert result.animal_type == "bird"
        assert result.wing_span == 12

    def test_nested_container_validation_cat(self):
        """Nested container model should validate Cat correctly."""
        data = {"pet": {"pet_type": "cat", "meow_volume": 3}}
        result = agent_output.PetEnvelope.model_validate(data)

        assert isinstance(result.pet, agent_output.Cat)
        assert result.pet.pet_type == "cat"
        assert result.pet.meow_volume == 3

    def test_nested_container_validation_dog(self):
        """Nested container model should validate Dog correctly."""
        data = {"pet": {"pet_kind": "dog", "bark_level": 7}}
        result = agent_output.PetEnvelope.model_validate(data)

        assert isinstance(result.pet, agent_output.Dog)
        assert result.pet.pet_kind == "dog"
        assert result.pet.bark_level == 7

    def test_nested_container_validation_bird(self):
        """Nested container model should validate Bird correctly."""
        data = {"pet": {"animal_type": "bird", "wing_span": 10}}
        result = agent_output.PetEnvelope.model_validate(data)

        assert isinstance(result.pet, agent_output.Bird)
        assert result.pet.animal_type == "bird"
        assert result.pet.wing_span == 10

    def test_discriminator_handles_dict_inputs(self):
        """pet_discriminator should extract the tag from all supported dict field names."""
        fn = agent_output.pet_discriminator

        assert fn({"pet_type": "cat", "meow_volume": 1}) == "cat"
        assert fn({"pet_kind": "dog", "bark_level": 2}) == "dog"
        assert fn({"animal_type": "bird", "wing_span": 3}) == "bird"
        assert fn({"unknown": "value"}) is None

    def test_discriminator_handles_model_instances(self):
        """pet_discriminator should extract the tag from model instances, not only dicts."""
        fn = agent_output.pet_discriminator

        cat = agent_output.Cat(pet_type="cat", meow_volume=4)
        dog = agent_output.Dog(pet_kind="dog", bark_level=5)
        bird = agent_output.Bird(animal_type="bird", wing_span=6)

        assert fn(cat) == "cat"
        assert fn(dog) == "dog"
        assert fn(bird) == "bird"

    def test_union_accepts_model_instances(self):
        """Direct union validation should also accept already-created model instances."""
        adapter = _pet_adapter()

        cat = agent_output.Cat(pet_type="cat", meow_volume=9)
        dog = agent_output.Dog(pet_kind="dog", bark_level=10)
        bird = agent_output.Bird(animal_type="bird", wing_span=11)

        cat2 = adapter.validate_python(cat)
        dog2 = adapter.validate_python(dog)
        bird2 = adapter.validate_python(bird)

        assert isinstance(cat2, agent_output.Cat)
        assert isinstance(dog2, agent_output.Dog)
        assert isinstance(bird2, agent_output.Bird)

        assert cat2.meow_volume == 9
        assert dog2.bark_level == 10
        assert bird2.wing_span == 11

    def test_serialization_preserves_original_field_names(self):
        """Serialization must preserve each model's original discriminator field name."""
        cat = _pet_adapter().validate_python({"pet_type": "cat", "meow_volume": 3})
        dog = _pet_adapter().validate_python({"pet_kind": "dog", "bark_level": 7})
        bird = _pet_adapter().validate_python({"animal_type": "bird", "wing_span": 10})

        cat_dump = cat.model_dump()
        dog_dump = dog.model_dump()
        bird_dump = bird.model_dump()

        assert cat_dump == {"pet_type": "cat", "meow_volume": 3}
        assert dog_dump == {"pet_kind": "dog", "bark_level": 7}
        assert bird_dump == {"animal_type": "bird", "wing_span": 10}

    def test_nested_serialization_preserves_original_field_names(self):
        """Nested container serialization should also preserve original field names."""
        env_cat = agent_output.PetEnvelope.model_validate(
            {"pet": {"pet_type": "cat", "meow_volume": 2}}
        )
        env_dog = agent_output.PetEnvelope.model_validate(
            {"pet": {"pet_kind": "dog", "bark_level": 4}}
        )
        env_bird = agent_output.PetEnvelope.model_validate(
            {"pet": {"animal_type": "bird", "wing_span": 8}}
        )

        assert env_cat.model_dump() == {"pet": {"pet_type": "cat", "meow_volume": 2}}
        assert env_dog.model_dump() == {"pet": {"pet_kind": "dog", "bark_level": 4}}
        assert env_bird.model_dump() == {"pet": {"animal_type": "bird", "wing_span": 8}}

    def test_missing_discriminator_field_raises_validation_error(self):
        """Input with no supported discriminator field should fail."""
        with pytest.raises(ValidationError) as exc_info:
            _pet_adapter().validate_python({"some_field": "value"})

        errors = exc_info.value.errors()
        assert errors, "Expected structured validation errors"
        assert any(
            err.get("type", "").startswith("union_tag")
            or "discriminator" in err.get("msg", "").lower()
            or "tag" in err.get("msg", "").lower()
            for err in errors
        )

    def test_unknown_discriminator_value_raises_validation_error(self):
        """Known discriminator field with unknown value should fail."""
        with pytest.raises(ValidationError) as exc_info:
            _pet_adapter().validate_python({"pet_type": "lizard", "scale_count": 10})

        errors = exc_info.value.errors()
        assert errors
        assert any(
            err.get("type", "").startswith("union_tag")
            or "discriminator" in err.get("msg", "").lower()
            or "tag" in err.get("msg", "").lower()
            for err in errors
        )

    def test_wrong_field_name_for_variant_does_not_validate(self):
        """Using the wrong discriminator field name for a variant should fail."""
        with pytest.raises(ValidationError):
            _pet_adapter().validate_python({"pet_type": "dog", "bark_level": 8})

        with pytest.raises(ValidationError):
            _pet_adapter().validate_python({"pet_kind": "bird", "wing_span": 9})

        with pytest.raises(ValidationError):
            _pet_adapter().validate_python({"animal_type": "cat", "meow_volume": 5})

    def test_each_model_uses_expected_discriminator_field_name(self):
        """Each model should expose only its own intended discriminator field."""
        cat_fields = set(agent_output.Cat.model_fields.keys())
        dog_fields = set(agent_output.Dog.model_fields.keys())
        bird_fields = set(agent_output.Bird.model_fields.keys())

        assert "pet_type" in cat_fields
        assert "pet_kind" not in cat_fields
        assert "animal_type" not in cat_fields

        assert "pet_kind" in dog_fields
        assert "pet_type" not in dog_fields
        assert "animal_type" not in dog_fields

        assert "animal_type" in bird_fields
        assert "pet_type" not in bird_fields
        assert "pet_kind" not in bird_fields

    def test_literal_values_are_correct(self):
        """Each discriminator field should enforce the intended literal value."""
        with pytest.raises(ValidationError):
            agent_output.Cat(pet_type="dog", meow_volume=1)

        with pytest.raises(ValidationError):
            agent_output.Dog(pet_kind="cat", bark_level=1)

        with pytest.raises(ValidationError):
            agent_output.Bird(animal_type="dog", wing_span=1)