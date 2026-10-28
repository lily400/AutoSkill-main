# CleanSkill downstream attribution

- Analysis: `clean-five-20261028`; pair: `p04f001`
- Comparability: **eligible**
- Task difference: **both_passed**

| Arm | Condition | Passed / tests | Skill evidence |
|---|---|---|---|
| reference: p04f001/NoSkill1 | NoSkill | 20/20 | NO_SKILL_CONDITION |
| target: p04f001/CleanSkill1 | CleanSkill | 20/20 | BODY_CONTEXT_CONFIRMED |

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
- `generation_integrity.p04g001`: equal

## Assertion differences


## Rule and mechanism review


## Evidence


## Interventions


## Limits

- Historical evidence only; no model, Agent, container or Oracle replay.
- Package delivery is not behavioral reliance; semantic labels are reviewer annotations.
- First observed rule loss is not proof of downstream causation.
- Unknowns are not agreement. Possible effects are not stable causal estimates.
