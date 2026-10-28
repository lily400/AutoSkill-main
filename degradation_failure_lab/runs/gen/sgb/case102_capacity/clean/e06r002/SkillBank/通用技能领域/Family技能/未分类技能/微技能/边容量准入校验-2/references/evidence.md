# 边容量准入校验 Evidence

- family: 未分类技能
- skill_id: 2f3c4ace-1ca8-53a7-8b8b-3cd72ddc0fee
- support_count: 1

## Evidence 1

- support_id: 1bdb0120-25a7-52b8-a045-319d4d5e281d
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 51671:52107
- confidence: 0.85
- quote: MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge)

R27. A vehicle may only enter an edge in the movement execution phase if:
1. The edge’s Status = OPEN.
2. Approving its entry would not cause occupancy to exceed MaxVehicles(edge).
3. Any signal or intersection rules at the downstream node allow entry.

R28. Vehicles that requested ENTER_EDGE but fail any of the conditions in R27 instead perform WAIT at their current node.
