# Nested Discriminator with Different Field Names

Implement a discriminated union in Pydantic v2 where three models use different discriminator field names, and the union is validated inside a nested container model.

Requirements:

1. Define three models:
   - `Cat` with fields:
     - `pet_type: Literal["cat"]`
     - `meow_volume: int`
   - `Dog` with fields:
     - `pet_kind: Literal["dog"]`
     - `bark_level: int`
   - `Bird` with fields:
     - `animal_type: Literal["bird"]`
     - `wing_span: int`

2. Define a callable discriminator function named `pet_discriminator` that:
   - accepts either a `dict` or a model instance
   - extracts the discriminator value from exactly one of:
     - `pet_type`
     - `pet_kind`
     - `animal_type`
   - returns the correct tag value (`"cat"`, `"dog"`, `"bird"`) or `None` when no discriminator can be found

3. Define `Pet` as a discriminated union using:
   - `Annotated[...]`
   - `Tag(...)` on each variant
   - `Discriminator(pet_discriminator)`

4. Define a nested container model:
   - `class PetEnvelope(BaseModel):`
   - field: `pet: Pet`

5. Validation must work for:
   - nested dict input through `PetEnvelope.model_validate(...)`
   - direct union validation through `TypeAdapter(Pet).validate_python(...)`
   - model-instance input passed back through the union validator

6. Serialization must preserve the original discriminator field names:
   - `Cat` serializes with `pet_type`
   - `Dog` serializes with `pet_kind`
   - `Bird` serializes with `animal_type`

7. Export exactly these names from `agent_output.py`:
   - `Cat`
   - `Dog`
   - `Bird`
   - `Pet`
   - `PetEnvelope`
   - `pet_discriminator`

## Output

Create a file called `agent_output.py` with your implementation.
## Runtime Interface

- Inputs directory: /workspace/input
- Documentation context directory: /workspace/docs
- Skill assets directory: /workspace/skill
- Final submission file: /workspace/agent_output.py
- Tests run from /workspace/tests/test.sh with TEST_ROOT_DIR=/workspace.
