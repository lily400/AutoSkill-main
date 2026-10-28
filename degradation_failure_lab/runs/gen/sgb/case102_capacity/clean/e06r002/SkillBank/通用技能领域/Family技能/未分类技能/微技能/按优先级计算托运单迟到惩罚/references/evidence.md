# 按优先级计算托运单迟到惩罚 Evidence

- family: 未分类技能
- skill_id: d097f190-6b6f-5b0e-b989-589cb4cac21f
- support_count: 1

## Evidence 1

- support_id: 3934c3b2-90fb-54fe-8de5-211b68ee856c
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 32707:33677
- confidence: 0.80
- quote: R41. An incident is an event that changes the status or capacity of an edge for a range of ticks.

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
