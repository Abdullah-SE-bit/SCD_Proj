"""Shared test inputs: the worked example of Description 5.4 with every gate passing."""

from scd_verdict.config import DIMENSIONS

WORKED = (3.5, 2.0, 3.0, 4.0, 3.5, 4.5)
PROFILE = {"goal": "portfolio", "hours_per_week": 10, "weeks_available": 8, "team_size": 2}
EVIDENCE = [{"evidence_id": f"card{n}#c0", "source": source, "url": f"https://example.org/{n}"}
            for n, source in enumerate(("hackernews", "github", "producthunt", "github"))]


def scores(values=WORKED, confidence=0.72, **overrides):
    """A dict of six records; pass dimension=None to make that scorer abstain."""
    built = {}
    for dimension, value in zip(DIMENSIONS, values, strict=True):
        built[dimension] = {"dimension": dimension, "score": value, "confidence": confidence,
                            "evidence_ids": [item["evidence_id"] for item in EVIDENCE], "features": {},
                            "reason": "test input", "rubric_version": f"{dimension}@v1", "model": "test"}
    built["feasibility"]["features"] = {"effort_hours": 120}
    for dimension, change in overrides.items():
        if change is None:
            del built[dimension]
        else:
            built[dimension].update(change)
    return built
