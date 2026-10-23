"""Task-specific assertions outside the generic preprocessing patch."""
import hashlib
import re

SOURCE_SHA256 = "a3831d75f00d59a0527a469dc26af5dcf741294e25572c46bb587b28f7e2165d"


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


def target_source(source):
    return "\n".join(source.splitlines()[437:449])


def assert_rule_fidelity(source, excerpt):
    # Preserve the entire default/exception block, rather than matching FTP=True alone.
    assert normalized(target_source(source)) in normalized(excerpt), "RULE_CONTEXT_MISSING_OR_CHANGED"


def unique_source_ranges(source, excerpt):
    blocks = []
    for text in re.split(r"\n\s*\n+", excerpt.strip()):
        pattern = r"\s+".join(re.escape(part) for part in text.split())
        matches = [{"start": m.start(), "end": m.end(),
                    "line_start": source.count("\n", 0, m.start()) + 1,
                    "line_end": source.count("\n", 0, m.end() - 1) + 1}
                   for m in re.finditer(pattern, source)]
        blocks.append({"text_sha256": digest(text), "text": text, "source_candidates": matches})
    return blocks
