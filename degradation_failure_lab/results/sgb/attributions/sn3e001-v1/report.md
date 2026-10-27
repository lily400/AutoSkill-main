# CleanSkill downstream attribution

- Analysis: `sn3e001-attribution-v1`; pair: `sn3e001-pair-1`
- Comparability: **eligible**
- Task difference: **possible_help**

| Arm | Condition | Passed / tests | Skill evidence |
|---|---|---|---|
| reference: sn3e001/NoSkill1 | NoSkill | 0/8 | NO_SKILL_CONDITION |
| target: sn3e001/CleanSkill1 | CleanSkill | 8/8 | FILE_ACCESSED_BODY_CONTEXT_NOT_FULLY_CONFIRMED |

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
- `generation_integrity.sn3r001`: equal

## Assertion differences

- `test_cl_case[1-case0]`: failed → passed (possible_help)
- `test_cl_case[2-case1]`: failed → passed (possible_help)
- `test_cl_case[3-case2]`: failed → passed (possible_help)
- `test_cl_case[4-case3]`: failed → passed (possible_help)
- `test_cl_case[5-case4]`: failed → passed (possible_help)
- `test_cl_case[6-case5]`: failed → passed (possible_help)
- `test_cl_case[7-case6]`: failed → passed (possible_help)
- `test_cl_case[8-case7]`: failed → passed (possible_help)

## Rule and mechanism review

- `sanctuary-objectives-4` (sn3r001): End condition 1 requires four supported Conservation objectives.; first observed loss = None; review = reviewed
  - source: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - window: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - support: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - draft: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - spec: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - registered: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - skill: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - target: rule context before action = True; behavioral use = UNKNOWN; Anchored code-writing action; delivery check concerns the retained excerpt only. Reading is not proof of reliance; task itself explicitly supplies scheduling structure.
- `sanctuary-trigger-10` (sn3r001): Triggering via condition 1 or 2 awards the triggering player 10 points.; first observed loss = None; review = reviewed
  - source: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - window: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - support: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - draft: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - spec: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - registered: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - skill: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - target: rule context before action = True; behavioral use = UNKNOWN; Anchored code-writing action; delivery check concerns the retained excerpt only. Reading is not proof of reliance; task itself explicitly supplies scheduling structure.
- `sanctuary-last-turn-5` (sn3r001): A different player meeting condition 1 or 2 on their final extra turn receives 5 points.; first observed loss = None; review = reviewed
  - source: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - window: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - support: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - draft: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - spec: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - registered: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - skill: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - target: rule context before action = True; behavioral use = UNKNOWN; Anchored code-writing action; delivery check concerns the retained excerpt only. Reading is not proof of reliance; task itself explicitly supplies scheduling structure.
- `sanctuary-extra-turns` (sn3r001): After a condition 1/2 trigger every other player gets exactly one further clockwise turn; condition 3 alone ends immediately.; first observed loss = None; review = reviewed
  - source: preserved — Compared source/adjacent artifacts: numerical value and role/timing condition retained. No claim of Agent reliance.
  - window: ambiguous — One-turn/exclusion/immediate-end clauses are explicit; full clockwise extra-turn ordering is not explicit at this anchor. Separate ordinary-turn Skills do not settle the full conjunction.
  - support: ambiguous — One-turn/exclusion/immediate-end clauses are explicit; full clockwise extra-turn ordering is not explicit at this anchor. Separate ordinary-turn Skills do not settle the full conjunction.
  - draft: ambiguous — One-turn/exclusion/immediate-end clauses are explicit; full clockwise extra-turn ordering is not explicit at this anchor. Separate ordinary-turn Skills do not settle the full conjunction.
  - spec: ambiguous — One-turn/exclusion/immediate-end clauses are explicit; full clockwise extra-turn ordering is not explicit at this anchor. Separate ordinary-turn Skills do not settle the full conjunction.
  - registered: ambiguous — One-turn/exclusion/immediate-end clauses are explicit; full clockwise extra-turn ordering is not explicit at this anchor. Separate ordinary-turn Skills do not settle the full conjunction.
  - skill: ambiguous — One-turn/exclusion/immediate-end clauses are explicit; full clockwise extra-turn ordering is not explicit at this anchor. Separate ordinary-turn Skills do not settle the full conjunction.
  - target: rule context before action = True; behavioral use = UNKNOWN; Anchored code-writing action; delivery check concerns the retained excerpt only. Reading is not proof of reliance; task itself explicitly supplies scheduling structure.
- [observed; preservation] The source-backed numeric rule, including role/timing, is present in the actual final Skill body. (reviewer: Codex assistant (source-grounded review; not independent human sign-off); evidence: E-SOURCE, E-WINDOW, E-SUPPORT, E-DRAFT, E-SPEC, E-REGISTERED, E-SKILL-1)
- [observed; preservation] The source-backed numeric rule, including role/timing, is present in the actual final Skill body. (reviewer: Codex assistant (source-grounded review; not independent human sign-off); evidence: E-SOURCE, E-WINDOW, E-SUPPORT, E-DRAFT, E-SPEC, E-REGISTERED, E-SKILL-2)
- [observed; preservation] The source-backed numeric rule, including role/timing, is present in the actual final Skill body. (reviewer: Codex assistant (source-grounded review; not independent human sign-off); evidence: E-SOURCE, E-WINDOW, E-SUPPORT, E-DRAFT, E-SPEC, E-REGISTERED, E-SKILL-3)
- [observed; behavior] NoSkill submitted objective threshold 1 and marker values 2/1; CleanSkill submitted threshold 4 and markers 10/5. Original Oracle results are 0/8 versus 8/8 in this pair. (reviewer: Codex assistant (source-grounded review; not independent human sign-off); evidence: E-CODE-NoSkill1, E-CODE-CleanSkill1, E-SCORE-NoSkill1, E-SCORE-CleanSkill1)
- [hypothesis; causal] The delivered numeric rules may explain the improvement, conditional on eligible pairing and pre-action excerpt delivery. This is a single-pair mechanism hypothesis, not a verified causal or stable-success conclusion. (reviewer: Codex assistant (source-grounded review; not independent human sign-off); evidence: E-SKILL-1, E-SKILL-2, E-SKILL-3, E-CODE-NoSkill1, E-CODE-CleanSkill1)

