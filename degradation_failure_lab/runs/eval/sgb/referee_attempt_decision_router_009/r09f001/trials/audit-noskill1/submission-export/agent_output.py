from typing import Any, Dict


def _get(d: Dict[str, Any], *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _decision_for_input(data: Dict[str, Any]):
    obs = data.get('observations') or {}
    event = (data.get('event') or '').strip().lower()

    # The routing card categories are fixed buckets.
    # We select the first applicable bucket in the requested order.
    # Order: bar movement/lockout/body position/command/other
    reason = ''
    red = False

    # Bar movement
    if event in ('bench', 'squat', 'deadlift'):
        if _get(obs, 'bar', 'downward_during_ascent_mm', default=0) not in (None, 0):
            red = True
            reason = 'bar movement'
        elif _get(obs, 'bar', 'downward_during_ascent_cm', default=0) not in (None, 0):
            red = True
            reason = 'bar movement'

    # Lockout
    if not red and event == 'bench':
        left = _get(obs, 'lockout', 'left_elbow_locked', default=None)
        right = _get(obs, 'lockout', 'right_elbow_locked', default=None)
        both = _get(obs, 'lockout', 'both_locked_simultaneously', default=None)
        if both is False or left is False or right is False:
            red = True
            reason = 'lockout'

    # Body position
    if not red and event in ('bench', 'squat', 'deadlift'):
        body = obs.get('body_contact') or {}
        feet = obs.get('feet') or {}
        squat = obs.get('squat_depth') or {}
        if body.get('buttocks_up') or body.get('head_up'):
            red = True
            reason = 'body position'
        elif event == 'squat' and squat.get('hip_crease_below_knee') is False:
            red = True
            reason = 'body position'
        elif event in ('squat', 'deadlift') and feet.get('flat') is False:
            red = True
            reason = 'body position'

    # Command
    if not red:
        cmds = obs.get('commands') or {}
        if event == 'bench' and cmds.get('waited_for_press') is False:
            red = True
            reason = 'command'
        elif event == 'squat' and cmds.get('waited_for_start') is False:
            red = True
            reason = 'command'
        elif event == 'deadlift' and cmds.get('waited_for_rack') is False:
            red = True
            reason = 'command'

    # Other
    if not red:
        spotter = obs.get('spotter') or {}
        if spotter.get('bar_touched_after_start'):
            red = True
            reason = 'other'

    decision = 'Red' if red else 'White'
    if not red:
        reason = ''
    return decision, reason


def solve(input_data):
    decision, reason = _decision_for_input(input_data or {})
    routing_card = {
        'Referee Position': input_data.get('position', ''),
        'Platform': input_data.get('platform', ''),
        'Event': input_data.get('event', ''),
        'Attempt': input_data.get('attempt', ''),
        'Decision': decision,
        'Reason if Red': reason,
        'Recipient': 'Recorder',
        'Submission': 'Immediate'
    }
    return {
        'routing_card': routing_card,
        'decision': decision,
        'reason': reason,
    }
