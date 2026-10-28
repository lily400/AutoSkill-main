# 信号相位通行门控校验 Evidence

- family: 未分类技能
- skill_id: bf353d26-6bae-5420-af2e-9952d66eb683
- support_count: 1

## Evidence 1

- support_id: c4ca79bc-b5d5-56d7-be04-2dc4b91092cb
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 64417:65337
- confidence: 0.80
- quote: On tick 1, the controller chooses V1: ENTER_EDGE(E1) to move toward N2.

3. Worked Example B:Signal at Central Intersection

This example focuses on node N3’s signal.

Assume at tick 4:
- Vehicle V2 on E2 has RemainingTravelTime = 1.
- Vehicle V3 on E5 has RemainingTravelTime = 1.
- Both edges are open and uncongested.
- Tick 4 corresponds to t mod 6 = 4, which is Phase C at N3 (GreenEdges = {E18, E19, E7}).

Processing tick 4:
- In the Movement Execution Phase, V2 and V3 both decrement remaining travel time from 1 to 0.
- They attempt to arrive at N3.
- However, Phase C does not include E2 or E5 in GreenEdges.

By R34 and S6:
- Neither V2 nor V3 may complete the movement into the intersection at tick 4.
- Their arrival is postponed to tick 5; they remain effectively at the downstream boundary of their edges.

At tick 5 (t mod 6 = 5, still Phase C), the same restriction applies; they still cannot enter N3.
