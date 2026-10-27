from typing import Any, Dict, List


def solve(input_data: Dict[str, Any]) -> Dict[str, Any]:
    players: List[str] = input_data.get('players', [])
    turn_log: List[Dict[str, Any]] = input_data.get('turn_log', [])

    n = len(players)
    if n == 0 or not turn_log:
        return {
            'end_trigger': {'turn_index': -1, 'player': None, 'conditions_met': []},
            'scheduled_turns_after_trigger': [],
            'markers': {},
            'pile_recycled': False,
        }

    player_index = {p: i for i, p in enumerate(players)}

    trigger_idx = None
    trigger_turn = None
    trigger_conditions = []
    for i, turn in enumerate(turn_log):
        conds = []
        if turn.get('supported_objectives', 0) >= 1:
            conds.append(1)
        if turn.get('zoo_full', False):
            conds.append(2)
        if turn.get('pile_empty', False):
            conds.append(3)
        if conds:
            trigger_idx = i
            trigger_turn = turn
            trigger_conditions = conds
            break

    if trigger_turn is None:
        return {
            'end_trigger': {'turn_index': -1, 'player': None, 'conditions_met': []},
            'scheduled_turns_after_trigger': [],
            'markers': {},
            'pile_recycled': False,
        }

    trigger_player = trigger_turn['player']
    markers = {p: 0 for p in players}
    scheduled = []
    pile_recycled = False

    has_12 = any(c in (1, 2) for c in trigger_conditions)
    if has_12:
        markers[trigger_player] = 2
        start = (player_index[trigger_player] + 1) % n
        for offset in range(n - 1):
            scheduled.append(players[(start + offset) % n])
        if trigger_turn.get('pile_empty', False):
            pile_recycled = True

        final_turns = turn_log[trigger_idx + 1: trigger_idx + 1 + len(scheduled)]
        for turn in final_turns:
            conds = []
            if turn.get('supported_objectives', 0) >= 1:
                conds.append(1)
            if turn.get('zoo_full', False):
                conds.append(2)
            if turn.get('pile_empty', False):
                conds.append(3)
            if any(c in (1, 2) for c in conds):
                markers[turn['player']] = 1
    else:
        scheduled = []

    return {
        'end_trigger': {
            'turn_index': trigger_idx,
            'player': trigger_player,
            'conditions_met': trigger_conditions,
        },
        'scheduled_turns_after_trigger': scheduled,
        'markers': markers,
        'pile_recycled': pile_recycled,
    }
