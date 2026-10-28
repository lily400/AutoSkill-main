# 边最大容量计算 Evidence

- family: 未分类技能
- skill_id: 517e7d17-b12f-59d1-8578-64cf81e2202f
- support_count: 1

## Evidence 1

- support_id: 96865fd7-0234-5868-a98b-f6d810d26e5e
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 8575:9011
- confidence: 0.80
- quote: MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge)

R27. A vehicle may only enter an edge in the movement execution phase if:
1. The edge’s Status = OPEN.
2. Approving its entry would not cause occupancy to exceed MaxVehicles(edge).
3. Any signal or intersection rules at the downstream node allow entry.

R28. Vehicles that requested ENTER_EDGE but fail any of the conditions in R27 instead perform WAIT at their current node.
