"""Verdict rules as data (M11-003). The deployed values come from a ConfigMap file named by VERDICT_CONFIG; without
that variable the packaged defaults apply. The file is read on every call, so a changed ConfigMap needs no rebuild.
"""

import json
import math
import os
from pathlib import Path
from typing import Any

DIMENSIONS = ("demand_pain", "competition", "differentiation", "feasibility", "risk", "learning")
DEFAULTS = Path(__file__).with_name("defaults.json")


class InvalidInput(ValueError):
    """A request or configuration that the engine must refuse."""


def number(value: Any, name: str, low: float = -math.inf, high: float = math.inf) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InvalidInput(f"{name} must be a number")
    if not low <= value <= high:
        raise InvalidInput(f"{name} must be between {low:g} and {high:g}")
    return float(value)


def load(overrides: Any = None) -> dict[str, Any]:
    """Deployed configuration with the request's top-level sections merged over it, validated."""
    path = Path(os.environ.get("VERDICT_CONFIG") or DEFAULTS)
    config = json.loads(path.read_text(encoding="utf-8"))
    if overrides is not None and not isinstance(overrides, dict):
        raise InvalidInput("config must be an object")
    for key, value in (overrides or {}).items():
        if key not in config or not isinstance(config[key], dict) or not isinstance(value, dict):
            raise InvalidInput(f"unknown or malformed config section: {key}")
        config[key] = {**config[key], **value}
    validate(config)
    return config


def validate(config: dict[str, Any]) -> None:
    try:
        thresholds = config["thresholds"]
        go, no = (number(thresholds[k], k, 0, 100) for k in ("T_go", "T_no"))
        number(thresholds["floor"], "floor", 0, 5)
        if no > go:
            raise InvalidInput("T_no must not exceed T_go")
        if not set(config["floor_dimensions"]) <= set(DIMENSIONS):
            raise InvalidInput("floor_dimensions has an unknown dimension")
        for goal, weights in config["weights"].items():
            if set(weights) != set(DIMENSIONS):
                raise InvalidInput(f"weights for {goal} must name the six dimensions")
            total = sum(number(w, f"weight {goal}", 0, 100) for w in weights.values())
            if not math.isclose(total, 100):
                raise InvalidInput(f"weights for {goal} must add to 100")
        confidence = config["confidence"]
        for key in ("mean_weight", "sources_weight", "minimum"):
            number(confidence[key], key, 0, 1)
        number(confidence["sources_cap"], "sources_cap", 1)
        number(config["evidence_gate"]["min_sources"], "min_sources", 0)
        number(config["evidence_gate"]["min_platforms"], "min_platforms", 0)
        number(config["duplicate_gate"]["min_differentiation"], "min_differentiation", 0, 5)
    except (KeyError, TypeError, AttributeError) as error:
        raise InvalidInput(f"configuration is incomplete: {error}") from None
