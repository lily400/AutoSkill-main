from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


COORDINATOR = "coordinator"
DAY7_OFFSET = timedelta(days=7)
DAY30_OFFSET = timedelta(days=30)
REQUIRED_SECTIONS = set(range(1, 8))
REQUIRED_STAKEHOLDERS = {"customers", "employees", "investors", "regulators", "partners"}
REQUIRED_INTERNAL_DATA = {
    "customer_support",
    "sales",
    "product",
    "ops",
    "legal",
}


def _parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _ts_str(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _due_ts(activation_ts: str, offset: timedelta) -> str:
    return _ts_str(_parse_ts(activation_ts) + offset)


def _draft_violations(draft: Dict[str, Any], due_ts: str, company_public: bool, tma_platforms: List[str], artifact_flags: Dict[str, bool]) -> List[str]:
    v: List[str] = []
    if draft.get("report_ts") != due_ts:
        v.append("MIN_WAIT_VIOLATION")
        return v
    if draft.get("recipient") != COORDINATOR:
        v.append("RECIPIENT_NOT_COORD")
    if not REQUIRED_SECTIONS.issubset(set(draft.get("sections_present", []))):
        v.append("SECTIONS_INCOMPLETE")
    if not draft.get("has_trust_snapshot", False):
        v.append("TRUST_SNAPSHOT_MISSING")
    else:
        scores = set(draft.get("stakeholder_scores_present", []))
        if not REQUIRED_STAKEHOLDERS.issubset(scores):
            v.append("TRUST_STAKEHOLDERS_INCOMPLETE")
    if not draft.get("mentions_likes_discounted", False):
        v.append("LIKES_NOT_DISCOUNTED")
    if not draft.get("has_ire_comparison", False):
        v.append("IRE_COMPARISON_MISSING")
    if not draft.get("has_channel_effectiveness", False):
        v.append("CHANNEL_EFFECTIVENESS_MISSING")
    tj = draft.get("has_timing_judgments", {})
    if not (isinstance(tj, dict) and isinstance(tj.get("fast_enough"), bool) and isinstance(tj.get("missed_window"), bool)):
        v.append("TIMING_JUDGMENTS_MISSING")
    refs = set(draft.get("references_internal_data", []))
    if not REQUIRED_INTERNAL_DATA.issubset(refs):
        v.append("INTERNAL_DATA_MISSING")
    # Require attestation coverage of all monitored TMA platforms; if the draft
    # lacks an explicit list, treat missing coverage as noncompliant when any
    # platforms are configured.
    if tma_platforms:
        covered = set(draft.get("tma_platforms_covered", draft.get("references_internal_data", [])))
        if not set(tma_platforms).issubset(covered):
            v.append("INTERNAL_DATA_MISSING")
    if company_public and not draft.get("references_stock", False):
        v.append("STOCK_REQUIRED_MISSING")
    if any(artifact_flags.get(k, False) for k in artifact_flags):
        if not draft.get("has_conflict_handling", False):
            v.append("CONFLICT_HANDLING_MISSING")
    return v


def _request_action(req: Dict[str, Any]) -> str:
    text = " ".join(str(req.get(k, "")) for k in ("from_role", "requested_action", "requested_content")).lower()
    if any(term in text for term in ["public", "external", "press", "publish", "share", "post", "announce"]):
        return "ROUTE_INTERNAL_ONLY"
    return "ACK_INTERNAL"


def solve(input_data):
    activation_ts = input_data["activation_ts"]
    company_public = bool(input_data.get("company_public", False))
    tma_platforms = list(input_data.get("tma_platforms", []))
    drafts = list(input_data.get("drafts", []))
    artifact_flags = dict(input_data.get("artifact_flags", {}))
    requests = list(input_data.get("requests", []))

    day7_due = _due_ts(activation_ts, DAY7_OFFSET)
    day30_due = _due_ts(activation_ts, DAY30_OFFSET)

    global_codes = set()
    selected_day7 = None
    selected_day30 = None

    def eval_due(due_ts: str, missing_code: str):
        matching = [d for d in drafts if d.get("report_ts") == due_ts]
        if not matching:
            global_codes.add(missing_code)
            return None
        compliant = []
        for idx, d in enumerate(matching):
            v = _draft_violations(d, due_ts, company_public, tma_platforms, artifact_flags)
            if not v:
                compliant.append((d.get("report_ts"), idx, d))
            else:
                global_codes.update(v)
        if compliant:
            compliant.sort(key=lambda x: (x[0], x[1]))
            return compliant[0][2].get("report_ts")
        return None

    selected_day7 = eval_due(day7_due, "MISSING_DAY7")
    selected_day30 = eval_due(day30_due, "MISSING_DAY30")

    request_actions = []
    for req in requests:
        act = _request_action(req)
        request_actions.append(act)
        if act == "ROUTE_INTERNAL_ONLY":
            global_codes.add("EXTERNAL_SHARING_REQUEST")

    status = "ok" if not global_codes else "needs_fix"
    return {
        "status": status,
        "codes": sorted(global_codes),
        "selected_day7": selected_day7,
        "selected_day30": selected_day30,
        "request_actions": request_actions,
    }
