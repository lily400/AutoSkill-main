from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


COORDINATOR = "coordinator"
DAY7_OFFSET = timedelta(days=7)
DAY30_OFFSET = timedelta(days=30)
REQUIRED_SECTIONS = set(range(1, 8))
REQUIRED_STAKEHOLDERS = {
    "customers",
    "employees",
    "investors",
    "regulators",
    "partners",
}
REQUIRED_INTERNAL_DATA = {
    "customer_support",
    "social_media",
    "news_coverage",
    "product_metrics",
    "ops_incidents",
}


def parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def draft_violations(draft: Dict[str, Any], due_ts: str, company_public: bool, tma_platforms: List[str], artifact_flags: Dict[str, bool]) -> List[str]:
    codes: List[str] = []
    if draft.get("report_ts") != due_ts:
        codes.append("MIN_WAIT_VIOLATION")
        return codes

    if draft.get("recipient") != COORDINATOR:
        codes.append("RECIPIENT_NOT_COORD")
    if set(draft.get("sections_present", [])) != REQUIRED_SECTIONS:
        codes.append("SECTIONS_INCOMPLETE")
    if not draft.get("has_trust_snapshot", False):
        codes.append("TRUST_SNAPSHOT_MISSING")
    if not REQUIRED_STAKEHOLDERS.issubset(set(draft.get("stakeholder_scores_present", []))):
        codes.append("TRUST_STAKEHOLDERS_INCOMPLETE")
    if not draft.get("mentions_likes_discounted", False):
        codes.append("LIKES_NOT_DISCOUNTED")
    if not draft.get("has_ire_comparison", False):
        codes.append("IRE_COMPARISON_MISSING")
    if not draft.get("has_channel_effectiveness", False):
        codes.append("CHANNEL_EFFECTIVENESS_MISSING")
    tj = draft.get("has_timing_judgments", {}) or {}
    if not (isinstance(tj, dict) and isinstance(tj.get("fast_enough"), bool) and isinstance(tj.get("missed_window"), bool)):
        codes.append("TIMING_JUDGMENTS_MISSING")
    if not REQUIRED_INTERNAL_DATA.issubset(set(draft.get("references_internal_data", []))):
        codes.append("INTERNAL_DATA_MISSING")
    if company_public and not draft.get("references_stock", False):
        codes.append("STOCK_REQUIRED_MISSING")
    if any(artifact_flags.values()) and not draft.get("has_conflict_handling", False):
        codes.append("CONFLICT_HANDLING_MISSING")
    return codes


def request_action(req: Dict[str, Any]) -> str:
    content = (req.get("requested_content") or "").lower()
    action = (req.get("requested_action") or "").lower()
    external_markers = ["public", "external", "press", "publish", "share", "post", "announce"]
    if any(m in content for m in external_markers) or any(m in action for m in external_markers):
        return "ROUTE_INTERNAL_ONLY"
    return "ACK_INTERNAL"


def solve(input_data: Dict[str, Any]) -> Dict[str, Any]:
    activation = parse_ts(input_data["activation_ts"])
    day7_due = iso_z(activation + DAY7_OFFSET)
    day30_due = iso_z(activation + DAY30_OFFSET)
    drafts = input_data.get("drafts", [])
    company_public = bool(input_data.get("company_public", False))
    tma_platforms = input_data.get("tma_platforms", [])
    artifact_flags = input_data.get("artifact_flags", {}) or {}

    codes = set()
    selected_day7: Optional[str] = None
    selected_day30: Optional[str] = None

    def evaluate_due(due_ts: str, missing_code: str) -> Optional[str]:
        matching = [d for d in drafts if d.get("report_ts") == due_ts]
        if not matching:
            codes.add(missing_code)
            return None
        compliant: List[Tuple[str, int, Dict[str, Any]]] = []
        for idx, d in enumerate(matching):
            v = draft_violations(d, due_ts, company_public, tma_platforms, artifact_flags)
            if not v:
                compliant.append((d.get("report_ts", due_ts), idx, d))
            else:
                codes.update(v)
        if compliant:
            compliant.sort(key=lambda x: (x[0], x[1]))
            return compliant[0][0]
        return None

    selected_day7 = evaluate_due(day7_due, "MISSING_DAY7")
    selected_day30 = evaluate_due(day30_due, "MISSING_DAY30")

    request_actions = [request_action(r) for r in input_data.get("requests", [])]
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
