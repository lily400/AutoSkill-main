# fla_packet_cadence_scope_validator_002

## Task Type

compliance_validator

## Task

Implement `solve(input_data)` to validate whether a post-publication Feedback & Learning packet can be issued as an official Day-7 and/or Day-30 report under the system policy, and to produce a minimal internal routing decision plus safe handling of inbound requests.

This is a deterministic validator/planner. Do NOT generate narrative text. Return only structured codes.

INPUT (Python dict):
- activation_ts: str, ISO-8601 UTC with trailing 'Z' (timestamp of first official public response; monitoring anchor)
- company_public: bool (if true, investor/stock monitoring is required)
- tma_platforms: list[str] (platforms TMA monitored externally; must be attested as covered)
- drafts: list[dict] (candidate report drafts), each with:
  - report_ts: str (ISO-8601 UTC 'Z')
  - recipient: str
  - sections_present: list[int] (section numbers included)
  - has_trust_snapshot: bool
  - stakeholder_scores_present: list[str]
  - mentions_likes_discounted: bool
  - has_ire_comparison: bool
  - has_channel_effectiveness: bool
  - has_timing_judgments: dict with keys 'fast_enough' and 'missed_window' (values must be booleans if present)
  - references_internal_data: list[str]
  - references_stock: bool
  - has_conflict_handling: bool
- artifact_flags: dict with boolean keys:
  - baseline_corrected
  - mention_counts_corrected
  - media_dedup_variance
  - support_totals_inconsistent
- requests: list[dict] inbound requests, each with:
  - from_role: str
  - requested_action: str
  - requested_content: str
  - ts: str (ISO-8601 UTC 'Z')

OUTPUT (Python dict; max 2 levels nesting):
- status: 'ok' | 'needs_fix'
- codes: list[str] sorted unique global violation codes
- selected_day7: str | null (chosen draft report_ts for Day-7, else null)
- selected_day30: str | null (chosen draft report_ts for Day-30, else null)
- request_actions: list[str] one action code per request (same order as input)

POLICY RULES (must be implemented exactly; constants must be hardcoded inside solve() and NOT provided via input):
1) Cadence
   - There is a minimum wait period after activation before any formal report can be issued.
   - Official reports are due at exact timestamps: activation + 7 days and activation + 30 days.
   - A draft can only satisfy Day-7 (or Day-30) if its report_ts equals the exact due timestamp.

2) Routing
   - All official outputs must be addressed internally to the coordinator role only.
   - Any draft addressed to any other recipient is noncompliant.

3) Required structure/content gates for an official report
   - Must include sections 1 through 7.
   - Must include a Trust Recovery Snapshot.
   - Snapshot must score all required stakeholder groups plus an overall score.
   - Must explicitly discount likes as meaningful.
   - Must compare actual outcomes vs IRE Risk Index AND predicted containment window.
   - Must assess which channel worked best.
   - Must include explicit timing judgments: both 'fast_enough' and 'missed_window' must be present and boolean.

4) Monitoring scope attestation
   - Monitoring must cover all TMA platforms listed in input_data['tma_platforms'].
   - Monitoring must also cover a required set of internal data categories.
   - If company_public is true, stock/investor series must be included; otherwise it is optional.

5) Conflict handling
   - If ANY artifact_flags value is true, the report must include conflict-handling.

6) Inbound requests safety
   - If a request attempts external/public sharing of any metrics/content, return an internal-only refusal/route action code.
   - Otherwise return an internal-ack routing action code.

SELECTION / MINIMAL PLAN
- For each due timestamp (Day-7 and Day-30), select exactly one draft if and only if it has zero violations for that due timestamp.
- If multiple drafts are fully compliant for the same due timestamp, choose the one with the earliest report_ts (they will be equal if both match due time; then choose the first in input order).
- If no compliant draft exists for a due timestamp, selected_dayX must be null.

GLOBAL VIOLATION CODES
- If a due report is missing (no draft at the exact due timestamp), add: MISSING_DAY7 or MISSING_DAY30.
- If drafts exist at the due timestamp but none are compliant, add the union of their violation codes (excluding cadence mismatch, since they match).
- If drafts exist but none match the due timestamp, only the MISSING_DAYX code applies for that day.
- Additionally, add EXTERNAL_SHARING_REQUEST if any inbound request triggers the external-sharing rule.

Per-draft violation codes (used when evaluating drafts at the due timestamp):
- RECIPIENT_NOT_COORD
- SECTIONS_INCOMPLETE
- TRUST_SNAPSHOT_MISSING
- TRUST_STAKEHOLDERS_INCOMPLETE
- LIKES_NOT_DISCOUNTED
- IRE_COMPARISON_MISSING
- CHANNEL_EFFECTIVENESS_MISSING
- TIMING_JUDGMENTS_MISSING
- INTERNAL_DATA_MISSING
- STOCK_REQUIRED_MISSING
- CONFLICT_HANDLING_MISSING
- MIN_WAIT_VIOLATION

Request action codes (one per request):
- ROUTE_INTERNAL_ONLY
- ACK_INTERNAL

Implementation notes:
- Parse timestamps as UTC Z.
- Hardcode: minimum wait period, day offsets, coordinator recipient string, required stakeholder set, required internal data categories.
- Do not invent data; only validate fields present.

## Expected Output Summary

```json
{
  "format": "dict",
  "key_results": {
    "status": "ok|needs_fix",
    "codes": [],
    "selected_day7": "ISO-8601|null",
    "selected_day30": "ISO-8601|null",
    "request_actions": []
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
