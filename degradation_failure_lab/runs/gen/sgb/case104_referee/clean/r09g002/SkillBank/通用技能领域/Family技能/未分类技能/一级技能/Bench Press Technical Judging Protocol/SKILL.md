---
id: "3e5cbcb7-9334-5e9f-9eaf-eff81c412c4c"
name: "Bench Press Technical Judging Protocol"
description: "Apply bench-press competition standards to render a defensible White/Red verdict on a completed attempt by checking commands, bar path, lockout, and body position, then recording a single red-reason category when applicable."
version: "0.1.0"
tags:
  - "powerlifting"
  - "bench_press"
  - "technical_judging"
  - "rule_application"
  - "referee_decision"
  - "未分类技能"
  - "profile:rule_system_application_game_mechanics_2::未分类技能"
triggers:
  - "A bench press attempt has concluded and a verdict is required"
  - "A coach protest or automated overlay disputes a technical fault on a bench attempt"
  - "A referee must classify a red reason for a bench attempt"
examples:
  - input: "Coach protests that the micro-dip was camera wobble and the foot slide was negligible; overlay reports no dip above a 3 mm threshold."
    output: "Red — downward bar movement during press. The observed dip of the whole bar during ascent governs; the overlay threshold may under-report short dips and the protest claim does not overturn the observed fault."
    notes: "Overlay and protest are evidence, not verdicts."
---

# Bench Press Technical Judging Protocol

Apply bench-press competition standards to render a defensible White/Red verdict on a completed attempt by checking commands, bar path, lockout, and body position, then recording a single red-reason category when applicable.

## Prompt

When a bench press attempt has concluded and a verdict is required, evaluate the attempt against the bench standards in a fixed order: commands (Start, Press, Rack — lifter must wait for each), bar path (any downward movement of the whole bar during the ascent is a failed attempt), lockout (arms fully extended and bar motionless at the top before the rack command), and body position (head, shoulders, buttocks in contact with the bench; feet flat on the platform; declared foot blocks must stay flat and unmoved). Weigh coach protests and automated overlay findings as evidence, not as verdicts: a threshold-based overlay may under-report short-duration dips, and a protest claim does not by itself overturn an observed fault. Render White or Red; if Red, select one reason category (downward bar movement during press; incomplete lockout / not motionless at top; buttocks/feet/head/shoulders position fault; command fault; other with brief note). Do not use for squat or deadlift attempts or for purely administrative matters.

## Objective

Produce a defensible White/Red decision for a bench press attempt against the rulebook.
## Applicable Signals

- Bench press attempt concluded with verdict pending
- Dispute over bar dip, lockout, position, or commands
- Conflicting evidence between coach protest and automated overlay

## Contraindications

- Event is squat or deadlift
- Only administrative or scheduling matters are at issue
- No completed attempt to evaluate

## Intervention Moves

- Verify each required command was given and awaited
- Inspect bar path for downward movement of the whole bar during ascent
- Check full arm extension and motionless bar at top before rack command
- Check head, shoulders, buttocks contact and flat, stable feet (including declared foot blocks)
- Weigh protest and overlay evidence against observed standards
- Assign White or Red and select a single red-reason category

## Workflow Steps

- Confirm the attempt has concluded and the event is bench press.
- Check command compliance: Start, Press, Rack each given and awaited.
- Check bar path: any downward movement of the whole bar during ascent is a failed attempt.
- Check lockout: arms fully extended and bar motionless at top before the rack command.
- Check position: head, shoulders, buttocks in contact with bench; feet flat on platform; declared foot blocks flat and unmoved.
- Evaluate protest and overlay evidence, noting overlay calibration limits and that a protest claim alone does not overturn an observed fault.
- Render White or Red; if Red, select one reason category and record it for the Tournament Director.

## Constraints

- Judge against the stated bench standards, not against protest assertions.
- Select exactly one red-reason category when the decision is Red.
- Treat automated overlay thresholds as potentially under-reporting short-duration dips.
- Foot blocks are only relevant if declared; undeclared blocks are not permitted.

## Cautions

- Camera wobble or glare may distort evidence; distinguish artifact claims from observed faults.
- A negligible-looking foot slide still requires checking that contact remained flat and continuous.
- Do not let irrelevant materials (schedules, sponsor sheets) influence the technical verdict.

## Output Contract

- A White/Red decision for the bench attempt, with a single selected red-reason category when Red, recorded for the Tournament Director immediately after the attempt concludes.

## Example Therapist Responses

### Example 1

- Client/Input: Coach protests that the micro-dip was camera wobble and the foot slide was negligible; overlay reports no dip above a 3 mm threshold.
- Therapist/Output: Red — downward bar movement during press. The observed dip of the whole bar during ascent governs; the overlay threshold may under-report short dips and the protest claim does not overturn the observed fault.
- Notes: Overlay and protest are evidence, not verdicts.

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- A bench press attempt has concluded and a verdict is required
- A coach protest or automated overlay disputes a technical fault on a bench attempt
- A referee must classify a red reason for a bench attempt

## Examples

### Example 1

Input:

  Coach protests that the micro-dip was camera wobble and the foot slide was negligible; overlay reports no dip above a 3 mm threshold.

Output:

  Red — downward bar movement during press. The observed dip of the whole bar during ascent governs; the overlay threshold may under-report short dips and the protest claim does not overturn the observed fault.

Notes:

  Overlay and protest are evidence, not verdicts.
