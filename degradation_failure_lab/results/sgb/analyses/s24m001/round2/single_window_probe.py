"""Default: offline validation only. --execute requires subsequent human approval.

One frozen POST, redirects disabled, no retry, no SDK model client, no expansion.
The output directory is an exclusive attempt marker; never reuse it.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

from fidelity import SOURCE_SHA256, assert_rule_fidelity, digest


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(bundle):
    config = read(bundle / "single_window_config.json")
    body = (bundle / "single_window_request.json").read_bytes()
    request = json.loads(body)
    window = (bundle / "single_window.txt").read_bytes().decode("utf-8")
    source = (Path(config["source_run"]) / "inputs/input001/feed-exports.md").read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256 == config["source_sha256"]
    assert hashlib.sha256(body).hexdigest() == config["request_sha256"]
    assert digest(window) == config["window_sha256"]
    assert digest(request["messages"][0]["content"]) == config["system_prompt_sha256"]
    payload = json.loads(request["messages"][-1]["content"])
    assert payload["excerpt"] == window
    assert_rule_fidelity(source.decode("utf-8"), window)
    assert config["http_attempt_limit"] == 1 and config["transport_retries"] == config["json_repair_requests"] == 0
    assert not any(config[k] for k in ("automatic_expand", "automatic_compile", "automatic_register"))
    assert config["endpoint"] == "https://api.deepseek.com/v1/chat/completions"
    assert request["model"] == config["model"] == "deepseek-flash"
    upstream = Path(config["official_upstream"])
    assert hashlib.sha256((upstream / "AutoSkill4Doc/stages/extractor.py").read_bytes()).hexdigest() == config["native_plan_parser_sha256"]
    # Bind all imported official files, not only the extractor.
    for relative, expected in read(Path(config["source_run"]) / "upstream_before.json").items():
        assert hashlib.sha256((upstream / relative).read_bytes()).hexdigest() == expected, relative
    sys.path.insert(0, str(upstream))
    return config, body


def classify(response_bytes):
    from autoskill.utils.json import json_from_llm_text
    from AutoSkill4Doc.stages.extractor import LLMDocumentSkillExtractor
    try:
        response = json.loads(response_bytes)
        choices = response["choices"]
        assert len(choices) == 1
        content = choices[0]["message"]["content"]
        assert isinstance(content, str)
    except (ValueError, KeyError, TypeError, AssertionError):
        return {"state": "RESPONSE_ENVELOPE_ERROR"}
    result = {"usage": response.get("usage"), "response_model": response.get("model"),
              "finish_reason": choices[0].get("finish_reason"), "cost": "UNKNOWN"}
    try:
        parsed = json_from_llm_text(content)
    except (ValueError, TypeError) as exc:
        return dict(result, state="JSON_PARSE_FAILURE", error_type=type(exc).__name__)
    extractor = object.__new__(LLMDocumentSkillExtractor)
    extractor.max_candidates_per_unit = 4
    extractor._complete_extract_json = lambda **kwargs: parsed  # Saved response only; no repair request.
    plans = extractor._plan_unit_skills(payload={}, record=None, section_heading="Feed exports")
    raw = parsed.get("skills") if isinstance(parsed, dict) else parsed
    schema_ok = isinstance(parsed, dict) and isinstance(raw, list) and len(raw) <= 4
    result.update(parsed=parsed, native_plan_candidates=plans, prompt_schema_top_level_ok=schema_ok)
    if not schema_ok:
        state = "SCHEMA_MISMATCH"
    elif not raw:
        state = "EMPTY_PLAN"
    elif not plans:
        state = "CANDIDATE_FILTERED"
    else:
        state = "NONEMPTY_PLAN_TARGET_REVIEW_REQUIRED"
    if result["finish_reason"] != "stop":
        return dict(result, state="INCOMPLETE_RESPONSE", parsed_state=state)
    return dict(result, state=state, target_rule_review="NOT_AUTOMATICALLY_ESTABLISHED")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def post_once(config, body, token):
    request = urllib.request.Request(config["endpoint"], data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + token})
    # Proxy environment is not inherited; one explicit endpoint, no redirect retry.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    with opener.open(request, timeout=config["timeout_s"]) as response:
        return response.read()


def execute_once(config, body, out, transport, token):
    out.mkdir(parents=True, exist_ok=False)  # Refuse even a previous failed attempt.
    def write(name, obj):
        (out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "request.json").write_bytes(body)
    write("attempt.json", {"http_attempts": 1, "state": "ATTEMPT_RESERVED", "probe_id": config["probe_id"],
        "request_sha256": hashlib.sha256(body).hexdigest(), "window_sha256": config["window_sha256"],
        "system_prompt_sha256": config["system_prompt_sha256"]})
    start = time.monotonic()
    try:
        raw = transport(config, body, token)
    except urllib.error.HTTPError as exc:
        (out / "http_error_body.bin").write_bytes(exc.read())
        result = {"state": "HTTP_ERROR", "http_status": exc.code}
    except (OSError, urllib.error.URLError) as exc:
        result = {"state": "TRANSPORT_ERROR", "error_type": type(exc).__name__}
    else:
        (out / "response.raw.json").write_bytes(raw)  # Save before parsing.
        result = classify(raw)
    result.update(elapsed_s=time.monotonic() - start, http_attempts=1, retries=0,
                  expand_calls=0, compile_calls=0, register_calls=0)
    write("result.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    config, body = validate(args.bundle.resolve())
    if not args.execute:
        print(json.dumps({"state": "OFFLINE_READY", "model_calls": 0, "request_sha256": config["request_sha256"]}))
        return
    if args.out is None:
        parser.error("--out is required with --execute")
    for protected in (args.bundle, Path(config["source_run"]), Path(config["official_upstream"])):
        if args.out.resolve() == protected.resolve() or protected.resolve() in args.out.resolve().parents:
            parser.error("Execution output must be separate from frozen input, history, and official source")
    token = os.environ.get(config["credential_env"], "").strip()
    if not token:
        parser.error("Missing secure credential environment variable; no request attempted")
    print(json.dumps(execute_once(config, body, args.out.resolve(), post_once, token), ensure_ascii=True))


if __name__ == "__main__":
    main()
