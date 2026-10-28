# AFN 状态快照结构化表示 Evidence

- family: 未分类技能
- skill_id: 53a03e0c-8321-5a5d-be09-8665642e8b76
- support_count: 1

## Evidence 1

- support_id: 237c9545-a9c7-5b7b-b398-3c7bb9690bb8
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 17625:17991
- confidence: 0.70
- quote: AFN State Representation & Worked Examples

1. State Snapshot Format
T1. The simulation state at tick t is represented by a structured snapshot with the following sections:

1.1 GLOBAL Section
T2. The GLOBAL section has:
- TimeTick:current tick index.
- ScenarioName:e.g., "Morning Rush".
- ScoreSoFar:current cumulative service score (may be provisional).

Example:
