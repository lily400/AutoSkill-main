# 同相位实体规范排序规则 Evidence

- family: 未分类技能
- skill_id: 2a0027f2-f608-579c-82cb-dd9b628d283a
- support_count: 1

## Evidence 1

- support_id: 07927e8a-90ad-5bd1-b102-04a46ccbf055
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 5602:6427
- confidence: 0.70
- quote: R13. Within a phase, if an ordering is required between entities, the canonical ordering is ascending VehicleID, then ascending NodeID, unless a rule specifies a different priority.

4. Vehicles
R14. Each vehicle has:
- VehicleID (unique).
- VehicleType in {BIKE, VAN, TRUCK, MINI_TRUCK}
- CapacityUnits (integer >= 1)
- HomeDepot (a node)
- CurrentLocation, which is either:
  - A node (NodeID plus optional parking bay), or
  - An edge (EdgeID plus RemainingTravelTime)
- LoadUnitsUsed (integer) and a list of assigned consignments currently onboard.
- Status in {IDLE_AT_NODE, MOVING, LOADING, UNLOADING, OFFLINE}.

R15. Vehicle speed is defined via travel time multipliers:
- BIKE: multiplier 1.5
- VAN: multiplier 1.0
- MINI_TRUCK: multiplier 1.0
- TRUCK: multiplier 0.8

R16. The travel time of a vehicle on an edge is:
