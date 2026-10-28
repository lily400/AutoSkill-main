# 货运交付与延误判定 Evidence

- family: 未分类技能
- skill_id: 20fcdd02-8fae-5c9e-a2e7-d5e30a089d04
- support_count: 1

## Evidence 1

- support_id: 74b19706-4468-5deb-a6c3-283a00a52ce9
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 7281:8354
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
