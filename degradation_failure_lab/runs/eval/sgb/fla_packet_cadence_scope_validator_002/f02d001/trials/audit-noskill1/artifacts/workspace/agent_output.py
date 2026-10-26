from datetime import datetime, timedelta, timezone


def _parse_ts(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _ts(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def solve(input_data):
    coordinator = "coordinator"
    required_sections = set(range(1, 8))
    required_stakeholders = {"patients", "caregivers", "clinicians", "operations", "regulators", "overall"}
    required_internal = {"baseline", "mention_counts", "media_dedup", "support_totals"}

    activation = _parse_ts(input_data["activation_ts"])
    day7_ts = _ts(activation + timedelta(days=7))
    day30_ts = _ts(activation + timedelta(days=30))

    artifact_flags = input_data.get("artifact_flags", {})
    any_conflict_flag = any(bool(v) for v in artifact_flags.values())

    def eval_draft(draft, due_ts):
        codes = []
        if draft.get("report_ts") != due_ts:
            codes.append("MIN_WAIT_VIOLATION")
            return codes
        if draft.get("recipient") != coordinator:
            codes.append("RECIPIENT_NOT_COORD")
        if set(draft.get("sections_present", [])) != required_sections:
            codes.append("SECTIONS_INCOMPLETE")
        if not draft.get("has_trust_snapshot", False):
            codes.append("TRUST_SNAPSHOT_MISSING")
        if not required_stakeholders.issubset(set(draft.get("stakeholder_scores_present", []))):
            codes.append("TRUST_STAKEHOLDERS_INCOMPLETE")
        if not draft.get("mentions_likes_discounted", False):
            codes.append("LIKES_NOT_DISCOUNTED")
        if not draft.get("has_ire_comparison", False):
            codes.append("IRE_COMPARISON_MISSING")
        if not draft.get("has_channel_effectiveness", False):
            codes.append("CHANNEL_EFFECTIVENESS_MISSING")
        tj = draft.get("has_timing_judgments", {})
        if not isinstance(tj, dict) or not isinstance(tj.get("fast_enough", None), bool) or not isinstance(tj.get("missed_window", None), bool):
            codes.append("TIMING_JUDGMENTS_MISSING")
        if not required_internal.issubset(set(draft.get("references_internal_data", []))):
            codes.append("INTERNAL_DATA_MISSING")
        if input_data.get("company_public", False) and not draft.get("references_stock", False):
            codes.append("STOCK_REQUIRED_MISSING")
        if any_conflict_flag and not draft.get("has_conflict_handling", False):
            codes.append("CONFLICT_HANDLING_MISSING")
        return sorted(set(codes))

    drafts = input_data.get("drafts", [])
    day7_candidates = [d for d in drafts if d.get("report_ts") == day7_ts]
    day30_candidates = [d for d in drafts if d.get("report_ts") == day30_ts]

    def select(due_ts, candidates):
        if not candidates:
            return None, ["MISSING_DAY7" if due_ts == day7_ts else "MISSING_DAY30"]
        evaluated = [(i, d, eval_draft(d, due_ts)) for i, d in enumerate(drafts) if d.get("report_ts") == due_ts]
        compliant = [(i, d) for i, d, codes in evaluated if not codes]
        if compliant:
            i, d = min(compliant, key=lambda x: (drafts[x[0]].get("report_ts"), x[0]))
            return d.get("report_ts"), []
        union_codes = set()
        for _, _, codes in evaluated:
            union_codes.update(codes)
        return None, sorted(union_codes)

    selected_day7, codes7 = select(day7_ts, day7_candidates)
    selected_day30, codes30 = select(day30_ts, day30_candidates)

    codes = set(codes7) | set(codes30)

    request_actions = []
    for req in input_data.get("requests", []):
        action_text = str(req.get("requested_action", "")).lower()
        content_text = str(req.get("requested_content", "")).lower()
        external_share = any(tok in action_text for tok in ["external", "public", "publish", "share", "release"]) or any(tok in content_text for tok in ["external", "public", "publish", "share", "release", "press", "investor", "media"])
        if external_share:
            request_actions.append("ROUTE_INTERNAL_ONLY")
            codes.add("EXTERNAL_SHARING_REQUEST")
        else:
            request_actions.append("ACK_INTERNAL")

    status = "ok" if not codes else "needs_fix"
    return {
        "status": status,
        "codes": sorted(codes),
        "selected_day7": selected_day7,
        "selected_day30": selected_day30,
        "request_actions": request_actions,
    }
