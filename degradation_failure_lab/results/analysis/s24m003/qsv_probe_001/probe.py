"""One authorized qsv Plan probe. Default is offline validation only."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate():
    config = read(ROOT / "probe_spec.json")
    body = (ROOT / "historical_request.json").read_bytes()
    request = json.loads(body)
    assert sha(body) == config["request_sha256"]
    assert body == Path(config["request_source"]).read_bytes()
    assert sha((ROOT / "historical_response.json").read_bytes()) == config["response_sha256"]
    assert sha(request["messages"][0]["content"].encode()) == config["system_sha256"]
    assert sha(request["messages"][1]["content"].encode()) == config["user_sha256"]
    assert {k: v for k, v in request.items() if k != "messages"} == config["request_parameters"]
    assert request["model"] == config["model"] and request["stream"] is False
    assert config["endpoint"] == "https://api.deepseek.com/v1/chat/completions"
    assert config["max_model_http_attempts"] == 1
    assert config["transport_retries"] == config["json_repair_requests"] == 0
    assert config["other_model_stages"] is False
    protected_bytes = (ROOT / "protected_before.json").read_bytes()
    assert sha(protected_bytes) == config["protected_manifest_sha256"]
    protected = json.loads(protected_bytes)
    for relative, expected in protected["source_files"].items():
        assert sha((Path(protected["source_root"]) / relative).read_bytes()) == expected, relative
    for folder, files in protected["runs"].items():
        assert {p.relative_to(folder).as_posix() for p in Path(folder).rglob("*") if p.is_file()} == set(files)
        for relative, expected in files.items():
            assert sha((Path(folder) / relative).read_bytes()) == expected, relative
    previous = protected["previous_report"]
    assert sha(Path(previous["path"]).read_bytes()) == previous["sha256"]
    for path, expected in protected["helper_files"].items():
        assert sha(Path(path).read_bytes()) == expected
    return config, body


def classify(raw):
    try:
        envelope = json.loads(raw)
        choices = envelope["choices"]
        assert len(choices) == 1
        content = choices[0]["message"]["content"]
        assert isinstance(content, str)
    except (ValueError, KeyError, TypeError, AssertionError):
        return {"state": "RESPONSE_ENVELOPE_ERROR", "strict_json_valid": False}
    result = {"model": envelope.get("model"), "system_fingerprint": envelope.get("system_fingerprint"),
              "finish_reason": choices[0].get("finish_reason"), "usage": envelope.get("usage"),
              "strict_json_valid": False, "candidates": [], "candidate_count": 0}
    try:
        parsed = json.loads(content)
        result["strict_json_valid"] = True
    except (ValueError, TypeError):
        parsed = None
    # Reuse the tested native JSON/Plan parser with an in-memory saved-response stub.
    # It never invokes a client, repair, expansion, compiler or registry.
    lab = ROOT.parents[3]
    helpers = lab / "results/analysis/s24m001/round2"
    sys.path.insert(0, str(helpers))
    sys.path.insert(0, str(Path(read(ROOT / "probe_spec.json")["source_root"])))
    spec = importlib.util.spec_from_file_location("saved_plan_contract", helpers / "single_window_probe.py")
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract)
    native = contract.classify(raw)
    result["native_parser_state"] = native["state"]
    result["native_candidates"] = native.get("native_plan_candidates", [])
    result["native_candidate_count"] = len(result["native_candidates"])
    if result["finish_reason"] != "stop":
        result["state"] = "INCOMPLETE_RESPONSE"
    elif not result["strict_json_valid"]:
        result["state"] = "INVALID_JSON"
    elif not isinstance(parsed, dict) or not isinstance(parsed.get("skills"), list) or len(parsed["skills"]) > 4:
        result["state"] = "SCHEMA_MISMATCH"
    else:
        result["candidates"] = parsed["skills"]
        result["candidate_count"] = len(parsed["skills"])
        if not parsed["skills"]:
            result["state"] = "EMPTY_PLAN"
        elif not result["native_candidate_count"]:
            result["state"] = "CANDIDATE_FILTERED"
        else:
            result["state"] = "NONEMPTY_PLAN"
    return result


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def post_once(config, body, token):
    request = urllib.request.Request(config["endpoint"], data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + token})
    # Match the historical client's system-proxy handling; no SDK, redirect or retry handler.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler(), NoRedirect())
    with opener.open(request, timeout=config["timeout_s"]) as response:
        return response.status, response.read()


def execute_once(config, body, out, transport, token):
    assert token and token.encode() not in body
    out.mkdir(exist_ok=False)  # Persistent single-attempt gate, even after a failure.
    def write(name, value):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    def save_response(name, raw):
        safe = raw.replace(token.encode(), b"[REDACTED]")
        (out / name).write_bytes(safe)
        return safe, {"wire_response_sha256": sha(raw), "saved_response_sha256": sha(safe),
                      "credential_redaction_required": safe != raw}
    (out / "request.json").write_bytes(body)
    write("attempt.json", {"probe_id": config["probe_id"], "http_attempts_reserved": 1,
        "request_sha256": sha(body), "window_sha256": config["window_sha256"],
        "system_sha256": config["system_sha256"], "user_sha256": config["user_sha256"],
        "max_model_http_attempts": 1, "retries": 0, "state": "ATTEMPT_RESERVED"})
    start = time.monotonic()
    try:
        status, raw = transport(config, body, token)  # Sole model HTTP attempt.
    except urllib.error.HTTPError as exc:
        safe, evidence = save_response("http_error_body.bin", exc.read())
        result = {"state": "HTTP_ERROR", "http_status": exc.code, **evidence}
    except (OSError, urllib.error.URLError) as exc:
        result = {"state": "TRANSPORT_ERROR", "error_type": type(exc).__name__}
    else:
        safe, evidence = save_response("response.raw.json", raw)  # Save before any parsing.
        if evidence["credential_redaction_required"]:
            result = {"state": "RESPONSE_REDACTED", "http_status": status, **evidence}
        else:
            result = {**classify(safe), "http_status": status, **evidence}
    result.update(http_model_request_attempts=1, retries=0, json_repair_requests=0,
        outline_calls=0, expand_calls=0, compile_calls=0, register_calls=0,
        elapsed_s=time.monotonic() - start, request_sha256=sha(body), price_and_cost="UNKNOWN")
    write("result.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config, body = validate()
    if not args.execute:
        print(json.dumps({"state": "OFFLINE_READY", "new_model_requests": 0,
                          "request_sha256": config["request_sha256"]}))
        return
    output = ROOT / "live_001"
    if output.exists():
        raise FileExistsError("Attempt already reserved; no resend permitted")
    token = os.environ.get(config["credential_env"], "").strip()
    if not token:
        raise RuntimeError("Credential unavailable; no HTTP attempt")
    result = execute_once(config, body, output, post_once, token)
    print(json.dumps({k: result.get(k) for k in (
        "state", "http_model_request_attempts", "candidate_count", "native_candidate_count",
        "model", "system_fingerprint", "finish_reason", "usage", "elapsed_s",
        "request_sha256", "saved_response_sha256")}, ensure_ascii=True))


if __name__ == "__main__":
    main()
