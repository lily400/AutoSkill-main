"""Create a hash-checked lab copy and apply three local preprocessing fixes."""
from pathlib import Path
import difflib
import hashlib
import json
import argparse


REPLACEMENTS = {
    "AutoSkill4Doc/ingest.py": [
        ('    preview_text = str(preview or "").strip()\n',
         '    preview_text = str(preview or "").strip()\n'
         '    # URI user-info and inline code are not author/contact evidence.\n'
         '    preview_text = re.sub(r"`[^`\\n]*`|[A-Za-z][A-Za-z0-9+.-]*://\\S+", "", preview_text)\n'),
    ],
    "AutoSkill4Doc/document/windowing.py": [
        ('import re\n', 'import hashlib\nimport re\n'),
        ('_BULLET_RE = re.compile(r"^\\s*(?:[-*•]|\\d+[.)])\\s+")',
         '_BULLET_RE = re.compile(r"^\\s*(?:[-*•]|\\d+[.)])\\s+", re.MULTILINE)'),
        ('    key = f"{record.doc_id}:{section.heading}:{paragraph_start}:{paragraph_end}:{effective_strategy}"',
         '    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()\n'
         '    key = f"{record.doc_id}:{section.heading}:{paragraph_start}:{paragraph_end}:{effective_strategy}:{start}:{end}:{text_hash}"'),
    ],
}


def prepare(run: Path, upstream: Path, destination: Path):
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite lab copy: {destination}")
    recorded = json.loads((run / "upstream_before.json").read_text(encoding="utf-8"))
    changes, patch = {}, []
    for relative, digest in recorded.items():
        original = (upstream / relative).read_bytes()
        assert hashlib.sha256(original).hexdigest() == digest, relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original)
    tests = destination / "tests"
    tests.mkdir(exist_ok=True)
    for name in ("test_document_windowing.py",):
        (tests / name).write_bytes((upstream / "tests" / name).read_bytes())
    for relative, replacements in REPLACEMENTS.items():
        path = destination / relative
        before = path.read_text(encoding="utf-8")
        after = before
        for old, new in replacements:
            assert after.count(old) == 1, (relative, old)
            after = after.replace(old, new, 1)
        path.write_bytes(after.encode("utf-8"))
        patch.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                        fromfile=f"a/{relative}", tofile=f"b/{relative}"))
        changes[relative] = {"original_sha256": recorded[relative], "patched_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    return {"method": "lab-preprocess-v1", "official_commit": "94c47ca488d4ba4117d20272e66d49b9877e68cf",
            "copied_recorded_files": len(recorded), "changed_files": changes}, "".join(patch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if any(root.resolve() == out or root.resolve() in out.parents for root in (args.run, args.upstream)):
        raise ValueError("Output must be outside original run and official source")
    out.mkdir(parents=True, exist_ok=False)
    manifest, patch = prepare(args.run, args.upstream, out / "patched_upstream")
    (out / "patch_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (out / "preprocessing.patch").write_bytes(patch.encode("utf-8"))
