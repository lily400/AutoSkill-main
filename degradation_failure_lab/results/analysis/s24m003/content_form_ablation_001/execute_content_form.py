"""Content-form A/B probe; exact bytes, two attempts, no retries. Default offline."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DESIGN = ROOT.parent / "content_form_design_001"
EXPECTED = {
    "A": "edec566353ca7e3d55abdabf56b44ad80662cdeb8839bd863ac7ed288c1c023c",
    "B": "3d5193a46be9999e0e6c13745dcf2cecf970c8e168c5419721c9e3fea023dabf",
}
sys.dont_write_bytecode = True
def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_bytes())
def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def pair_helper():
    path = ROOT.parent / "domain_identity_ablation_001/ablation.py"
    spec = importlib.util.spec_from_file_location("saved_AB_gate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def protected_check():
    protected = read(ROOT / "protected_before.json")
    for folder, entries in protected["trees"].items():
        assert {p.relative_to(folder).as_posix() for p in Path(folder).rglob("*") if p.is_file()} == set(entries)
    for path, expected in protected["files"].items():
        assert sha(Path(path).read_bytes()) == expected, path
    return {"unchanged": True, "files": len(protected["files"]), "trees": len(protected["trees"])}

def validate():
    config = read(ROOT / "execution_spec.json")
    assert sha(Path(__file__).read_bytes()) == config["script_sha256"]
    assert sha((ROOT/"protected_before.json").read_bytes()) == config["protected_manifest_sha256"]
    assert sha((DESIGN/"preregistered_metrics.json").read_bytes()) == config["metrics_sha256"]
    protected_check()
    assert config["order"] == ["A","B"] and config["max_model_http_attempts"] == 2
    assert config["per_arm_max_attempts"] == 1 and config["other_model_stages"] is False
    assert config["retries"] == config["redirects"] == config["repair_requests"] == 0
    planned = read(DESIGN / "future_execution_plan.json")
    assert config["endpoint"] == planned["endpoint"] == "https://api.deepseek.com/v1/chat/completions"
    assert config["timeout_s"] == planned["timeout_s"] == 180
    manifest = read(DESIGN / "source_manifest.json")
    assert read(DESIGN/"validation_results.json")["status"] == "PASS"
    bodies = {}
    for arm in ("A","B"):
        body = (DESIGN/arm/"request.json").read_bytes()
        assert sha(body) == EXPECTED[arm] == config["arms"][arm]["request_sha256"]
        request = json.loads(body)
        assert {k:v for k,v in request.items() if k!="messages"} == planned["request_parameters"]
        payload = json.loads(request["messages"][1]["content"])
        assert payload["taxonomy"]["domain_type"] == "scrapy"
        assert payload["section"]["span"] == {"start":15603,"end":17155}
        assert len(payload["excerpt"]) == (1552 if arm=="A" else 1643)
        for field, value in (("window",payload["excerpt"]),
                             ("system",request["messages"][0]["content"]),
                             ("user",request["messages"][1]["content"])):
            assert sha(value.encode()) == config["arms"][arm][field+"_sha256"]
        assert sha(payload["excerpt"].encode()) == manifest["arms"][arm]["excerpt_sha256"]
        bodies[arm] = body  # Never reconstruct or serialize the HTTP body.
    return config, bodies

def bounded_transport(config, output, post):
    consumed = set()
    def send(actual_config, body, token):
        arm = next((key for key,value in EXPECTED.items() if sha(body)==value),None)
        assert arm is not None, "Unfrozen input"
        assert arm not in consumed and len(consumed)<2, "Attempt budget already consumed"
        assert actual_config["endpoint"] == config["endpoint"]
        assert actual_config["timeout_s"] == config["timeout_s"]
        consumed.add(arm)  # Failure consumes the arm; no resend.
        def event(state):
            with (output/"events.jsonl").open("a",encoding="utf-8") as handle:
                handle.write(json.dumps({"arm":arm,"state":state,"request_sha256":sha(body),
                    "utc":datetime.datetime.now(datetime.timezone.utc).isoformat()})+"\n")
        event("HTTP_ATTEMPT_STARTED")
        try:
            return post(actual_config,body,token)  # Exactly one call; no retry/repair.
        finally:
            event("HTTP_ATTEMPT_RETURNED_OR_RAISED")
    return send

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute",action="store_true")
    args = parser.parse_args()
    config,bodies = validate()
    if not args.execute:
        print(json.dumps({"state":"OFFLINE_READY","model_calls":0,"order":["A","B"]}))
        return
    assert read(ROOT/"contract_tests.json")["passed"]
    token = os.environ.get("DEEPSEEK_API_KEY","").strip()
    if not token:
        raise RuntimeError("Credential unavailable; zero HTTP attempts")
    old = pair_helper()
    output = ROOT/"live"
    transport = bounded_transport(config,output,old.helper().post_once)
    # Reuse the unchanged, tested A-then-B loop and persistent global/per-arm gates.
    result = old.execute_pair(config,bodies,output,transport,token)
    print(json.dumps({arm:{key:value.get(key) for key in
        ("state","http_model_request_attempts","candidate_count","native_candidate_count",
         "system_fingerprint","finish_reason","usage","elapsed_s")}
        for arm,value in result.items()}))

if __name__ == "__main__":
    main()
