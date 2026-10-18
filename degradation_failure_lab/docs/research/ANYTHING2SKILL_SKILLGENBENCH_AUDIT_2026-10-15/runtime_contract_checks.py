"""Offline contract checks. No model, Docker, network, or upstream source edits."""
from __future__ import annotations

import ast
import contextlib
import dataclasses
import io
import json
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT / "SkillGenBench"


def selected_defs(relative_path, names, namespace):
    tree = ast.parse((UPSTREAM / relative_path).read_text(encoding="utf-8"))
    nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    assert {node.name for node in nodes} == set(names)
    code = compile(ast.Module(body=nodes, type_ignores=[]), relative_path, "exec")
    exec(code, namespace)


ns = dict(Path=Path, Any=Any, re=re, json=json, shutil=shutil, dataclass=dataclasses.dataclass,
          datetime=datetime, IGNORE_PATTERNS=shutil.ignore_patterns(".DS_Store", "__pycache__"),
          RUN_ID_RE=re.compile(r"^\d{8}-\d{6}$"))
selected_defs("scripts/generated_skills_layout.py", [
    "ResolvedSkillPackage", "sanitize_package_name", "extract_frontmatter_name",
    "package_name_from_skill_text", "package_name_from_skill_file", "_flat_package",
    "_nested_package", "resolve_skill_package", "has_skill_package", "skill_base_dir",
    "_looks_like_run_dir", "latest_run_id", "copy_tree_contents",
], ns)
ns["SKILL_METHOD_PROFILES"] = {"noskill": "direct_llm", "noskill_claude": "claude_agent_no_skill", "skillsbench_generate": "claude_agent_no_skill"}
ns["_DEFAULT_PROFILE"] = "claude_agent_with_skill"
selected_defs("scripts/skill_method_profiles.py", ["get_profile", "stages_skill", "runner_for"], ns)
selected_defs("scripts/claude_runner.py", ["StagedSkillMounts", "prepare_skill_for_claude", "_extract_text", "_estimate_tokens_from_events", "parse_claude_log"], ns)

results = {}
with tempfile.TemporaryDirectory(prefix="runtime-contract-", dir=ROOT) as tmp:
    base = Path(tmp).resolve()
    assert base.is_relative_to(ROOT.resolve())  # Verify cleanup stays in audit workspace.
    leaf = base / "two-skills"
    for name in ["alpha", "beta"]:
        (leaf / name).mkdir(parents=True)
        (leaf / name / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\n", encoding="utf-8")
    try:
        ns["resolve_skill_package"](leaf)
    except ValueError as exc:
        results["two_nested_skills"] = {"error_type": type(exc).__name__, "message_prefix": str(exc).split(" under ")[0]}
    else:
        raise AssertionError("Expected ambiguity for two packages")

    cfg = {"source_type": "code_doc", "collection_slug": "fixture", "task_id": "fixture-task", "skill_scope": "task"}
    skills = base / "skills"
    agnostic = skills / "candidate" / "model" / "run" / "code_doc" / "fixture" / "agnostic"
    agnostic.mkdir(parents=True)
    (agnostic / "SKILL.md").write_text("---\nname: library\ndescription: test\n---\n", encoding="utf-8")
    lookup = ns["skill_base_dir"](cfg, skills, "candidate", "model", "run")
    results["agnostic_lookup"] = {"produced": agnostic.relative_to(skills).as_posix(), "resolved": lookup.relative_to(skills).as_posix(), "available": ns["has_skill_package"](lookup)}
    assert not results["agnostic_lookup"]["available"]

    legacy = skills / "candidate" / "legacy" / "model" / "code_doc" / "fixture" / "tasks" / "fixture-task"
    legacy.mkdir(parents=True)
    (legacy / "SKILL.md").write_text("---\nname: legacy\ndescription: test\n---\n", encoding="utf-8")
    lookup = ns["skill_base_dir"](cfg, skills, "candidate", "model", "missing-explicit-run")
    results["explicit_run_falls_back"] = lookup.relative_to(skills).as_posix()
    assert lookup == legacy

    (legacy / "references").mkdir()
    (legacy / "references" / "guide.md").write_text("fixture reference", encoding="utf-8")
    (legacy / "scripts").mkdir()
    (legacy / "scripts" / "helper.py").write_text("# never executed\n", encoding="utf-8")
    staged = ns["prepare_skill_for_claude"](cfg, skills, "candidate", base / "stage", "model", "missing-explicit-run")
    results["whole_package_staging"] = {"references_copied": (staged.workspace_skill_dir / "references" / "guide.md").is_file(), "scripts_copied": (staged.workspace_skill_dir / "scripts" / "helper.py").is_file()}
    assert all(results["whole_package_staging"].values())

    log = base / "failed_skill.jsonl"
    log.write_text("\n".join(json.dumps(e) for e in [
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "x", "name": "Skill", "input": {"skill": "missing-skill"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "x", "is_error": True, "content": "Unknown skill"}]}},
    ]), encoding="utf-8")
    results["failed_skill_call_counted_as_triggered"] = ns["parse_claude_log"](log)["skill_triggered"]
    assert results["failed_skill_call_counted_as_triggered"] is True

    selected_defs("scripts/run_eval.py", ["source_label", "mean_metric", "mean_bool_metric", "skipped_after_pass_record", "run_task_eval"], ns)
    ns["RESULTS_DIR"] = base / "mock-results"
    ns["_write_trial_json"] = lambda path, payload: path.write_text(json.dumps(payload), encoding="utf-8")
    ns["_dispatch_trial"] = lambda *args, **kwargs: {"pass": args[1] == 2, "status": "pass" if args[1] == 2 else "fail"}
    with contextlib.redirect_stdout(io.StringIO()):
        summary = ns["run_task_eval"](cfg, 3, "candidate", skills, {}, base, early_stop_on_pass=False)
    results["pass_rate_of_false_true_false"] = {"trials_executed": summary["trials_executed"], "reported_pass_rate": summary["pass_rate"], "arithmetic_trial_mean": sum(t["pass"] for t in summary["trials"]) / 3}
    assert summary["pass_rate"] == 1.0

out = ROOT / "runtime_contract_checks.json"
out.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(results, indent=2, ensure_ascii=False))
