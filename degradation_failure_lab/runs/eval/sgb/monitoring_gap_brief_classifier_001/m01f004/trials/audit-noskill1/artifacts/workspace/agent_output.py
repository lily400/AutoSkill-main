from __future__ import annotations

from typing import Any, Dict, List
import re


NO_SYSTEMATIC = "NO_SYSTEMATIC_MONITORING"
NEEDS_IMPROVED = "NEEDS_IMPROVED_MONITORING"
SYSTEMATIC = "SYSTEMATIC_MONITORING_PRESENT"
NOT_SPECIFIED = "NOT_SPECIFIED_IN_CH8"

ACTION_ORDER = {
    NO_SYSTEMATIC: ["WORKGROUP", "STD_PROTOCOLS", "PARTNERSHIPS", "ECOSYS_MON"],
    NEEDS_IMPROVED: ["STD_PROTOCOLS", "ECOSYS_MON", "WORKGROUP", "PARTNERSHIPS"],
    SYSTEMATIC: ["STD_PROTOCOLS", "ECOSYS_MON", "WORKGROUP"],
    NOT_SPECIFIED: ["WORKGROUP", "STD_PROTOCOLS"],
}

CHALLENGES = [
    "INADEQUATE_FUNDS",
    "LACK_TRAINED_PERSONNEL",
    "INSUFFICIENT_TOOLS_PROTOCOLS",
    "POOR_DATA_MANAGEMENT",
    "INFO_SHARING_GAPS",
    "RARE_FLUCTUATING_TRADEOFFS",
]

NAME_TO_CLASS = {
}


def _classify_name(name: str) -> str:
    return NAME_TO_CLASS.get(name, NOT_SPECIFIED)


def _guardrail(claimed_status: Any) -> str:
    if not isinstance(claimed_status, str) or not claimed_status.strip():
        return "OK"
    s = claimed_status.lower()
    if re.search(r"\b(will\s+go\s+extinct|certain\s+extinction|go\s+extinct|extinct\b)", s):
        return "BLOCK"
    if re.search(r"\b(within\s+\d+\s+(?:years?|months?|days?)|by\s+\d{4}|by\s+20\d{2})\b", s):
        return "BLOCK"
    if re.search(r"\b[a-z]+\s+[a-z]+\b", s) and any(tok in s for tok in ["extinct", "extinction", "will"]):
        return "BLOCK"
    return "OK"


def _actions_for(monitoring_class: str, mode: str) -> List[str]:
    limit = 2 if mode == "short" else 4
    ordered = ACTION_ORDER.get(monitoring_class, ["WORKGROUP", "STD_PROTOCOLS"])
    return ordered[:limit]


def solve(input_data: Dict[str, Any]) -> Dict[str, Any]:
    items = input_data.get("items", []) or []
    request = input_data.get("request", {}) or {}
    mode = request.get("mode", "short")
    include_actions = bool(request.get("include_actions", False))
    include_challenges = bool(request.get("include_challenges", False))

    briefs = []
    for item in items:
        item_id = item.get("id")
        name = item.get("name", "")
        claimed_status = item.get("claimed_status")
        monitoring_class = _classify_name(name)
        brief = {
            "id": item_id,
            "monitoring_class": monitoring_class,
            "guardrail": _guardrail(claimed_status),
        }
        if include_actions:
            brief["actions"] = _actions_for(monitoring_class, mode)
        if include_challenges:
            brief["challenges"] = list(CHALLENGES)
        briefs.append(brief)

    return {"briefs": briefs}
