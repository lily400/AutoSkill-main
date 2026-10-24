"""Two-arm domain identity diagnosis; no model calls unless --execute."""
import argparse
import copy
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[3]
SOURCE = LAB.parent / "AutoSkill-main"
HISTORY = LAB / "runs/case024_scrapy/clean/s24m003/http/019"
PRIOR = ROOT.parent / "qsv_probe_001"
EXPECTED_A = "670bde12f3ceb64ccd0c9206cbf844860499e4de1ce5ef473644ca052a7385bb"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SOURCE))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def helper():
    spec = importlib.util.spec_from_file_location("frozen_qsv_transport", PRIOR / "probe.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fields(a, b, path=""):
    if type(a) is not type(b):
        return [{"path": path, "A": a, "B": b}]
    if isinstance(a, dict):
        result = []
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                result.append({"path": path + "/" + key, "A": a.get(key), "B": b.get(key)})
            else:
                result += fields(a[key], b[key], path + "/" + key)
        return result
    if isinstance(a, list):
        if len(a) != len(b):
            return [{"path": path, "A": a, "B": b}]
        return [item for i, (x, y) in enumerate(zip(a, b)) for item in fields(x, y, path + "/" + str(i))]
    return [] if a == b else [{"path": path, "A": a, "B": b}]


def expanded(request):
    value = copy.deepcopy(request)
    value["messages"][1]["content"] = json.loads(value["messages"][1]["content"])
    return value


def build_arms(body):
    from AutoSkill4Doc.taxonomy import load_skill_taxonomy
    from AutoSkill4Doc.prompts import maybe_offline_prompt, OFFLINE_CHANNEL_DOC
    assert sha(body) == EXPECTED_A, "Original HTTP019 binding mismatch"
    a = json.loads(body)
    payload = json.loads(a["messages"][1]["content"])
    assert payload["max_candidates"] == 4 and payload["document"]["domain"] == ""
    default = load_skill_taxonomy(domain_type="default")
    scrapy = load_skill_taxonomy(domain_type="scrapy")
    def prompt(taxonomy):
        return maybe_offline_prompt(channel=OFFLINE_CHANNEL_DOC, kind="extract_plan",
                                    max_candidates=4, taxonomy=taxonomy)
    assert a["messages"][0]["content"] == prompt(default)
    assert payload["taxonomy"] == default.to_dict()
    assert a["messages"][1]["content"] == json.dumps(payload, ensure_ascii=False)
    b = copy.deepcopy(a)
    b["messages"][0]["content"] = prompt(scrapy)
    payload["taxonomy"] = scrapy.to_dict()
    b["messages"][1]["content"] = json.dumps(payload, ensure_ascii=False)
    check_diff(a, b)
    return {"A": body, "B": json.dumps(b, ensure_ascii=False, indent=2).encode("utf-8")}


def check_diff(a, b):
    diff = fields(expanded(a), expanded(b))
    expected = {
        "/messages/0/content",
        "/messages/1/content/taxonomy/domain_type",
        "/messages/1/content/taxonomy/taxonomy_id",
    }
    assert {x["path"] for x in diff} == expected and len(diff) == 3, "Unregistered field change"
    # Guard the entire system string, not just its field name.
    mark = chr(96)
    old = "Domain type is externally provided as " + mark + "default" + mark + "."
    new = "Domain type is externally provided as " + mark + "scrapy" + mark + "."
    assert a["messages"][0]["content"].count(old) == 1
    assert b["messages"][0]["content"] == a["messages"][0]["content"].replace(old, new, 1)
    for item in diff[1:]:
        if item["path"] != "/messages/0/content":
            assert item["A"] == "default" and item["B"] == "scrapy"
    return diff


def protected_check():
    before = read(ROOT / "protected_before.json")
    for name, files in before["trees"].items():
        folder = Path(name)
        actual = {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}
        assert actual == set(files), "Protected file membership changed: " + name
    for path, expected in before["files"].items():
        assert sha(Path(path).read_bytes()) == expected, "Protected bytes changed: " + path
    return {"protected_files": len(before["files"]), "protected_trees": len(before["trees"]),
            "unchanged": True}


def validate():
    config = read(ROOT / "experiment_spec.json")
    assert sha((ROOT / "protected_before.json").read_bytes()) == config["protected_manifest_sha256"]
    protected_check()
    assert sha(Path(__file__).read_bytes()) == config["probe_script_sha256"]
    bodies = build_arms((HISTORY / "request.json").read_bytes())
    assert config["max_model_http_attempts"] == 2 and config["per_arm_max_attempts"] == 1
    assert config["retries"] == config["repair_requests"] == 0
    assert config["other_model_stages"] is False
    assert config["endpoint"] == read(HISTORY / "event.json")["endpoint"]
    assert config["endpoint"] == "https://api.deepseek.com/v1/chat/completions"
    assert config["timeout_s"] == 180
    for arm in ("A", "B"):
        entry = config["arms"][arm]
        body = (ROOT / arm / "request.json").read_bytes()
        assert body == bodies[arm] and sha(body) == entry["request_sha256"]
        request = json.loads(body)
        user = json.loads(request["messages"][1]["content"])
        for field, text in (("window", user["excerpt"]),
                            ("system", request["messages"][0]["content"]),
                            ("user", request["messages"][1]["content"])):
            assert sha(text.encode()) == entry[field + "_sha256"]
        assert {k: v for k, v in request.items() if k != "messages"} == config["request_parameters"]
        assert request["stream"] is False
    actual_diff = check_diff(json.loads(bodies["A"]), json.loads(bodies["B"]))
    assert actual_diff == read(ROOT / "field_diff.json")
    return config, bodies


def execute_pair(config, bodies, output, transport, token):
    assert token and all(token.encode() not in body for body in bodies.values())
    output.mkdir(exist_ok=False)  # Global persistent gate: cannot resume or resend either arm.
    write(output / "reservation.json", {"max_model_http_attempts": 2, "arms": ["A", "B"],
        "per_arm_max_attempts": 1, "retries": 0, "redirects": 0,
        "state": "TWO_ATTEMPT_BUDGET_RESERVED", "restart_permitted": False})
    saved = {}
    old = helper()
    for arm in ("A", "B"):  # Only these two calls; no SDK, retry, repair or full pipeline.
        arm_config = {**config, **config["arms"][arm], "probe_id": config["probe_id"] + "-" + arm}
        saved[arm] = old.execute_once(arm_config, bodies[arm], output / arm, transport, token)
    write(output / "summary.json", {"arms": saved, "http_model_request_attempts": 2,
        "retries": 0, "other_model_calls": 0})
    return saved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config, bodies = validate()
    if not args.execute:
        print(json.dumps({"state": "OFFLINE_READY", "new_model_requests": 0,
                          "diff_paths": [x["path"] for x in read(ROOT / "field_diff.json")]}))
        return
    token = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not token:
        raise RuntimeError("Credential unavailable; zero HTTP calls")
    results = execute_pair(config, bodies, ROOT / "live", helper().post_once, token)
    print(json.dumps({arm: {k: result.get(k) for k in
        ("state", "http_model_request_attempts", "candidate_count", "native_candidate_count",
         "system_fingerprint", "finish_reason", "usage", "elapsed_s")} for arm, result in results.items()}))


if __name__ == "__main__":
    main()
