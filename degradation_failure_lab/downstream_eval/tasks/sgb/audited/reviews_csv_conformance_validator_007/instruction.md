# reviews_csv_conformance_validator_007

## Task Type

validation_tool

## Task

Implement `solve(input_data)` that acts as a **Processed Reviews CSV Conformance Validator with Casing Enforcement**.

INPUT: a dict with keys:
- `csv_text`: string — the full processed reviews CSV content including header row.

OUTPUT: a dict with keys:
- `ok`: bool — whether the CSV conforms to the SOP.
- `message`: string — if `ok` is true, a short success message; if `ok` is false, an SOP-compliant ERROR message.
- `details`: dict — machine-readable diagnostics with keys:
  - `row_count`: int
  - `missing_columns`: list[str]
  - `invalid_values`: list[dict] (each dict includes `row` (1-based data row index), `column`, `value`)

RULES (from the SOP):
- The CSV must be parseable and contain all required columns for processed reviews.
- The classification columns must contain only the allowed lowercase values (no normalization; casing violations are errors).
- The CSV must contain at least the minimum number of rows required for meaningful analysis.
- If any rule fails, return the exact SOP ERROR template for processed reviews, with a single specific Issue string describing the first detected problem.
- If multiple problems exist, precedence is: missing required column(s) first, then invalid classification value(s), then insufficient row count.
- The Issue string must match SOP examples in style, including calling out lowercase requirements when casing is wrong.

## Expected Output Summary

```json
{
  "format": "dict",
  "key_results": {
    "ok": "bool",
    "message": "string",
    "details": "dict"
  }
}
```

## Runtime Interface

- Documentation context directory: /workspace/docs
- Skill assets directory: /workspace/skill
- Final submission file: /workspace/agent_output.py
- The submission must define solve(input_data).
- Tests will call solve(input_data) directly for each bundled test case.
- Tests run from /workspace/tests/test.sh with TEST_ROOT_DIR=/workspace.
