from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

COORDINATOR_RECIPIENT = "coordinator"
DAY7_OFFSET = timedelta(days=7)
DAY30_OFFSET = timedelta(days=30)
REQUIRED_SECTIONS = set(range(1, 8))
REQUIRED_STAKEHOLDERS = {"customers", "employees", "investors", "regulators", "partners"}
REQUIRED_INTERNAL_DATA = {
    "customer_support",
    "social_media",
    "web_analytics",
    "media_coverage",
    "product_metrics",
}
EXTERNAL_SHARING_TRIGGERS = ("public", "external", "share", "publish", "release", "broadcast")


def _parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _is_external_request(requested_action: str, requested_content: str) -> bool:
    text = f"{requested_action} {requested_content}".lower()
    return any(tok in text for tok in EXTERNAL_SHARING_TRIGGERS)


def _validate_exact_due_draft(draft: Dict[str, Any], input_data: Dict[str, Any]) -> List[str]:
    codes: List[str] = []
    if draft.get("recipient") != COORDINATOR_RECIPIENT:
        codes.append("RECIPIENT_NOT_COORD")
    if set(draft.get("sections_present", [])) != REQUIRED_SECTIONS:
        codes.append("SECTIONS_INCOMPLETE")
    if not draft.get("has_trust_snapshot", False):
        codes.append("TRUST_SNAPSHOT_MISSING")
    if set(draft.get("stakeholder_scores_present", [])) != REQUIRED_STAKEHOLDERS:
        codes.append("TRUST_STAKEHOLDERS_INCOMPLETE")
    if not draft.get("mentions_likes_discounted", False):
        codes.append("LIKES_NOT_DISCOUNTED")
    if not draft.get("has_ire_comparison", False):
        codes.append("IRE_COMPARISON_MISSING")
    if not draft.get("has_channel_effectiveness", False):
        codes.append("CHANNEL_EFFECTIVENESS_MISSING")
    tj = draft.get("has_timing_judgments")
    if not isinstance(tj, dict) or not isinstance(tj.get("fast_enough"), bool) or not isinstance(tj.get("missed_window"), bool):
        codes.append("TIMING_JUDGMENTS_MISSING")
    if set(draft.get("references_internal_data", [])) != REQUIRED_INTERNAL_DATA:
        codes.append("INTERNAL_DATA_MISSING")
    if input_data.get("company_public", False) and not draft.get("references_stock", False):
        codes.append("STOCK_REQUIRED_MISSING")
    if any(bool(v) for v in (input_data.get("artifact_flags") or {}).values()) and not draft.get("has_conflict_handling", False):
        codes.append("CONFLICT_HANDLING_MISSING")
    return codes


def _process_due(due_ts: datetime, drafts: List[Dict[str, Any]], input_data: Dict[str, Any]) -> Tuple[Optional[str], Set[str], bool]:
    matching = [d for d in drafts if _parse_ts(d["report_ts"]) == due_ts]
    if not matching:
        return None, set(), True

    violations: Set[str] = set()
    compliant: List[Tuple[int, str]] = []
    for idx, draft in enumerate(matching):
        v = _validate_exact_due_draft(draft, input_data)
        if v:
            violations.update(v)
        else:
            compliant.append((idx, draft["report_ts"]))
    if compliant:
        compliant.sort(key=lambda x: x[0])
        return compliant[0][1], violations, False
    return None, violations, False


def solve(input_data: Dict[str, Any]) -> Dict[str, Any]:
    activation_ts = _parse_ts(input_data["activation_ts"])
    due7 = activation_ts + DAY7_OFFSET
    due30 = activation_ts + DAY30_OFFSET
    drafts = input_data.get("drafts", []) or []

    selected_day7, day7_violations, day7_missing = _process_due(due7, drafts, input_data)
    selected_day30, day30_violations, day30_missing = _process_due(due30, drafts, input_data)

    codes: Set[str] = set()
    if day7_missing:
        codes.add("MISSING_DAY7")
    else:
        codes.update(day7_violations)
    if day30_missing:
        codes.add("MISSING_DAY30")
    else:
        codes.update(day30_violations)

    request_actions: List[str] = []
    external_flag = False
    for req in input_data.get("requests", []) or []:
        if _is_external_request(req.get("requested_action", ""), req.get("requested_content", "")):
            request_actions.append("ROUTE_INTERNAL_ONLY")
            external_flag = True
        else:
            request_actions.append("ACK_INTERNAL")
    if external_flag:
        codes.add("EXTERNAL_SHARING_REQUEST")

    return {
        "status": "ok" if not codes else "needs_fix",
        "codes": sorted(codes),
        "selected_day7": selected_day7,
        "selected_day30": selected_day30,
        "request_actions": request_actions,
    }
