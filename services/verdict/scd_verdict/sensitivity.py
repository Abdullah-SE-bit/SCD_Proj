"""Does a small change flip the verdict? (SCR-008, SCR-009; AMB-05, AMB-07). Pure functions.

Twelve weight runs (each weight up and down by the configured share, the difference spread over the other weights in
proportion) and two score runs (the least confident score up and down by one point, kept within 0 to 5). Any run
with another verdict makes the card BORDERLINE. A verdict that never reached scoring has no runs.
"""

from typing import Any

from scd_verdict import engine
from scd_verdict.config import DIMENSIONS

Scores = dict[str, dict[str, Any]]


def shift_weight(weights: dict[str, float], dimension: str, factor: float) -> dict[str, float]:
    """The weights after one of them is multiplied by factor; they still add to 100."""
    changed = weights[dimension] * factor
    rest = 100 - weights[dimension]
    if rest <= 0 or changed > 100:
        return dict(weights)
    scale = (100 - changed) / rest
    return {d: changed if d == dimension else weights[d] * scale for d in weights}


def least_confident(scores: Scores) -> str:
    """Ties: the lower score, then the fixed dimension order."""
    return min((d for d in DIMENSIONS if d in scores), key=lambda d: (scores[d]["confidence"], scores[d]["score"]))


def reached_scoring(core: dict[str, Any], config: dict[str, Any]) -> bool:
    return (set(core["gates"].values()) == {"pass"}
            and not set(core["abstained"]) & set(config["floor_dimensions"])
            and core["confidence"] >= config["confidence"]["minimum"])


def runs(scores: Scores, profile: dict[str, Any], evidence: list[dict[str, Any]],
         config: dict[str, Any]) -> list[dict[str, Any]]:
    """Every sensitivity run with its verdict and score."""
    goal = profile["goal"]
    weights = config["weights"][goal]
    change = config["sensitivity"]["weight_change"]
    results = []
    for dimension in DIMENSIONS:
        for factor in (1 + change, 1 - change):
            shifted = shift_weight(weights, dimension, factor)
            altered = {**config, "weights": {**config["weights"], goal: shifted}}
            core = engine.decide(scores, profile, evidence, altered)
            results.append({"change": f"{dimension} weight {weights[dimension]:g} to {shifted[dimension]:g}",
                            "verdict": core["verdict"], "score": round(core["score"], 3)})
    if scores:
        dimension = least_confident(scores)
        for delta in (config["sensitivity"]["score_change"], -config["sensitivity"]["score_change"]):
            value = min(5.0, max(0.0, scores[dimension]["score"] + delta))
            altered_scores = {**scores, dimension: {**scores[dimension], "score": value}}
            core = engine.decide(altered_scores, profile, evidence, config)
            results.append({"change": f"{dimension} score {scores[dimension]['score']:g} to {value:g}",
                            "verdict": core["verdict"], "score": round(core["score"], 3)})
    return results


def check(core: dict[str, Any], scores: Scores, profile: dict[str, Any], evidence: list[dict[str, Any]],
          config: dict[str, Any]) -> dict[str, Any]:
    """The stability fields of a verdict."""
    done = runs(scores, profile, evidence, config) if reached_scoring(core, config) else []
    flips = [run for run in done if run["verdict"] != core["verdict"]]
    return {"stability": "BORDERLINE" if flips else "STABLE",
            "sensitivity": {"runs": len(done), "flipped": len(flips)}, "flips": flips}
