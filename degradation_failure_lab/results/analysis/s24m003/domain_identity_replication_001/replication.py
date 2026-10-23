"""Exact-byte B-then-A replication. Default is offline validation."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / "domain_identity_ablation_001"
EXPECTED = {
    "A": "670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb",
    "B": "edec566353ca7e3d55abdabf56b44ad80662cdeb8839bd863ac7ed288c1c023c",
}
sys.dont_write_bytecode = True


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def helper():
    path = ROOT.parent / "qsv_probe_001/probe.py"
    spec = importlib.util.spec_from_file_location("saved_probe_transport", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def protected_check():
    before = read(ROOT / "protected_before.json")
    for folder, entries in before["trees"].items():
        actual = {p.relative_to(folder).as_posix() for p in Path(folder).rglob("*") if p.is_file()}
        assert actual == set(entries), "Protected directory membership changed"
    for path, expected in before["files"].items():
        assert sha(Path(path).read_bytes()) == expected, "Protected bytes changed: " + path
    return {"unchanged": True, "files": len(before["files"]), "trees": len(before["trees"])}


def validate():
    config = read(ROOT / "replication_spec.json")
    assert sha(Path(__file__).read_bytes()) == config["script_sha256"]
    assert sha((ROOT / "protected_before.json").read_bytes()) == config["protected_manifest_sha256"]
    assert sha((ROOT / "metrics.json").read_bytes()) == config["metrics_sha256"]
    protected_check()
    assert config["order"] == ["B", "A"] and config["max_http_attempts"] == 2
    assert config["per_arm_max_attempts"] == 1
    assert config["retries"] == config["redirects"] == config["repair_requests"] == 0
    assert config["other_model_stages"] is False
    previous = read(PRIOR / "experiment_spec.json")
    assert config["endpoint"] == previous["endpoint"] == "https://api.deepseek.com/v1/chat/completions"
    assert config["timeout_s"] == previous["timeout_s"] == 180
    bodies = {}
    for arm in ("B", "A"):
        original = PRIOR / "live" / arm / "request.json"
        frozen = (ROOT / arm / "request.json").read_bytes()
        assert frozen == original.read_bytes(), "Byte mismatch"
        assert sha(frozen) == EXPECTED[arm] == config["arms"][arm]["request_sha256"]
        assert config["arms"][arm] == previous["arms"][arm]
        request = json.loads(frozen)
        assert {k: v for k, v in request.items() if k != "messages"} == previous["request_parameters"]
        assert request["stream"] is False
        user = json.loads(request["messages"][1]["content"])
        assert user["taxonomy"]["domain_type"] == ("scrapy" if arm == "B" else "default")
        for field, text in (("window", user["excerpt"]),
                            ("system", request["messages"][0]["content"]),
                            ("user", request["messages"][1]["content"])):
            assert sha(text.encode("utf-8")) == config["arms"][arm][field + "_sha256"]
        bodies[arm] = frozen  # Send the file bytes, never a reserialization.
    return config, bodies


def execute_pair(config, bodies, output, transport, token):
    assert token and all(token.encode() not in value for value in bodies.values())
    output.mkdir(exist_ok=False)  # Persistent total-budget gate; no resume or restart.
    write(output / "reservation.json", {"order": ["B", "A"], "http_budget_reserved": 2,
        "per_arm_max_attempts": 1, "retries": 0, "redirects": 0, "restart_permitted": False})
    def event(arm, state):
        with (output / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"arm": arm, "state": state,
                "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}) + "\n")
    old = helper()
    results = {}
    for arm in ("B", "A"):
        event(arm, "ATTEMPT_STARTED")
        entry = {**config, **config["arms"][arm], "probe_id": config["probe_id"] + "-" + arm}
        results[arm] = old.execute_once(entry, bodies[arm], output / arm, transport, token)
        event(arm, results[arm]["state"])
    write(output / "summary.json", {"order": ["B", "A"], "http_model_request_attempts": 2,
        "retries": 0, "other_model_calls": 0, "arms": results})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config, bodies = validate()
    if not args.execute:
        print(json.dumps({"state": "OFFLINE_READY", "model_requests": 0, "order": ["B", "A"]}))
        return
    token = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not token:
        raise RuntimeError("Credential unavailable; zero HTTP attempts")
    result = execute_pair(config, bodies, ROOT / "live", helper().post_once, token)
    print(json.dumps({arm: {key: value.get(key) for key in
        ("state", "http_model_request_attempts", "candidate_count", "native_candidate_count",
         "system_fingerprint", "finish_reason", "usage", "elapsed_s")}
        for arm, value in result.items()}))


if __name__ == "__main__":
    main()
