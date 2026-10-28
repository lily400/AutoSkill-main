# CleanSkill downstream attribution

- Analysis: `capacity006-final-20261028`; pair: `capacity006-e06f003`
- Comparability: **eligible**
- Task difference: **both_failed**

| Arm | Condition | Passed / tests | Skill evidence |
|---|---|---|---|
| reference: e06f003/NoSkill1 | NoSkill | 1/8 | NO_SKILL_CONDITION |
| target: e06f003/CleanSkill1 | CleanSkill | 1/8 | BODY_CONTEXT_CONFIRMED |

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
- `generation_integrity.e06r002`: equal

## Assertion differences

- `test_cl_case[1-case0]`: failed → failed (both_failed)
- `test_cl_case[3-case2]`: failed → failed (both_failed)
- `test_cl_case[4-case3]`: failed → failed (both_failed)
- `test_cl_case[5-case4]`: failed → failed (both_failed)
- `test_cl_case[6-case5]`: failed → failed (both_failed)
- `test_cl_case[7-case6]`: failed → failed (both_failed)
- `test_cl_case[8-case7]`: failed → failed (both_failed)

## Rule and mechanism review


## Evidence


## Interventions


## Limits

- Historical evidence only; no model, Agent, container or Oracle replay.
- Package delivery is not behavioral reliance; semantic labels are reviewer annotations.
- First observed rule loss is not proof of downstream causation.
- Unknowns are not agreement. Possible effects are not stable causal estimates.
