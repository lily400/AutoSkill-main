---
id: "2685db91-5b0a-5d1e-81a3-170e8d51b8d1"
name: "Bar Path and Lockout Fault Check"
description: "Inspect the ascent of a press attempt for downward bar movement and verify full arm extension with a motionless bar at the top. Use when judging press-phase faults or resolving lockout disputes."
version: "0.1.0"
tags:
  - "powerlifting"
  - "bench_press"
  - "bar_path"
  - "lockout"
  - "technical_judging"
  - "未分类技能"
  - "profile:rule_system_application_game_mechanics_2::未分类技能"
triggers:
  - "Coach claims elbow was locked and bar stable"
  - "Overlay reports sub-threshold oscillation near the top"
  - "Press-phase fault or lockout dispute under review"
examples:
  - input: "Coach claims the right elbow was locked and the bar stable before rack; overlay reports top oscillation under 2 mm with a 3 mm dip threshold."
    output: "Lockout check: arms fully extended and bar motionless at top — no lockout red. Downward-movement check: no visible whole-bar dip; overlay threshold is advisory only. Determination: no bar-path or lockout red applies."
    notes: "Overlay under-reporting warning noted but did not change the visual determination."
---

# Bar Path and Lockout Fault Check

Inspect the ascent of a press attempt for downward bar movement and verify full arm extension with a motionless bar at the top. Use when judging press-phase faults or resolving lockout disputes.

## Prompt

Apply this micro-check only to the press-phase bar path and lockout question. Review the ascent for any downward movement of the whole bar, then verify arms are fully extended and the bar is held motionless at the top before the rack command. Treat automated overlay thresholds as advisory only; do not let a sub-threshold reading override a visible fault. Return a determination of whether a downward-movement red or a lockout red applies.

## Objective

Detect downward bar movement during press and incomplete lockout.
## Applicable Signals

- Dispute over whether the bar dipped during ascent
- Claim that elbows were locked and bar stable before rack
- Automated overlay reporting oscillation below its detection threshold

## Contraindications

- Fault under review is a position fault (head, shoulders, buttocks, feet)
- Fault under review is a command fault
- Question concerns equipment or foot-block declarations rather than bar path

## Intervention Moves

- Scan the full ascent for any downward movement of the whole bar
- Check that arms are fully extended at the top
- Confirm the bar is motionless at the top before the rack command
- Weigh overlay threshold findings against direct visual evidence

## Workflow Steps

- Identify the ascent window of the attempt under review.
- Inspect the ascent for any downward movement of the whole bar; any such movement constitutes a failed attempt.
- Verify arms are fully extended at the top of the press.
- Verify the bar is held motionless at the top before the rack command.
- Compare any automated overlay findings against the visual evidence, noting that threshold-based tools may under-report short-duration dips.
- Determine whether a downward-movement red or a lockout red applies and record the reason.

## Constraints

- Any downward movement of the whole bar during the ascent is a failed attempt.
- Lockout requires full arm extension and a motionless bar at the top before the rack command.
- Automated overlay thresholds are advisory and must not override visible faults.

## Cautions

- Calibration may under-report short-duration dips if lighting glare is present.
- Do not extend this check to position or command faults; route those separately.

## Output Contract

- A determination of whether a downward-movement red or a lockout red applies, with the selected reason recorded for the decision routing card.

## Example Therapist Responses

### Example 1

- Client/Input: Coach claims the right elbow was locked and the bar stable before rack; overlay reports top oscillation under 2 mm with a 3 mm dip threshold.
- Therapist/Output: Lockout check: arms fully extended and bar motionless at top — no lockout red. Downward-movement check: no visible whole-bar dip; overlay threshold is advisory only. Determination: no bar-path or lockout red applies.
- Notes: Overlay under-reporting warning noted but did not change the visual determination.

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- Coach claims elbow was locked and bar stable
- Overlay reports sub-threshold oscillation near the top
- Press-phase fault or lockout dispute under review

## Examples

### Example 1

Input:

  Coach claims the right elbow was locked and the bar stable before rack; overlay reports top oscillation under 2 mm with a 3 mm dip threshold.

Output:

  Lockout check: arms fully extended and bar motionless at top — no lockout red. Downward-movement check: no visible whole-bar dip; overlay threshold is advisory only. Determination: no bar-path or lockout red applies.

Notes:

  Overlay under-reporting warning noted but did not change the visual determination.
