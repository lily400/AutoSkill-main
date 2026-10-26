from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional


COORDINATOR = "coordinator"
REQUIRED_SECTIONS = set(range(1, 8))
REQUIRED_STAKEHOLDERS = {"customers", "employees", "investors", "regulators", "partners", "media", "overall"}
REQUIRED_INTERNAL_DATA = {"channel_data", "support_data", "refund_data", "churn_data", "uninstall_data", "cancel_data", "forecast_data"}


def _parse_ts(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _fmt_ts(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _has_bools_dict(d: Any, keys: List[str]) -> bool:
    return isinstance(d, dict) and all(k in d and isinstance(d[k], bool) for k in keys)


def _violations_for_draft(draft: Dict[str, Any], due_ts: datetime, activation_ts: datetime, company_public: bool, tma_platforms: List[str], artifact_flags: Dict[str, bool]) -> List[str]:
    codes: List[str] = []
    report_ts = _parse_ts(draft["report_ts"])
    if report_ts < activation_ts + timedelta(days=7):
        codes.append("MIN_WAIT_VIOLATION")
    if report_ts != due_ts:
        return codes
    if draft.get("recipient") != COORDINATOR:
        codes.append("RECIPIENT_NOT_COORD")
    if not REQUIRED_SECTIONS.issubset(set(draft.get("sections_present", []))):
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
    if not _has_bools_dict(draft.get("has_timing_judgments"), ["fast_enough", "missed_window"]):
        codes.append("TIMING_JUDGMENTS_MISSING")
    internal = set(draft.get("references_internal_data", []))
    if not REQUIRED_INTERNAL_DATA.issubset(internal) or not set(tma_platforms).issubset(internal):
        codes.append("INTERNAL_DATA_MISSING")
    if company_public and not draft.get("references_stock", False):
        codes.append("STOCK_REQUIRED_MISSING")
    if any(artifact_flags.values()) and not draft.get("has_conflict_handling", False):
        codes.append("CONFLICT_HANDLING_MISSING")
    return codes


def _request_action(req: Dict[str, Any]) -> str:
    text = " ".join(str(req.get(k, "")).lower() for k in ("requested_action", "requested_content"))
    if any(x in text for x in ["public", "external", "share", "publish", "post", "broadcast", "press", "release"]):
        return "ROUTE_INTERNAL_ONLY"
    return "ACK_INTERNAL"


def _evaluate_due(drafts: List[Dict[str, Any]], due_ts: datetime, activation_ts: datetime, company_public: bool, tma_platforms: List[str], artifact_flags: Dict[str, bool], global_codes: set) -> Optional[str]:
    matching = [d for d in drafts if _parse_ts(d["report_ts"]) == due_ts]
    if not matching:
        global_codes.add("MISSING_DAY7" if due_ts == activation_ts + timedelta(days=7) else "MISSING_DAY30")
        return None
    compliant = []
    union_codes = set()
    for d in matching:
        v = _violations_for_draft(d, due_ts, activation_ts, company_public, tma_platforms, artifact_flags)
        if not v:
            compliant.append(d)
        union_codes.update(v)
    if compliant:
        compliant.sort(key=lambda d: (_parse_ts(d["report_ts"]), drafts.index(d)))
        return compliant[0]["report_ts"]
    global_codes.update(union_codes)
    return None


def solve(input_data):
    activation_ts = _parse_ts(input_data["activation_ts"])
    company_public = bool(input_data.get("company_public", False))
    tma_platforms = list(input_data.get("tma_platforms", []))
    drafts = list(input_data.get("drafts", []))
    artifact_flags = dict(input_data.get("artifact_flags", {}))
    requests = list(input_data.get("requests", []))

    global_codes = set()
    selected_day7 = _evaluate_due(drafts, activation_ts + timedelta(days=7), activation_ts, company_public, tma_platforms, artifact_flags, global_codes)
    selected_day30 = _evaluate_due(drafts, activation_ts + timedelta(days=30), activation_ts, company_public, tma_platforms, artifact_flags, global_codes)

    request_actions = []
    for req in requests:
        action = _request_action(req)
        request_actions.append(action)
        if action == "ROUTE_INTERNAL_ONLY":
            global_codes.add("EXTERNAL_SHARING_REQUEST")

    status = "ok" if not global_codes else "needs_fix"
    return {
        "status": status,
        "codes": sorted(global_codes),
        "selected_day7": selected_day7,
        "selected_day30": selected_day30,
        "request_actions": request_actions,
    }
