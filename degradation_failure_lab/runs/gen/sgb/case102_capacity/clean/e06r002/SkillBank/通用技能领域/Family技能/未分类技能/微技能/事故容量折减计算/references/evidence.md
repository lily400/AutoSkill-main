# 事故容量折减计算 Evidence

- family: 未分类技能
- skill_id: 272c6898-fbc4-5677-abfc-bc4e991d997c
- support_count: 1

## Evidence 1

- support_id: ce384486-b16c-5c37-be48-77df0bbd1d0f
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 22123:22574
- confidence: 0.80
- quote: At tick 6 (t mod 6 = 0, Phase A), E2 is green but E5 is not; V2 may enter N3 at tick 6, while V3 must wait until Phase B (ticks 2-3 modulo 6), ie, tick 8 or 9, to enter.

4. Worked Example C:Capacity Reduction Incident
Consider incident I1 on E9 (N4 to N9) with CapacityMultiplier = 0.5.

- Baseline for E9: LaneCount = 2, CapacityPerLane = 2.
- Baseline MaxVehicles = 4.
- During I1 (ticks 4-15 inclusive), effective MaxVehicles = floor(4 × 0.5) = 2.
