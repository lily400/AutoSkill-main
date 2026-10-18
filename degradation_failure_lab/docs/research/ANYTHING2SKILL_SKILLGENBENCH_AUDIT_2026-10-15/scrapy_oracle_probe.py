"""One-rule sensitivity audit using unchanged official tests; no Agent/model.

Only TEST_ROOT_DIR redirects the submitted file. No oracle file is rewritten.
This is a local Windows pytest probe, not an official Docker evaluation.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parent
REPO = BASE / "SkillGenBench"
ORACLE = REPO / "skill_evaluation/code_doc/scrapy/scrapy-task-024/tests/eval.py"
SOURCE = REPO / "data_source/code_doc/scrapy/tasks/scrapy-task-024/materials/docs/topics/feed-exports.md"
CORRECT = '''"""Built-in backend overwrite defaults from the supplied source document."""
from urllib.parse import urlsplit as _urlsplit

def default_feed_overwrite(uri):
    if not isinstance(uri, str):
        raise TypeError("uri must be a string")
    if not uri:
        raise ValueError("uri must not be empty")
    if uri.startswith("/"):
        return False
    defaults = {"file": False, "ftp": True, "s3": True, "gs": True, "stdout": False}
    scheme = _urlsplit(uri).scheme
    if scheme not in defaults:
        raise ValueError("unsupported scheme")
    return defaults[scheme]
'''
before = hashlib.sha256(ORACLE.read_bytes()).hexdigest()
results = []
for variant, code in [
    ("source_derived_correct_submission", CORRECT),
    ("single_rule_mutant_ftp_true_to_false", CORRECT.replace('"ftp": True', '"ftp": False')),
]:
    with tempfile.TemporaryDirectory(prefix="scrapy_audit_", dir=BASE) as folder:
        Path(folder, "agent_output.py").write_text(code, encoding="utf-8")
        env = os.environ.copy()
        env.update(TEST_ROOT_DIR=folder, PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        command = [sys.executable, "-B", "-m", "pytest", "-p", "no:cacheprovider", str(ORACLE), "-q"]
        proc = subprocess.run(command, cwd=folder, env=env, capture_output=True, text=True, timeout=60)
        results.append({"variant": variant, "submission": code, "exit_code": proc.returncode,
                        "stdout": proc.stdout, "stderr": proc.stderr})
report = {
    "scope": "LOCAL_UNMODIFIED_PYTEST_WITH_TEST_ROOT_DIR_NOT_DOCKER",
    "task_id": "scrapy-task-024", "models_called": False,
    "python": sys.version, "pytest": pytest.__version__,
    "oracle_sha256_before": before,
    "oracle_sha256_after": hashlib.sha256(ORACLE.read_bytes()).hexdigest(),
    "source_path": str(SOURCE.relative_to(REPO)),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "knowledge_provenance": "Backend booleans: feed-exports.md lines 438-449. Unknown scheme ValueError: instruction.md requirement 4, not asserted to originate in source docs.",
    "limitations": "Auditor saw oracle; not a blind Gold construction or generated-skill score. Tests one target rule; does not prove all equivalent implementations accepted or all errors detected.",
    "results": results,
}
(BASE / "scrapy_oracle_probe_results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"unchanged_oracle": report["oracle_sha256_before"] == report["oracle_sha256_after"],
                  "results": [{"variant": r["variant"], "exit_code": r["exit_code"], "summary": r["stdout"].strip().splitlines()[-1]} for r in results]}, ensure_ascii=False))
