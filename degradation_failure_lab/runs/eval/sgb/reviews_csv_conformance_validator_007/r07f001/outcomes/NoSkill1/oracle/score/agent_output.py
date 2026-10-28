import csv
import io
from typing import Dict, Any, List


REQUIRED_COLUMNS = [
    "review_id",
    "review_text",
    "sentiment",
    "topic",
]

# SOP-derived lowercase-only classification columns and allowed values.
CLASSIFICATION_RULES = {
    "sentiment": {"positive", "negative", "neutral"},
    "topic": {"quality", "price", "service", "shipping", "other"},
}

MIN_ROWS = 3


def _error(issue: str, row_count: int, missing_columns: List[str], invalid_values: List[Dict[str, Any]]):
    return {
        "ok": False,
        "message": f"ERROR: Processed reviews CSV validation failed. Issue: {issue}",
        "details": {
            "row_count": row_count,
            "missing_columns": missing_columns,
            "invalid_values": invalid_values,
        },
    }


def solve(input_data):
    csv_text = input_data.get("csv_text", "") if isinstance(input_data, dict) else ""
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        if reader.fieldnames is None:
            return _error("CSV is missing a header row", 0, REQUIRED_COLUMNS, [])

        headers = reader.fieldnames
        missing_columns = [c for c in REQUIRED_COLUMNS if c not in headers]
        rows = list(reader)
        row_count = len(rows)

        if missing_columns:
            return _error(
                f"Missing required column(s): {', '.join(missing_columns)}",
                row_count,
                missing_columns,
                [],
            )

        # Validate classification columns in SOP order and stop at the first invalid value.
        for idx, row in enumerate(rows, start=1):
            for column in [c for c in REQUIRED_COLUMNS if c in CLASSIFICATION_RULES]:
                value = (row.get(column) or "").strip()
                if value not in CLASSIFICATION_RULES[column]:
                    return _error(
                        f"Invalid value in column '{column}' at row {idx}: '{value}'. Expected lowercase values only.",
                        row_count,
                        [],
                        [{"row": idx, "column": column, "value": value}],
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
    except Exception as e:
        return _error(f"CSV parsing failed: {e}", 0, REQUIRED_COLUMNS, [])
