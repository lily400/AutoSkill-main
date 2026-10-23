"""Read saved s24m001 evidence only. No SDK import, credentials, or network.

Replays only selected pure functions extracted by AST from recorded source.
Those replays explain branches; they are not additional historical model runs.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import os
import re
import sys
import types
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--fixed-clone", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run, upstream, out = args.run.resolve(), args.upstream.resolve(), args.out.resolve()
    protected = [run, upstream] + ([args.fixed_clone.resolve()] if args.fixed_clone else [])
    if any(root == out or root in out.parents for root in protected):
        raise ValueError("Output must be outside original run and upstream sources")
    out.mkdir(parents=True, exist_ok=True)

    def guard(event, values):
        if event.startswith("socket.") or event.startswith("subprocess.") or event == "os.system":
            raise RuntimeError("Offline diagnosis forbids network and subprocesses")
        if event == "open":
            path, mode, flags = values
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)))
            if writing and not Path(path).resolve().is_relative_to(out):
                raise RuntimeError("Write outside diagnosis output forbidden")
        if event in {"os.remove", "os.rename", "os.rmdir"}:
            raise RuntimeError("Diagnosis never deletes or renames evidence")
        if event == "os.mkdir" and not Path(values[0]).resolve().is_relative_to(out):
            raise RuntimeError("Directory creation outside diagnosis output forbidden")

    sys.addaudithook(guard)

    def write(name, value):
        dest = out / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        dest.write_bytes(data.encode("utf-8"))

    def extract_functions(relative, names, namespace):
        path = upstream / relative
        tree = ast.parse(path.read_text(encoding="utf-8"))
        nodes = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in names]
        assert len(nodes) == len(names), (relative, names)
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)] + nodes,
                            type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)

    before = inventory(run)
    manifest = read(run / "artifact_manifest.json")
    manifest_bad = [k for k, v in manifest.items() if before.get(k) != v]
    assert not manifest_bad, manifest_bad
    upstream_record = read(run / "upstream_before.json")
    upstream_bad = [k for k, v in upstream_record.items() if sha((upstream / k).read_bytes()) != v]
    assert not upstream_bad, upstream_bad
    assert upstream_record == read(run / "upstream_after.json")
    fixed_bad = []
    if args.fixed_clone:
        fixed_bad = [k for k, v in upstream_record.items()
                     if not (args.fixed_clone / k).exists() or sha((args.fixed_clone / k).read_bytes()) != v]
    wrapper_bad = [k for k, v in read(run / "wrapper_manifest.json").items()
                   if sha((run / "wrapper_snapshot" / k).read_bytes()) != v]
    assert not wrapper_bad, wrapper_bad
    intermediate = next((run / "SkillBank/.runtime/intermediate_runs").iterdir())
    ingested = read(intermediate / "ingest/result.json")
    doc, windows = ingested["documents"][0], ingested["windows"]
    source_path = run / "inputs/input001/feed-exports.md"
    source = source_path.read_text(encoding="utf-8")
    assert doc["raw_text"] == source.rstrip("\n")
    assert sha(source_path.read_bytes()) == "a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d"
    calls, rows, source_maps, payloads = [], [], [], []
    for directory in sorted((run / "http").iterdir()):
        request, response, event = [read(directory / f"{n}.json") for n in ("request", "response", "event")]
        assert event["response_sha256"] == sha((directory / "response.json").read_bytes())
        assert event["returned_body_unchanged"] and event["success"]
        content = response["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        user = request["messages"][-1]["content"]
        payload = json.loads(user)
        plan = "excerpt" in payload
        call = {"http": int(directory.name), "stage": "Plan" if plan else "Outline",
                "request_sha256": sha((directory / "request.json").read_bytes()),
                "response_sha256": sha((directory / "response.json").read_bytes()),
                "user_utf8_sha256": sha(user.encode()), "system_utf8_sha256": sha(request["messages"][0]["content"].encode()),
                "input_chars": len(user), "finish_reason": response["choices"][0]["finish_reason"],
                "parsed_response": parsed, "logical_call_id": event["logical_call_id"],
                "attempt_index": event["attempt_index"], "retry_of": event["retry_of"],
                "model_requested": request["model"], "model_returned": response["model"],
                "usage": response["usage"], "seconds": event["seconds"],
                "replacement_characters_in_messages": sum(m["content"].count("\ufffd") for m in request["messages"])}
        if plan:
            matches = [i for i, w in enumerate(windows) if payload["excerpt"] == w["text"].strip() and payload["section"]["span"] == w["span"]]
            assert len(matches) == 1, matches
            index, excerpt = matches[0], payload["excerpt"]
            window = windows[index]
            assert parsed == {"skills": []} and content == '{"skills": []}'
            call["window_ordinal"] = index + 1
            payloads.append(payload)
            key = f"{window['doc_id']}:{window['section_heading']}:{window['paragraph_start']}:{window['paragraph_end']}:{window['strategy']}"
            assert str(uuid.uuid5(uuid.NAMESPACE_URL, f"autoskill4doc-window:{key}")) == window["window_id"]
            blocks = []
            for bi, text in enumerate(re.split(r"\n\s*\n+", excerpt), 1):
                pattern = r"\s+".join(re.escape(t) for t in re.split(r"\s+", text.strip()))
                candidates = [{"start": m.start(), "end": m.end(),
                               "line_start": source.count("\n", 0, m.start()) + 1,
                               "line_end": source.count("\n", 0, m.end() - 1) + 1}
                              for m in re.finditer(pattern, source)]
                blocks.append({"block": bi, "text": text, "candidate_source_ranges": candidates,
                               "mapping_status": "unique_whitespace_normalized" if len(candidates) == 1 else "ambiguous" if candidates else "unmatched"})
            source_maps.append({"window_ordinal": index + 1, "window_id": window["window_id"],
                                "declared_span": window["span"], "blocks": blocks})
            row = {"window": index + 1, "http": int(directory.name), "window_id": window["window_id"],
                   "window_text_utf8_sha256": sha(window["text"].encode()), "chars": len(window["text"]),
                   "span_start": window["span"]["start"], "span_end": window["span"]["end"],
                   "chunk_index": window["metadata"].get("section_chunk_index"),
                   "paragraph_start": window["paragraph_start"], "paragraph_end": window["paragraph_end"],
                   "original_source_span_exact": source[window["span"]["start"]:window["span"]["end"]] == window["text"],
                   "ftp_default_table_fragment": "- FTP: `True`" in excerpt,
                   "overwrite_definition": "`overwrite`: whether to overwrite" in excerpt,
                   "ftp_uri_example": "ftp://user:pass@ftp.example.com" in excerpt,
                   "appe_exception": "`APPE`" in excerpt,
                   "raw_plan_items": len(parsed["skills"]), "request_sha256": call["request_sha256"],
                   "response_sha256": call["response_sha256"],
                   **{k: response["usage"][k] for k in ("prompt_tokens", "completion_tokens", "total_tokens")}}
            rows.append(row)
            write(f"windows/w{index + 1:02d}_{window['window_id']}.txt", window["text"])
        else:
            selected = {h["candidate_index"] for h in parsed["headings"]}
            write("outline_evidence.json", {"selected_indices": sorted(selected), "candidates": payload["candidates"], "parsed_response": parsed})
        calls.append(call)
    rows.sort(key=lambda x: x["window"])
    assert [r["window"] for r in rows] == list(range(1, 19))
    assert len(read(run / "model_calls.json")) == len(calls) == 19
    # Execute saved-response parsing and the early return only; the spies forbid expansion.
    ns = {"re": re}
    extract_functions("AutoSkill4Doc/core/llm_utils.py", {"maybe_json_dict"}, ns)
    extract_functions("AutoSkill4Doc/stages/extractor.py", {"_plan_unit_skills", "_extract_unit_skills"}, ns)
    replay = []
    for call, payload in zip([c for c in calls if c["stage"] == "Plan"], payloads):
        def forbidden_expand(**kwargs):
            raise AssertionError("Expand must not be entered for saved empty Plan")
        instance = types.SimpleNamespace(max_candidates_per_unit=4,
                                         _complete_extract_json=lambda **kwargs: call["parsed_response"],
                                         _build_unit_payload=lambda **kwargs: payload,
                                         _expand_planned_skill=forbidden_expand)
        instance._plan_unit_skills = types.MethodType(ns["_plan_unit_skills"], instance)
        planned = instance._plan_unit_skills(payload=payload, record=None, section_heading="Feed exports")
        extracted = ns["_extract_unit_skills"](instance, record=None, section_heading="Feed exports", section_level=1,
                                               span=None, unit_text=payload["excerpt"], unit_type="window")
        assert planned == extracted == []
        replay.append({"http": call["http"], "parsed_plan_items": len(planned), "extracted_items": len(extracted), "expand_entered": False})
    # Replay the exact front-matter predicate and paragraph keep/drop predicate.
    extract_functions("AutoSkill4Doc/core/common.py", {"normalize_text", "dedupe_strings"}, ns)
    ingest_tree = ast.parse((upstream / "AutoSkill4Doc/ingest.py").read_text(encoding="utf-8"))
    assignments = [n for n in ingest_tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id in {"_NON_CONTENT_HEADING_MARKERS", "_CONTACT_LINE_RE", "_AUTHOR_HEADING_RE"} for t in n.targets)]
    exec(compile(ast.Module(body=assignments, type_ignores=[]), "recorded_ingest_constants", "exec"), ns)
    extract_functions("AutoSkill4Doc/ingest.py", {"_looks_like_front_matter_heading"}, ns)
    ftp_start = source.index("### FTP\n")
    ftp_end = source.index("\n### ", ftp_start + 1)
    ftp_body = source[ftp_start:ftp_end].split("\n", 1)[1].strip()
    ftp_guard = ns["_looks_like_front_matter_heading"]("FTP", preview=ftp_body[:240])
    assert ftp_guard and not any(s["heading"] == "FTP" for s in doc["sections"])
    window_tree = ast.parse((upstream / "AutoSkill4Doc/document/windowing.py").read_text(encoding="utf-8"))
    assignments = [n for n in window_tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id in {"_DEFAULT_PRIORITY_MARKERS", "_DEFAULT_ANCHORS", "_DIALOGUE_LINE_RE", "_BULLET_RE"} for t in n.targets)]
    exec(compile(ast.Module(body=assignments, type_ignores=[]), "recorded_window_constants", "exec"), ns)
    extract_functions("AutoSkill4Doc/document/windowing.py", {"_has_process_signal", "_is_dialogue_heavy"}, ns)
    feeds = next(s for s in doc["sections"] if s["heading"] == "FEEDS")
    rule_blocks = []
    for paragraph in re.split(r"\n\s*\n+", feeds["text"]):
        if "`overwrite`: whether" not in paragraph and "`APPE`" not in paragraph and "- FTP: `True`" not in paragraph:
            continue
        signal = ns["_has_process_signal"](paragraph, priority_markers=ns["_DEFAULT_PRIORITY_MARKERS"], anchor_markers=ns["_DEFAULT_ANCHORS"])
        retained = not ns["_is_dialogue_heavy"](paragraph) and (signal or len(paragraph) <= 320)
        rule_blocks.append({"text": paragraph, "chars": len(paragraph), "process_signal": signal,
                            "retained_by_block_predicate": retained,
                            "present_in_any_excerpt": any(paragraph in p["excerpt"] for p in payloads)})
    ids = Counter(w["window_id"] for w in windows)
    aggregate = read(intermediate / f"extract/aggregate/{doc['doc_id']}.json")
    totals = {k: sum(c["usage"][k] for c in calls) for k in ("prompt_tokens", "completion_tokens", "total_tokens")}
    summary = {"run": str(run), "new_model_requests": 0, "mode": "offline_saved_evidence_and_pure_AST_replay",
               "artifact_manifest_entries_verified": len(manifest), "artifact_manifest_mismatches": manifest_bad,
               "run_files_before": len(before), "wrapper_files_verified": len(read(run / 'wrapper_manifest.json')),
               "upstream_recorded_files_verified": len(upstream_record), "upstream_mismatches": upstream_bad,
               "fixed_clone_mismatches": fixed_bad, "source_bytes_sha256": sha(source_path.read_bytes()),
               "source_lf_utf8_sha256": sha(source.encode()), "ingest_raw_text_sha256": sha(doc['raw_text'].encode()),
               "ingest_normalization": "One terminal LF removed; other characters identical", "sections": len(doc['sections']),
               "windows": len(windows), "unique_text_sha256": len({r['window_text_utf8_sha256'] for r in rows}),
               "unique_request_sha256": len({r['request_sha256'] for r in rows}), "unique_window_ids": len(ids),
               "colliding_ids": {k: [i + 1 for i, w in enumerate(windows) if w['window_id'] == k] for k, v in ids.items() if v > 1},
               "extract_window_files": len(list((intermediate / 'extract/windows').glob('*/*.json'))),
               "aggregate_expected_ids": len(aggregate['expected_window_ids']), "aggregate_processed_ids": len(aggregate['processed_window_ids']),
               "aggregate_complete": aggregate['complete'], "source_block_mapping_counts": dict(Counter(b['mapping_status'] for w in source_maps for b in w['blocks'])),
               "declared_span_exact_count": sum(r['original_source_span_exact'] for r in rows),
               "ftp_frontmatter_predicate": ftp_guard, "ftp_body_preview": ftp_body[:240], "rule_block_filter_replay": rule_blocks,
               "ftp_table_http": [r['http'] for r in rows if r['ftp_default_table_fragment']],
               "overwrite_definition_http": [r['http'] for r in rows if r['overwrite_definition']],
               "appe_exception_http": [r['http'] for r in rows if r['appe_exception']],
               "plan_system_hashes": sorted({c['system_utf8_sha256'] for c in calls if c['stage'] == 'Plan'}),
               "http_attempts": len(calls), "usage_totals": totals,
               "cached_prompt_tokens": sum(c['usage'].get('prompt_cache_hit_tokens', 0) for c in calls),
               "retries": sum(c['attempt_index'] > 1 for c in calls),
               "replacement_characters_in_messages": sum(c['replacement_characters_in_messages'] for c in calls),
               "exception_file_exists": (run / 'exception.json').exists(),
               "duration_seconds": (datetime.fromisoformat(read(run/'execution.json')['ended_at']) - datetime.fromisoformat(read(run/'invocation.json')['started_at'])).total_seconds(),
               "skill_md_files": [p.relative_to(run).as_posix() for p in (run/'SkillBank').rglob('SKILL.md')]}
    after = inventory(run)
    assert before == after, "Original run changed while diagnosing"
    summary['original_run_unchanged_during_analysis'] = True
    write("run_inventory_before.json", before)
    write("run_inventory_after.json", after)
    write("findings.json", summary)
    write("http_analysis.json", calls)
    write("source_alignment.json", source_maps)
    write("offline_parser_replay.json", replay)
    write("plan_system_prompt.txt", read(run / 'http/002/request.json')['messages'][0]['content'])
    write("plan_taxonomy.json", payloads[0]['taxonomy'])
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    write("window_request_map.csv", buffer.getvalue())
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
