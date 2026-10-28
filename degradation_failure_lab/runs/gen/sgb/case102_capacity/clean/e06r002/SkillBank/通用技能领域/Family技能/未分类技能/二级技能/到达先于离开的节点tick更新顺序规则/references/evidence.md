# 到达先于离开的节点tick更新顺序规则 Evidence

- family: 未分类技能
- skill_id: 229c44db-e7ea-5d6e-b34d-aa7c88339b4d
- support_count: 1

## Evidence 1

- support_id: 54699be3-5ffb-56ae-8fbd-66b3ebe1327c
- relation_type: constraint
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 30069:30960
- confidence: 0.80
- quote: R28. Vehicles that requested ENTER_EDGE but fail any of the conditions in R27 instead perform WAIT at their current node.

R29. At a signalized downstream node:
- Each incoming edge has a signal group.
- Only edges whose signal group is in a GREEN phase may release new vehicles onto the intersection during that tick.
- The order of release for vehicles on a single incoming edge during a green phase is by arrival order at the node queue (FIFO).

R30. At an unsignalized downstream node:
- Movements are controlled by a priority ranking of incoming edges.
- Higher-priority edge queues are processed before lower-priority queues.
- If two vehicles from different edges with the same priority would conflict, the vehicle with the lower VehicleID moves first.

R31. If a vehicle arrives at a node at the same tick other vehicles attempt to leave it, arrivals are processed before departures.
