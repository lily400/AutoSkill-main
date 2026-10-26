from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set


COORDINATOR = "coordinator"
DAY7_OFFSET = timedelta(days=7)
DAY30_OFFSET = timedelta(days=30)

REQUIRED_STAKEHOLDERS = {
    "patients",
    "providers",
    "payers",
    "regulators",
    "employees",
    "partners",
    "public",
}

REQUIRED_INTERNAL_DATA = {
    "baseline",
    "mention_counts",
    "media_dedup",
    "support_totals",
}


def parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def eval_draft(draft: Dict[str, Any], due_ts: datetime, input_data: Dict[str, Any]) -> Set[str]:
    violations: Set[str] = set()

    report_ts = parse_ts(draft["report_ts"])
    if report_ts != due_ts:
        violations.add("MIN_WAIT_VIOLATION")
        return violations

    if draft.get("recipient") != COORDINATOR:
        violations.add("RECIPIENT_NOT_COORD")

    sections = set(draft.get("sections_present", []))
    if not all(i in sections for i in range(1, 8)):
        violations.add("SECTIONS_INCOMPLETE")

    if not draft.get("has_trust_snapshot", False):
        violations.add("TRUST_SNAPSHOT_MISSING")
    else:
        scores = set(draft.get("stakeholder_scores_present", []))
        if not REQUIRED_STAKEHOLDERS.issubset(scores):
            violations.add("TRUST_STAKEHOLDERS_INCOMPLETE")

    if not draft.get("mentions_likes_discounted", False):
        violations.add("LIKES_NOT_DISCOUNTED")
    if not draft.get("has_ire_comparison", False):
        violations.add("IRE_COMPARISON_MISSING")
    if not draft.get("has_channel_effectiveness", False):
        violations.add("CHANNEL_EFFECTIVENESS_MISSING")

    timing = draft.get("has_timing_judgments", {})
    if not isinstance(timing, dict) or not isinstance(timing.get("fast_enough"), bool) or not isinstance(timing.get("missed_window"), bool):
        violations.add("TIMING_JUDGMENTS_MISSING")

    refs = set(draft.get("references_internal_data", []))
    if not REQUIRED_INTERNAL_DATA.issubset(refs):
        violations.add("INTERNAL_DATA_MISSING")

    if input_data.get("company_public", False) and not draft.get("references_stock", False):
        violations.add("STOCK_REQUIRED_MISSING")

    if any(bool(v) for v in input_data.get("artifact_flags", {}).values()):
        if not draft.get("has_conflict_handling", False):
            violations.add("CONFLICT_HANDLING_MISSING")

    return violations


def request_action(req: Dict[str, Any]) -> str:
    content = f"{req.get('requested_action', '')} {req.get('requested_content', '')}".lower()
    external_terms = ["public", "external", "press", "share", "publish", "post", "tweet", "release", "customer-facing", "investor"]
    if any(term in content for term in external_terms):
        return "ROUTE_INTERNAL_ONLY"
    return "ACK_INTERNAL"


def solve(input_data):
    activation_ts = parse_ts(input_data["activation_ts"])
    due7 = activation_ts + DAY7_OFFSET
    due30 = activation_ts + DAY30_OFFSET

    codes: Set[str] = set()
    selected_day7: Optional[str] = None
    selected_day30: Optional[str] = None

    drafts = input_data.get("drafts", [])

    def select_for_due(due_ts: datetime, missing_code: str) -> Optional[str]:
        matching = [d for d in drafts if parse_ts(d["report_ts"]) == due_ts]
        if not matching:
            codes.add(missing_code)
            return None
        compliant = []
        for d in matching:
            v = eval_draft(d, due_ts, input_data)
            if not v:
                compliant.append(d)
            else:
                codes.update(v)
        if not compliant:
            return None
        compliant.sort(key=lambda d: (parse_ts(d["report_ts"]), drafts.index(d)))
        return compliant[0]["report_ts"]

    selected_day7 = select_for_due(due7, "MISSING_DAY7")
    selected_day30 = select_for_due(due30, "MISSING_DAY30")

    request_actions = []
    for req in input_data.get("requests", []):
        action = request_action(req)
        request_actions.append(action)
        if action == "ROUTE_INTERNAL_ONLY":
            codes.add("EXTERNAL_SHARING_REQUEST")

    status = "ok" if not codes else "needs_fix"

    return {
        "status": status,
        "codes": sorted(codes),
        "selected_day7": selected_day7,
        "selected_day30": selected_day30,
        "request_actions": request_actions,
    }
