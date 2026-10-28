# 装卸与任务分配流程 Evidence

- family: 未分类技能
- skill_id: f2918fa1-b55b-5c3a-b164-564a5eb75670
- support_count: 1

## Evidence 1

- support_id: 285f23ce-bf4a-51c0-bdc1-b79eaf90cd7c
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 14677:16937
- confidence: 0.70
- quote: S4. Return paths are modeled by additional edges:
- E13: N2 to N1 | LOCAL | 3 | 1 | 2 | UNSIGNALIZED
- E14: N3 to N2 | ARTERIAL | 2 | 2 | 2 | SIGNALIZED
- E15: N4 to N3 | ARTERIAL | 2 | 2 | 2 | SIGNALIZED
- E16: N3 to N5 | ARTERIAL | 2 | 2 | 2 | SIGNALIZED
- E17: N6 to N2 | LOCAL | 3 | 1 | 1 | UNSIGNALIZED
- E18: N7 to N3 | LOCAL | 3 | 1 | 1 | UNSIGNALIZED
- E19: N8 to N3 | LOCAL | 4 | 1 | 1 | UNSIGNALIZED
- E20: N9 to N4 | RING | 3 | 2 | 2 | SIGNALIZED
- E21: N10 to N5 | LOCAL | 3 | 1 | 1 | UNSIGNALIZED

3. Signal Settings
S5. Node N3 (Central Intersection) is signalized for edges arriving from N2, N4, N5, N10, N7, and N8.

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

S9. There are four vehicles:
- V1: type TRUCK, capacity 12 units, home depot N1, initially at N1, empty, status IDLE_AT_NODE.
- V2: type VAN, capacity 8 units, home depot N1, initially at N1, empty, status IDLE_AT_NODE.
- V3: type VAN, capacity 8 units, home depot N5, initially at N5, empty, status IDLE_AT_NODE.
- V4: type BIKE, capacity 2 units, home depot N4, initially at N4, empty, status IDLE_AT_NODE.

5. Consignments
S10. Initial consignments at tick 0:
1. C1: from N1 to N6, size 3, release time 0, due time 12, priority STANDARD.
2. C2: from N1 to N7, size 4, release time 0, due time 10, priority HIGH.
3. C3: from N5 to N10, size 5, release time 0, due time 9, priority STANDARD.
4. C4: from N5 to N8, size 4, release time 2, due time 14, priority LOW.
5. C5: from N4 to N9, size 2, release time 1, due time 8, priority CRITICAL.
6. C6: from N2 to N3, size 1, release time 3, due time 9, priority HIGH.

S11. All consignments start with Status = PENDING_AT_ORIGIN and no assigned vehicle.
