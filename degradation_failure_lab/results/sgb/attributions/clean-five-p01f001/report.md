# CleanSkill downstream attribution

- Analysis: `clean-five-20261028`; pair: `p01f001`
- Comparability: **eligible**
- Task difference: **both_failed**

| Arm | Condition | Passed / tests | Skill evidence |
|---|---|---|---|
| reference: p01f001/NoSkill1 | NoSkill | 5/16 | NO_SKILL_CONDITION |
| target: p01f001/CleanSkill1 | CleanSkill | 7/16 | BODY_CONTEXT_CONFIRMED |

## Pair qualification

- `task_id`: equal
- `task_checksum`: equal
- `task_assets`: equal
- `model`: equal
- `budget`: equal
- `agent_info`: equal
- `agent_code`: equal
- `runtime_versions`: equal
- `agent_image`: equal
- `runtime`: equal
- `extra_instruction_hashes`: equal
- `configuration`: equal
- `oracle_hash`: equal
- `assertion_set`: equal
- `frozen_run_identity`: equal
- `treatment`: equal
- `clean_document_condition`: equal
- `associated_generator`: equal
- `reference.execution`: equal
- `target.execution`: equal
- `generation_integrity.p01g001`: equal

## Assertion differences

- `test_input_10_produces_output_30`: failed → failed (both_failed)
- `test_log_is_structured_and_nontrivial`: failed → passed (possible_help)
- `test_multiple_inputs[-5-0]`: failed → failed (both_failed)
- `test_multiple_inputs[0-10]`: failed → passed (possible_help)
- `test_multiple_inputs[10-30]`: failed → failed (both_failed)
- `test_multiple_inputs[12-34]`: failed → failed (both_failed)
- `test_multiple_inputs[3-16]`: failed → failed (both_failed)
- `test_multiple_inputs[5-20]`: failed → failed (both_failed)
- `test_not_hardcoded_for_single_value`: failed → failed (both_failed)
- `test_order_matches_documented_pipeline_semantics`: failed → failed (both_failed)
- `test_wrap_sees_raw_input`: failed → failed (both_failed)

## Rule and mechanism review


## Evidence


## Interventions


## Limits

- Historical evidence only; no model, Agent, container or Oracle replay.
- Package delivery is not behavioral reliance; semantic labels are reviewer annotations.
- First observed rule loss is not proof of downstream causation.
- Unknowns are not agreement. Possible effects are not stable causal estimates.
