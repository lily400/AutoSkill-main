# CleanSkill downstream attribution

- Analysis: `s24p001-attribution-v1`; pair: `s24p001-pair-1`
- Comparability: **eligible**
- Task difference: **both_failed**

| Arm | Condition | Passed / tests | Skill evidence |
|---|---|---|---|
| reference: s24p001/NoSkill1 | NoSkill | 14/19 | NO_SKILL_CONDITION |
| target: s24p001/CleanSkill1 | CleanSkill | 12/19 | INDEX_ONLY_OBSERVED |

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
- `generation_integrity.s24a001`: equal

## Assertion differences

- `test_supported_backends[/tmp/export.json-False]`: failed → failed (both_failed)
- `test_supported_backends[file:///tmp/export.csv-False]`: failed → failed (both_failed)
- `test_supported_backends[file:///tmp/export.json-False]`: failed → failed (both_failed)
- `test_supported_backends[ftp://server/export.json-True]`: passed → failed (possible_harm)
- `test_supported_backends[gs://bucket/export.json-True]`: failed → failed (both_failed)
- `test_supported_backends[s3://bucket/export.json-True]`: failed → failed (both_failed)
- `test_supported_backends[stdout:-False]`: passed → failed (possible_harm)

## Rule and mechanism review

- `scrapy024.ftp-default-overwrite` (s24a001): FTP 后端的 overwrite 默认值为 True。; first observed loss = None; review = provisional
  - source: preserved — FTP 后端的 overwrite 默认值为 True。
  - window: preserved — 选中窗口保留目标命题。
  - support: preserved — 候选证据摘录仍保留目标命题。
  - draft: preserved — 草稿保留 FTP 默认 True。
  - spec: preserved — 保留 FTP 默认 True。
  - registered: preserved — 保留 FTP 默认 True。
  - skill: preserved — 最终正文第 35 行保留 FTP 默认 True。
  - target: rule context before action = None; behavioral use = UNKNOWN; 默认值断言不覆盖 APPE 或完整追加语义；读取不等于依赖。
- [observed; preservation] 目标 FTP 默认 True 命题保留至最终 Skill。 (reviewer: codex-offline-audit; pending human review; evidence: FTP-source, FTP-window, FTP-support, FTP-draft, FTP-spec, FTP-registered, FTP-skill)

## Evidence

- `FTP-source`: `runs/gen/sgb/case024_sgb/clean/s24a001/inputs/input001/feed-exports.md` {'kind': 'lines', 'value': [438, 439, 440, 441, 442, 443, 444, 445, 446], 'coordinate_space': 'generation_input'}; sha256 `a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d`; verified
- `FTP-window`: `runs/gen/sgb/case024_sgb/clean/s24a001/SkillBank/.runtime/intermediate_runs/20261025T211008_b6983176/ingest/result.json` {'kind': 'json_pointer', 'value': '/windows/17', 'coordinate_space': 'normalized_text'}; sha256 `918198fcb19b71555d060c9dc197348257f58171e71df73e3fab836ebde958c2`; verified
- `FTP-support`: `runs/gen/sgb/case024_sgb/clean/s24a001/SkillBank/.runtime/intermediate_runs/20261025T211008_b6983176/extract/windows/f7a76d82-16fa-5d4e-9e08-dcfb60e9f311/35c95315-785e-5f54-823a-cc6831e4cc4b.json` {'kind': 'json_pointer', 'value': '/supports/1', 'coordinate_space': 'normalized_text'}; sha256 `3f56d89bc4bfecf7357d8869d71fbd9d45e7bb5e7af07e685640bc526539af9f`; verified
- `FTP-draft`: `runs/gen/sgb/case024_sgb/clean/s24a001/SkillBank/.runtime/intermediate_runs/20261025T211008_b6983176/extract/windows/f7a76d82-16fa-5d4e-9e08-dcfb60e9f311/35c95315-785e-5f54-823a-cc6831e4cc4b.json` {'kind': 'json_pointer', 'value': '/skill_drafts/1', 'coordinate_space': 'artifact'}; sha256 `3f56d89bc4bfecf7357d8869d71fbd9d45e7bb5e7af07e685640bc526539af9f`; verified
- `FTP-spec`: `runs/gen/sgb/case024_sgb/clean/s24a001/SkillBank/.runtime/intermediate_runs/20261025T211008_b6983176/compile/result.json` {'kind': 'json_pointer', 'value': '/skill_specs/19', 'coordinate_space': 'artifact'}; sha256 `d1089bb713e56564f3aa122185626851a13ddcfba404517ffc2be1f74b41b3ad`; verified
- `FTP-registered`: `runs/gen/sgb/case024_sgb/clean/s24a001/SkillBank/.runtime/intermediate_runs/20261025T211008_b6983176/register/result.json` {'kind': 'json_pointer', 'value': '/skill_specs/11', 'coordinate_space': 'artifact'}; sha256 `98e51afdd0ff0c0d0504cef3b8b749b82712977eb5ff1504b46d4009981d048a`; verified
- `FTP-skill`: `runs/gen/sgb/case024_sgb/clean/s24a001/SkillBank/Users/docskill/feed-覆盖与追加策略选择/SKILL.md` {'kind': 'file', 'value': None, 'coordinate_space': 'skill_body'}; sha256 `c8814842c6bda55e4340547eb30e7896a016f34e249b9f910496861518538909`; verified

## Interventions


## Limits

- Historical evidence only; no model, Agent, container or Oracle replay.
- Package delivery is not behavioral reliance; semantic labels are reviewer annotations.
- First observed rule loss is not proof of downstream causation.
- Unknowns are not agreement. Possible effects are not stable causal estimates.
