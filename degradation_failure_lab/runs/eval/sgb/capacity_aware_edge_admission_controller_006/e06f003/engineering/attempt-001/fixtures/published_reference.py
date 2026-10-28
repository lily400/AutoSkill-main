def solve(input_data):
    import math

    t = int(input_data['tick'])
    edge_occupancy = input_data.get('edge_occupancy', {})
    enter_requests = input_data.get('enter_requests', [])
    active_incidents = input_data.get('active_incidents', [])

    # --- Morning Rush map constants (S3-S4) ---
    # EdgeID: (from_node, to_node, lane_count, cap_per_lane, to_signalized_node)
    EDGES = {
        'E1':  ('N1','N2',1,2, False),
        'E2':  ('N2','N3',2,2, True),
        'E3':  ('N3','N4',2,2, True),
        'E4':  ('N4','N5',1,2, False),
        'E5':  ('N5','N3',2,2, True),
        'E6':  ('N2','N6',1,1, False),
        'E7':  ('N3','N7',1,1, False),
        'E8':  ('N3','N8',1,1, False),
        'E9':  ('N4','N9',2,2, False),  # downstream N9 is HUB; signals only defined for N3/N4 in S5-S7
        'E10': ('N9','N3',2,2, True),
        'E11': ('N5','N10',1,1, False),
        'E12': ('N10','N3',1,1, True),
        'E13': ('N2','N1',1,2, False),
        'E14': ('N3','N2',2,2, False),
        'E15': ('N4','N3',2,2, True),
        'E16': ('N3','N5',2,2, False),
        'E17': ('N6','N2',1,1, False),
        'E18': ('N7','N3',1,1, True),
        'E19': ('N8','N3',1,1, True),
        'E20': ('N9','N4',2,2, True),
        'E21': ('N10','N5',1,1, False),
    }

    # --- Signal programs (R32-R34, S6-S7) ---
    # N3: cycle 6, phases A,B,C with green incoming edges
    N3_CYCLE = 6
    N3_PHASES = [
        (2, set(['E2','E10'])),       # ticks 0-1 mod 6
        (2, set(['E3','E5','E12'])),  # ticks 2-3 mod 6
        (2, set(['E18','E19','E7'])), # ticks 4-5 mod 6
    ]
    # N4: cycle 4
    N4_CYCLE = 4
    N4_PHASES = [
        (2, set(['E3'])),   # ticks 0-1 mod 4
        (2, set(['E20'])),  # ticks 2-3 mod 4
    ]

    def green_edges_for_node(node_id, tick):
        if node_id == 'N3':
            x = tick % N3_CYCLE
            acc = 0
            for dur, greens in N3_PHASES:
                if acc <= x < acc + dur:
                    return greens
                acc += dur
            return set()
        if node_id == 'N4':
            x = tick % N4_CYCLE
            acc = 0
            for dur, greens in N4_PHASES:
                if acc <= x < acc + dur:
                    return greens
                acc += dur
            return set()
        return None  # unsignalized/unknown

    # --- Incident application (R41-R44) ---
    # If multiple incidents affect an edge: closure overrides; else smallest multiplier.
    def incident_effect(edge_id, tick):
        closed = False
        mult = 1.0
        for inc in active_incidents:
            if inc.get('edge_id') != edge_id:
                continue
            st = int(inc.get('start_tick'))
            en = int(inc.get('end_tick'))
            if not (st <= tick < en):
                continue
            et = inc.get('effect_type')
            if et == 'CLOSE_EDGE':
                closed = True
            elif et == 'REDUCE_CAPACITY':
                cm = float(inc.get('capacity_multiplier'))
                if cm < mult:
                    mult = cm
        return closed, mult

    decisions = []
    for req in enter_requests:
        vid = req['vehicle_id']
        eid = req['edge_id']

        if eid not in EDGES:
            # Undefined edge in this scenario; treat as denied by closure-like reason.
            decisions.append({
                'vehicle_id': vid,
                'edge_id': eid,
                'approved': False,
                'action': 'WAIT',
                'reason': 'CLOSURE',
                'effective_max_vehicles': 0,
                'occupancy_before': 0,
            })
            continue

        _frm, to_node, lanes, cap_per_lane, _to_signalized = EDGES[eid]
        baseline_max = lanes * cap_per_lane  # R26

        occ_before = len(edge_occupancy.get(eid, []))

        is_closed, mult = incident_effect(eid, t)

        # Capacity rounding behavior: floor(baseline * multiplier) (Worked Example C)
        effective_max = int(math.floor(baseline_max * mult + 1e-12))

        if is_closed:
            approved = False
            reason = 'CLOSURE'
        elif occ_before + 1 > effective_max:
            approved = False
            reason = 'CAPACITY'
        else:
            greens = green_edges_for_node(to_node, t)
            if greens is None:
                approved = True
                reason = 'APPROVED'
            else:
                if eid in greens:
                    approved = True
                    reason = 'APPROVED'
                else:
                    approved = False
                    reason = 'SIGNAL'

        decisions.append({
            'vehicle_id': vid,
            'edge_id': eid,
            'approved': bool(approved),
            'action': 'ENTER_EDGE' if approved else 'WAIT',
            'reason': reason,
            'effective_max_vehicles': int(effective_max),
            'occupancy_before': int(occ_before),
        })

    return {'decisions': decisions}
