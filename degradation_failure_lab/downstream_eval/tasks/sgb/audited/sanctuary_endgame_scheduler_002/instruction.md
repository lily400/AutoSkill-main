# sanctuary_endgame_scheduler_002

## Task Type

function

## Task

Implement `solve(input_data)` that acts as an **End-of-Game Trigger & Extra-Turn Scheduler** for a turn-based tile game.

INPUT: a dict with keys:
- 'players': list of player ids (strings) in clockwise order.
- 'turn_log': list of turn dicts in chronological order. Each turn dict has:
  - 'player': player id (string)
  - 'supported_objectives': int (how many conservation objectives this player has supported at end of this turn)
  - 'zoo_full': bool (whether this player's zoo map is completely covered at end of this turn)
  - 'pile_empty': bool (whether the face-down pile is empty at end of this turn)
  - 'discard_count': int (number of tiles currently in discard pile at end of this turn)

OUTPUT: a dict with keys:
- 'end_trigger': dict with:
  - 'turn_index': int (index in turn_log where the game end was triggered)
  - 'player': player id who triggered the end
  - 'conditions_met': list of ints (subset of {1,2,3} that were met at that end-of-turn check)
- 'scheduled_turns_after_trigger': list of player ids in the exact order of turns that must still be played after the trigger turn (may be empty)
- 'markers': dict mapping player id -> int end-of-game marker points awarded (0 if none)
- 'pile_recycled': bool indicating whether the discard pile must be shuffled to form a new pile due to the pile being empty after an end was triggered

RULES (from the document):
- At the end of each turn, check whether at least one end condition is met; the first time this happens triggers the end.
- End conditions are: (1) supported all objectives; (2) zoo map completely covered; (3) face-down pile empty.
- If the trigger includes condition (1) and/or (2): the triggering player takes the higher-value end-of-game marker, and then every other player gets exactly one more turn (excluding the triggering player), in clockwise order starting with the next player.
- If the trigger is condition (3) occurring before any trigger of (1) or (2): the game ends immediately after that turn (no extra turns).
- If the pile is empty after the end has been triggered (i.e., on the trigger turn when (1)/(2) triggered and pile is empty), the discard pile is shuffled to form a new pile.
- During the extra-turn phase after someone else triggered via (1)/(2), if a player meets condition (1) and/or (2) on their own final extra turn, they take the lower-value end-of-game marker.

Notes:
- Do not perform scoring; only schedule remaining turns and assign end-of-game markers.
- If multiple conditions are met on the trigger turn, include all of them in 'conditions_met' but apply the correct scheduling/marker rules.
- Assume turn_log is long enough to include all extra turns that were actually played; your job is to compute what should be scheduled and which markers should be awarded according to the rules.

## Expected Output Summary

```json
{
  "format": "dict",
  "key_results": {
    "end_trigger": "dict",
    "scheduled_turns_after_trigger": "list",
    "markers": "dict",
    "pile_recycled": "bool"
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
