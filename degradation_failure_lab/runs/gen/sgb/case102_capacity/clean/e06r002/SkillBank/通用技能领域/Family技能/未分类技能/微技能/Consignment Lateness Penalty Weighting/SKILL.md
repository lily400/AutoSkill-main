---
id: "051b46c6-eb00-5693-995a-de8aaefaff4d"
name: "Consignment Lateness Penalty Weighting"
description: "Computes lateness penalties per tick for a late consignment based on its priority tier (LOW 0.5, STANDARD 1.0, HIGH 2.0, CRITICAL 4.0). Use when tallying penalties for late consignments during objective evaluation or Network Service Score computation."
version: "0.1.0"
tags:
  - "scoring"
  - "penalty"
  - "priority"
  - "lateness"
  - "objective_evaluation"
  - "未分类技能"
  - "profile:traffic_simulation_rules::未分类技能"
triggers:
  - "A consignment is late and penalties are being tallied"
  - "Computing Network Service Score"
  - "Objective evaluation requires per-consignment lateness penalty"
examples:
  - input: "A HIGH priority consignment is 3 ticks late."
    output: "Penalty weight 2.0 per tick; total penalty = 2.0 × 3 = 6.0."
    notes: "Weight selected from the HIGH tier."
  - input: "A LOW priority consignment is 4 ticks late."
    output: "Penalty weight 0.5 per tick; total penalty = 0.5 × 4 = 2.0."
    notes: "Weight selected from the LOW tier."
---

# Consignment Lateness Penalty Weighting

Computes lateness penalties per tick for a late consignment based on its priority tier (LOW 0.5, STANDARD 1.0, HIGH 2.0, CRITICAL 4.0). Use when tallying penalties for late consignments during objective evaluation or Network Service Score computation.

## Prompt

When a consignment is late and penalties are being tallied, look up its priority tier and apply the corresponding per-tick penalty weight: LOW=0.5, STANDARD=1.0, HIGH=2.0, CRITICAL=4.0. Multiply the weight by the number of late ticks to obtain the penalty contribution. Do not apply this move to on-time consignments or when priority is undefined.

## Objective

Apply correct priority-based penalty weight per late tick.
## Applicable Signals

- Consignment status is late
- Penalty tallying is in progress
- Network Service Score is being computed

## Contraindications

- Consignment is on time
- Priority is undefined

## Intervention Moves

- Identify the consignment priority tier
- Select the matching per-tick penalty weight (LOW 0.5, STANDARD 1.0, HIGH 2.0, CRITICAL 4.0)
- Multiply weight by number of late ticks to get the penalty contribution

## Workflow Steps

- Confirm the consignment is late and penalties are being tallied.
- Read the consignment priority tier.
- Map priority to penalty weight: LOW=0.5, STANDARD=1.0, HIGH=2.0, CRITICAL=4.0.
- Multiply the weight by the count of late ticks to produce the penalty value.

## Constraints

- Use only the four defined priority tiers and their fixed weights.
- Do not assign a penalty to on-time consignments.
- Do not proceed when priority is undefined.

## Cautions

- Weights are fixed per tier; do not interpolate or invent intermediate values.

## Output Contract

- Penalty value per late tick assigned by priority tier, with the total penalty contribution for the late consignment.

## Example Therapist Responses

### Example 1

- Client/Input: A HIGH priority consignment is 3 ticks late.
- Therapist/Output: Penalty weight 2.0 per tick; total penalty = 2.0 × 3 = 6.0.
- Notes: Weight selected from the HIGH tier.

### Example 2

- Client/Input: A LOW priority consignment is 4 ticks late.
- Therapist/Output: Penalty weight 0.5 per tick; total penalty = 0.5 × 4 = 2.0.
- Notes: Weight selected from the LOW tier.

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- A consignment is late and penalties are being tallied
- Computing Network Service Score
- Objective evaluation requires per-consignment lateness penalty

## Examples

### Example 1

Input:

  A HIGH priority consignment is 3 ticks late.

Output:

  Penalty weight 2.0 per tick; total penalty = 2.0 × 3 = 6.0.

Notes:

  Weight selected from the HIGH tier.

### Example 2

Input:

  A LOW priority consignment is 4 ticks late.

Output:

  Penalty weight 0.5 per tick; total penalty = 0.5 × 4 = 2.0.

Notes:

  Weight selected from the LOW tier.
