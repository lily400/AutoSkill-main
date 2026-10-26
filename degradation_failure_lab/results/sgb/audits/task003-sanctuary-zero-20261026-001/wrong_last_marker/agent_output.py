def solve(input_data):
    # Sanctuary: End of the game and final scoring (rulebook p.8)
    # Constants from the document:
    OBJ_TARGET = 4          # End condition (1): supported 4 objectives
    MARKER_TRIGGER = 10     # "take the 10-point End-of-game marker" when triggering via (1) and/or (2)
    MARKER_LAST_TURN = 10    # "take a 5-point End-of-game marker" if meeting (1)/(2) on last extra turn

    players = input_data['players']
    turn_log = input_data['turn_log']

    idx_of = {p: i for i, p in enumerate(players)}

    def conds(turn):
        c = []
        if turn.get('supported_objectives', 0) >= OBJ_TARGET:
            c.append(1)
        if bool(turn.get('zoo_full', False)):
            c.append(2)
        if bool(turn.get('pile_empty', False)):
            c.append(3)
        return c

    # 1) Find first trigger
    trigger_i = None
    trigger_conds = None
    trigger_player = None
    for i, t in enumerate(turn_log):
        c = conds(t)
        if c:
            trigger_i = i
            trigger_conds = c
            trigger_player = t['player']
            break

    if trigger_i is None:
        # No end triggered in provided log
        return {
            'end_trigger': None,
            'scheduled_turns_after_trigger': [],
            'markers': {p: 0 for p in players},
            'pile_recycled': False
        }

    markers = {p: 0 for p in players}

    # 2) Determine scheduling type
    trigger_has_12 = (1 in trigger_conds) or (2 in trigger_conds)
    trigger_has_3 = (3 in trigger_conds)

    scheduled = []
    pile_recycled = False

    if trigger_has_12:
        # Triggering player takes 10-point marker
        markers[trigger_player] = MARKER_TRIGGER

        # Everyone else gets 1 more turn, excluding trigger player, clockwise starting next
        start = (idx_of[trigger_player] + 1) % len(players)
        for k in range(len(players) - 1):
            scheduled.append(players[(start + k) % len(players)])

        # Pile recycling clause: if pile empty after you have triggered end of game
        # (i.e., on trigger turn when end triggered via 1/2 and pile is empty)
        if trigger_has_3:
            pile_recycled = True

        # 3) Assign 5-point marker to players who meet 1/2 on their last extra turn
        # We interpret "your last turn" as the single extra turn you get after someone else triggered.
        # So check each player's extra turn (if present in log) and award 5 if they meet 1/2.
        extra_turns_in_log = turn_log[trigger_i + 1: trigger_i + 1 + len(scheduled)]
        for t in extra_turns_in_log:
            p = t['player']
            c = conds(t)
            if (1 in c) or (2 in c):
                # Only if they don't already have 10 (they shouldn't, since trigger player excluded)
                if markers[p] == 0:
                    markers[p] = MARKER_LAST_TURN

    else:
        # Trigger did not include 1/2. If condition 3 happens before anyone meets 1 or 2,
        # game ends immediately after that turn.
        # Since this is the first trigger and it lacks 1/2, it must be condition 3-only.
        scheduled = []
        pile_recycled = False

    return {
        'end_trigger': {
            'turn_index': trigger_i,
            'player': trigger_player,
            'conditions_met': trigger_conds
        },
        'scheduled_turns_after_trigger': scheduled,
        'markers': markers,
        'pile_recycled': pile_recycled
    }
