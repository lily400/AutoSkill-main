# Tick 阶段顺序执行协议 Evidence

- family: 未分类技能
- skill_id: 446d6f51-4270-501e-af47-cef2dfa14001
- support_count: 1

## Evidence 1

- support_id: 2e64f94a-c007-53cb-b196-9c82c2f94047
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 47844:48871
- confidence: 0.85
- quote: R12. Each tick is processed in the following order:

1. Incident Resolution Phase:update the status of edges according to active incidents (openings, closures, clearances).
2. Movement Commitment Phase:vehicles at nodes decide which edge to enter or whether to remain.
3. Capacity & Conflict Check Phase:check edge capacities, signals, and priorities. Some movement commitments may be denied.
4. Movement Execution Phase:approved vehicles leave nodes and advance along edges; vehicles already on edges decrement their remaining travel time. Vehicles whose remaining travel time reaches 0 arrive at the downstream node.
5. Loading/Unloading Phase:vehicles at nodes load or unload consignments if an appropriate action is chosen and capacity allows.
6. Metric Update Phase:update delivery lateness, travel distance counters, and other statistics.

R13. Within a phase, if an ordering is required between entities, the canonical ordering is ascending VehicleID, then ascending NodeID, unless a rule specifies a different priority.
