import os
import sys
import importlib
import inspect
from typing import Annotated, get_args, get_origin, get_type_hints

import pytest

ROOT_DIR = os.getenv("TEST_ROOT_DIR", "/root")
OUTPUT_FILE = os.path.join(ROOT_DIR, "agent_output.py")

if not os.path.exists(OUTPUT_FILE):
    raise FileNotFoundError(f"agent_output.py not found at {OUTPUT_FILE}")

sys.path.insert(0, ROOT_DIR)
agent_output = importlib.import_module("agent_output")


def _get_value_annotation():
    hints = get_type_hints(agent_output.MyModel, include_extras=True)
    assert "value" in hints, "MyModel must define a field named 'value'"
    ann = hints["value"]
    assert get_origin(ann) is Annotated, "value must use typing.Annotated"
    return ann


def _get_annotated_metadata():
    ann = _get_value_annotation()
    args = get_args(ann)
    assert len(args) >= 2, "Annotated[value_type, ...metadata] must include validator metadata"
    base_type, *metadata = args
    return base_type, metadata


def _metadata_type_names(metadata):
    return [type(m).__name__ for m in metadata]


def _extract_log(instance):
    """
    Prefer instance.validation_log, then module-level VALIDATION_LOG.
    Require a list-like structured log for robust ordering checks.
    """
    if hasattr(instance, "validation_log"):
        log = getattr(instance, "validation_log")
    elif hasattr(agent_output, "VALIDATION_LOG"):
        log = getattr(agent_output, "VALIDATION_LOG")
    else:
        pytest.fail(
            "Implementation must expose a structured validation log via "
            "`instance.validation_log` or module-level `VALIDATION_LOG`."
        )

    assert isinstance(log, list), "Validation log must be a list"
    assert len(log) >= 4, "Validation log is too short to prove ordering"
    return log


def _normalize_event_name(event):
    """
    Accept either strings or dict entries like:
      'wrap_before'
      {'event': 'wrap_before', 'value': 10}
    """
    if isinstance(event, str):
        return event
    if isinstance(event, dict):
        assert "event" in event, "Dict log entries must contain an 'event' key"
        return event["event"]
    pytest.fail("Validation log entries must be strings or dicts with an 'event' key")


def _find_index(events, predicate):
    for i, e in enumerate(events):
        if predicate(e):
            return i
    return -1


class TestValidatorOrdering:
    def setup_method(self):
        if hasattr(agent_output, "VALIDATION_LOG") and isinstance(agent_output.VALIDATION_LOG, list):
            agent_output.VALIDATION_LOG.clear()

    def test_model_exists(self):
        assert hasattr(agent_output, "MyModel"), "agent_output must define MyModel"

    def test_value_field_uses_annotated(self):
        ann = _get_value_annotation()
        assert get_origin(ann) is Annotated

    def test_required_validator_kinds_present(self):
        _, metadata = _get_annotated_metadata()
        names = _metadata_type_names(metadata)

        assert any("BeforeValidator" == n for n in names), "Annotated metadata must include BeforeValidator"
        assert any("WrapValidator" == n for n in names), "Annotated metadata must include WrapValidator"
        assert any("AfterValidator" == n for n in names), "Annotated metadata must include AfterValidator"

    def test_input_10_produces_output_30(self):
        instance = agent_output.MyModel(value=10)
        assert instance.value == 30, f"Expected 30, got {instance.value}"

    @pytest.mark.parametrize(
        "input_val, expected",
        [
            (0, 10),
            (3, 16),
            (5, 20),
            (10, 30),
            (12, 34),
            (-5, 0),
        ],
    )
    def test_multiple_inputs(self, input_val, expected):
        instance = agent_output.MyModel(value=input_val)
        assert instance.value == expected, f"Input {input_val}: expected {expected}, got {instance.value}"

    def test_log_is_structured_and_nontrivial(self):
        instance = agent_output.MyModel(value=10)
        log = _extract_log(instance)
        events = [_normalize_event_name(e) for e in log]

        assert len(events) >= 4
        assert any("wrap" in e for e in events), "Log must include wrap-related events"
        assert any("before" in e for e in events), "Log must include before-related events"
        assert any("after" in e for e in events), "Log must include after-related events"

    def test_wrap_sees_raw_input(self):
        instance = agent_output.MyModel(value=10)
        log = _extract_log(instance)

        found = False
        for entry in log:
            if isinstance(entry, dict):
                event = entry.get("event", "")
                if "wrap" in event and ("before" in event or "start" in event):
                    if entry.get("value") == 10 or entry.get("input") == 10 or entry.get("raw") == 10:
                        found = True
                        break
            elif isinstance(entry, str):
                if "wrap" in entry and "10" in entry:
                    found = True
                    break

        assert found, "Wrap validator should log that it observed raw input 10"

    def test_order_matches_documented_pipeline_semantics(self):
        """
        We do not require exact event names, but we require a sequence that demonstrates:
        1) wrap starts first
        2) before runs during inner validation
        3) wrap resumes after handler returns
        4) after occurs after inner validation result is available

        Pydantic docs state that with Annotated, before and wrap validators run
        right-to-left, then after validators run left-to-right.
        """
        instance = agent_output.MyModel(value=10)
        events = [_normalize_event_name(e).lower() for e in _extract_log(instance)]

        wrap_start_idx = _find_index(
            events,
            lambda e: ("wrap" in e) and ("before" in e or "start" in e or "enter" in e)
        )
        before_idx = _find_index(
            events,
            lambda e: e == "before" or "before_validator" in e or e.startswith("before_")
        )
        wrap_end_idx = _find_index(
            events,
            lambda e: ("wrap" in e) and ("after" in e or "end" in e or "exit" in e or "resume" in e)
        )
        after_idx = _find_index(
            events,
            lambda e: e == "after" or "after_validator" in e or e.startswith("after_")
        )

        assert wrap_start_idx != -1, f"Could not find wrap-start event in log: {events}"
        assert before_idx != -1, f"Could not find before event in log: {events}"
        assert wrap_end_idx != -1, f"Could not find wrap-end event in log: {events}"
        assert after_idx != -1, f"Could not find after event in log: {events}"

        assert wrap_start_idx < before_idx, (
            "Wrap should begin before the inner pipeline's before-validator runs"
        )
        assert before_idx < wrap_end_idx, (
            "Before-validator should run before wrap resumes with the handler result"
        )
        assert wrap_end_idx < after_idx or before_idx < after_idx, (
            "After-validator must occur after inner validation has progressed beyond raw-input handling"
        )

    def test_not_hardcoded_for_single_value(self):
        vals = [-11, -1, 1, 7, 19]
        outputs = [agent_output.MyModel(value=v).value for v in vals]
        expected = [2 * v + 10 for v in vals]
        assert outputs == expected, f"Expected affine transform 2*x+10, got {outputs}"

    def test_model_instantiation_uses_pydantic_validation(self):
        import pydantic

        assert issubclass(agent_output.MyModel, pydantic.BaseModel), "MyModel must inherit from pydantic.BaseModel"

    def test_no_decorator_based_field_validator_requirement(self):
        """
        Optional but useful for benchmark purity:
        discourage solving the task with @field_validator instead of Annotated metadata.
        """
        source = inspect.getsource(agent_output)
        assert "@field_validator" not in source, (
            "Use Annotated validator metadata directly for this benchmark task."
        )