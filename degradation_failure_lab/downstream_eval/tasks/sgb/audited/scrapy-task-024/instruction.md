# Feed Export Default Overwrite Behavior

This is a basic calibration task.

Implement Scrapy feed export default overwrite resolution for built-in storage backends.

Create `agent_output.py` with a function:

    default_feed_overwrite(uri: str) -> bool

The function must determine Scrapy’s default `overwrite` behavior for the given feed URI, based on Scrapy’s built-in feed storage backends.

## Requirements

1. Correctly parse the URI scheme.
2. Match Scrapy built-in behavior for these cases:
   - local filesystem via `file:///tmp/export.json`
   - local filesystem via absolute path `/tmp/export.json`
   - `ftp://server/export.json`
   - `s3://bucket/export.json`
   - `gs://bucket/export.json`
   - `stdout:`
3. Return the built-in default overwrite behavior for each supported backend.
   - The expected defaults are defined in Scrapy's feed exports documentation (see the task's `docs/` folder).
4. Reject unsupported schemes by raising `ValueError`.
5. Include a brief module-level explanation or docstring describing the behavior of each supported backend.

## Notes

- Base your implementation on Scrapy built-in feed export storage behavior, not on generic URI conventions.
- Do not add custom backend assumptions for `http`, `https`, `ftps`, `stderr`, or other unsupported schemes.
- Treat an absolute local path like `/tmp/export.json` as a local filesystem feed URI (equivalent backend to `file:///tmp/export.json`).
## Runtime Interface

- Inputs directory: /workspace/input
- Documentation context directory: /workspace/docs
- Skill assets directory: /workspace/skill
- Final submission file: /workspace/agent_output.py
- Tests run from /workspace/tests/test.sh with TEST_ROOT_DIR=/workspace.
