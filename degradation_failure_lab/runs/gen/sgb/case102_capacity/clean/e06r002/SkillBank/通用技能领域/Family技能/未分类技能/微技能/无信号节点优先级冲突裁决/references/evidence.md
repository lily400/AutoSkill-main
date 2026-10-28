# 无信号节点优先级冲突裁决 Evidence

- family: 未分类技能
- skill_id: ce42f188-5a29-5be4-8bcc-43617ba9a0f2
- support_count: 1

## Evidence 1

- support_id: 621dbde1-5c22-5a31-ba26-c66e84e1440c
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 8890:9781
- confidence: 0.85
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
