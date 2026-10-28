
"""Authorize one exact SGB JSON-task NoSkill/CleanSkill experiment.

Must run BEFORE pilot prepare.

Preview:
    python scripts/sgb/authorize_downstream.py --task monitoring_gap_brief_classifier_001 --generator-run m01g001 --experiment m01f002

Approve:
    python scripts/sgb/authorize_downstream.py --task monitoring_gap_brief_classifier_001 --generator-run m01g001 --experiment m01f002 --approve

No model calls are made by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from downstream_eval.sgb.downstream_authorization import authorization_path, authorize, load_authorization, ADAPTERS
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")


def fail(message):
    raise SystemExit("BLOCKED: " + message)


def inside(relative):
    path = Path(relative)
    if path.is_absolute():
        fail("Absolute path not allowed")
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


def task_bytes(value):
    # Same JSON serialization as degradation_lab.io.write.
    return (
        json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--generator-run", required=True)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()

    task_id = args.task
    generator = args.generator_run
    experiment = args.experiment

    for value in (task_id, generator, experiment):
        if not IDENTIFIER.fullmatch(value):
            fail("Invalid identifier: " + value)

    task_rel = f"configs/tasks/sgb/{task_id}.json"
    task_path = inside(task_rel)
    task = load(task_path)

    if task.get("task_id") != task_id:
        fail("Task identity mismatch")

    if task.get("adapter") not in ADAPTERS:
        fail("This script supports audited JSON/object tasks only")

    if task.get("conditions") != {
        "NoSkill1": "NoSkill",
        "CleanSkill1": "CleanSkill",
    }:
        fail("Task does not match paired protocol")

    case_id = task.get("case_id")
    if not isinstance(case_id, str) or not IDENTIFIER.fullmatch(case_id):
        fail("Invalid Case ID")

    # Confirm task binding has not changed.
    dataset = load(ROOT / "configs/datasets/sgb.json")
    registry_path = inside(dataset["registry"])

    if sha256(registry_path) != dataset["registry_sha256"]:
        fail("SGB registry hash mismatch")

    matches = []
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("original_task_id") == task_id:
                matches.append(row)

    if len(matches) != 1:
        fail("Expected exactly one registered task")

    binding = matches[0].get("pilot_config", {})

    if (
        binding.get("path") != task_rel
        or binding.get("sha256") != sha256(task_path)
    ):
        fail("Pilot task binding mismatch")

    case = load(
        ROOT / "cases" / "sgb" / case_id / "case.json"
    )

    if case.get("case_id") != case_id:
        fail("Case identity mismatch")

    gate_rel = case["execution_gate"]
    gate_path = inside(gate_rel)

    if gate_rel not in task.get("freeze_files", []):
        fail("Gate is not included in frozen task files")

    gate = load(gate_path)

    if gate.get("task_id") != task_id:
        fail("Gate task identity mismatch")

    if gate.get("authorization_contract") != "exact-generation-v1":
        fail("Unsupported authorization contract")

    if (
        gate.get("status") != "PASS"
        or gate.get("requested_generation", {}).get(
            "authorization_status"
        ) != "AUTHORIZED"
    ):
        fail("Generation authorization is not PASS")

    if gate["requested_generation"].get("run_id") != generator:
        fail("Generator run does not match upstream authorization")

    generation_path = (
        ROOT / "runs" / "gen" / "sgb"
        / case_id / "clean" / generator
    )

    result = load(generation_path / "official_result.json")
    invocation = load(generation_path / "invocation.json")

    if (
        result.get("status") != "completed"
        or result.get("errors")
        or invocation.get("run_id") != generator
        or invocation.get("case_id") != case_id
        or invocation.get("condition_id") != "clean"
        or invocation.get("execution_kind") != "official"
        or invocation.get("real_generation") is not True
    ):
        fail("Completed real Clean generation required")

    protocol = load(
        ROOT / "configs/sgb/clean_pair_protocol.json"
    )
    template = load(inside(task["profile_template"]))

    if (
        protocol.get("protocol_id") != "clean-pair-v1"
        or protocol.get("conditions") != task["conditions"]
        or protocol.get("model") != template.get("model")
        or protocol.get("budget") != template.get("budget")
        or protocol.get("repeats_per_arm") != 1
    ):
        fail("Formal protocol or model configuration mismatch")

    per_arm = template["budget"]["max_requests"]
    total = per_arm * len(task["conditions"])

    if per_arm != 6 or total != 12:
        fail("Expected 6 requests per arm, 12 total")

    config_hash = hashlib.sha256(
        task_bytes(task)
    ).hexdigest()

    record = authorization_path(ROOT, task_id, experiment)

    print(json.dumps({
        "task_id": task_id,
        "generator_run_id": generator,
        "experiment_id": experiment,
        "model": template["model"]["name"],
        "conditions": task["conditions"],
        "per_arm_http_limit": per_arm,
        "global_http_limit": total,
        "task_config_sha256": config_hash,
        "authorization_record": record.relative_to(ROOT).as_posix(),
    }, ensure_ascii=False, indent=2))

    if record.exists():
        load_authorization(ROOT, task, generator, experiment)
        print("ALREADY_AUTHORIZED: No change")
        return

    if not args.approve:
        print("PREVIEW_ONLY: Add --approve to authorize")
        return

    record, _ = authorize(ROOT, task, generator, experiment)

    print("AUTHORIZED_DOWNSTREAM:", experiment)
    print("AUTHORIZATION_RECORD:", record)
    print(
        "NEXT: python scripts/sgb/pilot.py prepare"
        f" --task {task_id}"
        f" --generator-run {generator}"
        f" --experiment {experiment}"
    )


if __name__ == "__main__":
    main()
