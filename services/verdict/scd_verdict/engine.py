"""The decision flow of Description Figure 4 (FLW-001). Pure: same input, same output; no model, network, clock or
randomness (M11-001, M11-002, VER-001).

Order: evidence, feasibility, risk and duplicate gates; weighted score; abstention on missing floor dimensions;
confidence; threshold and floor. A scorer that abstains sends no record, and the engine never guesses it (AMB-09).
"""

from typing import Any

from scd_verdict import gates, scoring
from scd_verdict.config import DIMENSIONS

INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
GATE_ORDER = ("evidence", "feasibility", "risk", "duplicate")


def decide(scores: gates.Scores, profile: dict[str, Any], evidence: list[dict[str, Any]],
           config: dict[str, Any]) -> dict[str, Any]:
    """The verdict core for one set of scores: verdict, gates, score, confidence, reasons."""
    weights = config["weights"][profile["goal"]]
    sources, platforms = gates.count_sources(scores, evidence)
    results = {
        "evidence": gates.evidence_gate(sources, platforms, config),
        "feasibility": gates.feasibility_gate(scores, profile),
        "risk": gates.risk_gate(scores),
        "duplicate": gates.duplicate_gate(scores, config),
    }
    abstained = [d for d in DIMENSIONS if d not in scores]
    missing_floor = [d for d in abstained if d in config["floor_dimensions"]]
    score = scoring.weighted_score(scores, weights)
    confidence = scoring.confidence(scores, sources, config)
    verdict, reasons = _verdict(results, missing_floor, score, confidence, scores, config)
    return {
        "verdict": verdict,
        "score": score,
        "confidence": confidence,
        # the documented gate values are pass and fail; a gate without its facts is reported as not passed
        "gates": {name: gates.PASS if results[name][0] == gates.PASS else gates.FAIL for name in GATE_ORDER},
        "gate_reasons": {name: results[name][1] for name in GATE_ORDER},
        "reasons": reasons,
        "abstained": abstained,
        "weakest_dimension": scoring.weakest(scores, config),
    }


def _verdict(results: dict[str, gates.Gate], missing_floor: list[str], score: float, confidence: float,
             scores: gates.Scores, config: dict[str, Any]) -> tuple[str, list[str]]:
    not_scored = [f"not scored for lack of evidence: {', '.join(missing_floor)}"] if missing_floor else []
    for name in GATE_ORDER:  # the first gate that does not pass decides, whatever the score (GAT-001)
        outcome, reason = results[name]
        if outcome == gates.UNKNOWN or (name == "evidence" and outcome == gates.FAIL):
            return INSUFFICIENT, [reason, *not_scored]  # the card names what is missing (U10)
        if outcome == gates.FAIL:
            return "NO-GO", [reason]
    if not_scored:
        return INSUFFICIENT, not_scored
    minimum = config["confidence"]["minimum"]
    if confidence < minimum:
        return INSUFFICIENT, [f"confidence {confidence:.2f} is below {minimum:g}"]
    breaches = scoring.below_floor(scores, config)
    verdict = scoring.threshold_verdict(score, breaches, config)
    floor = config["thresholds"]["floor"]
    return verdict, [f"{d} is below the floor of {floor:g}" for d in breaches]
