"""M1 public API. Walking skeleton: both routes serve one fixed verdict, labelled FIXTURE DATA.

Nothing is evaluated and the orchestrator is not called yet; the real Validate flow arrives with P05.04.
"""

from typing import Any

from scd_gateway.base import Request, Service

MAX_IDEA = 2000
RUN_ID = "fixture-run"
SCORES = {"demand_pain": (3.5, 15), "competition": (2.0, 15), "differentiation": (3.0, 15),
          "feasibility": (4.0, 25), "risk": (3.5, 10), "learning": (4.5, 20)}  # dimension: score, weight
RUN: dict[str, Any] = {
    "run_id": RUN_ID,
    "status": "completed",
    "label": "FIXTURE DATA",
    "verdict": {
        "idea_id": "fixture-idea", "version": 1, "run_id": RUN_ID,
        "verdict": "GO", "stability": "BORDERLINE", "score": 70.5, "confidence": 0.74,
        "gates": {"evidence": "pass", "feasibility": "pass", "risk": "pass", "duplicate": "pass"},
        "weights": {dimension: weight for dimension, (_, weight) in SCORES.items()},
        "thresholds": {"T_go": 70, "T_no": 50, "floor": 1.5},
        "scores": [{"dimension": dimension, "score": score, "confidence": 0.7,
                    "evidence_ids": ["fixture_card#c0"], "features": {},
                    "reason": "FIXTURE DATA: no evidence was collected or scored.",
                    "rubric_version": f"{dimension}@v0", "model": "fixture"}
                   for dimension, (score, _) in SCORES.items()],
        "weakest_dimension": "competition",
        "what_would_make_go": [],
        "sensitivity": {"runs": 14, "flipped": 3},
        "versions": {"engine": "fixture", "rubrics": "fixture", "profile_weights": "fixture"},
    },
}

service = Service("gateway", "M1")


@service.route("POST", "/validate")
def validate(request: Request) -> tuple[int, Any]:
    idea = request["body"].get("idea")
    if not isinstance(idea, str) or not idea.strip() or len(idea) > MAX_IDEA:
        return 400, {"error": f"idea must be text of 1 to {MAX_IDEA} characters"}
    return 200, {"run_id": RUN_ID}


@service.route("GET", "/runs/{id}")
def run(request: Request) -> tuple[int, Any]:
    if request["params"]["id"] != RUN_ID:
        return 404, {"error": "unknown run"}
    return 200, RUN


if __name__ == "__main__":
    service.run()
