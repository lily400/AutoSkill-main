"""Package only independent audit artifacts; never edit audited repositories."""
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPORT = BASE / "ANYTHING2SKILL_SKILLGENBENCH_FEASIBILITY_AUDIT_2026-10-15.md"
PACKAGE = "ANYTHING2SKILL_SKILLGENBENCH_AUDIT_2026-10-15"
marker = "## 附录A：64个文档任务与来源清单"
body = REPORT.read_text(encoding="utf-8").split(marker)[0]
appendix = (BASE / "appendix_a_tasks.md").read_text(encoding="utf-8")
appendix = appendix.split("\n", 1)[1].lstrip()
REPORT.write_text(body + marker + "\n\n" + appendix, encoding="utf-8")

excluded = {REPORT.name, "artifact_manifest.json", "delivery_validation.json", "hf_dataset_metadata.json"}
files = sorted(p for p in BASE.iterdir() if p.is_file() and p.name not in excluded
               and p.suffix.lower() in {".md", ".json", ".jsonl", ".csv", ".py"})
files += sorted(p for p in (BASE / "hf_snapshot_samples").rglob("*") if p.is_file())
records = [{"relative_path": p.relative_to(BASE).as_posix(), "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
checks = []
for p in files:
    if p.parent == BASE and p.suffix == ".json":
        json.loads(p.read_text(encoding="utf-8-sig"))
        checks.append({"check": "parse_delivery_json", "path": p.name, "pass": True})
text = REPORT.read_text(encoding="utf-8")
for ref in re.findall(r"\]\((" + PACKAGE + r"/[^)]+)\)", text):
    path = BASE / ref.removeprefix(PACKAGE + "/")
    assert path.is_file(), ref
    checks.append({"check": "relative_report_link", "path": ref, "pass": True})
assert len(re.findall(r"^## \d+\.", text, re.M)) == 15
assert sum(line.startswith("|") for line in appendix.splitlines()) == 66
assert "**Q7：" in text and "**本轮不执行。**" in text
validation = {"status": "PASS", "scope": "Artifact structure and links only, not scientific or runtime validation",
              "numbered_sections": 15, "appendix_task_rows": 64, "evidence_file_count": len(files), "checks": checks}
(BASE / "delivery_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
v = BASE / "delivery_validation.json"
records.append({"relative_path": v.name, "bytes": v.stat().st_size, "sha256": hashlib.sha256(v.read_bytes()).hexdigest()})
manifest = {"audit_date": "2026-10-15", "source_base": str(BASE), "evidence_directory": PACKAGE,
            "report": {"name": REPORT.name, "bytes": REPORT.stat().st_size,
                       "sha256": hashlib.sha256(REPORT.read_bytes()).hexdigest()},
            "files": records, "exclusions": "Raw Git checkouts and incomplete hf_dataset_metadata.json are not copied. Manifest excludes itself to avoid a circular hash."}
(BASE / "artifact_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"report_bytes": REPORT.stat().st_size, "evidence_files": len(records), "validation": "PASS"}))
