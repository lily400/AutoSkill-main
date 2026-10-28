# 阶段内实体规范排序规则 Evidence

- family: 未分类技能
- skill_id: b6e41188-61e5-5ffb-a538-7007fe703ade
- support_count: 1

## Evidence 1

- support_id: 8b4125a2-e2d2-5eae-b470-dbe504eb8de5
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 4603:5783
- confidence: 0.80
- quote: R11. The occupancy of an edge at time t is the set of vehicles currently traveling along it, with their remaining travel time.

3. Time and Update Order
R12. Each tick is processed in the following order:

1. Incident Resolution Phase:update the status of edges according to active incidents (openings, closures, clearances).
2. Movement Commitment Phase:vehicles at nodes decide which edge to enter or whether to remain.
3. Capacity & Conflict Check Phase:check edge capacities, signals, and priorities. Some movement commitments may be denied.
4. Movement Execution Phase:approved vehicles leave nodes and advance along edges; vehicles already on edges decrement their remaining travel time. Vehicles whose remaining travel time reaches 0 arrive at the downstream node.
5. Loading/Unloading Phase:vehicles at nodes load or unload consignments if an appropriate action is chosen and capacity allows.
6. Metric Update Phase:update delivery lateness, travel distance counters, and other statistics.

R13. Within a phase, if an ordering is required between entities, the canonical ordering is ascending VehicleID, then ascending NodeID, unless a rule specifies a different priority.
