# 到达先于离开的节点事件排序规则 Evidence

- family: 未分类技能
- skill_id: 80d4597c-cdeb-5438-af5c-2a26945edf6b
- support_count: 1

## Evidence 1

- support_id: e1379368-bc49-5266-ad72-7afdce982260
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 9651:10087
- confidence: 0.65
- quote: R31. If a vehicle arrives at a node at the same tick other vehicles attempt to leave it, arrivals are processed before departures.

8. Traffic Signals
R32. Each signalized node has a fixed signal cycle defined by:
- CycleLength in ticks.
- A repeating ordered list of Phases. Each phase has:
  - Duration in ticks.
  - GreenEdges: the set of incoming edges allowed to release vehicles.

R33. The phase active at tick t is determined by:
