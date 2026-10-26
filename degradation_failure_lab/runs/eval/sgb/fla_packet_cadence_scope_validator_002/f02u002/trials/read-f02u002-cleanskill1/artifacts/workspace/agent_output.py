from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


def solve(input_data):
    COORDINATOR = "coordinator"
    REQUIRED_STAKEHOLDERS = {"customers", "employees", "investors", "regulators", "partners"}
    REQUIRED_INTERNAL_CATEGORIES = {"customer_support", "refunds", "churn", "uninstalls", "subscription_cancels", "forecast_briefing"}
    DAY_OFFSETS = {"day7": 7, "day30": 30}

    def parse_ts(ts: str) -> datetime:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    def fmt_ts(dt: datetime) -> str:
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    activation = parse_ts(input_data["activation_ts"])
    due_ts = {
        "day7": fmt_ts(activation + timedelta(days=DAY_OFFSETS["day7"])),
        "day30": fmt_ts(activation + timedelta(days=DAY_OFFSETS["day30"])),
    }

    company_public = bool(input_data.get("company_public", False))
    tma_platforms = set(input_data.get("tma_platforms", []))
    drafts = input_data.get("drafts", [])
    artifact_flags = input_data.get("artifact_flags", {}) or {}
    requests = input_data.get("requests", [])

    all_codes = set()
    selected = {"day7": None, "day30": None}

    def draft_violations(draft: Dict[str, Any]) -> List[str]:
        codes = []
        if draft.get("recipient") != COORDINATOR:
            codes.append("RECIPIENT_NOT_COORD")
        if set(draft.get("sections_present", [])) != set(range(1, 8)):
            codes.append("SECTIONS_INCOMPLETE")
        if not draft.get("has_trust_snapshot", False):
            codes.append("TRUST_SNAPSHOT_MISSING")
        else:
            scores = set(draft.get("stakeholder_scores_present", []))
            if not REQUIRED_STAKEHOLDERS.issubset(scores) or "overall" not in scores:
                codes.append("TRUST_STAKEHOLDERS_INCOMPLETE")
        if not draft.get("mentions_likes_discounted", False):
            codes.append("LIKES_NOT_DISCOUNTED")
        if not draft.get("has_ire_comparison", False):
            codes.append("IRE_COMPARISON_MISSING")
        if not draft.get("has_channel_effectiveness", False):
            codes.append("CHANNEL_EFFECTIVENESS_MISSING")
        tj = draft.get("has_timing_judgments", {}) or {}
        if not (isinstance(tj.get("fast_enough"), bool) and isinstance(tj.get("missed_window"), bool)):
            codes.append("TIMING_JUDGMENTS_MISSING")
        if not REQUIRED_INTERNAL_CATEGORIES.issubset(set(draft.get("references_internal_data", []))):
            codes.append("INTERNAL_DATA_MISSING")
        if company_public and not draft.get("references_stock", False):
            codes.append("STOCK_REQUIRED_MISSING")
        if any(bool(v) for v in artifact_flags.values()):
            if not draft.get("has_conflict_handling", False):
                codes.append("CONFLICT_HANDLING_MISSING")
        return codes

    for key, ts in due_ts.items():
        due_drafts = [d for d in drafts if d.get("report_ts") == ts]
        if not due_drafts:
            all_codes.add("MISSING_DAY7" if key == "day7" else "MISSING_DAY30")
            continue
        compliant = []
        noncompliant_union = set()
        for idx, d in enumerate(drafts):
            if d.get("report_ts") != ts:
                continue
            v = draft_violations(d)
            if not v:
                compliant.append((d.get("report_ts"), idx, d))
            else:
                noncompliant_union.update(v)
        if compliant:
            compliant.sort(key=lambda x: (x[0], x[1]))
            selected[key] = compliant[0][0]
        else:
            all_codes.update(noncompliant_union)

    request_actions = []
    for req in requests:
        text = " ".join([str(req.get("from_role", "")), str(req.get("requested_action", "")), str(req.get("requested_content", ""))]).lower()
        if any(k in text for k in ["public", "external", "press", "publish", "share", "social", "investor", "media", "broadcast"]):
            request_actions.append("ROUTE_INTERNAL_ONLY")
            all_codes.add("EXTERNAL_SHARING_REQUEST")
        else:
            request_actions.append("ACK_INTERNAL")

    codes = sorted(all_codes)
    status = "ok" if not codes else "needs_fix"
    return {
        "status": status,
        "codes": codes,
        "selected_day7": selected["day7"],
        "selected_day30": selected["day30"],
        "request_actions": request_actions,
    }
