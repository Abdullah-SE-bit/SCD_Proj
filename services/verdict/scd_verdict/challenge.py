"""Challenge adjustments (SCR-007, AMB-08). Only objections the critic accepted reach this module.

Each accepted objection lowers its dimension's score by one step, up to the cap, and its confidence by one step for
the same counted objections. The engine then recomputes everything; the input scores are not changed.
"""

from typing import Any

Scores = dict[str, dict[str, Any]]


def apply(scores: Scores, objections: list[dict[str, Any]],
          config: dict[str, Any]) -> tuple[Scores, list[dict[str, Any]]]:
    """(adjusted copy of the scores, one adjustment per challenged dimension that has a score)."""
    rule = config["challenge"]
    step = rule["score_step"]
    countable = int(rule["max_score_reduction"] / step + 1e-9) if step else 0
    adjusted = {dimension: dict(record) for dimension, record in scores.items()}
    changes = []
    for dimension in scores:
        raised = sum(1 for objection in objections if objection["dimension"] == dimension)
        counted = min(raised, countable)
        if not counted:
            continue
        record = adjusted[dimension]
        before = record["score"], record["confidence"]
        record["score"] = max(0.0, before[0] - counted * step)
        record["confidence"] = round(max(0.0, before[1] - counted * rule["confidence_step"]), 9)
        changes.append({"dimension": dimension, "objections": raised, "counted": counted,
                        "score_before": before[0], "score_after": record["score"],
                        "confidence_before": before[1], "confidence_after": record["confidence"]})
    return adjusted, changes
