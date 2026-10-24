import importlib.util
import os
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.feature import match_template

ROOT_DIR = os.getenv("TEST_ROOT_DIR", "/workspace")
OUTPUT_FILE = os.path.join(ROOT_DIR, "agent_output.py")
INPUT_DIR = Path("/workspace/input")


def load_module():
    assert os.path.exists(OUTPUT_FILE), f"agent_output.py not found at {OUTPUT_FILE}"
    spec = importlib.util.spec_from_file_location("agent_output", OUTPUT_FILE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_inputs():
    search = np.asarray(Image.open(INPUT_DIR / "search_image.png").convert("L"), dtype=float)
    template = np.asarray(Image.open(INPUT_DIR / "template_10x10.png").convert("L"), dtype=float)
    return search, template


def summarize(search, template, pad_input):
    response = match_template(search, template, pad_input=pad_input)
    peak = np.unravel_index(int(np.argmax(response)), response.shape)
    return [int(response.shape[0]), int(response.shape[1])], [int(peak[0]), int(peak[1])]


def compute_expected():
    search, template = load_inputs()
    shape_no_pad, peak_no_pad = summarize(search, template, pad_input=False)
    shape_pad, peak_pad = summarize(search, template, pad_input=True)
    return {
        "shape_no_pad": shape_no_pad,
        "shape_pad": shape_pad,
        "peak_no_pad": peak_no_pad,
        "peak_pad": peak_pad,
    }


def test_function_exists():
    module = load_module()
    assert hasattr(module, "match_template_padding_summary")


def test_result_matches_runtime_behavior():
    module = load_module()
    result = module.match_template_padding_summary(
        str(INPUT_DIR / "search_image.png"),
        str(INPUT_DIR / "template_10x10.png"),
    )
    assert isinstance(result, dict)
    assert result == compute_expected()


def test_source_mentions_match_template_and_pad_input():
    source = Path(OUTPUT_FILE).read_text(encoding="utf-8")
    assert "match_template" in source
    assert "pad_input" in source
