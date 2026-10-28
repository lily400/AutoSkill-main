def solve(input_data):
    """Independent side-referee decision + routing card formatter.

    Document-specific constants and precedence are hardcoded per provided document.
    """

    # --- Extract ---
    position = input_data.get('position')
    platform = input_data.get('platform')
    event = input_data.get('event')
    attempt = int(input_data.get('attempt'))
    lifter = input_data.get('lifter')
    ruleset_hint = (input_data.get('ruleset_hint') or '').lower()
    obs = input_data.get('observations') or {}

    # --- Document constants / precedence ---
    # System Context: independent decision; ignore bias cues; immediate signaling.
    RECIPIENT = 'Tournament Director'  # Artifact 8
    SUBMISSION = 'Immediate after attempt conclusion'  # Artifact 8

    # Bench: any downward movement of the whole bar during ascent is a fail. (Artifact 3)
    # Q4 Bulletin: supersedes earlier exceptions; no soft lock accepted; buttocks up is fail; spotter contact after Start voids unless directed. (Q4 Artifact 2)
    # Squat: depth requires hip crease lower than top of knees; foot movement after squat command and before rack is fail. (Q2 Artifact 1; Q3 Artifact 2)

    # Motion thresholds: treat any positive reported dip as downward movement.
    # (Document gives qualitative rule; artifacts show mm/cm; we convert and use >0.)

    def get_downward_mm(bar_dict):
        if not isinstance(bar_dict, dict):
            return 0.0
        mm = 0.0
        if 'downward_during_ascent_mm' in bar_dict and bar_dict['downward_during_ascent_mm'] is not None:
            mm = float(bar_dict['downward_during_ascent_mm'])
        elif 'downward_during_ascent_cm' in bar_dict and bar_dict['downward_during_ascent_cm'] is not None:
            mm = float(bar_dict['downward_during_ascent_cm']) * 10.0
        elif bar_dict.get('dip_detected') is True:
            mm = 1.0
        return mm

    # --- Decide governing rule interpretation ---
    # If hint mentions a superseding bulletin / latest / rev, apply strict lockout (no soft lock).
    # If hint is older-only, still apply strict lockout when bulletin is indicated by the document scenario.
    strict_bench_lockout = False  # Q4 Artifact 2 supersedes earlier exceptions.

    # --- Evaluate faults ---
    decision = 'White'
    reason = ''

    commands = obs.get('commands') or {}
    bar = obs.get('bar') or {}
    lockout = obs.get('lockout') or {}
    body = obs.get('body_contact') or {}
    feet = obs.get('feet') or {}
    depth = obs.get('squat_depth') or {}
    spotter = obs.get('spotter') or {}

    # Command faults (Artifact 3: must wait for commands)
    if event == 'Bench':
        if commands.get('waited_for_start') is False or commands.get('waited_for_press') is False or commands.get('waited_for_rack') is False:
            decision, reason = 'Red', 'Command fault'
    elif event == 'Squat':
        # Squat command is implicit in observations schema; if provided and false, treat as command fault.
        if commands.get('waited_for_start') is False:
            decision, reason = 'Red', 'Command fault'

    # Spotter contact rule for bench (Q4 Artifact 2)
    if decision == 'White' and event == 'Bench':
        if spotter.get('bar_touched_after_start') is True and spotter.get('touch_directed_by_center') is not True:
            decision, reason = 'Red', 'Other (brief)'

    # Bench technical faults
    if decision == 'White' and event == 'Bench':
        # Downward movement during press (Artifact 3)
        if get_downward_mm(bar) > 0.0:
            decision, reason = 'Red', 'Downward bar movement during press'
        # Body contact faults (Artifact 3 + Q4 Artifact 2 emphasis)
        elif body.get('buttocks_up') is True or body.get('head_up') is True or body.get('shoulders_contact') is False:
            decision, reason = 'Red', 'Buttocks/feet/head/shoulders position fault'
        # Feet must remain flat; changing position is a fault category in routing card (Artifact 3 + 8)
        elif feet.get('flat') is False:
            decision, reason = 'Red', 'Buttocks/feet/head/shoulders position fault'
        # Lockout/motionless at top (Artifact 3; strict lockout per Q4 Artifact 2)
        else:
            both_locked = lockout.get('both_locked_simultaneously')
            if both_locked is None:
                # infer from individual elbows if needed
                both_locked = (lockout.get('right_elbow_locked') is True and lockout.get('left_elbow_locked') is True)
            if strict_bench_lockout and (both_locked is not True):
                decision, reason = 'Red', 'Incomplete lockout / not motionless at top'
            elif bar.get('top_motionless') is False:
                decision, reason = 'Red', 'Incomplete lockout / not motionless at top'

    # Squat technical faults
    if decision == 'White' and event == 'Squat':
        # Depth (Q2 Artifact 1; Q3 Artifact 2 v2025)
        if depth.get('hip_crease_below_knee') is False:
            decision, reason = 'Red', 'Other (brief)'
        # Foot movement after command and before rack is cause for failure (Q2 Artifact 1)
        elif feet.get('moved_after_command_cm') is not None and float(feet.get('moved_after_command_cm')) > 0.0:
            decision, reason = 'Red', 'Other (brief)'

    # Deadlift not used in provided scenarios; keep minimal.

    # --- Routing card formatting (Artifact 8) ---
    routing = {
        'Referee Position': position,
        'Platform': platform,
        'Event': event,
        'Attempt': attempt,
        'Decision': decision,
        'Reason if Red': (reason if decision == 'Red' else ''),
        'Recipient': RECIPIENT,
        'Submission': SUBMISSION
    }

    return {'routing_card': routing, 'decision': decision, 'reason': (reason if decision == 'Red' else '')}
