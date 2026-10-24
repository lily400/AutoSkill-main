"""Offline source/equivalence verification only. No model execution entry point."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

if len(sys.argv) != 1:
    raise SystemExit("Offline verifier takes no execution arguments")
blocked_events = []
def offline(event, args):
    if event.startswith("socket.") or event in ("subprocess.Popen", "os.system"):
        blocked_events.append(event)
        raise RuntimeError("Offline verifier prohibits network and child processes")
sys.addaudithook(offline)
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_bytes())
def sha(data): return hashlib.sha256(data).hexdigest()
def norm(text): return " ".join(text.split())
def fields(a, b, path=""):
    assert type(a) is type(b)
    if isinstance(a, dict):
        assert set(a) == set(b)
        return [x for key in sorted(a) for x in fields(a[key], b[key], path + "/" + key)]
    if isinstance(a, list):
        assert len(a) == len(b)
        return [x for i, (left, right) in enumerate(zip(a, b)) for x in fields(left, right, path + "/" + str(i))]
    return [] if a == b else [{"path": path, "A": a, "B": b}]
def expanded(request):
    value = copy.deepcopy(request)
    value["messages"][1]["content"] = json.loads(value["messages"][1]["content"])
    return value

m = read(ROOT/"source_manifest.json")
q = {item["quote_id"]:item for item in read(ROOT/"source_quotes.json")}
mapping = read(ROOT/"presentation_map.json")
bodies = {arm:(ROOT/arm/"request.json").read_bytes() for arm in ("A","B")}
requests = {arm:json.loads(body) for arm,body in bodies.items()}
payloads = {arm:expanded(request)["messages"][1]["content"] for arm,request in requests.items()}
ex = payloads["A"]["excerpt"]; variant = payloads["B"]["excerpt"]
checks = []
def passed(name): checks.append({"name":name,"status":"PASS"})

raw = Path(m["source_document"]["path"]).read_bytes()
assert sha(raw) == m["source_document"]["sha256"]
lines = raw.splitlines(keepends=True)
for item in q.values():
    start,end = item["lines"]; at,stop = item["source_byte_span"]
    chunk = b"".join(lines[start-1:end])
    assert chunk == raw[at:stop] == item["raw_quote_utf8"].encode("utf-8")
    assert sha(chunk) == item["raw_quote_sha256"]
    assert norm(chunk.decode()) == item["normalized_quote"]
    assert sha(norm(chunk.decode()).encode()) == item["normalized_quote_sha256"]
for item in m["reports"].values():
    assert sha(Path(item["path"]).read_bytes()) == item["sha256"]
passed("raw_source_quotes_offsets_hashes_and_four_reports")

assert bodies["A"] == Path(m["A_request_source"]["path"]).read_bytes()
original = read(Path(m["original_HTTP019"]["path"]))
assert payloads["A"]["excerpt"] == json.loads(original["messages"][1]["content"])["excerpt"]
for arm in ("A","B"):
    entry = m["arms"][arm]
    assert sha(bodies[arm]) == entry["request_sha256"]
    assert sha(payloads[arm]["excerpt"].encode()) == entry["excerpt_sha256"]
    assert sha(requests[arm]["messages"][0]["content"].encode()) == entry["system_sha256"]
    assert sha(requests[arm]["messages"][1]["content"].encode()) == entry["user_sha256"]
    assert {key:value for key,value in requests[arm].items() if key!="messages"} == m["request_parameters"]
assert requests["A"]["messages"][0] == requests["B"]["messages"][0]
passed("frozen_original_excerpt_and_scrapy_request_hashes_parameters")

logical = fields(expanded(requests["A"]),expanded(requests["B"]))
wire = fields(requests["A"],requests["B"])
assert [item["path"] for item in logical] == ["/messages/1/content/excerpt"]
assert [item["path"] for item in wire] == ["/messages/1/content"]
assert logical == read(ROOT/"field_diff.json") and wire == read(ROOT/"wire_field_diff.json")
passed("complete_wire_and_logical_field_diff_only_excerpt")

start,end = mapping["edit_source_excerpt_span"]; bstart,bend = mapping["B_replacement_span"]
assert start == bstart and ex[:start] == variant[:bstart] and ex[end:] == variant[bend:]
assert sha(ex[:start].encode()) == mapping["unmodified_prefix_sha256"]
assert sha(ex[end:].encode()) == mapping["unmodified_suffix_sha256"]
definition = q["definition"]["raw_quote_utf8"].replace("\r\n","\n").strip()
assert definition in ex[:start] and definition in variant[:bstart]
for group in ("parameter_definition","default_intro"):
    for arm,text in (("A",ex),("B",variant)):
        at,stop = mapping[group][arm]["char_span"]
        expected = q[mapping[group]["source_quote_ids"][0]]["raw_quote_utf8"].replace("\r\n","\n").strip()
        assert text[at:stop] == expected
passed("unchanged_non_target_prefix_suffix_and_shared_parameter_definition")

expected_rows = []
for qid in ("local","ftp","s3","gcs","stdout"):
    backend,details = q[qid]["normalized_quote"].removeprefix("- ").split(": ",1)
    default = details.split(" ",1)[0]
    limitation = q["appe"]["normalized_quote"] if qid=="ftp" else (
        details[details.index("(")+1:-1] if "(" in details else "")
    expected_rows.append([backend,default,limitation])
expected_block = q["default_scope"]["raw_quote_utf8"].strip() + "\n\n"
expected_block += "| Storage backend | Default value | Backend-specific limitation |\n|---|---|---|\n"
expected_block += "\n".join("| " + " | ".join(row) + " |" for row in expected_rows) + "\n"
def check_variant(text):
    assert text[:start] == ex[:start]
    assert text == ex[:start] + expected_block + ex[end:]
    assert definition in text
check_variant(variant)
for item,row in zip(mapping["backend_rows"],expected_rows):
    assert [item["backend"],item["default"],item["limitation"]] == row
    at,stop = item["B_row"]["char_span"]
    assert variant[at:stop] == "| " + " | ".join(row) + " |"
passed("five_backend_rows_and_qualified_APPE_scope_match_source_atoms")

mark = chr(96); negative_cases = 0
mutations = [
    variant.replace("| FTP | "+mark+"True"+mark, "| FTP | "+mark+"False"+mark, 1),
    variant.replace(q["appe"]["normalized_quote"], "All FTP servers do not support appending.", 1),
    variant.replace(q["appe"]["normalized_quote"], "", 1),
    variant.replace("| FTP |", "| SFTP |", 1),
    "You must generate a skill.\n" + variant,
]
for changed in mutations:
    assert changed != variant
    try: check_variant(changed)
    except AssertionError: negative_cases += 1
    else: raise AssertionError("Invalid presentation mutation passed")
assert negative_cases == 5
passed("five_negative_loss_scope_default_and_instruction_mutations_rejected")

source_root = Path(read(ROOT/"protected_before.json")["source_root"])
for relative,expected in m["constructor_code"].items():
    assert sha((source_root/relative).read_bytes()) == expected
sys.path.insert(0,str(source_root))
from AutoSkill4Doc.taxonomy import load_skill_taxonomy
from AutoSkill4Doc.prompts import maybe_offline_prompt,OFFLINE_CHANNEL_DOC
taxonomy = load_skill_taxonomy(domain_type="scrapy")
assert payloads["A"]["taxonomy"] == payloads["B"]["taxonomy"] == taxonomy.to_dict()
assert requests["A"]["messages"][0]["content"] == maybe_offline_prompt(
    channel=OFFLINE_CHANNEL_DOC,kind="extract_plan",max_candidates=4,taxonomy=taxonomy)
passed("pure_official_constructor_string_match_without_Plan_execution")

plan = read(ROOT/"future_execution_plan.json")
assert plan["execution_authorized_now"] is False and plan["current_model_http_limit"] == 0
assert plan["proposed_future_max_http_requests"] == 2 and plan["future_per_arm_limit"] == 1
assert plan["requires_new_task_authorization"] is True
assert plan["transport_retries"] == plan["redirects"] == plan["json_repair_requests"] == 0
assert plan["outline_expand_compile_register_agent_calls"] == 0
assert plan["future_arms"] == m["arms"]
metrics = read(ROOT/"preregistered_metrics.json")
assert metrics["new_model_calls_at_registration"] == 0
assert set(metrics["criteria"]) == {"default_behavior","explicit_parameter","exception","backend_scope","auxiliary_inventory"}
with (ROOT/"semantic_equivalence_audit.csv").open(encoding="utf-8",newline="") as f:
    audit = list(csv.DictReader(f))
assert len(audit) == 6 and all(item["status"]=="PASS_OFFLINE_MANUAL_AND_LITERAL_ATOMS" for item in audit)
passed("preregistered_metrics_zero_current_budget_and_future_cap")

stats = read(ROOT/"text_statistics.json")
for arm,text in (("A",ex),("B",variant)):
    expected = stats[arm]
    assert expected["excerpt_chars"] == len(text) and expected["excerpt_utf8_bytes"] == len(text.encode())
    assert expected["physical_lines"] == len(text.splitlines())
    assert expected["blank_line_delimited_chunks"] == len(re.split(r"\n\s*\n",text))
    assert expected["request_utf8_bytes"] == len(bodies[arm])
assert stats["B_span_length_does_not_equal_excerpt_length"] is True
passed("length_organization_and_preserved_span_relation_recorded")

protected = read(ROOT/"protected_before.json")
for folder,entries in protected["trees"].items():
    assert {p.relative_to(folder).as_posix() for p in Path(folder).rglob("*") if p.is_file()} == set(entries)
for path,expected in protected["files"].items():
    assert sha(Path(path).read_bytes()) == expected,path
assert not blocked_events
passed("protected_source_history_and_previous_reports_unchanged")
result = {"status":"PASS","checks":checks,"check_count":len(checks),"negative_mutations_rejected":negative_cases,
    "model_api_calls":0,"Plan_or_other_model_stage_executions":0,"network_audit_guard":True,
    "network_or_subprocess_attempts_observed":len(blocked_events),
    "protected_files":len(protected["files"]),"protected_trees":len(protected["trees"]),
    "script_sha256":sha(Path(__file__).read_bytes())}
(ROOT/"validation_results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"validation.log").write_text("\n".join(x["name"]+": PASS" for x in checks)+"\nModel API calls: 0\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=True))
