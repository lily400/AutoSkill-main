---
id: "abcdd505-af46-547b-ab28-ef5fd68f2e3a"
name: "CLOSE_EDGE Entry Restriction Rule"
description: "Enforces that while a CLOSE_EDGE incident is active on an edge, vehicles already on the edge continue to travel normally but no new vehicles may enter. Use when routing or admitting vehicles onto an edge under an active closure."
version: "0.1.0"
tags:
  - "traffic_simulation"
  - "incident_handling"
  - "constraint_enforcement"
  - "edge_closure"
  - "vehicle_admission"
triggers:
  - "A CLOSE_EDGE incident is active on a target edge"
  - "A vehicle is about to enter an edge"
examples:
  - input: "A CLOSE_EDGE incident is active on edge E5 for the current tick; a vehicle requests entry to E5."
    output: "Entry denied; the vehicle is not admitted to E5, while vehicles already on E5 continue traveling."
    notes: "Applies only while StartTick <= t < EndTick."
---

# CLOSE_EDGE Entry Restriction Rule

Enforces that while a CLOSE_EDGE incident is active on an edge, vehicles already on the edge continue to travel normally but no new vehicles may enter. Use when routing or admitting vehicles onto an edge under an active closure.

## Prompt

Before admitting any vehicle onto a target edge, check whether a CLOSE_EDGE incident is active on that edge for the current tick (StartTick <= t < EndTick). If active, block all new vehicle entries while allowing vehicles already on the edge to continue traveling as normal. If the incident window has expired (t >= EndTick) or the incident is REDUCE_CAPACITY rather than CLOSE_EDGE, do not apply this restriction.

## Objective

Prevent new vehicle entry onto closed edges while allowing existing traffic to proceed.
## Applicable Signals

- CLOSE_EDGE incident active on the target edge
- Vehicle attempting to enter an edge
- Current tick within incident window (StartTick <= t < EndTick)

## Contraindications

- Incident is REDUCE_CAPACITY rather than CLOSE_EDGE
- Incident window has expired (t >= EndTick)

## Intervention Moves

- Check active incidents on the target edge before admitting a vehicle
- Block new entries while CLOSE_EDGE is active
- Allow vehicles already on the edge to continue traveling normally

## Workflow Steps

- Identify the target edge for the vehicle entry.
- Determine whether a CLOSE_EDGE incident is active on that edge for the current tick (StartTick <= t < EndTick).
- If active, deny new vehicle entry to the edge.
- Leave vehicles already on the edge unaffected so they continue traveling as normal.
- If the incident window has expired or the effect is not CLOSE_EDGE, do not apply this restriction.

## Constraints

- Restriction applies only while StartTick <= t < EndTick.
- Only CLOSE_EDGE incidents trigger this admission block.
- Vehicles already on the edge must not be stopped by this rule.

## Cautions

- Do not confuse CLOSE_EDGE with REDUCE_CAPACITY; capacity reduction does not block entry.
- Re-evaluate each tick since the incident window is exclusive at EndTick.

## Output Contract

- No new vehicles admitted to a closed edge; on-edge vehicles unaffected and continue traveling normally.

## Example Therapist Responses

### Example 1

- Client/Input: A CLOSE_EDGE incident is active on edge E5 for the current tick; a vehicle requests entry to E5.
- Therapist/Output: Entry denied; the vehicle is not admitted to E5, while vehicles already on E5 continue traveling.
- Notes: Applies only while StartTick <= t < EndTick.

## Triggers

- A CLOSE_EDGE incident is active on a target edge
- A vehicle is about to enter an edge

## Examples

### Example 1

Input:

  A CLOSE_EDGE incident is active on edge E5 for the current tick; a vehicle requests entry to E5.

Output:

  Entry denied; the vehicle is not admitted to E5, while vehicles already on E5 continue traveling.

Notes:

  Applies only while StartTick <= t < EndTick.
