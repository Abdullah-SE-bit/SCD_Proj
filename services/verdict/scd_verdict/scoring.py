"""Weighted score, confidence and the threshold decision (SCR-001, SCR-003 to SCR-006). Pure functions.

Comparisons use unrounded values; PRECISION only removes binary floating-point noise, so a score that is exactly on a
threshold counts as on it.
"""

from typing import Any

from scd_verdict.config import DIMENSIONS

PRECISION = 9
Scores = dict[str, dict[str, Any]]


def weighted_score(scores: Scores, weights: dict[str, float]) -> float:
    """sum(weight x score) / 5 over the scored dimensions, rescaled by the weight they carry (AMB-09)."""
    carried = sum(weights[d] for d in scores)
    if not carried:
        return 0.0
    return round(sum(weights[d] * scores[d]["score"] for d in scores) / carried * 20, PRECISION)


def confidence(scores: Scores, sources: int, config: dict[str, Any]) -> float:
    """0.7 x mean dimension confidence + 0.3 x min(1, sources/5). A dimension without a score counts as 0."""
    rule = config["confidence"]
    mean = sum(record["confidence"] for record in scores.values()) / len(DIMENSIONS)
    coverage = min(1.0, sources / rule["sources_cap"])
    return round(rule["mean_weight"] * mean + rule["sources_weight"] * coverage, PRECISION)


def below_floor(scores: Scores, config: dict[str, Any]) -> list[str]:
    floor = config["thresholds"]["floor"]
    return [d for d in DIMENSIONS if d in config["floor_dimensions"] and d in scores and scores[d]["score"] < floor]


def weakest(scores: Scores, config: dict[str, Any]) -> str | None:
    """The lowest score, a floor breach first; ties go to the fixed dimension order."""
    candidates = below_floor(scores, config) or [d for d in DIMENSIONS if d in scores]
    return min(candidates, key=lambda d: scores[d]["score"]) if candidates else None


def threshold_verdict(score: float, breaches: list[str], config: dict[str, Any]) -> str:
    thresholds = config["thresholds"]
    if score >= thresholds["T_go"] and not breaches:
        return "GO"
    return "PIVOT" if score >= thresholds["T_no"] else "NO-GO"
