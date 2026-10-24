"""Check immutable run/source/report snapshots; no model dependencies."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
for key in ("run", "upstream", "fixed-clone", "audit", "patched", "out"):
    parser.add_argument("--" + key, type=Path, required=True)
args = parser.parse_args()
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
expected_run = read(args.audit / "evidence/run_inventory_before.json")
current_run = {p.relative_to(args.run).as_posix(): sha(p) for p in args.run.rglob("*") if p.is_file()}
assert current_run == expected_run
upstream = read(args.run / "upstream_before.json")
assert upstream == read(args.run / "upstream_after.json")
assert all(sha(args.upstream / p) == sha(args.fixed_clone / p) == digest for p, digest in upstream.items())
report_sha = sha(args.audit / "zero_skill_extraction_diagnosis.md")
assert report_sha == "cdd4015a8de8ac9f6dab9eae177989bae44e32fd747a7d5eebd5eeb49ced0d6c"
changed = {p: sha(args.patched / p) for p, h in upstream.items() if sha(args.patched / p) != h}
assert set(changed) == {"AutoSkill4Doc/ingest.py", "AutoSkill4Doc/document/windowing.py"}
provenance = read(args.audit.parents[2] / "data/manifests/sgb_scrapy024_provenance.json")
source_paths = [args.run / "inputs/input001/feed-exports.md", Path(provenance["frozen_audit_source"]),
               args.audit.parents[2] / "data/raw_sources/scrapy" / provenance["skillgenbench_commit"] / "feed-exports.md"]
source_hashes = {str(p): sha(p) for p in source_paths}
assert all(h == provenance["frozen_source_sha256"] for h in source_hashes.values())
result = {"verified": True, "original_run_files_unchanged": len(current_run),
          "official_files_matching_record_and_fixed_clone": len(upstream),
          "prior_report_sha256": report_sha, "patched_files_only": changed,
          "clean_sources": source_hashes, "new_model_requests": 0}
with args.out.open("x", encoding="utf-8") as stream:
    json.dump(result, stream, indent=2, ensure_ascii=False)
print(json.dumps(result, ensure_ascii=True))
