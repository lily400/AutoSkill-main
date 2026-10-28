# 节点到达先于离开处理 Evidence

- family: 未分类技能
- skill_id: 9cdfb7b3-4b4f-5977-ad7c-600102ad33ad
- support_count: 1

## Evidence 1

- support_id: 56a32510-1198-5b13-a3b6-c5115f4a1d3a
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 52747:53470
- confidence: 0.80
- quote: R31. If a vehicle arrives at a node at the same tick other vehicles attempt to leave it, arrivals are processed before departures.

8. Traffic Signals

R32. Each signalized node has a fixed signal cycle defined by:
- CycleLength in ticks.
- A repeating ordered list of Phases. Each phase has:
  - Duration in ticks.
  - GreenEdges: the set of incoming edges allowed to release vehicles.

R33. The phase active at tick t is determined by:

PhaseIndex = (t mod CycleLength) projected into the phase list.

R34. A vehicle may enter the intersection from an edge only if that edge is in GreenEdges for the active phase at tick t.

9. Loading and Unloading

R35. Loading and unloading consume time and may span multiple ticks.
