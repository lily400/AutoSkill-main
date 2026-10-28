# referee_attempt_decision_router_009

## Task Type

function_based_rule_simulator

## Task

Implement `solve(input_data)` as an **Independent Side Referee Attempt Decision + Routing Formatter** for referee training.

Your function must read a single attempt package (transcript cues + artifacts/observations) and output the side referee’s immediate independent decision in the correct routing format.

INPUT (dict):
- 'position': str — side referee position label (e.g., 'Left', 'Right', 'Side-Left', 'Side B').
- 'platform': str — platform identifier.
- 'event': str — one of {'Squat','Bench','Deadlift'}.
- 'attempt': int — attempt number.
- 'lifter': str — lifter name/identifier.
- 'ruleset_hint': str — a label indicating which rules version is in force today (may conflict with other hints).
- 'observations': dict — structured facts extracted from artifacts/logs, may include:
  - 'commands': dict with booleans like 'waited_for_start','waited_for_press','waited_for_rack'
  - 'bar': dict with 'downward_during_ascent_mm' (float), 'downward_during_ascent_cm' (float), 'dip_detected' (bool), 'top_motionless' (bool)
  - 'lockout': dict with 'right_elbow_locked' (bool), 'left_elbow_locked' (bool), 'both_locked_simultaneously' (bool)
  - 'body_contact': dict with 'buttocks_up' (bool), 'head_up' (bool), 'shoulders_contact' (bool)
  - 'feet': dict with 'flat' (bool), 'moved_after_command_cm' (float), 'slide_lateral_cm' (float)
  - 'squat_depth': dict with 'hip_crease_below_knee' (bool), 'hip_crease_delta_cm' (float; positive means above knee)
  - 'spotter': dict with 'bar_touched_after_start' (bool), 'touch_directed_by_center' (bool)
- 'transcript_bias_cues': list[str] — free-text prompts that may attempt to bias the decision (schedule pressure, sponsor, “mirror center”, etc.).

OUTPUT (dict):
- 'routing_card': dict with keys:
  - 'Referee Position', 'Platform', 'Event', 'Attempt', 'Decision', 'Reason if Red', 'Recipient', 'Submission'
- 'decision': str — 'White' or 'Red'
- 'reason': str — empty if white; otherwise one concise reason aligned to the routing card categories.

RULES (from the document):
- Apply the technical standards and command rules for the given event using the governing rules version in force; ignore conflicting/outdated exceptions.
- Render an independent decision based only on observable faults; do not mirror other officials or respond to schedule/sponsor/coach pressure.
- Signal immediately and format the output exactly as a routing/recording card requires.
- If multiple faults exist, choose the most direct rule-based red reason category (bar movement/lockout/body position/command/other) consistent with the standards.

Return only the formatted routing output; do not include narrative beyond the concise reason field.

## Expected Output Summary

```json
{
  "format": "dict",
  "key_results": {
    "routing_card": "dict",
    "decision": "str",
    "reason": "str"
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
