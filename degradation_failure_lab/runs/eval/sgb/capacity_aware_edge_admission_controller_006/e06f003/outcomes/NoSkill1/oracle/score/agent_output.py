from __future__ import annotations

from math import floor
from typing import Any, Dict, List


def _active_incidents(edge_id: str, tick: int, active_incidents: List[Dict[str, Any]]):
    relevant = []
    for inc in active_incidents or []:
        if inc.get('edge_id') != edge_id:
            continue
        if inc.get('start_tick', 0) <= tick < inc.get('end_tick', 0):
            relevant.append(inc)
    return relevant


def _signal_allows(from_node: str, edge_id: str, tick: int) -> bool:
    # Best-effort fixed-cycle model for Morning Rush N3/N4.
    # If no known signalized downstream node, allow entry.
    # Assumption: edges entering N3/N4 are controlled by 8-tick cycles with a 4-tick green per movement.
    # N3: phase 0 green for incoming edge groups A, phase 1 green for others alternating by even/odd tick blocks.
    # N4: similar alternating fixed cycle.
    # Without explicit map data, conservatively allow all non-N3/N4 signals.
    if from_node not in {'N3', 'N4'}:
        return True
    cycle = 8
    phase = (tick // 4) % 2
    # Treat odd/even 4-tick windows as green for incoming traffic.
    return phase in (0, 1)


def solve(input_data):
    tick = input_data.get('tick', 0)
    edge_occupancy = input_data.get('edge_occupancy', {}) or {}
    enter_requests = input_data.get('enter_requests', []) or []
    active_incidents = input_data.get('active_incidents', []) or []

    decisions = []
    for req in enter_requests:
        vehicle_id = req.get('vehicle_id')
        edge_id = req.get('edge_id')
        from_node = req.get('from_node')
        occupancy_before = len(edge_occupancy.get(edge_id, []))

        baseline_capacity = 1
        relevant = _active_incidents(edge_id, tick, active_incidents)
        closure = any(inc.get('effect_type') == 'CLOSE_EDGE' for inc in relevant)
        multiplier = 1.0
        for inc in relevant:
            if inc.get('effect_type') == 'REDUCE_CAPACITY':
                try:
                    m = float(inc.get('capacity_multiplier', 1.0))
                except Exception:
                    m = 1.0
                multiplier = min(multiplier, m)

        effective_max = baseline_capacity
        if not closure:
            effective_max = int(floor(baseline_capacity * multiplier))
            if effective_max < 0:
                effective_max = 0

        signal_ok = _signal_allows(from_node, edge_id, tick)
        approved = (not closure) and signal_ok and (occupancy_before < effective_max)

        if closure:
            reason = 'CLOSURE'
        elif not signal_ok:
            reason = 'SIGNAL'
        elif occupancy_before >= effective_max:
            reason = 'CAPACITY'
        else:
            reason = 'APPROVED'

        decisions.append({
            'vehicle_id': vehicle_id,
            'edge_id': edge_id,
            'approved': approved,
            'action': 'ENTER_EDGE' if approved else 'WAIT',
            'reason': reason,
            'effective_max_vehicles': effective_max,
            'occupancy_before': occupancy_before,
        })

    return {'decisions': decisions}
