# tests/test_parser.py - Log parsing and metric extraction
import tempfile
from pathlib import Path

import pytest
import yaml

from hpc_regression.parser import extract_metrics, validate_metrics, load_parser_config


def test_extract_metrics_from_dict():
    """Extract metrics using inline parser config."""
    config = {
        "patterns": [
            {"name": "mlups", "regex": r"MLUPS:\s*([\d.e+-]+)", "type": "float"},
            {"name": "runtime", "regex": r"runtime:\s*([\d.]+)", "type": "float"},
            {"name": "status", "regex": r"status:\s*(\w+)", "type": "str"},
        ]
    }
    log = "MLUPS: 2.1e6\nruntime: 38.5\nstatus: success"
    metrics = extract_metrics(log, parser_config=config)
    assert metrics["mlups"] == 2100000.0
    assert metrics["runtime"] == 38.5
    assert metrics["status"] == "success"


def test_extract_metrics_from_file(tmp_path):
    """Extract metrics using parser config file."""
    config_path = tmp_path / "parser_config.yaml"
    config_path.write_text(yaml.safe_dump({
        "patterns": [
            {"name": "value", "regex": r"value=(\d+)", "type": "int"},
        ]
    }))
    log = "some output value=42 more output"
    metrics = extract_metrics(log, config_path=config_path)
    assert metrics["value"] == 42


def test_extract_metrics_empty_config():
    """Empty or missing config returns empty dict."""
    assert extract_metrics("log", parser_config={}) == {}
    assert extract_metrics("log", parser_config=None) == {}


def test_validate_metrics_required():
    """Validate required metrics."""
    metrics = {"a": 1, "b": 2}
    valid, errors = validate_metrics(metrics, required=["a", "b"])
    assert valid
    assert len(errors) == 0

    valid, errors = validate_metrics(metrics, required=["a", "b", "c"])
    assert not valid
    assert "Missing required metric: c" in errors


def test_validate_metrics_ranges():
    """Validate metric ranges."""
    metrics = {"x": 5.0, "y": 100.0}
    valid, _ = validate_metrics(metrics, ranges={"x": (0, 10), "y": (50, 200)})
    assert valid

    valid, errors = validate_metrics(metrics, ranges={"x": (10, 20)})
    assert not valid
    assert any("below min" in e for e in errors)

    valid, errors = validate_metrics(metrics, ranges={"x": (0, 3)})
    assert not valid
    assert any("above max" in e for e in errors)
