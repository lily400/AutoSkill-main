# AFN 控制器目标与优先级评估 Evidence

- family: 未分类技能
- skill_id: b1cbd14c-b4fe-50c9-bec5-022f912cc86e
- support_count: 1

## Evidence 1

- support_id: f6353d5f-e884-5450-88f9-3f69282615e7
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 60747:61798
- confidence: 0.60
- quote: AFN State Representation & Worked Examples

1. State Snapshot Format

T1. The simulation state at tick t is represented by a structured snapshot with the following sections:
1. GLOBAL
2. NODES
3. EDGES
4. VEHICLES
5. CONSIGNMENTS
6. INCIDENTS_ACTIVE

1.1 GLOBAL Section

T2. The GLOBAL section has:
- TimeTick:current tick index.
- ScenarioName:e.g., "Morning Rush".
- ScoreSoFar:current cumulative service score (may be provisional).

Example:

GLOBAL
TimeTick: 0
ScenarioName: Morning Rush
ScoreSoFar: 0

1.2 NODES Section

T3. Each node entry includes:
- NodeID
- NodeType
- PackagesAtNode:list of ConsignmentIDs currently waiting here.
- ParkingVehicles:list of VehicleIDs currently parked here.

Example excerpt:

NODES
N1 DEPOT PackagesAtNode: [C1, C2] ParkingVehicles: [V1, V2]
N2 HUB PackagesAtNode: [] ParkingVehicles: []
N6 CUSTOMER PackagesAtNode: [] ParkingVehicles: []

1.3 EDGES Section

T4. Each edge entry includes:
- EdgeID
- Status (OPEN or CLOSED)
- Occupancy:list of items of the form (VehicleID, RemainingTravelTime)

Example:
