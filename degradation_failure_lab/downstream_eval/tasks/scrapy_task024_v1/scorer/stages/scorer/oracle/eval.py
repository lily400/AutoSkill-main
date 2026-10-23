"""
Test cases for scrapy_task_024: Feed Export Default Overwrite Behavior

This test file supports both local testing and Docker testing via the TEST_ROOT_DIR
environment variable. By default, it uses /root (Docker mode).

Local testing:
    TEST_ROOT_DIR=/path/to/solution pytest tests/eval.py

Docker testing:
    pytest tests/eval.py
"""

import importlib
import inspect
import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = os.getenv("TEST_ROOT_DIR", "/root")
OUTPUT_FILE = os.path.join(ROOT_DIR, "agent_output.py")


def load_agent_module():
    sys.path.insert(0, ROOT_DIR)
    try:
        if "agent_output" in sys.modules:
            del sys.modules["agent_output"]
        return importlib.import_module("agent_output")
    finally:
        sys.path.remove(ROOT_DIR)


def get_target_function(module):
    """
    Prefer an explicitly named function. Fall back to a single public function only
    if there is no ambiguity.
    """
    preferred_names = [
        "default_feed_overwrite",
        "get_default_overwrite",
        "determine_default_overwrite",
        "feed_export_overwrite_default",
    ]
    for name in preferred_names:
        obj = getattr(module, name, None)
        if inspect.isfunction(obj):
            return obj

    public_functions = [
        getattr(module, name)
        for name in dir(module)
        if not name.startswith("_") and inspect.isfunction(getattr(module, name))
    ]
    assert len(public_functions) == 1, (
        "Could not uniquely identify target function. "
        "Please expose a single public function or use a conventional name like "
        "`default_feed_overwrite`."
    )
    return public_functions[0]


class TestFeedExportOverwriteBehavior:
    def test_file_exists(self):
        assert os.path.exists(OUTPUT_FILE), f"agent_output.py not found at {OUTPUT_FILE}"

    def test_file_not_empty(self):
        code = Path(OUTPUT_FILE).read_text(encoding="utf-8")
        assert code.strip(), "agent_output.py is empty"

    def test_has_module_doc_or_comments(self):
        code = Path(OUTPUT_FILE).read_text(encoding="utf-8")
        has_doc_hint = (
            '"""' in code or "'''" in code or "# " in code
        )
        assert has_doc_hint, "Expected a brief explanation/docstring/comments documenting backend behavior"

    def test_has_callable_target(self):
        module = load_agent_module()
        func = get_target_function(module)
        assert callable(func)

    @pytest.mark.parametrize(
        ("uri", "expected"),
        [
            ("file:///tmp/export.json", False),
            ("file:///tmp/export.csv", False),
            ("/tmp/export.json", False),   # local absolute path without scheme
            ("ftp://server/export.json", True),
            ("s3://bucket/export.json", True),
            ("gs://bucket/export.json", True),
            ("stdout:", False),
        ],
    )
    def test_supported_backends(self, uri, expected):
        module = load_agent_module()
        func = get_target_function(module)
        result = func(uri)

        assert isinstance(result, bool), f"Expected bool for {uri}, got {type(result).__name__}"
        assert result is expected, f"Incorrect default overwrite for {uri}: expected {expected}, got {result}"

    @pytest.mark.parametrize(
        "uri",
        [
            "http://example.com/export.json",
            "https://example.com/export.json",
            "ftps://secure-server/export.json",
            "stderr:",
            "mysql://db/export.json",
            "unknown://somewhere/file",
        ],
    )
    def test_unsupported_schemes_raise(self, uri):
        module = load_agent_module()
        func = get_target_function(module)
        with pytest.raises(ValueError):
            func(uri)

    def test_rejects_empty_string(self):
        module = load_agent_module()
        func = get_target_function(module)
        with pytest.raises((ValueError, TypeError)):
            func("")

    def test_rejects_non_string(self):
        module = load_agent_module()
        func = get_target_function(module)
        with pytest.raises((TypeError, AttributeError, ValueError)):
            func(None)