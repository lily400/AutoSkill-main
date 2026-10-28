# 信号交叉口相位-绿灯边映射查询 Evidence

- family: 未分类技能
- skill_id: 7ba74262-2445-50bc-9936-6b2950cefcaf
- support_count: 1

## Evidence 1

- support_id: 00b7b717-eafa-59d7-ae00-3b6d864c5662
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 36400:37129
- confidence: 0.70
- quote: S5. Node N3 (Central Intersection) is signalized for edges arriving from N2, N4, N5, N10, N7, and N8.

S6. N3 has CycleLength = 6 ticks and three phases:
- Phase A (ticks 0-1 mod 6): GreenEdges = {E2, E10} (traffic arriving from N2 and N9).
- Phase B (ticks 2-3 mod 6): GreenEdges = {E3, E5, E12} (traffic arriving from N4, N5, N10).
- Phase C (ticks 4-5 mod 6): GreenEdges = {E18, E19, E7} (traffic arriving from N7, N8, and return from N7).

S7. Node N4 is signalized for edges arriving from N3 and N9 with a simple cycle:
- CycleLength = 4 ticks.
- Phase 1 (ticks 0-1 mod 4): GreenEdges = {E3}.
- Phase 2 (ticks 2-3 mod 4): GreenEdges = {E20}.

4. Vehicles in the Morning Rush Scenario

S8. The scenario begins at tick t = 0.
