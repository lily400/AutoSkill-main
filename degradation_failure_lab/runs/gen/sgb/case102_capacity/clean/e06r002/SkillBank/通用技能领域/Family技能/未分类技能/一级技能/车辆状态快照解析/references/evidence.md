# 车辆状态快照解析 Evidence

- family: 未分类技能
- skill_id: 7a90ecb6-a5c8-5129-ab01-9f8db8b78041
- support_count: 1

## Evidence 1

- support_id: ffcb6192-b86d-52b3-b46c-2d6aad8d807a
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 18924:19385
- confidence: 0.70
- quote: VEHICLES
V1 TRUCK LocationType: NODE LocationID: N1 Status: IDLE_AT_NODE LoadUnitsUsed: 0 OnboardConsignments: []
V2 VAN   LocationType: NODE LocationID: N1 Status: IDLE_AT_NODE LoadUnitsUsed: 0 OnboardConsignments: []

1.5 CONSIGNMENTS Section
T6. Each consignment entry includes:
- ConsignmentID
- Status
- CurrentNode (if status is PENDING_AT_ORIGIN or waiting at an intermediate node).
- AssignedVehicleID (if any).
- DeliveredTime (if delivered).

Example:
