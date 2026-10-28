# 货物状态快照解析 Evidence

- family: 未分类技能
- skill_id: 12d1ad66-9416-5cce-87f7-c629df2206c1
- support_count: 1

## Evidence 1

- support_id: 0c219e6c-8bb9-5679-beb3-2cd6f6f6381f
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
