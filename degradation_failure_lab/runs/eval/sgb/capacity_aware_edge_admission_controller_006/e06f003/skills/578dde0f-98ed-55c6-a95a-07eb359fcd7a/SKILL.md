---
id: "578dde0f-98ed-55c6-a95a-07eb359fcd7a"
name: "Incident Effect Application During Resolution Phase"
description: "Applies active incident effects to edges during the Incident Resolution Phase of each tick, honoring StartTick/EndTick windows and reverting to baseline when expired. Use when advancing simulation ticks with active or scheduled incidents."
version: "0.1.0"
tags:
  - "traffic_simulation"
  - "incident_handling"
  - "tick_update"
  - "edge_capacity"
triggers:
  - "A tick is being processed and incidents exist"
  - "An incident's StartTick or EndTick boundary is reached"
examples:
  - input: "Tick t within [StartTick, EndTick) for a REDUCE_CAPACITY incident with CapacityMultiplier 0.5 on an edge."
    output: "Edge capacity scaled to 50% of baseline for that tick."
    notes: "Effect applied during Incident Resolution Phase."
  - input: "Tick t >= EndTick for a CLOSE_EDGE incident with no other active incident on the edge."
    output: "Edge reverted to baseline attributes; new entries permitted."
    notes: "EndTick is exclusive."
---

# Incident Effect Application During Resolution Phase

Applies active incident effects to edges during the Incident Resolution Phase of each tick, honoring StartTick/EndTick windows and reverting to baseline when expired. Use when advancing simulation ticks with active or scheduled incidents.

## Prompt

During the Incident Resolution Phase of tick t, for each incident evaluate whether StartTick <= t < EndTick. If active, apply its effect to the affected edge: for CLOSE_EDGE, block new vehicle entry while allowing vehicles already on the edge to continue; for REDUCE_CAPACITY, apply the CapacityMultiplier to the edge capacity. If t >= EndTick, revert the edge to its baseline attributes unless another active incident modifies it. Update edge attributes accordingly and report the resulting state.

## Objective

Correctly apply and expire incident effects on edges per tick.
## Applicable Signals

- Active or scheduled incidents present at current tick
- Tick equals an incident StartTick or reaches EndTick

## Contraindications

- No incidents are defined or active
- Outside the Incident Resolution Phase

## Intervention Moves

- Check StartTick <= t < EndTick for each incident
- Apply CLOSE_EDGE by blocking new entries while allowing on-edge vehicles to continue
- Apply REDUCE_CAPACITY by scaling edge capacity with CapacityMultiplier
- Revert edge to baseline when t >= EndTick unless another active incident applies

## Workflow Steps

- Identify all incidents affecting edges at tick t.
- For each incident, test whether StartTick <= t < EndTick.
- If active, apply the effect: CLOSE_EDGE blocks new entries (existing on-edge vehicles continue); REDUCE_CAPACITY scales capacity by CapacityMultiplier.
- If t >= EndTick, revert the edge to baseline attributes unless another active incident modifies it.
- Record updated edge attributes for the tick.

## Constraints

- EndTick is exclusive.
- CapacityMultiplier must be in (0,1].
- CLOSE_EDGE does not stop vehicles already on the edge.

## Cautions

- Multiple incidents may affect the same edge; baseline reversion applies only if no other active incident modifies it.

## Output Contract

- Edge attributes updated to reflect active incidents or reverted to baseline.

## Example Therapist Responses

### Example 1

- Client/Input: Tick t within [StartTick, EndTick) for a REDUCE_CAPACITY incident with CapacityMultiplier 0.5 on an edge.
- Therapist/Output: Edge capacity scaled to 50% of baseline for that tick.
- Notes: Effect applied during Incident Resolution Phase.

### Example 2

- Client/Input: Tick t >= EndTick for a CLOSE_EDGE incident with no other active incident on the edge.
- Therapist/Output: Edge reverted to baseline attributes; new entries permitted.
- Notes: EndTick is exclusive.

## Triggers

- A tick is being processed and incidents exist
- An incident's StartTick or EndTick boundary is reached

## Examples

### Example 1

Input:

  Tick t within [StartTick, EndTick) for a REDUCE_CAPACITY incident with CapacityMultiplier 0.5 on an edge.

Output:

  Edge capacity scaled to 50% of baseline for that tick.

Notes:

  Effect applied during Incident Resolution Phase.

### Example 2

Input:

  Tick t >= EndTick for a CLOSE_EDGE incident with no other active incident on the edge.

Output:

  Edge reverted to baseline attributes; new entries permitted.

Notes:

  EndTick is exclusive.
