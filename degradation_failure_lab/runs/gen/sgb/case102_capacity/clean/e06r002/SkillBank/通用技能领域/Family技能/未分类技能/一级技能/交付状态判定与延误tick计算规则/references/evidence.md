# 交付状态判定与延误tick计算规则 Evidence

- family: 未分类技能
- skill_id: 45604ce9-4ef0-5a7e-a285-7fb55f63928b
- support_count: 1

## Evidence 1

- support_id: 86f4f642-e618-525b-8ead-3675741e668d
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 50373:51669
- confidence: 0.70
- quote: R21. A consignment is considered delivered when it is unloaded at DestinationNode.

R22. Lateness of a consignment is defined as:
- 0 if delivered at or before DueTime.
- Otherwise, DeliveredTime:DueTime in ticks.

6. Legal Actions Per Tick

R23. At each tick, each non-offline vehicle may choose exactly one action from this list:
- WAIT: remain at its current node and do nothing.
- ENTER_EDGE(edgeID): if currently at a node, request to enter a specific outgoing edge.
- CONTINUE_TRAVEL: if already on an edge, continue moving (implicit if no other action is available).
- START_LOADING(consignmentIDs): begin loading one or more consignments at the current node.
- START_UNLOADING(consignmentIDs): begin unloading specified consignments that are on the vehicle and whose destination or allowed transfer node matches the current node.
- GO_OFFLINE: switch status to OFFLINE if at its HomeDepot.
- GO_ONLINE: switch from OFFLINE to IDLE_AT_NODE at HomeDepot (only if already at that node).

R24. Actions are requests until validated in the capacity & conflict check phase.

R25. If a vehicle is on an edge (Status = MOVING), it may not start loading or unloading; its only valid action is CONTINUE_TRAVEL.

7. Edge Capacity, Queues, and Conflicts

R26. Each edge has a total vehicle capacity:
