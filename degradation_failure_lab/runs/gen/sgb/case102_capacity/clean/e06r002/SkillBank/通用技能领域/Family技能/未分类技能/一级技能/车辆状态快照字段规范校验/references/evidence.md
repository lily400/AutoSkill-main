# 车辆状态快照字段规范校验 Evidence

- family: 未分类技能
- skill_id: e6fa8c9e-42b0-5f33-aa08-11f1c16a7bf8
- support_count: 1

## Evidence 1

- support_id: 6eccf7b3-6277-53cd-83e3-73dc791c2511
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 39951:40209
- confidence: 0.70
- quote: 1.4 VEHICLES Section

T5. Each vehicle entry includes:
- VehicleID
- VehicleType
- LocationType in {NODE, EDGE}
- LocationID (NodeID or EdgeID)
- If on edge: RemainingTravelTime
- Status
- LoadUnitsUsed
- OnboardConsignments:list of ConsignmentIDs.

Example:
