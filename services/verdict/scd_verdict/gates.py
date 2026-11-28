"""The four hard gates (GAT-001 to GAT-005), checked before any score. Pure functions.

A gate returns (outcome, reason). Outcome "pass", "fail", or "unknown" when the facts it needs are missing: an
unknown gate never passes by default (AMB-09). Facts come from the evidence items and from the scorers' features:
feasibility.features.effort_hours, risk.features.blocker, differentiation.features.duplicate_product.
"""

from typing import Any

PASS, FAIL, UNKNOWN = "pass", "fail", "unknown"
Gate = tuple[str, str]
Scores = dict[str, dict[str, Any]]


def count_sources(scores: Scores, evidence: list[dict[str, Any]]) -> tuple[int, int]:
    """(independent sources, platforms) among the evidence the scores cite: distinct card URLs and sources (AMB-10)."""
    cited = {i for record in scores.values() for i in record["evidence_ids"]}
    used = [item for item in evidence if item["evidence_id"] in cited]
    return len({item["url"].rstrip("/").lower() for item in used}), len({item["source"].lower() for item in used})


def evidence_gate(sources: int, platforms: int, config: dict[str, Any]) -> Gate:
    need = config["evidence_gate"]
    if sources >= need["min_sources"] and platforms >= need["min_platforms"]:
        return PASS, f"{sources} sources on {platforms} platforms"
    return FAIL, (f"only {sources} independent sources on {platforms} platforms; "
                  f"needs {need['min_sources']} on {need['min_platforms']}")


def available_hours(profile: dict[str, Any]) -> float:
    return profile["hours_per_week"] * profile["weeks_available"] * profile["team_size"]  # AMB-19


def feasibility_gate(scores: Scores, profile: dict[str, Any]) -> Gate:
    effort = scores.get("feasibility", {}).get("features", {}).get("effort_hours")
    if isinstance(effort, bool) or not isinstance(effort, (int, float)) or not effort >= 0:
        return UNKNOWN, "no build effort estimate"
    hours = available_hours(profile)
    if effort <= hours:
        return PASS, f"estimated {effort:g} hours fit the {hours:g} available"
    return FAIL, f"estimated {effort:g} hours, {hours:g} available: short by {effort - hours:g} hours"


def risk_gate(scores: Scores) -> Gate:
    if "risk" not in scores:
        return UNKNOWN, "risk was not scored"
    blocker = scores["risk"]["features"].get("blocker")
    if blocker:
        return FAIL, f"legal or safety blocker: {blocker}"
    return PASS, "no legal or safety blocker found"


def duplicate_gate(scores: Scores, config: dict[str, Any]) -> Gate:
    if "differentiation" not in scores:
        return UNKNOWN, "differentiation was not scored"
    record = scores["differentiation"]
    product = record["features"].get("duplicate_product")
    needed = config["duplicate_gate"]["min_differentiation"]
    if product and record["score"] < needed:
        return FAIL, f"{product} already serves the same user with the same core features"
    return PASS, "no blocking duplicate"
