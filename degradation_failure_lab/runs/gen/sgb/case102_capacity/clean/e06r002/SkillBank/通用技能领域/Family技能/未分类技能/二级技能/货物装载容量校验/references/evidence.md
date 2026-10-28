# 货物装载容量校验 Evidence

- family: 未分类技能
- skill_id: 48d90833-a43e-5b3d-993f-6ae2c2015282
- support_count: 1

## Evidence 1

- support_id: 6bbb18f9-74b1-5de5-bb21-2df32742e2e3
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 49693:50371
- confidence: 0.85
- quote: R18. OFFLINE vehicles do not move or handle consignments until explicitly reactivated by a scenario or controller decision.

5. Consignments (Packages)

R19. Each consignment has:
- ConsignmentID (unique).
- OriginNode, DestinationNode.
- SizeUnits (integer >= 1).
- ReleaseTime (tick at or after which it becomes available at OriginNode).
- DueTime (target latest arrival tick at DestinationNode).
- PriorityLevel in {LOW, STANDARD, HIGH, CRITICAL}.
- Status in {PENDING_AT_ORIGIN, ON_VEHICLE, DELIVERED, CANCELLED}.
- AssignedVehicleID (optional).

R20. A consignment may only be loaded onto a vehicle if SizeUnits plus the vehicle’s current load do not exceed CapacityUnits.
