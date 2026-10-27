from typing import Any, Dict, List


def solve(input_data: Dict[str, Any]) -> Dict[str, Any]:
    players: List[str] = input_data.get('players', [])
    turn_log: List[Dict[str, Any]] = input_data.get('turn_log', [])

    end_trigger = {
        'turn_index': -1,
        'player': None,
        'conditions_met': [],
    }
    scheduled_turns_after_trigger: List[str] = []
    markers: Dict[str, int] = {p: 0 for p in players}
    pile_recycled = False

    trigger_idx = None
    trigger_turn = None
    trigger_conditions = []

    for i, turn in enumerate(turn_log):
        conds = []
        if turn.get('supported_objectives', 0) >= 4:
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

    if trigger_idx is None:
        return {
            'end_trigger': end_trigger,
            'scheduled_turns_after_trigger': scheduled_turns_after_trigger,
            'markers': markers,
            'pile_recycled': pile_recycled,
        }

    end_trigger = {
        'turn_index': trigger_idx,
        'player': trigger_turn['player'],
        'conditions_met': sorted(trigger_conditions),
    }

    has_1_or_2 = any(c in (1, 2) for c in trigger_conditions)
    if has_1_or_2:
        if trigger_turn.get('pile_empty', False):
            pile_recycled = True
        if players:
            start = (players.index(trigger_turn['player']) + 1) % len(players)
            ordered = players[start:] + players[:start]
            scheduled_turns_after_trigger = [p for p in ordered if p != trigger_turn['player']]
        markers[trigger_turn['player']] = 10

        for p in scheduled_turns_after_trigger:
            for turn in turn_log[trigger_idx + 1:]:
                if turn.get('player') == p:
                    if turn.get('supported_objectives', 0) >= 4 or turn.get('zoo_full', False):
                        markers[p] = 5
                    break

    return {
        'end_trigger': end_trigger,
        'scheduled_turns_after_trigger': scheduled_turns_after_trigger,
        'markers': markers,
        'pile_recycled': pile_recycled,
    }
