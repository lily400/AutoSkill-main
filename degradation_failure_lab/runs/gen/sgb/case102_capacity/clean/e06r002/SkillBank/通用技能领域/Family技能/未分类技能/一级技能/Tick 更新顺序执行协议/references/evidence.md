# Tick 更新顺序执行协议 Evidence

- family: 未分类技能
- skill_id: 494b96ff-2a1a-55ce-a8dd-7cfd17507adb
- support_count: 2

## Evidence 1

- support_id: eea89237-223a-5bf5-b3b5-02739b61e638
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 25782:26962
- confidence: 0.85
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

## Evidence 2

- support_id: 77fc7d7a-bc4b-57f1-8e69-d2fc81745677
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 4603:5783
- confidence: 0.85
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
