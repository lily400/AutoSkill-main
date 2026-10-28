from typing import Any, Dict


def _get(d: Dict[str, Any], *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _has_true(obs: Dict[str, Any], path: tuple) -> bool:
    val = _get(obs, *path, default=False)
    return bool(val)


def solve(input_data):
    position = input_data.get('position', '')
    platform = input_data.get('platform', '')
    event = input_data.get('event', '')
    attempt = input_data.get('attempt', '')
    observations = input_data.get('observations', {}) or {}

    decision = 'White'
    reason = ''

    # Bench press judging priority: commands -> bar path -> lockout -> body position.
    if event == 'Bench':
        cmds = observations.get('commands', {}) or {}
        waited_start = cmds.get('waited_for_start', True)
        waited_press = cmds.get('waited_for_press', True)
        waited_rack = cmds.get('waited_for_rack', True)

        if not (waited_start and waited_press and waited_rack):
            decision = 'Red'
            reason = 'command fault'
        else:
            bar = observations.get('bar', {}) or {}
            down_mm = bar.get('downward_during_ascent_mm')
            down_cm = bar.get('downward_during_ascent_cm')
            downward = False
            if down_mm is not None:
                downward = downward or float(down_mm) > 0
            if down_cm is not None:
                downward = downward or float(down_cm) > 0

            if downward:
                decision = 'Red'
                reason = 'downward bar movement during press'
            else:
                lockout = observations.get('lockout', {}) or {}
                body = observations.get('body_contact', {}) or {}
                feet = observations.get('feet', {}) or {}

                incomplete_lockout = False
                if lockout:
                    if lockout.get('both_locked_simultaneously') is False:
                        incomplete_lockout = True
                    if lockout.get('right_elbow_locked') is False or lockout.get('left_elbow_locked') is False:
                        incomplete_lockout = True
                    if bar.get('top_motionless') is False:
                        incomplete_lockout = True

                if incomplete_lockout:
                    decision = 'Red'
                    reason = 'incomplete lockout / not motionless at top'
                else:
                    body_fault = False
                    if body.get('buttocks_up'):
                        body_fault = True
                    if body.get('head_up'):
                        body_fault = True
                    if body.get('shoulders_contact') is False:
                        body_fault = True
                    if feet.get('flat') is False:
                        body_fault = True
                    if feet.get('moved_after_command_cm', 0) and float(feet.get('moved_after_command_cm', 0)) > 0:
                        body_fault = True
                    if feet.get('slide_lateral_cm', 0) and float(feet.get('slide_lateral_cm', 0)) > 0:
                        body_fault = True

                    if body_fault:
                        decision = 'Red'
                        reason = 'buttocks/feet/head/shoulders position fault'

    else:
        # For non-bench events, use any directly observable technical faults if present.
        # Keep the output conservative when no fault is explicitly evidenced.
        if _has_true(observations, ('commands', 'waited_for_start')) is False:
            decision = 'Red'
            reason = 'command fault'
        elif _has_true(observations, ('bar', 'dip_detected')):
            decision = 'Red'
            reason = 'downward bar movement during press'
        elif observations.get('lockout'):
            lockout = observations.get('lockout', {}) or {}
            if lockout.get('both_locked_simultaneously') is False or lockout.get('right_elbow_locked') is False or lockout.get('left_elbow_locked') is False:
                decision = 'Red'
                reason = 'incomplete lockout / not motionless at top'
        elif observations.get('body_contact'):
            body = observations.get('body_contact', {}) or {}
            if body.get('buttocks_up') or body.get('head_up') or body.get('shoulders_contact') is False:
                decision = 'Red'
                reason = 'buttocks/feet/head/shoulders position fault'
        elif observations.get('feet'):
            feet = observations.get('feet', {}) or {}
            if feet.get('flat') is False or float(feet.get('moved_after_command_cm', 0) or 0) > 0 or float(feet.get('slide_lateral_cm', 0) or 0) > 0:
                decision = 'Red'
                reason = 'buttocks/feet/head/shoulders position fault'

    routing_card = {
        'Referee Position': position,
        'Platform': platform,
        'Event': event,
        'Attempt': attempt,
        'Decision': decision,
        'Reason if Red': reason if decision == 'Red' else '',
        'Recipient': 'Tournament Director',
        'Submission': 'Immediate'
    }

    return {
        'routing_card': routing_card,
        'decision': decision,
        'reason': reason if decision == 'Red' else ''
    }

