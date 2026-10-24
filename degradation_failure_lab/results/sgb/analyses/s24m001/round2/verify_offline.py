"""Replay saved Outline, exercise preprocessing/tests, and freeze a Plan request.

No model client is constructed. Network and subprocess audit events are denied.
"""
import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

from fidelity import SOURCE_SHA256, assert_rule_fidelity, digest, unique_source_ranges


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    run, upstream, out = args.run.resolve(), args.upstream.resolve(), args.out.resolve()
    if any(root == out or root in out.parents for root in (run, upstream)):
        raise ValueError("Output must be outside original evidence and source")
    out.mkdir(parents=True, exist_ok=False)
    checkpoint_temp = tempfile.TemporaryDirectory(prefix="s24cp_", dir=Path.cwd())
    checkpoint_root = Path(checkpoint_temp.name).resolve()
    def guard(event, values):
        if event.startswith("socket.") or event.startswith("subprocess.") or event == "os.system":
            raise RuntimeError("OFFLINE_ONLY: no network/subprocess allowed")
        if event == "open":
            path, mode, flags = values
            if ((isinstance(mode, str) and any(x in mode for x in "wax+")) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)):
                if not any(Path(path).resolve().is_relative_to(root) for root in (out, checkpoint_root)):
                    raise RuntimeError("Write outside validation output forbidden")
    sys.addaudithook(guard)
    def write(name, value):
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        (out / name).write_bytes(text.encode("utf-8"))
    manifest = read(run / "artifact_manifest.json")
    assert all(hashlib.sha256((run / p).read_bytes()).hexdigest() == h for p, h in manifest.items())
    old = read(next(run.glob("SkillBank/.runtime/intermediate_runs/*/ingest/result.json")))
    source_bytes = (run / "inputs/input001/feed-exports.md").read_bytes()
    assert hashlib.sha256(source_bytes).hexdigest() == SOURCE_SHA256
    source = source_bytes.decode("utf-8").replace("\r\n", "\n")
    sys.path.insert(0, str(upstream))
    from AutoSkill4Doc.ingest import HeuristicDocumentIngestor, compute_content_hash
    from AutoSkill4Doc.document.windowing import build_windows_for_record
    from AutoSkill4Doc.models import DocumentRecord
    from autoskill.llm.base import LLM
    outline_request = read(run / "http/001/request.json")
    outline_response = read(run / "http/001/response.json")["choices"][0]["message"]["content"]
    class SavedOutline(LLM):
        reads = 0
        def complete(self, *, system, user, temperature=0.0):
            assert self.reads == 0, "Expected exactly one saved Outline read"
            assert system == outline_request["messages"][0]["content"]
            assert json.loads(user) == json.loads(outline_request["messages"][-1]["content"])
            self.reads += 1
            return outline_response
    saved = SavedOutline()
    record = DocumentRecord.from_dict(old["documents"][0])
    record.sections = HeuristicDocumentIngestor(llm=saved, llm_rate_limit_requests=0)._parse_sections_with_fallback(
        raw_text=record.raw_text, default_title=record.title, logger=None)
    windows = build_windows_for_record(record, strategy="recommended", max_section_chars=10000)
    baseline_exact = None
    if args.baseline:
        baseline_exact = ([s.to_dict() for s in record.sections] == old["documents"][0]["sections"]
                          and [w.to_dict() for w in windows] == old["windows"])
        assert baseline_exact, "Cannot reproduce historical sections/windows from saved Outline"
    else:
        record.content_hash = record.checksum = compute_content_hash(title=record.title, raw_text=record.raw_text,
            sections=record.sections, metadata=record.metadata, authors=record.authors, year=record.year,
            domain=record.domain, source_type=record.source_type)
    # Never invoke pipeline.build/extract_from_doc/Expand/compile/register.
    import test_preprocessing
    test_preprocessing.ScrapyFidelityTest.source = source
    test_preprocessing.ScrapyFidelityTest.record = record
    test_preprocessing.ScrapyFidelityTest.windows = windows
    test_preprocessing.ScrapyFidelityTest.historical_windows = old["windows"]
    test_preprocessing.ScrapyFidelityTest.checkpoint_dir = checkpoint_root
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_preprocessing)
    if not args.baseline:
        spec = importlib.util.spec_from_file_location("legacy_windowing", upstream / "tests/test_document_windowing.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    log = io.StringIO()
    tests = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    with zipfile.ZipFile(out / "checkpoint_contract.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path in checkpoint_root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(checkpoint_root))
    checkpoint_temp.cleanup()
    write("tests.log", log.getvalue())
    write("tests.json", {"tests_run": tests.testsRun, "failures": [(t.id(), message) for t, message in tests.failures],
                         "errors": [(t.id(), message) for t, message in tests.errors], "skipped": tests.skipped,
                         "passed": tests.wasSuccessful(), "new_model_requests": 0})
    write("sections.json", [s.to_dict() for s in record.sections])
    write("windows.json", [w.to_dict() for w in windows])
    source_map = [{"window_ordinal": i, "window_id": w.window_id, "text_sha256": digest(w.text),
                   "blocks": unique_source_ranges(source, w.text)} for i, w in enumerate(windows, 1)]
    write("source_mapping.json", source_map)
    faithful = []
    for i, window in enumerate(windows, 1):
        try:
            assert_rule_fidelity(source, window.text)
            faithful.append(i)
        except AssertionError:
            pass
    historical = []
    for number in range(2, 20):
        req = read(run / f"http/{number:03d}/request.json")
        resp = read(run / f"http/{number:03d}/response.json")
        payload = json.loads(req["messages"][-1]["content"])
        matches = [i for i, w in enumerate(old["windows"], 1) if w["text"] == payload["excerpt"] and w["span"] == payload["section"]["span"]]
        assert len(matches) == 1
        choices = resp["choices"]
        assert len(choices) == 1 and choices[0]["message"]["content"] == '{"skills": []}'
        historical.append({"http": number, "window_ordinal": matches[0], "excerpt_sha256": digest(payload["excerpt"]),
            "excerpt_chars": len(payload["excerpt"]), "contains_full_target_rule": False,
            "code_fence_count": payload["excerpt"].count("```"), "section_heading": payload["section"]["heading"],
            "raw_response": choices[0]["message"], "finish_reason": choices[0]["finish_reason"],
            "response_choice_count": len(choices), "usage": resp["usage"],
            "request_sha256": hashlib.sha256((run / f"http/{number:03d}/request.json").read_bytes()).hexdigest()})
        with unittest.TestCase().assertRaises(AssertionError):
            assert_rule_fidelity(source, payload["excerpt"])
    write("historical_plan_checks.json", historical)
    result = {"mode": "official_baseline" if args.baseline else "lab-preprocess-v1", "new_model_requests": 0,
        "saved_outline_response_reads": saved.reads, "historical_baseline_reproduced_exactly": baseline_exact,
        "sections": len(record.sections), "windows": len(windows), "unique_window_ids": len({w.window_id for w in windows}),
        "ftp_sections": sum(s.heading == "FTP" for s in record.sections), "faithful_window_ordinals": faithful,
        "tests_run": tests.testsRun, "test_failures": len(tests.failures), "test_errors": len(tests.errors),
        "source_sha256": SOURCE_SHA256, "historical_plan_requests_checked": len(historical),
        "source_code_fence_count": source.count("```"), "window_code_fence_count": sum(w.text.count("```") for w in windows)}
    if not args.baseline:
        assert tests.wasSuccessful(), log.getvalue()
        assert faithful and len({w.window_id for w in windows}) == len(windows)
        selected = windows[faithful[0] - 1]
        from AutoSkill4Doc.stages.extractor import LLMDocumentSkillExtractor
        from AutoSkill4Doc.taxonomy import load_skill_taxonomy
        from AutoSkill4Doc.prompts import maybe_offline_prompt, OFFLINE_CHANNEL_DOC
        builder = object.__new__(LLMDocumentSkillExtractor)
        builder.max_candidates_per_unit = 4
        builder.taxonomy = load_skill_taxonomy(domain_type="")
        payload = builder._build_unit_payload(record=record, section_heading=selected.section_heading,
            section_level=selected.section_level, span=selected.span, unit_text=selected.text,
            unit_type="window", unit_metadata=selected.metadata)
        system = maybe_offline_prompt(channel=OFFLINE_CHANNEL_DOC, kind="extract_plan", max_candidates=4, taxonomy=builder.taxonomy)
        request = copy.deepcopy(read(run / "http/002/request.json"))
        assert system == request["messages"][0]["content"]
        request["messages"][-1]["content"] = json.dumps(payload, ensure_ascii=False)
        assert_rule_fidelity(source, json.loads(request["messages"][-1]["content"])["excerpt"])
        write("single_window_request.json", request)
        write("single_window.txt", selected.text)
        write("single_window_source_map.json", source_map[faithful[0] - 1])
        request_chars = sum(len(m["content"]) for m in request["messages"])
        old_ratios = []
        for n in range(2, 20):
            old_request = read(run / f"http/{n:03d}/request.json")
            old_response = read(run / f"http/{n:03d}/response.json")
            old_ratios.append(old_response["usage"]["prompt_tokens"] / sum(len(m["content"]) for m in old_request["messages"]))
        config = {"probe_id": "s24-single-window-preprocess-v1", "execution_authorized": False,
            "method": "lab-preprocess-v1 + unchanged official Plan prompt; diagnostic transport only",
            "source_run": str(run), "official_upstream": r"D:\AS\AutoSkill-main\AutoSkill-main",
            "official_commit": "94c47ca488d4ba4117d20272e66d49b9877e68cf",
            "source_sha256": SOURCE_SHA256, "window_ordinal": faithful[0], "window_id": selected.window_id,
            "window_chars": len(selected.text), "window_sha256": digest(selected.text), "system_prompt_sha256": digest(system),
            "request_sha256": hashlib.sha256((out / "single_window_request.json").read_bytes()).hexdigest(),
            "model": request["model"], "endpoint": "https://api.deepseek.com/v1/chat/completions",
            "credential_env": "DEEPSEEK_API_KEY", "timeout_s": 180,
            "http_attempt_limit": 1, "transport_retries": 0, "json_repair_requests": 0,
            "automatic_expand": False, "automatic_compile": False, "automatic_register": False,
            "input_chars_system_plus_user": request_chars,
            "estimated_prompt_tokens_from_old_ratios": [round(request_chars * min(old_ratios)), round(request_chars * max(old_ratios))],
            "token_estimate_note": "Empirical proxy only, not DeepSeek tokenizer count or a guaranteed bound",
            "max_completion_tokens": request["max_tokens"], "price_and_actual_cost": "UNKNOWN",
            "candidate_schema": "Original prompt: skills list with at most 4 lightweight planned assets; empty list permitted",
            "native_plan_parser_sha256": hashlib.sha256((upstream / "AutoSkill4Doc/stages/extractor.py").read_bytes()).hexdigest(),
            "metadata_note": "Document provenance metadata is retained from s24m001; this probe is a new diagnostic execution, not continuation of that run"}
        write("single_window_config.json", config)
        result["single_window"] = config
    assert all(hashlib.sha256((run / p).read_bytes()).hexdigest() == h for p, h in manifest.items())
    write("validation.json", result)
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