## Evidence

- `E-SOURCE`: `data/raw_sources/sgb/5a8bd61d/7cfb819b60252946/context.md` {'kind': 'lines', 'value': [38, 94, 95], 'coordinate_space': 'original_source'}; sha256 `7cfb819b60252946ec058d5430460b8795e93b4670381cd89efaf3d45ab66b0c`; verified
- `E-WINDOW`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/.runtime/intermediate_runs/20261026T230744_1cab6017/ingest/result.json` {'kind': 'json_pointer', 'value': '/windows/3', 'coordinate_space': 'artifact'}; sha256 `78006b7dc4ea58e3a31b09c8581935479b8be19658446e8faa8a67f720b59c40`; verified
- `E-SUPPORT`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/.runtime/intermediate_runs/20261026T230744_1cab6017/compile/result.json` {'kind': 'json_pointer', 'value': '/support_records/7', 'coordinate_space': 'artifact'}; sha256 `027097a0015471ea299ca75722ccfaebf379ed41140ebd85c962354a9723ee5b`; verified
- `E-DRAFT`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/.runtime/intermediate_runs/20261026T230744_1cab6017/extract/result.json` {'kind': 'json_pointer', 'value': '/skill_drafts/24', 'coordinate_space': 'artifact'}; sha256 `ff5fe1a5c036cb656645995e537db9b40374796aa93bf08b9a4e6c30937af563`; verified
- `E-SPEC`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/.runtime/intermediate_runs/20261026T230744_1cab6017/compile/result.json` {'kind': 'json_pointer', 'value': '/skill_specs/7', 'coordinate_space': 'artifact'}; sha256 `027097a0015471ea299ca75722ccfaebf379ed41140ebd85c962354a9723ee5b`; verified
- `E-REGISTERED`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/.runtime/document_registry/skills/12088cea-5a72-5997-94e9-56794cb7b6dd.json` {'kind': 'json_pointer', 'value': '', 'coordinate_space': 'artifact'}; sha256 `ffa2ec3ff36ac374d359045e8b9951e8b96e6023154062f9bd6c6aa138d0db98`; verified
- `E-CODE-NoSkill1`: `runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/trials/audit-noskill1/submission-export/agent_output.py` {'kind': 'file', 'value': None, 'coordinate_space': 'artifact'}; sha256 `1382deee94edc043e4e75208aecddae093d5f61142fb0331c9b7c6a6cb0937cc`; verified
- `E-SCORE-NoSkill1`: `runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/outcomes/NoSkill1/result.json` {'kind': 'json_pointer', 'value': '/oracle/task_result', 'coordinate_space': 'artifact'}; sha256 `356d3d9f9511e65fe3da675a5f08def0f6a7c693b26a7ff657058f58cbf2f98a`; verified
- `E-CODE-CleanSkill1`: `runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/trials/audit-cleanskill1/submission-export/agent_output.py` {'kind': 'file', 'value': None, 'coordinate_space': 'artifact'}; sha256 `a5917ac47a324801a823ba9d7049c516d5972338891e6763809b98087dcdaaf8`; verified
- `E-SCORE-CleanSkill1`: `runs/eval/sgb/sanctuary_endgame_scheduler_002/sn3e001/outcomes/CleanSkill1/result.json` {'kind': 'json_pointer', 'value': '/oracle/task_result', 'coordinate_space': 'artifact'}; sha256 `aae743780fbb10c64a60142e8151903e7098ded3676a4dcb18a6f2d1df93bc26`; verified
- `E-SKILL-1`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/Users/docskill/终局触发与额外回合结算/SKILL.md` {'kind': 'lines', 'value': [58], 'coordinate_space': 'skill_body'}; sha256 `6bbab2fbcd673a83b5c91af74a5aff3aacd86d85ff5ad4fa2cb18c6dc04808a0`; verified
- `E-SKILL-2`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/Users/docskill/终局触发与额外回合结算/SKILL.md` {'kind': 'lines', 'value': [61], 'coordinate_space': 'skill_body'}; sha256 `6bbab2fbcd673a83b5c91af74a5aff3aacd86d85ff5ad4fa2cb18c6dc04808a0`; verified
- `E-SKILL-3`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/Users/docskill/终局触发与额外回合结算/SKILL.md` {'kind': 'lines', 'value': [63], 'coordinate_space': 'skill_body'}; sha256 `6bbab2fbcd673a83b5c91af74a5aff3aacd86d85ff5ad4fa2cb18c6dc04808a0`; verified
- `E-SKILL-4`: `runs/gen/sgb/case003_san/clean/sn3r001/SkillBank/Users/docskill/终局触发与额外回合结算/SKILL.md` {'kind': 'lines', 'value': [61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71], 'coordinate_space': 'skill_body'}; sha256 `6bbab2fbcd673a83b5c91af74a5aff3aacd86d85ff5ad4fa2cb18c6dc04808a0`; verified

## Interventions


## Limits

- Historical evidence only; no model, Agent, container or Oracle replay.
- Package delivery is not behavioral reliance; semantic labels are reviewer annotations.
- First observed rule loss is not proof of downstream causation.
- Unknowns are not agreement. Possible effects are not stable causal estimates.
