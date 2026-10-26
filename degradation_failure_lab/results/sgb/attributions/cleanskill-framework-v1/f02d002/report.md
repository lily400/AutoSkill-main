# CleanSkill downstream attribution

- Analysis: `f02d002-attribution-v1`; pair: `f02d002-pair-1`
- Comparability: **eligible**
- Task difference: **both_failed**

| Arm | Condition | Passed / tests | Skill evidence |
|---|---|---|---|
| reference: f02d002/NoSkill1 | NoSkill | 1/9 | NO_SKILL_CONDITION |
| target: f02d002/CleanSkill1 | CleanSkill | 1/9 | INDEX_ONLY_OBSERVED |

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
- `generation_integrity.f02a001`: equal

## Assertion differences

- `test_cl_case[1-case0]`: failed → failed (both_failed)
- `test_cl_case[3-case2]`: failed → failed (both_failed)
- `test_cl_case[4-case3]`: failed → failed (both_failed)
- `test_cl_case[5-case4]`: failed → failed (both_failed)
- `test_cl_case[6-case5]`: failed → failed (both_failed)
- `test_cl_case[7-case6]`: failed → failed (both_failed)
- `test_cl_case[8-case7]`: failed → failed (both_failed)
- `test_cl_case[9-case8]`: failed → failed (both_failed)

## Rule and mechanism review

- `fla.coordinator-identity.BRO` (f02a001): BRO 是协调者；内部路由与报告应交给 BRO。; first observed loss = draft; review = provisional
  - source: preserved — BRO 是协调者；内部路由与报告应交给 BRO。
  - window: preserved — 选中窗口保留目标命题。
  - support: preserved — 候选证据摘录仍保留目标命题。
  - draft: omitted — 泛化为角色分工说明，未给出具体 BRO 映射。
  - spec: omitted — 延续泛化描述，未恢复 BRO 映射。
  - registered: omitted — 延续泛化描述，未恢复 BRO 映射。
  - skill: omitted — 该最终正文未包含具体 BRO 角色映射。
  - target: rule context before action = None; behavioral use = UNKNOWN; 正文无 BRO 命题，不能声称 Agent 已读到且未遵循 BRO。
- [observed; preservation] BRO 在 support 中保留、在角色参考 draft 中遗漏；后续未恢复。 (reviewer: codex-offline-audit; pending human review; evidence: BRO-source, BRO-window, BRO-support, BRO-draft, BRO-spec, BRO-registered, BRO-skill)
- [inferred; preservation] 该最终正文缺少 BRO 映射，限制了 Agent 仅从此正文恢复具体协调者身份的信息来源。 (reviewer: codex-offline-audit; pending human review; evidence: BRO-source, BRO-draft, BRO-skill)
- [hypothesis; causal] 补回有源支持的 BRO 映射可能改善协调者判断；当前结果不能证明 Skill 诱发额外失败。 (reviewer: codex-offline-audit; pending human review; evidence: BRO-source, BRO-draft, BRO-skill)

## Evidence

- `BRO-source`: `runs/gen/sgb/case002_fla/clean/f02a001/inputs/input001/context.md` {'kind': 'lines', 'value': [18, 51, 75], 'coordinate_space': 'generation_input'}; sha256 `1e92d08ba8d88c578e7008a1a0775427086533292de10612028bd2e1271520ed`; verified
- `BRO-window`: `runs/gen/sgb/case002_fla/clean/f02a001/SkillBank/.runtime/intermediate_runs/20261025T211242_7bbc7943/ingest/result.json` {'kind': 'json_pointer', 'value': '/windows/1', 'coordinate_space': 'normalized_text'}; sha256 `16813311d763ae6819cfe7fa219587633562c7c92455fa63e8a67ed83ff65950`; verified
- `BRO-support`: `runs/gen/sgb/case002_fla/clean/f02a001/SkillBank/.runtime/intermediate_runs/20261025T211242_7bbc7943/extract/windows/38c3c99f-fdbf-5684-955c-ed296075f457/667d218b-0b51-5445-88ff-c3116e891f78.json` {'kind': 'json_pointer', 'value': '/supports/1', 'coordinate_space': 'normalized_text'}; sha256 `7e1641fbd9c8d65761d8ab06aac0b099f8ac863d94775a0a5432a2b2cb7e584d`; verified
- `BRO-draft`: `runs/gen/sgb/case002_fla/clean/f02a001/SkillBank/.runtime/intermediate_runs/20261025T211242_7bbc7943/extract/windows/38c3c99f-fdbf-5684-955c-ed296075f457/667d218b-0b51-5445-88ff-c3116e891f78.json` {'kind': 'json_pointer', 'value': '/skill_drafts/1', 'coordinate_space': 'artifact'}; sha256 `7e1641fbd9c8d65761d8ab06aac0b099f8ac863d94775a0a5432a2b2cb7e584d`; verified
- `BRO-spec`: `runs/gen/sgb/case002_fla/clean/f02a001/SkillBank/.runtime/intermediate_runs/20261025T211242_7bbc7943/compile/result.json` {'kind': 'json_pointer', 'value': '/skill_specs/1', 'coordinate_space': 'artifact'}; sha256 `3a26308bed11e31739389e6b2f9184f231eb7552d867363f69e36953214132d7`; verified
- `BRO-registered`: `runs/gen/sgb/case002_fla/clean/f02a001/SkillBank/.runtime/intermediate_runs/20261025T211242_7bbc7943/register/result.json` {'kind': 'json_pointer', 'value': '/skill_specs/0', 'coordinate_space': 'artifact'}; sha256 `ecea75ac6470a0c7fee405e1298163b0c814233e1e42e5ef2a9009051381c39d`; verified
- `BRO-skill`: `runs/gen/sgb/case002_fla/clean/f02a001/SkillBank/Users/docskill/多智能体协作链路认知参考/SKILL.md` {'kind': 'file', 'value': None, 'coordinate_space': 'skill_body'}; sha256 `556c411b7162672109901a51f35042f1e6616da868feabec39df774415f970d7`; verified

## Interventions

- `BRO-skill-repair` v1: planned; 只补回 BRO 协调者映射；比较 recipient 相关断言，不承诺整体通过。

## Limits

- Historical evidence only; no model, Agent, container or Oracle replay.
- Package delivery is not behavioral reliance; semantic labels are reviewer annotations.
- First observed rule loss is not proof of downstream causation.
- Unknowns are not agreement. Possible effects are not stable causal estimates.
