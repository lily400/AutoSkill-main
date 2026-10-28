import csv
import io
from typing import Any, Dict, List


REQUIRED_COLUMNS = [
    "review_id",
    "review",
    "is_sportswear",
    "is_apparel_product",
    "brand",
    "competitor_or_nike",
]

ALLOWED_VALUES = {
    "is_sportswear": {"yes", "no"},
    "is_apparel_product": {"yes", "no"},
    "competitor_or_nike": {"nike", "competitor", "n/a"},
}

MIN_ROWS = 20


def _error(issue: str, row_count: int, missing_columns: List[str], invalid_values: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "ok": False,
        "message": f"ERROR: Processed reviews CSV validation failed. Issue: {issue}",
        "details": {
            "row_count": row_count,
            "missing_columns": missing_columns,
            "invalid_values": invalid_values,
        },
    }


def solve(input_data: Dict[str, Any]) -> Dict[str, Any]:
    csv_text = input_data.get("csv_text", "") if isinstance(input_data, dict) else ""
    if not isinstance(csv_text, str):
        csv_text = str(csv_text)

    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        if reader.fieldnames is None:
            return _error("CSV could not be parsed or is missing a header row", 0, REQUIRED_COLUMNS[:], [])
        rows = list(reader)
    except Exception:
        return _error("CSV could not be parsed", 0, REQUIRED_COLUMNS[:], [])

    row_count = len(rows)
    header = reader.fieldnames or []

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing_columns:
        return _error(
            f"Missing required column(s): {', '.join(missing_columns)}",
            row_count,
            missing_columns,
            [],
        )

    first_invalid = None
    for idx, row in enumerate(rows, start=1):
        for col in ["is_sportswear", "is_apparel_product", "competitor_or_nike"]:
            value = (row.get(col) or "")
            if value not in ALLOWED_VALUES[col]:
                first_invalid = {"row": idx, "column": col, "value": value}
                break
        if first_invalid:
            break

    if first_invalid:
        return _error(
            f"Invalid value in row {first_invalid['row']} column {first_invalid['column']}: {first_invalid['value']!r}; values must be lowercase and within the allowed set",
            row_count,
            [],
            [first_invalid],
        )

    if row_count < MIN_ROWS:
        return _error(
            f"Only {row_count} rows found, expected at least {MIN_ROWS}",
            row_count,
            [],
            [],
        )

    return {
        "ok": True,
        "message": f"SUCCESS: Processed reviews CSV validated ({row_count} rows).",
        "details": {
            "row_count": row_count,
            "missing_columns": [],
            "invalid_values": [],
        },
    }
