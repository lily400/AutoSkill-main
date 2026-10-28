# 信号相位激活判定 Evidence

- family: 未分类技能
- skill_id: 7c827cd0-f8c6-5eed-8530-349ad41c6fc5
- support_count: 1

## Evidence 1

- support_id: 00a53854-916b-5c0f-8be2-0228b0e0636d
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 30830:31266
- confidence: 0.80
- quote: R31. If a vehicle arrives at a node at the same tick other vehicles attempt to leave it, arrivals are processed before departures.

8. Traffic Signals
R32. Each signalized node has a fixed signal cycle defined by:
- CycleLength in ticks.
- A repeating ordered list of Phases. Each phase has:
  - Duration in ticks.
  - GreenEdges: the set of incoming edges allowed to release vehicles.

R33. The phase active at tick t is determined by:
