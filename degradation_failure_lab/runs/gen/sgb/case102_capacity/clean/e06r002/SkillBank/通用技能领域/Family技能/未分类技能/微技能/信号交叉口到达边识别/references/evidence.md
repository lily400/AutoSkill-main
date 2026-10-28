# 信号交叉口到达边识别 Evidence

- family: 未分类技能
- skill_id: 3f0c5da5-3ebb-5a0d-8836-04f56b0c04af
- support_count: 1

## Evidence 1

- support_id: a40f9d5b-a840-5542-9bef-13a44e4cbb3f
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 35156:36501
- confidence: 0.60
- quote: Each line: EdgeID: From to To | RoadClass | BaseTravelTime | LaneCount | CapacityPerLane | SignalType at To

- E1: N1 to N2 | LOCAL | 3 | 1 | 2 | UNSIGNALIZED
- E2: N2 to N3 | ARTERIAL | 2 | 2 | 2 | SIGNALIZED
- E3: N3 to N4 | ARTERIAL | 2 | 2 | 2 | SIGNALIZED
- E4: N4 to N5 | LOCAL | 3 | 1 | 2 | UNSIGNALIZED
- E5: N5 to N3 | ARTERIAL | 2 | 2 | 2 | SIGNALIZED
- E6: N2 to N6 | LOCAL | 3 | 1 | 1 | UNSIGNALIZED
- E7: N3 to N7 | LOCAL | 3 | 1 | 1 | UNSIGNALIZED
- E8: N3 to N8 | LOCAL | 4 | 1 | 1 | UNSIGNALIZED
- E9: N4 to N9 | RING | 3 | 2 | 2 | SIGNALIZED
- E10: N9 to N3 | RING | 3 | 2 | 2 | SIGNALIZED
- E11: N5 to N10 | LOCAL | 3 | 1 | 1 | UNSIGNALIZED
- E12: N10 to N3 | LOCAL | 3 | 1 | 1 | UNSIGNALIZED

S4. Return paths are modeled by additional edges:
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
