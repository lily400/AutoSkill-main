# Tick 处理与快照生成流程 Evidence

- family: 未分类技能
- skill_id: 730695a2-c80a-54b5-aadf-c616118dd310
- support_count: 1

## Evidence 1

- support_id: a73154fd-53ca-5991-9388-99846403f6a0
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 41586:42230
- confidence: 0.70
- quote: CONSIGNMENTS
C1 Status: PENDING_AT_ORIGIN CurrentNode: N1 AssignedVehicleID: None DeliveredTime: -

At tick 0, the controller chooses actions:
- V1: START_LOADING([C1]).

Processing tick 0:
1. No incidents.
2. Movement commitments: none (V1 does not request movement).
3. Capacity & conflicts: nothing to resolve.
4. Movement execution: no vehicles move.
5. Loading phase: V1 starts loading C1.
   - WorkUnits = SizeUnits(C1) = 3.
   - HandlingRate(TRUCK) = 4, so job will complete in a single tick.
6. Metrics: none yet.

Snapshot at tick 1:
- V1 has finished loading C1 and is now idle at N1 with C1 onboard.

GLOBAL
TimeTick: 1
ScoreSoFar: 0
