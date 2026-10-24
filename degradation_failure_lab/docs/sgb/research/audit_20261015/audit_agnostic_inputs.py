"""Read-only inventory of the actual naive agnostic document input paths."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

AUDIT_ROOT = Path(__file__).resolve().parent
REPO = AUDIT_ROOT / "SkillGenBench"
EXPECTED_SHA = "5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d"
TEXT_SUFFIXES = {".md", ".mdx", ".txt", ".rst", ".py", ".yaml", ".yml", ".toml", ".csv", ".tsv", ".ini", ".cfg"}


def inspect_path(path: Path) -> dict:
    files = sorted(p for p in path.rglob("*") if p.is_file()) if path.exists() else []
    readable = []
    for file in files:
        if file.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        readable.append(file)
    return {
        "path": str(path.resolve()),
        "repo_relative_path": path.relative_to(REPO).as_posix(),
        "exists": path.exists(),
        "file_count": len(files),
        "naive_readable_text_file_count": len(readable),
        "files": [p.relative_to(REPO).as_posix() for p in files],
    }


def main() -> None:
    groups = []
    # Directory enumeration avoids permissive repairs to malformed task.json.
    for source_type in ["code_doc", "domain_knowledge_doc"]:
        for collection in sorted((REPO / "data_source" / source_type).iterdir()):
            if not collection.is_dir():
                continue
            docs = inspect_path(collection / "shared" / "materials" / "docs")
            tools = inspect_path(collection / "shared" / "materials" / "tools")
            groups.append({
                "source_type": source_type,
                "source_group": collection.name,
                "task_directory_ids": sorted(p.name for p in (collection / "tasks").iterdir() if p.is_dir()),
                "shared_docs": docs,
                "shared_tools": tools,
                "file_count": docs["file_count"] + tools["file_count"],
                "naive_agnostic_source_body_empty": docs["naive_readable_text_file_count"] + tools["naive_readable_text_file_count"] == 0,
            })
    baseline = REPO / "baseline" / "naive_prompt" / "generate_skill.py"
    result = {
        "scope": "READ_ONLY_FILESYSTEM_INVENTORY_NO_MODELS_NO_DOCKER_NO_UPSTREAM_EDITS",
        "audited_date": "2026-10-15",
        "expected_repo_sha": EXPECTED_SHA,
        "repo_root": str(REPO.resolve()),
        "baseline_file": str(baseline.resolve()),
        "baseline_sha256": hashlib.sha256(baseline.read_bytes()).hexdigest(),
        "baseline_evidence_lines": {"text_suffixes": [42, 46], "read_text_tree": [51, 73], "build_agnostic_user_prompt": [283, 304]},
        "groups_total": len(groups),
        "groups_by_source_type": {source: sum(g["source_type"] == source for g in groups) for source in ["code_doc", "domain_knowledge_doc"]},
        "groups_with_zero_shared_files": sum(g["file_count"] == 0 for g in groups),
        "groups_with_empty_naive_agnostic_source_body": sum(g["naive_agnostic_source_body_empty"] for g in groups),
        "interpretation": "The naive agnostic prompt reads only shared/materials/docs and shared/materials/tools. For these groups both bodies would be '(none)' after earlier JSON/import blockers are repaired; this is a code-path inference, not a model run.",
        "groups": groups,
    }
    (AUDIT_ROOT / "agnostic_shared_materials_audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["groups_total", "groups_by_source_type", "groups_with_zero_shared_files", "groups_with_empty_naive_agnostic_source_body"]}, indent=2))


if __name__ == "__main__":
    main()
