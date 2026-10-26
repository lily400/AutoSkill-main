def solve(input_data):
    from datetime import datetime, timedelta

    def parse_ts(s: str) -> datetime:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

    # ---------------- Document-specific constants (hardcoded) ----------------
    MIN_WAIT_HOURS = 24
    DAY7_OFFSET_DAYS = 7
    DAY30_OFFSET_DAYS = 30
    COORDINATOR_RECIPIENT = "BRO"
    REQUIRED_STAKEHOLDERS = {"Customers", "Employees", "Investors", "Regulators", "Partners", "Overall"}
    REQUIRED_INTERNAL_CATS = {
        "support_tickets",
        "refund_requests",
        "churn",
        "app_uninstalls",
        "subscription_cancellations",
        "employee_sentiment",
        "media_tone",
        "partner_regulator_events",
    }
    # -----------------------------------------------------------------------

    activation = parse_ts(input_data["activation_ts"])
    due7 = activation + timedelta(days=DAY7_OFFSET_DAYS)
    due30 = activation + timedelta(days=DAY30_OFFSET_DAYS)

    artifact_flags = input_data.get("artifact_flags", {}) or {}
    any_conflict = any(bool(artifact_flags.get(k, False)) for k in [
        "baseline_corrected",
        "mention_counts_corrected",
        "media_dedup_variance",
        "support_totals_inconsistent",
    ])

    def validate_at_due(draft, due_ts):
        codes = set()
        rts = parse_ts(draft["report_ts"])

        # exact due timestamp required for eligibility
        if rts != due_ts:
            return {"_NOT_AT_DUE"}

        # min wait
        if rts < activation + timedelta(hours=MIN_WAIT_HOURS):
            codes.add("MIN_WAIT_VIOLATION")

        # routing
        if draft.get("recipient") != COORDINATOR_RECIPIENT:
            codes.add("RECIPIENT_NOT_COORD")

        # sections 1..7
        secs = draft.get("sections_present", [])
        if set(secs) != {1, 2, 3, 4, 5, 6, 7} or len(secs) != 7:
            codes.add("SECTIONS_INCOMPLETE")

        # trust snapshot + stakeholders
        if not draft.get("has_trust_snapshot", False):
            codes.add("TRUST_SNAPSHOT_MISSING")
        else:
            present = set(draft.get("stakeholder_scores_present", []) or [])
            if present != REQUIRED_STAKEHOLDERS:
                codes.add("TRUST_STAKEHOLDERS_INCOMPLETE")

        # likes discounted
        if not draft.get("mentions_likes_discounted", False):
            codes.add("LIKES_NOT_DISCOUNTED")

        # IRE comparison
        if not draft.get("has_ire_comparison", False):
            codes.add("IRE_COMPARISON_MISSING")

        # channel effectiveness
        if not draft.get("has_channel_effectiveness", False):
            codes.add("CHANNEL_EFFECTIVENESS_MISSING")

        # timing judgments
        tj = draft.get("has_timing_judgments", {}) or {}
        if ("fast_enough" not in tj) or ("missed_window" not in tj) or (tj.get("fast_enough") not in (True, False)) or (tj.get("missed_window") not in (True, False)):
            codes.add("TIMING_JUDGMENTS_MISSING")

        # internal data categories
        refs = set(draft.get("references_internal_data", []) or [])
        if not REQUIRED_INTERNAL_CATS.issubset(refs):
            codes.add("INTERNAL_DATA_MISSING")

        # stock conditional
        if input_data.get("company_public", False) and not draft.get("references_stock", False):
            codes.add("STOCK_REQUIRED_MISSING")

        # conflict handling
        if any_conflict and not draft.get("has_conflict_handling", False):
            codes.add("CONFLICT_HANDLING_MISSING")

        return codes

    drafts = input_data.get("drafts", []) or []

    def pick_for(due_ts, missing_code):
        matching = []
        for d in drafts:
            v = validate_at_due(d, due_ts)
            if "_NOT_AT_DUE" not in v:
                matching.append((d, v))

        if not matching:
            return None, {missing_code}

        compliant = [d for (d, v) in matching if len(v) == 0]
        if compliant:
            # all have same report_ts == due_ts; choose first in input order
            return compliant[0]["report_ts"], set()

        agg = set()
        for _, v in matching:
            agg |= v
        return None, agg

    sel7, c7 = pick_for(due7, "MISSING_DAY7")
    sel30, c30 = pick_for(due30, "MISSING_DAY30")

    codes = set()
    codes |= c7
    codes |= c30

    # monitoring scope attestation: must have at least one platform listed (and by definition cover all listed)
    tma_plats = input_data.get("tma_platforms", [])
    if not isinstance(tma_plats, list) or len(tma_plats) == 0:
        codes.add("TMA_PLATFORMS_MISSING")

    # inbound requests
    request_actions = []
    external_triggered = False
    for req in input_data.get("requests", []) or []:
        action = (req.get("requested_action") or "").lower()
        content = (req.get("requested_content") or "").lower()
        wants_external = any(k in action for k in ["publish", "post", "share", "send", "external", "public"]) or any(
            k in content for k in ["public", "extern", "investor call", "press", "blog", "x", "twitter", "linkedin"]
        )
        if wants_external:
            request_actions.append("ROUTE_INTERNAL_ONLY")
            external_triggered = True
        else:
            request_actions.append("ACK_INTERNAL")

    if external_triggered:
        codes.add("EXTERNAL_SHARING_REQUEST")

    status = "ok" if not codes else "needs_fix"

    return {
        "status": status,
        "codes": sorted(codes),
        "selected_day7": sel7,
        "selected_day30": sel30,
        "request_actions": request_actions,
    }
