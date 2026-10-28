# 优先级加权迟到惩罚计算 Evidence

- family: 未分类技能
- skill_id: e598b080-e247-5c98-86b7-2bd83234735c
- support_count: 1

## Evidence 1

- support_id: 4079f874-eee1-5bee-8706-3d1400ada626
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 11318:12494
- confidence: 0.75
- quote: R40. A vehicle may mix loading and unloading in a single job only if the scenario explicitly permits that pattern; otherwise, jobs must be purely loading or purely unloading.

10. Incidents and Road Closures
R41. An incident is an event that changes the status or capacity of an edge for a range of ticks.

R42. Each incident has:
- IncidentID.
- AffectedEdgeID.
- StartTick, EndTick (EndTick is exclusive).
- EffectType in {CLOSE_EDGE, REDUCE_CAPACITY}.
- For REDUCE_CAPACITY, a CapacityMultiplier in (0,1].

R43. During the Incident Resolution Phase of tick t:
- If StartTick <= t < EndTick, the incident’s effect is applied.
- If t >= EndTick, the edge returns to its baseline attributes unless modified by another active incident.

R44. When a CLOSE_EDGE incident becomes active:
- Vehicles already on the edge continue to travel as normal.
- No new vehicles may enter while it is active.

11. Priorities and Service Levels
R45. Consignment priority affects penalties for lateness:
- LOW: penalty weight 0.5 per tick late.
- STANDARD: 1.0 per tick late.
- HIGH: 2.0 per tick late.
- CRITICAL: 4.0 per tick late.

R46. The Network Service Score for a completed scenario is:
