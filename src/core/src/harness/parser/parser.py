# parser/parser.py - Regex-based log parsing with YAML-defined parser_config
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def load_parser_config(path: str | Path) -> dict[str, Any]:
    """Load parser config from YAML."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def extract_metrics(
    text: str,
    parser_config: dict[str, Any] | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Extract metrics from log text using regex patterns.
    Uses parser_config dict or loads from config_path.
    """
    if parser_config is None and config_path:
        parser_config = load_parser_config(config_path)
    if not parser_config:
        return {}

    patterns = parser_config.get("patterns", [])
    metrics: dict[str, Any] = {}

    for p in patterns:
        name = p.get("name")
        regex = p.get("regex")
        type_hint = p.get("type", "str")
        if not name or not regex:
            continue
        try:
            m = re.search(regex, text)
            if m:
                raw = m.group(1)
                try:
                    if type_hint == "float":
                        metrics[name] = float(raw)
                    elif type_hint == "int":
                        metrics[name] = int(float(raw))
                    else:
                        metrics[name] = raw.strip()
                except (ValueError, IndexError) as e:
                    logger.debug("Metric %s: failed to convert %r: %s", name, raw, e)
        except re.error as e:
            logger.warning("Invalid regex for metric %s: %s", name, e)

    return metrics


def validate_metrics(
    metrics: dict[str, Any],
    required: list[str] | None = None,
    ranges: dict[str, tuple[float | None, float | None]] | None = None,
) -> tuple[bool, list[str]]:
    """
    Validate extracted metrics against required keys and optional ranges.
    Returns (valid, list of error messages).
    """
    errors: list[str] = []
    if required:
        for r in required:
            if r not in metrics:
                errors.append(f"Missing required metric: {r}")
    if ranges:
        for name, (lo, hi) in ranges.items():
            if name not in metrics:
                continue
            if lo is None and hi is None:
                continue
            #need to convert to float scientific notation is captured as a string
            try:
                lo_val = float(lo) if lo is not None else None
            except (TypeError, ValueError): #catch conversion errors
                errors.append(f"Invalid min for metric {name}")
                continue
            try:
                hi_val = float(hi) if hi is not None else None
            except (TypeError, ValueError):
                errors.append(f"Invalid max for metric {name}")
                continue

            try:
                v = float(metrics[name])
            except (TypeError, ValueError):
                errors.append(f"Metric {name} could not be converted to number (got {metrics[name]!r})")
                continue

            if lo_val is not None and v < lo_val:
                errors.append(f"Metric {name}={v} below min {lo_val}")
            if hi_val is not None and v > hi_val:
                errors.append(f"Metric {name}={v} above max {hi_val}")

    return len(errors) == 0, errors
