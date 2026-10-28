# 超容量进入请求的拒绝与等待回退 Evidence

- family: 未分类技能
- skill_id: d954539f-c4e1-500a-b366-90101b10e80b
- support_count: 1

## Evidence 1

- support_id: 4fb2864f-fb51-524c-9bb8-cafd7a021594
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 65560:67059
- confidence: 0.80
- quote: Consider incident I1 on E9 (N4 to N9) with CapacityMultiplier = 0.5.

- Baseline for E9: LaneCount = 2, CapacityPerLane = 2.
- Baseline MaxVehicles = 4.
- During I1 (ticks 4-15 inclusive), effective MaxVehicles = floor(4 × 0.5) = 2.

Suppose at tick 5, there are already 2 vehicles on E9. A third vehicle at N4 requests ENTER_EDGE(E9):
- In the Capacity & Conflict Check Phase, approving this would exceed MaxVehicles = 2.
- The request is denied; the vehicle instead performs WAIT at N4 for that tick.

## Question 5
