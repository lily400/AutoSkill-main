# 进入边失败回退WAIT规则 Evidence

- family: 未分类技能
- skill_id: d9f5202a-1d1b-5545-a2d2-49b57c524a65
- support_count: 1

## Evidence 1

- support_id: 4b65fb08-9d40-5169-812d-e605d2528a8c
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 51986:52433
- confidence: 0.80
- quote: R28. Vehicles that requested ENTER_EDGE but fail any of the conditions in R27 instead perform WAIT at their current node.

R29. At a signalized downstream node:
- Each incoming edge has a signal group.
- Only edges whose signal group is in a GREEN phase may release new vehicles onto the intersection during that tick.
- The order of release for vehicles on a single incoming edge during a green phase is by arrival order at the node queue (FIFO).
