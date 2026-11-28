"""POST /verdict: validate the request, run the engine, answer in the verdict contract (API-010, SCH-005)."""

import hashlib
import json
from typing import Any

from scd_verdict import engine
from scd_verdict.config import DIMENSIONS, InvalidInput, load, number

ENGINE_VERSION = "m11@v1"
RECORD_FIELDS = ("dimension", "score", "confidence", "evidence_ids", "features", "reason", "rubric_version", "model")


def text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidInput(f"{name} must be non-empty text")
    return value


def objects(value: Any, name: str, limit: int) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > limit or not all(isinstance(v, dict) for v in value):
        raise InvalidInput(f"{name} must be a list of at most {limit} objects")
    return value


def parse_scores(value: Any) -> dict[str, dict[str, Any]]:
    scores: dict[str, dict[str, Any]] = {}
    for record in objects(value, "scores", len(DIMENSIONS)):
        missing = [f for f in RECORD_FIELDS if f not in record]
        if missing:
            raise InvalidInput(f"a score lacks {', '.join(missing)}")
        dimension = record["dimension"]
        if dimension not in DIMENSIONS or dimension in scores:
            raise InvalidInput(f"unknown or repeated dimension: {dimension}")
        number(record["score"], f"{dimension} score", 0, 5)
        number(record["confidence"], f"{dimension} confidence", 0, 1)
        ids = record["evidence_ids"]
        if not isinstance(ids, list) or not ids or not all(isinstance(i, str) and i for i in ids):
            raise InvalidInput(f"{dimension} needs evidence ids; a scorer without evidence sends no record")
        if not isinstance(record["features"], dict):
            raise InvalidInput(f"{dimension} features must be an object")
        for field in ("reason", "rubric_version", "model"):
            text(record[field], f"{dimension} {field}")
        scores[dimension] = {f: record[f] for f in RECORD_FIELDS}
    return scores


def parse_profile(value: Any, config: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InvalidInput("profile must be an object")
    if not isinstance(value.get("goal"), str) or value["goal"] not in config["weights"]:
        raise InvalidInput(f"profile goal must be one of {', '.join(config['weights'])}")
    number(value.get("hours_per_week"), "hours_per_week", 0, 168)
    number(value.get("weeks_available"), "weeks_available", 0, 520)
    number(value.get("team_size"), "team_size", 1, 100)
    return value


def parse_evidence(value: Any) -> list[dict[str, Any]]:
    items = objects(value, "evidence", 1000)
    for item in items:
        for field in ("evidence_id", "url", "source"):
            text(item.get(field), f"evidence {field}")
    return items


def assemble(core: dict[str, Any], scores: dict[str, dict[str, Any]], profile: dict[str, Any],
             config: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    weights = config["weights"][profile["goal"]]
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:8]
    return {
        **meta,
        **core,
        "score": round(core["score"], 3),
        "confidence": round(core["confidence"], 3),
        "stability": "STABLE",
        "weights": weights,
        "thresholds": {k: config["thresholds"][k] for k in ("T_go", "T_no", "floor")},
        "scores": [scores[d] for d in DIMENSIONS if d in scores],
        "what_would_make_go": [],
        "sensitivity": {"runs": 0, "flipped": 0},  # no sensitivity runs yet (P03.02): runs 0 says so
        "versions": {"engine": ENGINE_VERSION,
                     "rubrics": ",".join(sorted(r["rubric_version"] for r in scores.values())) or "none",
                     "profile_weights": f"{profile['goal']}:{digest}"},
    }


def verdict(body: dict[str, Any], run_id: str) -> dict[str, Any]:
    config = load(body.get("config"))
    scores = parse_scores(body.get("scores"))
    profile = parse_profile(body.get("profile"), config)
    evidence = parse_evidence(body.get("evidence", []))
    version = body.get("version", 1)
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise InvalidInput("version must be a positive whole number")
    meta = {"idea_id": text(body.get("idea_id", "adhoc"), "idea_id"), "version": version,
            "run_id": text(body.get("run_id", run_id), "run_id")}
    return assemble(engine.decide(scores, profile, evidence, config), scores, profile, config, meta)
