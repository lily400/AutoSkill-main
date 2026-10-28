# 装卸期间车辆锁定约束 Evidence

- family: 未分类技能
- skill_id: 1d99d4c7-ebb1-59e6-9050-779cd4dc28b3
- support_count: 2

## Evidence 1

- support_id: 76927095-fe2d-5a95-9141-76868449dbc7
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 53472:54416
- confidence: 0.80
- quote: R36. Each loading/unloading job has an integer WorkUnits equal to the sum of the SizeUnits of the consignments being handled in that job.

R37. Each vehicle type has a HandlingRate:
- BIKE: 1 work unit per tick.
- VAN: 2 work units per tick.
- MINI_TRUCK: 3 work units per tick.
- TRUCK: 4 work units per tick.

R38. When a vehicle chooses START_LOADING or START_UNLOADING at tick t:
- Its Status becomes LOADING or UNLOADING.
- A job is created with the relevant consignments and total WorkUnits.
- During each subsequent Loading/Unloading Phase, WorkUnits is reduced by the vehicle’s HandlingRate.
- When WorkUnits reaches 0 or less, the job completes at the end of that tick:
  - For loading, consignments’ Status becomes ON_VEHICLE.
  - For unloading, consignments’ Status becomes DELIVERED or PENDING_AT_ORIGIN at a transfer node as specified by the scenario.

R39. While a job is in progress, the vehicle cannot move or start another job.

## Evidence 2

- support_id: 236ee33f-5333-5b59-8904-0261a75398d0
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 31551:32495
- confidence: 0.75
- quote: R36. Each loading/unloading job has an integer WorkUnits equal to the sum of the SizeUnits of the consignments being handled in that job.

R37. Each vehicle type has a HandlingRate:
- BIKE: 1 work unit per tick.
- VAN: 2 work units per tick.
- MINI_TRUCK: 3 work units per tick.
- TRUCK: 4 work units per tick.

R38. When a vehicle chooses START_LOADING or START_UNLOADING at tick t:
- Its Status becomes LOADING or UNLOADING.
- A job is created with the relevant consignments and total WorkUnits.
- During each subsequent Loading/Unloading Phase, WorkUnits is reduced by the vehicle’s HandlingRate.
- When WorkUnits reaches 0 or less, the job completes at the end of that tick:
  - For loading, consignments’ Status becomes ON_VEHICLE.
  - For unloading, consignments’ Status becomes DELIVERED or PENDING_AT_ORIGIN at a transfer node as specified by the scenario.

R39. While a job is in progress, the vehicle cannot move or start another job.
