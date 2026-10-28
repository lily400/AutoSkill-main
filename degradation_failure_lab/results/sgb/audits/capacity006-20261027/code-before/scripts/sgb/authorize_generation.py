
"""Authorize one exact Clean Anything2Skill generation.

Preview:
    python scripts/sgb/authorize_generation.py --case case102_capacity --run-id e06g001

Approve:
    python scripts/sgb/authorize_generation.py --case case102_capacity --run-id e06g001 --approve

This script never calls a model.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")


def fail(message):
    raise SystemExit("BLOCKED: " + message)


def inside(relative):
    path = Path(relative)
    if path.is_absolute():
        fail("Absolute paths are not allowed")
    result = (ROOT / path).resolve()
    if not result.is_relative_to(ROOT.resolve()):
        fail("Path escapes project")
    return result


def load(path):
    if not path.is_file():
        fail("Missing file: " + str(path))
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_gate(path, updated, original):
    if path.read_bytes() != original:
        fail("Gate changed during authorization")

    stamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    backup = path.with_name(path.name + ".bak." + stamp)
    shutil.copy2(path, backup)

    temp = path.with_name(path.name + ".tmp." + stamp)
    try:
        with temp.open("xb") as file:
            file.write(
                (json.dumps(updated, ensure_ascii=False, indent=2)
                 + "\n").encode("utf-8")
            )
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

    return backup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()

    case_id = args.case
    run_id = args.run_id

    if not IDENTIFIER.fullmatch(case_id):
        fail("Invalid case ID")
    if not IDENTIFIER.fullmatch(run_id):
        fail("Invalid run ID")

    case = load(
        ROOT / "cases" / "sgb" / case_id / "case.json"
    )

    if case.get("case_id") != case_id:
        fail("Case identity mismatch")

    conditions = load(
        ROOT / "cases" / "sgb" / case_id / "conditions.json"
    )
    if not any(
        c.get("condition_id") == "clean"
        and c.get("kind") == "clean"
        for c in conditions.get("conditions", [])
    ):
        fail("No admitted Clean condition")

    inputs = load(
        ROOT / "cases" / "sgb" / case_id
        / "inputs" / "clean.json"
    )

    if (inputs.get("case_id") != case_id
            or inputs.get("condition_id") != "clean"):
        fail("Input manifest mismatch")

    if not inputs.get("inputs"):
        fail("No source documents")

    for item in inputs["inputs"]:
        if sha256(inside(item["path"])) != item["sha256"]:
            fail("Source hash mismatch: " + item["path"])

    config_rel = case["generation_config"]
    config_path = inside(config_rel)
    config = load(config_path)

    http = config.get("max_http_calls")
    tokens = config.get("max_observed_total_tokens")

    if type(http) is not int or http <= 0:
        fail("Invalid HTTP budget")
    if type(tokens) is not int or tokens <= 0:
        fail("Invalid Token budget")
    if not config.get("llm", {}).get("model"):
        fail("Missing generation model")
    if not config.get("credential_env"):
        fail("Missing credential configuration")

    gate_path = inside(case["execution_gate"])
    original = gate_path.read_bytes()
    gate = load(gate_path)

    if gate.get("authorization_contract") != "exact-generation-v1":
        fail("Unsupported authorization contract")
    if not isinstance(gate.get("requested_generation"), dict):
        fail("Missing generation authorization object")
    if not gate.get("task_id"):
        fail("Missing task identity")

    approval = {
        "authorization_status": "AUTHORIZED",
        "run_id": run_id,
        "case_id": case_id,
        "condition_id": "clean",
        "configuration": config_rel,
        "configuration_sha256": sha256(config_path),
        "max_http_calls": http,
        "max_observed_total_tokens": tokens,
    }

    print(json.dumps({
        "case_id": case_id,
        "run_id": run_id,
        "model": config["llm"]["model"],
        "max_http_calls": http,
        "max_observed_total_tokens": tokens,
        "configuration_sha256": sha256(config_path),
        "note": "Token threshold is not a strict hard cap",
    }, ensure_ascii=False, indent=2))

    if (
        gate.get("status") == "PASS"
        and all(
            gate["requested_generation"].get(k) == v
            for k, v in approval.items()
        )
    ):
        print("ALREADY_AUTHORIZED")
        return

    if not args.approve:
        print("PREVIEW_ONLY: Add --approve to authorize")
        return

    # Never approve a generation identity already used.
    target = (
        ROOT / "runs" / "gen" / "sgb"
        / case_id / "clean" / run_id
    )

    if target.exists():
        fail("Generation run already exists")

    for pattern in (
        "gen/sgb/*/*/*/invocation.json",
        "case*/*/*/invocation.json",
    ):
        for path in (ROOT / "runs").glob(pattern):
            if load(path).get("run_id") == run_id:
                fail("Generation ID already used")

    index = ROOT / "results" / "run_index.jsonl"
    if index.is_file():
        for line in index.read_text(encoding="utf-8").splitlines():
            if line.strip() and json.loads(line).get("run_id") == run_id:
                fail("Run ID found in historical index")

    task_id = gate["task_id"]
    downstream = ROOT / "runs" / "eval" / "sgb" / task_id

    if downstream.exists() and any(
        downstream.glob("*/batch.started")
    ):
        fail("A downstream trial already started for this task")

    gate["status"] = "PASS"
    gate["reason"] = "User-authorized Clean generation " + run_id
    gate["requested_generation"] = approval

    backup = save_gate(gate_path, gate, original)

    print("AUTHORIZED_GENERATION:", run_id)
    print("BACKUP:", backup)
    print(
        "NEXT: python scripts/lab.py run"
        f" --case {case_id}"
        " --condition clean --repeat 1"
        f" --run-id {run_id}"
    )


if __name__ == "__main__":
    main()
