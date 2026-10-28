# Validator Ordering in Annotated Types

This is a basic calibration task.

Create a Pydantic model class named `MyModel` with a single field `value` that uses
`typing.Annotated` together with `BeforeValidator`, `WrapValidator`, and `AfterValidator`.

## Requirements

Your implementation must:

1. Define a class named `MyModel`.
2. Define a field named `value` using `Annotated[...]` metadata, not decorator-based field validators.
3. Use all three validator kinds on that one field:
   - `BeforeValidator`
   - `WrapValidator`
   - `AfterValidator`
4. Implement the affine transform `value_out = 2 * value_in + 10`.
   - This implies input `10` becomes output `30`.
5. Expose validator execution order through a structured log:
   - either `instance.validation_log`
   - or a module-level list named `VALIDATION_LOG`
6. The log must make it possible to verify:
   - wrap starts first and sees raw input
   - before runs before inner validation
   - after runs after inner validation
   - wrap resumes after the handler returns
7. The implementation must follow the documented ordering for Annotated validators in Pydantic.
8. Do not hardcode special handling for input 10.

## Structured log format

Use a list of dict entries (preferred), e.g.

```python
{
  "event": "wrap_start" | "before" | "wrap_end" | "after",
  "value": <number>,
}
```

Minimum expectations:

- The first wrap entry must record the raw input (e.g. `value=10` for input 10).
- The log must contain at least one wrap-start entry and one wrap-end/resume entry.

## Output

Create a file called `agent_output.py`.
## Runtime Interface

- Inputs directory: /workspace/input
- Documentation context directory: /workspace/docs
- Skill assets directory: /workspace/skill
- Final submission file: /workspace/agent_output.py
- Tests run from /workspace/tests/test.sh with TEST_ROOT_DIR=/workspace.
