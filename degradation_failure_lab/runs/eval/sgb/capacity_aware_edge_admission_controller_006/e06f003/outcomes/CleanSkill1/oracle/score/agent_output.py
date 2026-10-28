from math import floor


def solve(input_data):
    tick = input_data.get('tick', 0)
    edge_occupancy = input_data.get('edge_occupancy', {}) or {}
    enter_requests = input_data.get('enter_requests', []) or []
    active_incidents = input_data.get('active_incidents', []) or []

    # Morning Rush map / signal programs are not provided in the task input.
    # Implement robustly: if signal data exists in input_data, use it; otherwise
    # only edges explicitly marked as signal-controlled in provided structures will be gated.
    signal_nodes = input_data.get('signal_nodes', {}) or {}
    edge_to_downstream = input_data.get('edge_to_downstream', {}) or {}
    edge_defs = input_data.get('edge_definitions', {}) or {}

    def get_baseline_capacity(edge_id):
        # Prefer explicit edge definition if present.
        ed = edge_defs.get(edge_id, {}) if isinstance(edge_defs, dict) else {}
        lane_count = ed.get('lane_count', ed.get('LaneCount'))
        cap_per_lane = ed.get('capacity_per_lane', ed.get('CapacityPerLane'))
        if lane_count is not None and cap_per_lane is not None:
            try:
                return int(lane_count) * int(cap_per_lane)
            except Exception:
                pass
        # Fallback: if no definitions are given, infer no change from current occupancy.
        return len(edge_occupancy.get(edge_id, [])) if edge_id in edge_occupancy else 0

    def incident_effect(edge_id):
        close = False
        multipliers = []
        for inc in active_incidents:
            if inc.get('edge_id') != edge_id:
                continue
            s = inc.get('start_tick')
            e = inc.get('end_tick')
            if s is None or e is None:
                continue
            if not (s <= tick < e):
                continue
            eff = inc.get('effect_type')
            if eff == 'CLOSE_EDGE':
                close = True
            elif eff == 'REDUCE_CAPACITY':
                try:
                    multipliers.append(float(inc.get('capacity_multiplier', 1.0)))
                except Exception:
                    pass
        return close, (min(multipliers) if multipliers else None)

    def signal_allows(edge_id):
        downstream = edge_to_downstream.get(edge_id)
        if not downstream:
            return True
        sig = signal_nodes.get(downstream)
        if not sig:
            return True
        cycle = sig.get('CycleLength', sig.get('cycle_length'))
        phases = sig.get('phases', sig.get('Phases'))
        if not cycle or not phases:
            return False
        try:
            pos = tick % int(cycle)
        except Exception:
            return False
        acc = 0
        for ph in phases:
            dur = ph.get('Duration', ph.get('duration'))
            greens = ph.get('GreenEdges', ph.get('green_edges', []))
            if dur is None:
                continue
            acc += int(dur)
            if pos < acc:
                return edge_id in set(greens or [])
        return False

    decisions = []
    for req in enter_requests:
        vehicle_id = req.get('vehicle_id')
        edge_id = req.get('edge_id')
        occupancy_before = len(edge_occupancy.get(edge_id, []))
        baseline = get_baseline_capacity(edge_id)
        close, multiplier = incident_effect(edge_id)
        if close:
            effective = baseline
            approved = False
            reason = 'CLOSURE'
        else:
            effective = baseline
            if multiplier is not None:
                effective = floor(baseline * multiplier)
            signal_ok = signal_allows(edge_id)
            if not signal_ok:
                approved = False
                reason = 'SIGNAL'
            elif occupancy_before + 1 > effective:
                approved = False
                reason = 'CAPACITY'
            else:
                approved = True
                reason = 'APPROVED'
        decisions.append({
            'vehicle_id': vehicle_id,
            'edge_id': edge_id,
            'approved': approved,
            'action': 'ENTER_EDGE' if approved else 'WAIT',
            'reason': reason,
            'effective_max_vehicles': int(effective),
            'occupancy_before': int(occupancy_before),
        })

    return {'decisions': decisions}
