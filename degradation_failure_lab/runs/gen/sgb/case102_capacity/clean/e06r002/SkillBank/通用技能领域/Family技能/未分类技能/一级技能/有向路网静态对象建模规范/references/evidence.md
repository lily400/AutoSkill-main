# 有向路网静态对象建模规范 Evidence

- family: 未分类技能
- skill_id: ebbc3a65-a1e0-5ce8-8232-82a9945bd90c
- support_count: 1

## Evidence 1

- support_id: 8eeec535-57d0-5f8c-817d-737621f6c15e
- relation_type: support
- document: input001\context.md
- doc_id: 1291f40b-7db3-5798-9061-f3310b3f99fe
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case102_capacity\clean\e06g002\inputs\input001\context.md
- section: User Questions
- span: 3100:4365
- confidence: 0.80
- quote: R4. All behavior in the simulation must follow the rules in this document. If a situation is not covered, it is considered undefined until additional rules are added.

R5. The simulation tracks four primary object types:
- Nodes (intersections, depots, customer locations, hubs)
- Edges (directed road segments between nodes)
- Vehicles (mobile units that carry packages)
- Consignments (packages to be transported)

2. Nodes and Edges
R6. The network is a directed graph. Every edge has an ordered pair (from_node, to_node)

R7. Each node has:
- A unique identifier NodeID
- A NodeType in {INTERSECTION, DEPOT, CUSTOMER, HUB}
- Zero or more parking bays where vehicles can wait and load/unload
- Zero or more queues at incoming edges

R8. Each edge has:
- A unique identifier EdgeID.
- FromNode, ToNode.
- Length in abstract distance units.
- BaseTravelTime in ticks, representing the travel time for a reference vehicle under free flow.
- LaneCount (positive integer).
- CapacityPerLane: maximum number of vehicles that can be present on that edge at any time per lane.
- RoadClass in {LOCAL, ARTERIAL, RING}.
- SignalType at the downstream node in {SIGNALIZED, UNSIGNALIZED}.

R9. If an edge is conceptually two way, it is modeled as two separate directed edges.
