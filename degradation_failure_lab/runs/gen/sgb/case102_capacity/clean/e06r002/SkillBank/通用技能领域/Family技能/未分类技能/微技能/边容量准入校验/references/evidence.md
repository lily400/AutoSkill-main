# 边容量准入校验 Evidence

- family: 未分类技能
- skill_id: d3e1cf4c-29a0-51ad-a791-f42d7e30c644
- support_count: 1

## Evidence 1

- support_id: b9239b4b-47d6-55c8-80bc-712dece934b0
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 22576:24120
- confidence: 0.80
- quote: Suppose at tick 5, there are already 2 vehicles on E9. A third vehicle at N4 requests ENTER_EDGE(E9):
- In the Capacity & Conflict Check Phase, approving this would exceed MaxVehicles = 2.
- The request is denied; the vehicle instead performs WAIT at N4 for that tick.

1. Overview
R1. The Arclight Freight Network (AFN) is a fictional urban road and logistics system used to simulate movement of vehicles and packages over discrete time steps.

R2. Time is discrete. Each simulation step is called a tick. Ticks are indexed by non-negative integers t = 0, 1, 2,
