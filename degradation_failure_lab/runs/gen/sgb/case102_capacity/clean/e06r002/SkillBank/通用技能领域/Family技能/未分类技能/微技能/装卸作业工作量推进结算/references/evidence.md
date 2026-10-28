# 装卸作业工作量推进结算 Evidence

- family: 未分类技能
- skill_id: 21a93e15-34ac-5aa9-84f9-e281d0a7f541
- support_count: 1

## Evidence 1

- support_id: c9bdd533-c2ec-5028-aedd-13de07f4b41c
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 53472:54416
- confidence: 0.85
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
