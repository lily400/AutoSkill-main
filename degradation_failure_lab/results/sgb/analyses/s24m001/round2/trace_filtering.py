"""Offline sidecar: expose paragraph filtering and strict-window selection."""
import argparse
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
for name in ("upstream", "bundle", "run", "out"):
    parser.add_argument("--" + name, type=Path, required=True)
args = parser.parse_args()
def guard(event, values):
    if event.startswith("socket.") or event.startswith("subprocess.") or event == "os.system":
        raise RuntimeError("OFFLINE_ONLY")
sys.addaudithook(guard)
sys.path.insert(0, str(args.upstream.resolve()))
from AutoSkill4Doc.document import windowing as w
from AutoSkill4Doc.models import DocumentRecord, DocumentSection
from fidelity import digest, unique_source_ranges
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))
record = DocumentRecord.from_dict(read(next(args.run.glob("SkillBank/.runtime/intermediate_runs/*/ingest/result.json")))["documents"][0])
record.sections = [DocumentSection.from_dict(s) for s in read(args.bundle / "sections.json")]
windows = read(args.bundle / "windows.json")
source = (args.run / "inputs/input001/feed-exports.md").read_text(encoding="utf-8")
rows = []
for section in w._planning_sections(record.sections):
    if w._is_noise_section(section, markers=w._noise_section_markers()):
        continue
    for chunk in w._split_long_section(section, max_chars=10000):
        blocks = w._build_paragraph_blocks(chunk, anchor_markers=w._anchor_markers(), priority_markers=w._priority_markers())
        kept = {b.index for b in blocks}
        for index, (text, span) in enumerate(w._paragraphs_from_section(chunk)):
            if not any(x in text for x in ("overwrite", "Some FTP", "FTP:", "ftp://")):
                continue
            containing = [i for i, window in enumerate(windows, 1) if text in window["text"]]
            rows.append({"heading": section.heading, "chunk_metadata": chunk.metadata,
                "paragraph_index": index, "text": text, "chars": len(text), "sha256": digest(text),
                "declared_span": span.to_dict(), "process_signal": w._has_process_signal(text,
                    priority_markers=w._priority_markers(), anchor_markers=w._anchor_markers()),
                "kept_by_paragraph_filter": index in kept, "window_text_matches": containing,
                "source_mapping": unique_source_ranges(source, text),
                "mapping_warning": "Repeated wording can match a different backend; use section context, not text match alone"})
with args.out.open("x", encoding="utf-8") as stream:
    json.dump({"new_model_requests": 0, "rows": rows}, stream, ensure_ascii=False, indent=2)
print(json.dumps({"rows": len(rows), "new_model_requests": 0}))
