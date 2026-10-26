# CleanSkill downstream attribution

- Analysis: `cross-protocol-rejection-v1`; pair: `cross-protocol`
- Comparability: **ineligible**
- Task difference: **unresolved**

| Arm | Condition | Passed / tests | Skill evidence |
|---|---|---|---|
| reference: s24p002/NoSkill1 | NoSkill | 13/19 | NO_SKILL_CONDITION |
| target: s24u002/CleanSkill1 | CleanSkill | 19/19 | BODY_CONTEXT_CONFIRMED |

## Pair qualification

- `task_id`: equal
- `task_checksum`: equal
- `task_assets`: equal
- `model`: equal
- `budget`: equal
- `agent_info`: equal
- `agent_code`: different
- `runtime_versions`: equal
- `agent_image`: equal
- `runtime`: equal
- `extra_instruction_hashes`: different
- `configuration`: different
- `oracle_hash`: equal
- `assertion_set`: equal
- `frozen_run_identity`: equal
- `treatment`: equal
- `clean_document_condition`: equal
- `associated_generator`: equal
- `reference.execution`: equal
- `target.execution`: equal
- `generation_integrity.s24a001`: equal

## Assertion differences

- `test_file_exists`: passed → passed (unresolved)
- `test_file_not_empty`: passed → passed (unresolved)
- `test_has_callable_target`: passed → passed (unresolved)
- `test_has_module_doc_or_comments`: passed → passed (unresolved)
- `test_rejects_empty_string`: passed → passed (unresolved)
- `test_rejects_non_string`: passed → passed (unresolved)
- `test_supported_backends[/tmp/export.json-False]`: failed → passed (unresolved)
- `test_supported_backends[file:///tmp/export.csv-False]`: failed → passed (unresolved)
- `test_supported_backends[file:///tmp/export.json-False]`: failed → passed (unresolved)
- `test_supported_backends[ftp://server/export.json-True]`: failed → passed (unresolved)
- `test_supported_backends[gs://bucket/export.json-True]`: failed → passed (unresolved)
- `test_supported_backends[s3://bucket/export.json-True]`: failed → passed (unresolved)
- `test_supported_backends[stdout:-False]`: passed → passed (unresolved)
- `test_unsupported_schemes_raise[ftps://secure-server/export.json]`: passed → passed (unresolved)
- `test_unsupported_schemes_raise[http://example.com/export.json]`: passed → passed (unresolved)
- `test_unsupported_schemes_raise[https://example.com/export.json]`: passed → passed (unresolved)
- `test_unsupported_schemes_raise[mysql://db/export.json]`: passed → passed (unresolved)
- `test_unsupported_schemes_raise[stderr:]`: passed → passed (unresolved)
- `test_unsupported_schemes_raise[unknown://somewhere/file]`: passed → passed (unresolved)

## Rule and mechanism review


## Evidence


## Interventions


## Limits

- Historical evidence only; no model, Agent, container or Oracle replay.
- Package delivery is not behavioral reliance; semantic labels are reviewer annotations.
- First observed rule loss is not proof of downstream causation.
- Unknowns are not agreement. Possible effects are not stable causal estimates.
