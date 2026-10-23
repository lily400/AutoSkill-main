"""Read-only postmortem; saved Outline replay only, network/subprocess denied."""
import argparse
import csv
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import sys


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in root.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("lab", "patched", "fixed-clone", "out"):
        parser.add_argument("--" + key, type=Path, required=True)
    args = parser.parse_args()
    lab, patched, fixed, out = (p.resolve() for p in (args.lab, args.patched, args.fixed_clone, args.out))
    out.mkdir(parents=True, exist_ok=False)
    def guard(event, values):
        if event.startswith("socket.") or event.startswith("subprocess.") or event == "os.system":
            raise RuntimeError("OFFLINE_ONLY")
        if event == "open":
            path, mode, flags = values
            if (isinstance(mode, str) and any(c in mode for c in "wax+")) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT):
                if not Path(path).resolve().is_relative_to(out):
                    raise RuntimeError("Historical evidence is read-only")
    sys.addaudithook(guard)
    def write(name, value):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    runs = [lab / "runs/case024_scrapy/clean" / name for name in ("s24m001", "s24m002")]
    old_audit = lab / "results/analysis/s24m001"
    old_inventory = inventory(old_audit)
    run_inventory = [inventory(root) for root in runs]
    for root in runs:
        for relative, expected in read(root / "artifact_manifest.json").items():
            assert sha(root / relative) == expected, relative
        for relative, expected in read(root / "wrapper_manifest.json").items():
            assert sha(root / "wrapper_snapshot" / relative) == expected, relative
    previous, run = runs
    source_bytes = (run / "inputs/input001/feed-exports.md").read_bytes()
    source = source_bytes.decode("utf-8").replace("\r\n", "\n")
    assert source_bytes == (previous / "inputs/input001/feed-exports.md").read_bytes()
    upstream = Path(read(run / "environment.json")["upstream_path"])
    expected = read(run / "upstream_before.json")
    assert expected == read(run / "upstream_after.json") == read(previous / "upstream_before.json")
    assert all(sha(upstream / p) == sha(fixed / p) == h for p, h in expected.items())
    patch_manifest = read(old_audit / "round2/patch_manifest.json")
    differences = {p: {"recorded_s24m001": read(previous / "upstream_before.json")[p],
                       "recorded_s24m002": h, "current_official": sha(upstream / p),
                       "fixed_clone": sha(fixed / p), "patched_copy": sha(patched / p)}
                   for p, h in expected.items() if sha(patched / p) != h}
    assert set(differences) == set(patch_manifest["changed_files"])
    for p, values in differences.items():
        assert values["patched_copy"] == patch_manifest["changed_files"][p]["patched_sha256"]
    write("code_comparison.json", differences)

    # Import definitions, never call lab.main/runner.run/adapter.execute or any model constructor.
    sys.path.insert(0, str(lab / "src"))
    from degradation_lab import cli, runner, io
    current_resolution = io.resolve_upstream(lab)
    sys.path.insert(0, str(upstream))
    from AutoSkill4Doc import ingest
    from AutoSkill4Doc.document import windowing
    from AutoSkill4Doc.models import DocumentRecord, DocumentSection
    from autoskill.llm.base import LLM
    imported = {}
    for name, function in {"cli.main": cli.main, "runner.run": runner.ExperimentRunner.run,
                           "resolve_upstream": io.resolve_upstream,
                           "parse_sections": ingest.HeuristicDocumentIngestor._parse_sections_with_fallback,
                           "front_matter": ingest._looks_like_front_matter_heading,
                           "build_windows": windowing.build_windows_for_record,
                           "paragraph_filter": windowing._build_paragraph_blocks,
                           "window_identity": windowing._window_from_blocks}.items():
        path = Path(inspect.getsourcefile(function)).resolve()
        imported[name] = {"path": str(path), "sha256": sha(path), "first_line": function.__code__.co_firstlineno}
    write("import_paths.json", {"current_upstream_resolution": str(current_resolution),
        "current_override": os.environ.get("ANYTHING2SKILL_SOURCE"), "definitions_only": True,
        "historical_resolution": str(upstream), "functions": imported})

    saved = [read(next(root.glob("SkillBank/.runtime/intermediate_runs/*/ingest/result.json"))) for root in runs]
    record = DocumentRecord.from_dict(saved[1]["documents"][0])
    outline_req = read(run / "http/001/request.json")
    outline_resp = read(run / "http/001/response.json")["choices"][0]["message"]["content"]
    class SavedOutline(LLM):
        reads = 0
        def complete(self, *, system, user, temperature=0.0):
            assert self.reads == 0
            assert system == outline_req["messages"][0]["content"]
            assert json.loads(user) == json.loads(outline_req["messages"][-1]["content"])
            self.reads += 1
            return outline_resp
    outline = SavedOutline()
    pipeline = read(run / "config.json")["pipeline"]
    record.sections = ingest.HeuristicDocumentIngestor(llm=outline, llm_rate_limit_requests=0)._parse_sections_with_fallback(
        raw_text=record.raw_text, default_title=record.title, logger=None)
    windows = windowing.build_windows_for_record(record, strategy=pipeline["extract_strategy"],
                                                  max_section_chars=pipeline["max_section_chars"])
    assert [s.to_dict() for s in record.sections] == saved[1]["documents"][0]["sections"]
    assert [w.to_dict() for w in windows] == saved[1]["windows"]
    # Historical model content is inspected, not regenerated.
    rows, usage = [], {"outline": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                       "plan": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}
    (out / "windows").mkdir()
    complete_rule = re.sub(r"\s+", " ", "\n".join(source.splitlines()[437:449])).strip()
    events = []
    for number in range(1, 20):
        folder = run / f"http/{number:03d}"
        request, response, event = (read(folder / name) for name in ("request.json", "response.json", "event.json"))
        assert sha(folder / "response.json") == event["response_sha256"]
        assert event["success"] and event["attempt_index"] == 1 and event["retry_of"] is None
        events.append(event)
        group = "outline" if number == 1 else "plan"
        for key in usage[group]:
            usage[group][key] += response["usage"][key]
        if number == 1:
            continue
        payload = json.loads(request["messages"][-1]["content"])
        matches = [i for i, w in enumerate(windows, 1) if w.text == payload["excerpt"] and w.span.to_dict() == payload["section"]["span"]]
        assert len(matches) == 1
        ordinal = matches[0]
        text = payload["excerpt"]
        normalized = re.sub(r"\s+", " ", text)
        assert len(response["choices"]) == 1
        choice = response["choices"][0]
        assert choice["message"]["content"] == '{"skills": []}' and choice["finish_reason"] == "stop"
        (out / "windows" / f"{ordinal:02d}.txt").write_bytes(text.encode("utf-8"))
        rows.append({"http": number, "window_ordinal": ordinal, "window_id": windows[ordinal-1].window_id,
            "chars": len(text), "text_sha256": text_sha(text), "request_sha256": sha(folder / "request.json"),
            "system_sha256": text_sha(request["messages"][0]["content"]),
            "same_text_as_s24m001": text == saved[0]["windows"][ordinal-1]["text"],
            "contains_full_rule": complete_rule in normalized,
            "contains_overwrite_definition": "whether to overwrite the file if it already exists" in text,
            "contains_ftp_default_table": "- FTP: `True`" in text,
            "contains_appe_exception": "APPE" in text,
            "raw_content": choice["message"]["content"], "finish_reason": choice["finish_reason"],
            "usage": response["usage"]})
    write("http_events.json", events)
    write("window_request_checks.json", rows)
    with (out / "window_request_checks.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        keys = [k for k in rows[0] if k != "usage"] + list(usage["plan"])
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows({**{k:v for k,v in row.items() if k != "usage"},
                          **{k: row["usage"][k] for k in usage["plan"]}} for row in rows)
    ftp_body = source.split("### FTP\n", 1)[1].split("\n### S3", 1)[0].strip()
    blocks = []
    for text in re.split(r"\n\s*\n+", source):
        if ("whether to overwrite the file if it already exists" in text or text.startswith("Some FTP servers")
                or "- FTP: `True`" in text):
            section = DocumentSection(heading="FEEDS", text=text)
            blocks.append({"text": text, "chars": len(text), "process_signal": windowing._has_process_signal(text,
                priority_markers=windowing._priority_markers(), anchor_markers=windowing._anchor_markers()),
                "retained_blocks": len(windowing._build_paragraph_blocks(section,
                    priority_markers=windowing._priority_markers(), anchor_markers=windowing._anchor_markers()))})
    write("filter_replay.json", {"ftp_preview": ftp_body[:240],
        "ftp_classified_as_front_matter": ingest._looks_like_front_matter_heading("FTP", preview=ftp_body[:240]),
        "rule_paragraphs": blocks, "saved_outline_reads": outline.reads, "new_model_requests": 0})
    id_groups = {}
    for i, w in enumerate(windows, 1):
        id_groups.setdefault(w.window_id, []).append(i)
    section_differences = []
    for i, (a, b) in enumerate(zip(saved[0]["documents"][0]["sections"], saved[1]["documents"][0]["sections"]), 1):
        if a != b:
            section_differences.append({"ordinal": i, "heading": b["heading"],
                "changed_fields": {k: {"s24m001": a.get(k), "s24m002": b.get(k)} for k in set(a) | set(b) if a.get(k) != b.get(k)}})
    write("section_differences.json", section_differences)
    old_plan = read(old_audit / "round2/patched_ok/single_window_request.json")
    new_plan = read(run / "http/002/request.json")
    model_config_matches = {k: v for k, v in old_plan.items() if k != "messages"} == {k: v for k, v in new_plan.items() if k != "messages"}
    assert old_plan["messages"][0] == new_plan["messages"][0] and model_config_matches
    summary = {"new_model_requests": 0, "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "recorded_official_files": len(expected), "official_code_matches_previous_and_fixed_clone": True,
        "patched_differences": list(differences), "replay_matches_s24m002_exactly": True,
        "sections": len(record.sections), "ftp_sections": sum(s.heading == "FTP" for s in record.sections),
        "section_difference_count_vs_s24m001": len(section_differences),
        "windows": len(windows), "unique_texts": len({r['text_sha256'] for r in rows}),
        "unique_ids": len(id_groups), "collisions": {k:v for k,v in id_groups.items() if len(v)>1},
        "same_window_texts_as_s24m001": sum(r["same_text_as_s24m001"] for r in rows),
        "full_rule_request_count": sum(r["contains_full_rule"] for r in rows),
        "default_table_http": [r["http"] for r in rows if r["contains_ftp_default_table"]],
        "usage_by_stage": usage, "http_calls": len(events), "plan_empty_responses": len(rows),
        "cached_prompt_tokens": sum(e["usage"].get("prompt_cache_hit_tokens",0) for e in events),
        "execution": read(run / "execution.json"), "official_result": read(run / "official_result.json"),
        "previous_frozen_probe_prompt_and_model_config_match_s24m002": model_config_matches,
        "historical_preprocessing_function_trace_gap": "Window builder was not selected by historical profile filter; path is established by import, fixed source and exact saved-output replay"}
    write("summary.json", summary)
    assert old_inventory == inventory(old_audit)
    assert run_inventory == [inventory(root) for root in runs]
    write("integrity.json", {"original_runs_unchanged": {p.name: len(items) for p, items in zip(runs,run_inventory)},
        "prior_audit_files_unchanged": len(old_inventory), "new_model_requests": 0})
    print(json.dumps({k:v for k,v in summary.items() if k not in ("execution","official_result")}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
