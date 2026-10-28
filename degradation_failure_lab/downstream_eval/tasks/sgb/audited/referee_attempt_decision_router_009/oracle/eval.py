"""Pytest adapter for standardized domain_knowledge_doc bundles."""
from __future__ import annotations

import json
import math
import os
import signal
from pathlib import Path

import pytest

ROOT_DIR = Path(os.getenv("TEST_ROOT_DIR", "/workspace"))
AGENT_OUTPUT = ROOT_DIR / "agent_output.py"
TESTCASE_FILE = Path(__file__).with_name("testcases.json")


class Timeout:
    def __init__(self, seconds: int):
        self.seconds = int(seconds)

    def __enter__(self):
        if hasattr(signal, "SIGALRM") and self.seconds > 0:
            signal.signal(signal.SIGALRM, self._handle)
            signal.alarm(self.seconds)
        return self

    def __exit__(self, *_args):
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)

    @staticmethod
    def _handle(_signum, _frame):
        raise TimeoutError("Timed out while executing candidate code")


def load_bundle() -> dict:
    return json.loads(TESTCASE_FILE.read_text(encoding="utf-8"))


def normalize_value(value):
    if hasattr(value, "item") and callable(getattr(value, "item")):
        try:
            return normalize_value(value.item())
        except Exception:
            pass
    if isinstance(value, dict):
        return {key: normalize_value(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_value(item) for item in value]
    return value


def assert_close(actual, expected, path="result"):
    actual = normalize_value(actual)
    expected = normalize_value(expected)

    if isinstance(expected, bool):
        assert isinstance(actual, bool), f"{path}: expected bool, got {type(actual).__name__}"
        assert actual is expected, f"{path}: {actual!r} != {expected!r}"
        return

    if expected is None:
        assert actual is None, f"{path}: {actual!r} != None"
        return

    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        assert isinstance(actual, (int, float)) and not isinstance(actual, bool), (
            f"{path}: expected numeric value, got {type(actual).__name__}"
        )
        if isinstance(expected, float) or isinstance(actual, float):
            assert math.isclose(float(actual), float(expected), rel_tol=1e-5, abs_tol=1e-8), (
                f"{path}: {actual!r} != {expected!r}"
            )
        else:
            assert actual == expected, f"{path}: {actual!r} != {expected!r}"
        return

    if isinstance(expected, str):
        assert isinstance(actual, str), f"{path}: expected str, got {type(actual).__name__}"
        assert actual == expected, f"{path}: {actual!r} != {expected!r}"
        return

    if isinstance(expected, list):
        assert isinstance(actual, list), f"{path}: expected list, got {type(actual).__name__}"
        assert len(actual) == len(expected), f"{path}: len {len(actual)} != {len(expected)}"
        for idx, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            assert_close(actual_item, expected_item, f"{path}[{idx}]")
        return

    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: expected dict, got {type(actual).__name__}"
        assert set(actual.keys()) == set(expected.keys()), (
            f"{path}: keys {sorted(actual.keys())} != {sorted(expected.keys())}"
        )
        for key in sorted(expected.keys()):
            assert_close(actual[key], expected[key], f"{path}.{key}")
        return

    assert actual == expected, f"{path}: {actual!r} != {expected!r}"


def run_case(bundle: dict, case: dict):
    setup_code = bundle.get("setup_code", "") or ""
    candidate_code = AGENT_OUTPUT.read_text(encoding="utf-8")
    namespace: dict = {}
    timeout_seconds = int(bundle.get("timeout_seconds", 120) or 120)
    with Timeout(timeout_seconds):
        if setup_code:
            exec(setup_code, namespace)
        exec(candidate_code, namespace)
        solve = namespace.get(bundle.get("function_name", "solve"))
        assert callable(solve), "solve(input_data) is not defined"
        return solve(case["input"])


@pytest.mark.parametrize("case_index, case", list(enumerate(load_bundle().get("test_cases", []), start=1)))
def test_cl_case(case_index, case):
    assert AGENT_OUTPUT.exists(), f"agent_output.py not found: {AGENT_OUTPUT}"
    bundle = load_bundle()
    result = run_case(bundle, case)
    assert_close(result, case["expected_output"], f"case_{case_index}")
