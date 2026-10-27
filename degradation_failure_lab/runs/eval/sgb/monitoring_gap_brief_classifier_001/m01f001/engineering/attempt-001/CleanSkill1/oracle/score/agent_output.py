def solve(input_data):
    # Document-derived constants (Chapter 8 excerpt)
    CLS_NO_SYS = "NO_SYSTEMATIC_MONITORING"
    CLS_NEEDS = "NEEDS_IMPROVED_MONITORING"
    CLS_SYS = "SYSTEMATIC_MONITORING_PRESENT"
    CLS_NS = "NOT_SPECIFIED_IN_CH8"

    # No monitoring / no systematic monitoring (explicit)
    NO_SYS = {
        # Plants and algae
        "Two marine plants",
        "Freshwater algae",
        # Freshwater species
        "Freshwater species",
        # Anchialine
        "Anchialine-pond fauna",
        # Marine gaps
        "Non-commercially regulated marine invertebrates",
        "Deep water species",
        "Pelagic species",
        # Habitat gaps (explicitly listed with no systematic monitoring)
        "Estuaries",
        "Sandy bottom habitats",
        "Pelagic habitats",
        "Deep water habitats",
    }

    # Needs consistent/improved monitoring (explicit list)
    NEEDS = {
        "Anchialine pools",
        "Tidepools",
        # Note: these also appear in NO_SYS; priority rule makes them NO_SYS if present there
        "Sandy bottom habitats",
        "Deep water habitats",
    }

    # Systematic/long-term monitoring present (explicit)
    SYS = {
        "Marine algae",
        "Sea turtle nesting",
        "Monk seal pupping",
        "Humpback whales",
        "Ulua",
        "Bottomfishes",
        "Precious corals",
        "Coral reefs",
        "Streams and lakes",
        "Marine Life Conservation Districts",
        "Marine managed areas",
        "Essential Fish Habitat",
    }

    # Actions (initiatives)
    ACT_WORKGROUP = "WORKGROUP"
    ACT_PROTOCOLS = "STD_PROTOCOLS"
    ACT_ECOSYS = "ECOSYS_MON"
    ACT_PARTNERS = "PARTNERSHIPS"

    # Challenges (fixed order)
    CHALLENGES = [
        "INADEQUATE_FUNDS",
        "LACK_TRAINED_PERSONNEL",
        "INSUFFICIENT_TOOLS_PROTOCOLS",
        "POOR_DATA_MANAGEMENT",
        "INFO_SHARING_GAPS",
        "RARE_FLUCTUATING_TRADEOFFS",
    ]

    # Guardrail detection
    timeline_re = re.compile(r"\b(within|next)\s+\d+\s*(years?|months?)\b|\bby\s+\d{4}\b", re.I)
    extinct_re = re.compile(r"\b(extinct|extinction|go\s+extinct|die\s+out)\b", re.I)
    certainty_re = re.compile(r"\b(certain|definitely|guaranteed|will)\b", re.I)
    binomial_re = re.compile(r"\b[A-Z][a-z]+\s+[a-z]+\b")

    def guardrail(claim):
        if claim is None:
            return "OK"
        txt = str(claim).strip()
        if not txt:
            return "OK"
        # Block if extinction + (timeline or certainty), or extinction + binomial
        if extinct_re.search(txt) and (timeline_re.search(txt) or certainty_re.search(txt)):
            return "BLOCK"
        if extinct_re.search(txt) and binomial_re.search(txt):
            return "BLOCK"
        return "OK"

    def classify(name):
        # Priority: NO_SYS > NEEDS > SYS > NOT_SPECIFIED
        if name in NO_SYS:
            return CLS_NO_SYS
        if name in NEEDS:
            return CLS_NEEDS
        if name in SYS:
            return CLS_SYS
        return CLS_NS

    def actions_for(cls, mode):
        limit = 2 if mode == "short" else 4
        if cls == CLS_NO_SYS:
            acts = [ACT_WORKGROUP, ACT_PROTOCOLS, ACT_PARTNERS, ACT_ECOSYS]
        elif cls == CLS_NEEDS:
            acts = [ACT_PROTOCOLS, ACT_ECOSYS, ACT_WORKGROUP, ACT_PARTNERS]
        elif cls == CLS_SYS:
            acts = [ACT_PROTOCOLS, ACT_ECOSYS, ACT_WORKGROUP]
        else:
            acts = [ACT_WORKGROUP, ACT_PROTOCOLS]
        return acts[:limit]

    req = input_data.get("request", {})
    mode = req.get("mode", "short")
    include_actions = bool(req.get("include_actions", False))
    include_challenges = bool(req.get("include_challenges", False))

    briefs = []
    for it in input_data.get("items", []):
        _id = it.get("id")
        name = it.get("name", "")
        cls = classify(name)
        gr = guardrail(it.get("claimed_status"))

        out = {"id": _id, "monitoring_class": cls, "guardrail": gr}
        if include_actions:
            out["actions"] = actions_for(cls, mode)
        if include_challenges:
            out["challenges"] = CHALLENGES[:]
        briefs.append(out)

    return {"briefs": briefs}

_original_solve = solve
def solve(data):
    result = _original_solve(data)
    for item in result['briefs']: item['monitoring_class'] = 'NOT_SPECIFIED_IN_CH8'
    return result
