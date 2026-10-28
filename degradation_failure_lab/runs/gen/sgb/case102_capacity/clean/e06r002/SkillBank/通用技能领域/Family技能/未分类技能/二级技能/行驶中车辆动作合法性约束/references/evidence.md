# 行驶中车辆动作合法性约束 Evidence

- family: 未分类技能
- skill_id: fb8197f0-8b04-5737-97fc-0668903cd571
- support_count: 1

## Evidence 1

- support_id: b921ce3e-5264-51f8-aabc-33b32af1196f
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 29535:29813
- confidence: 0.75
- quote: R25. If a vehicle is on an edge (Status = MOVING), it may not start loading or unloading; its only valid action is CONTINUE_TRAVEL.

7. Edge Capacity, Queues, and Conflicts
R26. Each edge has a total vehicle capacity:

MaxVehicles(edge) = LaneCount(edge) × CapacityPerLane(edge)
