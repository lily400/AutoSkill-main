# capacity_aware_edge_admission_controller_006

## Task Type

function

## Task

Implement `solve(input_data)` as a **Capacity-aware edge admission controller**.

The tool runs the simulator's **Capacity & Conflict Check Phase** for a single tick, deciding which `ENTER_EDGE` requests are approved or denied.

INPUT (dict):
- 'tick': int — current tick t.
- 'edge_occupancy': dict[str, list[str]] — current vehicles on each edge (VehicleIDs). (Only counts for capacity.)
- 'enter_requests': list[dict] — each item:
  - 'vehicle_id': str
  - 'from_node': str
  - 'edge_id': str — requested outgoing edge to enter
- 'active_incidents': list[dict] — each item:
  - 'incident_id': str
  - 'edge_id': str
  - 'start_tick': int
  - 'end_tick': int (exclusive)
  - 'effect_type': str in {'CLOSE_EDGE','REDUCE_CAPACITY'}
  - 'capacity_multiplier': float (only for REDUCE_CAPACITY)

OUTPUT (dict):
- 'decisions': list[dict] aligned with input 'enter_requests' order, each item:
  - 'vehicle_id': str
  - 'edge_id': str
  - 'approved': bool
  - 'action': str — 'ENTER_EDGE' if approved else 'WAIT'
  - 'reason': str in {'APPROVED','CLOSURE','CAPACITY','SIGNAL'}
  - 'effective_max_vehicles': int — effective capacity used for the decision
  - 'occupancy_before': int

RULES (from the document; apply exactly):
- Edge admission requires: edge OPEN, capacity not exceeded, and downstream signal rules allow entry {R27}.
- If any condition fails, the vehicle performs WAIT {R28}.
- Baseline edge capacity is LaneCount × CapacityPerLane {R26}.
- Incidents apply during their active tick range; CLOSE_EDGE prevents new entry; REDUCE_CAPACITY multiplies baseline capacity and uses the document’s rounding behavior {R41-R44}.
- For signalized downstream nodes, entry is allowed only if the incoming edge is green for the active phase at tick t, computed by the fixed cycles {R32-R34, S6-S7}.
- Use the Morning Rush map’s edge definitions and signal programs for N3 and N4 {S3-S7}. (All other downstream nodes are treated as unsignalized for this tool.)
- If multiple incidents affect the same edge at the same tick, apply closure if any CLOSE_EDGE is active; otherwise apply the most restrictive capacity multiplier (smallest) among active REDUCE_CAPACITY incidents.

Note: This tool only decides approvals/denials and logs reasons; it does not advance time or mutate occupancy.

## Expected Output Summary

```json
{
  "format": "dict",
  "key_results": {
    "decisions": "list of per-request decision dicts"
  }
}
```

## Runtime Interface

- Documentation context directory: /workspace/docs
- Skill assets directory: /workspace/skill
- Final submission file: /workspace/agent_output.py
- The submission must define solve(input_data).
- Tests will call solve(input_data) directly for each bundled test case.
- Tests run from /workspace/tests/test.sh with TEST_ROOT_DIR=/workspace.
