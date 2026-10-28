---
id: "66bc7195-e00f-5601-8aa1-5365a6991d21"
name: "Body Position and Foot Contact Check"
description: "Verify head, shoulders, and buttocks contact with the bench and flat, stable feet (including declared foot blocks) to determine whether a position or foot-contact red applies. Use when position faults or foot-slide claims are raised."
version: "0.1.0"
tags:
  - "powerlifting"
  - "bench_press"
  - "position_check"
  - "foot_contact"
  - "technical_judging"
triggers:
  - "Coach argues foot slide was negligible and foot always flat"
  - "Side camera shows possible micro-slide or buttocks lift"
  - "Position fault is raised as a basis for a red"
examples:
  - input: "Coach claims the foot slide was negligible and the foot was always flat; side camera shows a micro-slide with continuous flat contact."
    output: "No position/foot-contact red: feet remained flat with continuous contact; micro-slide is negligible and not a position change."
    notes: "Distinguishes negligible micro-movement from a fault."
---

# Body Position and Foot Contact Check

Verify head, shoulders, and buttocks contact with the bench and flat, stable feet (including declared foot blocks) to determine whether a position or foot-contact red applies. Use when position faults or foot-slide claims are raised.

## Prompt

Apply the bench position criteria to the attempt under review. Check head, shoulders, and buttocks contact with the bench surface; check feet are flat on the platform and do not change position during the attempt; account for any declared foot blocks. Use available camera evidence (e.g., side view) to assess buttocks lift and foot slide. Distinguish negligible, continuous-contact micro-movement from an actual position fault. Return a determination of whether a position/foot-contact red applies, with the specific criterion cited.

## Objective

Detect buttocks lift, loss of bench contact, or foot position faults.
## Applicable Signals

- Claim that foot slide was negligible and foot remained flat
- Side camera evidence of micro-slide or possible buttocks lift
- Declared or undeclared foot blocks in question

## Contraindications

- Fault under review is bar path or lockout
- Fault under review is a command fault

## Intervention Moves

- Confirm head, shoulders, and buttocks remain in contact with the bench surface
- Confirm feet are flat on the platform and do not change position during the attempt
- Check whether foot blocks were declared and whether feet stayed flat on them
- Assess camera evidence for buttocks lift and foot slide, distinguishing continuous-contact micro-movement from a fault
- State whether a position/foot-contact red applies and cite the specific criterion

## Workflow Steps

- Identify the position criteria in scope: bench contact (head, shoulders, buttocks) and foot contact (flat, stable, no position change).
- Check declared foot blocks; if none declared, feet must be flat on the platform.
- Review camera evidence for buttocks lift and foot slide.
- Judge whether observed movement is a fault or negligible continuous-contact micro-movement.
- Return the determination: position/foot-contact red applies or not, with the criterion cited.

## Constraints

- Feet must remain flat and not change position during the attempt.
- Foot blocks are permitted only if declared.
- Head, shoulders, and buttocks must be in contact with the bench surface.

## Cautions

- Do not conflate negligible continuous-contact micro-slide with a position fault without clear evidence.
- Do not extend this check to bar-path, lockout, or command faults.

## Output Contract

- Determination of whether a position/foot-contact red applies, citing the specific criterion (bench contact or foot contact).

## Example Therapist Responses

### Example 1

- Client/Input: Coach claims the foot slide was negligible and the foot was always flat; side camera shows a micro-slide with continuous flat contact.
- Therapist/Output: No position/foot-contact red: feet remained flat with continuous contact; micro-slide is negligible and not a position change.
- Notes: Distinguishes negligible micro-movement from a fault.

## Triggers

- Coach argues foot slide was negligible and foot always flat
- Side camera shows possible micro-slide or buttocks lift
- Position fault is raised as a basis for a red

## Examples

### Example 1

Input:

  Coach claims the foot slide was negligible and the foot was always flat; side camera shows a micro-slide with continuous flat contact.

Output:

  No position/foot-contact red: feet remained flat with continuous contact; micro-slide is negligible and not a position change.

Notes:

  Distinguishes negligible micro-movement from a fault.
