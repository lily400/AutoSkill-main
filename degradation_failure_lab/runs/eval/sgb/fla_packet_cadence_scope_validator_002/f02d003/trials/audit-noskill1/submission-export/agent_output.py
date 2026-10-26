from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set


COORDINATOR = "coordinator"
DAY7_OFFSET = timedelta(days=7)
DAY30_OFFSET = timedelta(days=30)

REQUIRED_SECTIONS = set(range(1, 8))
REQUIRED_STAKEHOLDERS = {"patients", "providers", "regulators", "community", "overall"}
REQUIRED_INTERNAL_DATA = {
    "adverse_events",
    "case_counts",
    "support_totals",
    "media_mentions",
    "channel_metrics",
}


def _parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _bool(v: Any) -> bool:
    return isinstance(v, bool) and v is True


def _draft_violations(draft: Dict[str, Any], due_ts: datetime, input_data: Dict[str, Any]) -> List[str]:
    v: List[str] = []
    report_ts = _parse_ts(draft["report_ts"])
    if report_ts != due_ts:
        v.append("MIN_WAIT_VIOLATION")
    if draft.get("recipient") != COORDINATOR:
        v.append("RECIPIENT_NOT_COORD")
    if set(draft.get("sections_present", [])) != REQUIRED_SECTIONS:
        v.append("SECTIONS_INCOMPLETE")
    if not draft.get("has_trust_snapshot", False):
        v.append("TRUST_SNAPSHOT_MISSING")
    else:
        if set(draft.get("stakeholder_scores_present", [])) != REQUIRED_STAKEHOLDERS:
            v.append("TRUST_STAKEHOLDERS_INCOMPLETE")
    if not draft.get("mentions_likes_discounted", False):
        v.append("LIKES_NOT_DISCOUNTED")
    if not draft.get("has_ire_comparison", False):
        v.append("IRE_COMPARISON_MISSING")
    if not draft.get("has_channel_effectiveness", False):
        v.append("CHANNEL_EFFECTIVENESS_MISSING")
    tj = draft.get("has_timing_judgments", {})
    if not isinstance(tj, dict) or not isinstance(tj.get("fast_enough"), bool) or not isinstance(tj.get("missed_window"), bool):
        v.append("TIMING_JUDGMENTS_MISSING")
    if set(draft.get("references_internal_data", [])) != REQUIRED_INTERNAL_DATA:
        v.append("INTERNAL_DATA_MISSING")
    if input_data.get("company_public", False) and not draft.get("references_stock", False):
        v.append("STOCK_REQUIRED_MISSING")
    if any(bool(x) for x in input_data.get("artifact_flags", {}).values()) and not draft.get("has_conflict_handling", False):
        v.append("CONFLICT_HANDLING_MISSING")
    return v


def _request_action(req: Dict[str, Any]) -> str:
    text = f"{req.get('requested_action','')} {req.get('requested_content','')}".lower()
    external_terms = ["public", "external", "press", "publish", "share", "social", "investor", "media", "announce"]
    if any(t in text for t in external_terms):
        return "ROUTE_INTERNAL_ONLY"
    return "ACK_INTERNAL"


def solve(input_data: Dict[str, Any]) -> Dict[str, Any]:
    activation = _parse_ts(input_data["activation_ts"])
    due7 = activation + DAY7_OFFSET
    due30 = activation + DAY30_OFFSET

    drafts = input_data.get("drafts", [])
    codes: Set[str] = set()
    selected_day7: Optional[str] = None
    selected_day30: Optional[str] = None

    def choose_for_due(due_ts: datetime) -> Optional[str]:
        matching = []
        for idx, draft in enumerate(drafts):
            if _parse_ts(draft["report_ts"]) == due_ts:
                viol = _draft_violations(draft, due_ts, input_data)
                matching.append((idx, draft["report_ts"], viol))
        if not matching:
            return None
        compliant = [m for m in matching if not m[2]]
        if compliant:
            compliant.sort(key=lambda x: (x[1], x[0]))
            return compliant[0][1]
        for _, _, viol in matching:
            for code in viol:
                if code != "MIN_WAIT_VIOLATION":
                    codes.add(code)
        return None

    selected_day7 = choose_for_due(due7)
    if selected_day7 is None:
        if not any(_parse_ts(d["report_ts"]) == due7 for d in drafts):
            codes.add("MISSING_DAY7")

    selected_day30 = choose_for_due(due30)
    if selected_day30 is None:
        if not any(_parse_ts(d["report_ts"]) == due30 for d in drafts):
            codes.add("MISSING_DAY30")

    request_actions = [_request_action(r) for r in input_data.get("requests", [])]
    if any(a == "ROUTE_INTERNAL_ONLY" for a in request_actions):
        codes.add("EXTERNAL_SHARING_REQUEST")

    status = "ok" if not codes else "needs_fix"
    return {
        "status": status,
        "codes": sorted(codes),
        "selected_day7": selected_day7,
        "selected_day30": selected_day30,
        "request_actions": request_actions,
    }
