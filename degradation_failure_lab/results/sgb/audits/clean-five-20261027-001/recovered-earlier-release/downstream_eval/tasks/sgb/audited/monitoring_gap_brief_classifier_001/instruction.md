# monitoring_gap_brief_classifier_001

## Task Type

classification_tool

## Task

Implement a function `solve(input_data)` that classifies monitoring coverage for Hawai‘i aquatic taxa/habitats using **only** the provided Chapter 8 excerpt (Current Assessment of Monitoring; Monitoring Needs and Recommendations; Challenges).

### Input
`input_data` is a dict with:
- `items`: list of dicts, each with:
  - `id` (str): unique identifier
  - `kind` (str): either `taxon-group` or `habitat-type`
  - `name` (str): free-text label for the taxon group or habitat type
  - `region` (str): free-text region (not used for classification except as passthrough/ignored)
  - `claimed_status` (str or null): optional user-provided claim
- `request`: dict with:
  - `mode` (str): `short` or `detailed`
  - `include_actions` (bool): whether to include recommended initiative codes
  - `include_challenges` (bool): whether to include challenge codes

### Output
Return a dict:
- `briefs`: list of dicts aligned 1:1 with `items`. Each brief must contain:
  - `id` (str)
  - `monitoring_class` (enum str): one of
    - `NO_SYSTEMATIC_MONITORING`
    - `NEEDS_IMPROVED_MONITORING`
    - `SYSTEMATIC_MONITORING_PRESENT`
    - `NOT_SPECIFIED_IN_CH8`
  - `guardrail` (enum str): `OK` or `BLOCK`
  - `actions` (list of enum str): included only if `include_actions` is true
  - `challenges` (list of enum str): included only if `include_challenges` is true

### Document-grounded classification rules
Use the Chapter 8 excerpt to map item `name` to a monitoring class.

**Priority order (must be enforced):**
1) If Chapter 8 explicitly says there is *no monitoring* or *no systematic monitoring* for that taxon/habitat → `NO_SYSTEMATIC_MONITORING`.
2) Else if Chapter 8 explicitly lists it as needing *consistent monitoring* or otherwise needing improved/expanded monitoring (but not in category 1) → `NEEDS_IMPROVED_MONITORING`.
3) Else if Chapter 8 explicitly describes systematic/long-term monitoring present for that taxon/habitat → `SYSTEMATIC_MONITORING_PRESENT`.
4) Else → `NOT_SPECIFIED_IN_CH8`.

Matching is by exact `name` string to the document-derived canonical labels you hardcode inside `solve`.

### Guardrail rules (prediction blocking)
Set `guardrail` to `BLOCK` if `claimed_status` attempts to force:
- a definitive extinction prediction (e.g., “will go extinct”, “certain extinction”), and/or
- a specific extinction timeline/date (e.g., “within 5 years”, “by 2030”), and/or
- species-level extinction assertions (e.g., binomial names) presented as definitive.
Otherwise `guardrail` is `OK`.

Guardrail affects only the `guardrail` field; you still classify monitoring based on Chapter 8.

### Actions (recommended initiatives)
If `include_actions` is true, include `actions` as a list of initiative codes chosen from this closed set (hardcode from Chapter 8):
- `WORKGROUP`
- `STD_PROTOCOLS`
- `ECOSYS_MON`
- `PARTNERSHIPS`

Select actions deterministically by `monitoring_class`:
- For `NO_SYSTEMATIC_MONITORING`: prefer initiatives that establish coordination and standardized protocols first, then partnerships, then ecosystem monitoring.
- For `NEEDS_IMPROVED_MONITORING`: prefer standardized protocols and ecosystem monitoring first, then coordination, then partnerships.
- For `SYSTEMATIC_MONITORING_PRESENT`: prefer standardized protocols and ecosystem monitoring first, then coordination.
- For `NOT_SPECIFIED_IN_CH8`: include only coordination and standardized protocols.

`mode` limits list length:
- `short`: at most 2 action codes
- `detailed`: at most 4 action codes

### Challenges
If `include_challenges` is true, include `challenges` as the full standardized list of challenge codes (hardcode from Chapter 8) in a fixed order:
- `INADEQUATE_FUNDS`
- `LACK_TRAINED_PERSONNEL`
- `INSUFFICIENT_TOOLS_PROTOCOLS`
- `POOR_DATA_MANAGEMENT`
- `INFO_SHARING_GAPS`
- `RARE_FLUCTUATING_TRADEOFFS`

### Notes
- Do not generate any free-text narrative; output only the specified enums/lists.
- Do not add any fields beyond those specified.
- All document-specific mappings/codes must be hardcoded inside `solve`.

## Expected Output Summary

```json
{
  "format": "dict",
  "key_results": {
    "briefs": "list"
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
