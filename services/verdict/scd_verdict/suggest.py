"""What would make this GO (SCR-010, AMB-13). Pure functions.

A failed gate suggests removing its cause. A scored idea gets the smallest total score increase, in steps of 0.5 over
one dimension and then two, that gives a stable GO; if no such change is stable, the smallest one that gives GO. These
are suggestions: applying one means re-running the scorers and the engine on the changed idea.
"""

from itertools import combinations
from typing import Any

from scd_verdict import engine, gates, sensitivity
from scd_verdict.config import DIMENSIONS

STEP = 0.5
Scores = dict[str, dict[str, Any]]


def with_scores(scores: Scores, values: dict[str, float]) -> Scores:
    return {**scores, **{d: {**scores[d], "score": v} for d, v in values.items()}}


def candidates(scores: Scores) -> list[dict[str, float]]:
    """New score values, smallest total increase first; one dimension before two at the same total."""
    steps = {d: int((5 - scores[d]["score"]) / STEP + 1e-9) for d in DIMENSIONS if d in scores}
    found: list[tuple[int, int, int, dict[str, float]]] = []
    for order, dimension in enumerate(steps):
        found += [(k, 1, order, {dimension: scores[dimension]["score"] + k * STEP})
                  for k in range(1, steps[dimension] + 1)]
    for order, (a, b) in enumerate(combinations(steps, 2)):
        found += [(i + j, 2, order, {a: scores[a]["score"] + i * STEP, b: scores[b]["score"] + j * STEP})
                  for i in range(1, steps[a] + 1) for j in range(1, steps[b] + 1)]
    return [values for *_, values in sorted(found, key=lambda item: item[:3])]


def answer(change: str, core: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"change": change, "new_score": round(core["score"], 3), "new_verdict": core["verdict"]}]


def for_gate(core: dict[str, Any], scores: Scores, profile: dict[str, Any], evidence: list[dict[str, Any]],
             config: dict[str, Any]) -> list[dict[str, Any]]:
    """The cause of the first failed gate, removed."""
    failed = next(name for name in engine.GATE_ORDER if core["gates"][name] != gates.PASS)
    if failed == "feasibility":
        hours = gates.available_hours(profile)
        effort = scores["feasibility"]["features"]["effort_hours"]
        features = {**scores["feasibility"]["features"], "effort_hours": hours}
        changed = {**scores, "feasibility": {**scores["feasibility"], "features": features}}
        text = f"cut the build effort by {effort - hours:g} hours, to {hours:g}"
    elif failed == "risk":
        text = f"remove the blocker: {scores['risk']['features']['blocker']}"
        changed = {**scores, "risk": {**scores["risk"], "features": {**scores["risk"]["features"], "blocker": None}}}
    else:
        needed = config["duplicate_gate"]["min_differentiation"]
        text = (f"raise differentiation to {needed:g} against "
                f"{scores['differentiation']['features']['duplicate_product']}")
        changed = with_scores(scores, {"differentiation": needed})
    return answer(text, engine.decide(changed, profile, evidence, config))


def what_would_make_go(core: dict[str, Any], stability: str, scores: Scores, profile: dict[str, Any],
                       evidence: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    if core["verdict"] == engine.INSUFFICIENT or (core["verdict"] == "GO" and stability == "STABLE"):
        return []  # missing evidence is named on the card; a stable GO needs nothing
    if set(core["gates"].values()) != {gates.PASS}:
        return for_gate(core, scores, profile, evidence, config)
    fallback: list[dict[str, Any]] = []
    for values in candidates(scores):
        changed = with_scores(scores, values)
        result = engine.decide(changed, profile, evidence, config)
        if result["verdict"] != "GO":
            continue
        text = " and ".join(f"raise {d} from {scores[d]['score']:g} to {v:g}" for d, v in values.items())
        if sensitivity.check(result, changed, profile, evidence, config)["stability"] == "STABLE":
            return answer(text, result)
        fallback = fallback or answer(f"{text} (still borderline)", result)
    return fallback
