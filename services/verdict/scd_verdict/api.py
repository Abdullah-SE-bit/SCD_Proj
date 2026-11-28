"""POST /verdict and /whatif: validate the request, run the engine, answer in the contract (API-010, SCH-005)."""

import hashlib
import json
from typing import Any

from scd_verdict import challenge, engine, sensitivity, suggest
from scd_verdict.config import DIMENSIONS, InvalidInput, load, number

ENGINE_VERSION = "m11@v2"
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
        "weights": weights,
        "thresholds": {k: config["thresholds"][k] for k in ("T_go", "T_no", "floor")},
        "scores": [scores[d] for d in DIMENSIONS if d in scores],
        "versions": {"engine": ENGINE_VERSION,
                     "rubrics": ",".join(sorted(r["rubric_version"] for r in scores.values())) or "none",
                     "profile_weights": f"{profile['goal']}:{digest}"},
    }


def parse_objections(value: Any) -> list[dict[str, Any]]:
    items = objects(value, "accepted_objections", 100)
    for item in items:
        if item.get("dimension") not in DIMENSIONS:
            raise InvalidInput("each objection needs a known dimension")
        text(item.get("reason"), "objection reason")
    return items


def verdict(body: dict[str, Any], run_id: str) -> dict[str, Any]:
    """Challenge adjustments, gates and score, sensitivity and what would make it GO (Description Figure 3)."""
    config = load(body.get("config"))
    scores = parse_scores(body.get("scores"))
    profile = parse_profile(body.get("profile"), config)
    evidence = parse_evidence(body.get("evidence", []))
    objections = parse_objections(body.get("accepted_objections", []))
    version = body.get("version", 1)
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise InvalidInput("version must be a positive whole number")
    meta = {"idea_id": text(body.get("idea_id", "adhoc"), "idea_id"), "version": version,
            "run_id": text(body.get("run_id", run_id), "run_id")}
    scores, adjustments = challenge.apply(scores, objections, config)
    core = engine.decide(scores, profile, evidence, config)
    stability = sensitivity.check(core, scores, profile, evidence, config)
    wanted = suggest.what_would_make_go(core, stability["stability"], scores, profile, evidence, config)
    answer = assemble(core, scores, profile, config, meta)
    return {**answer, **stability, "what_would_make_go": wanted, "adjustments": adjustments}


def whatif(body: dict[str, Any], run_id: str) -> dict[str, Any]:
    """The verdict if some scores or profile values were different. Nothing is stored and no scorer runs."""
    changes = body.get("changes")
    if not isinstance(changes, dict) or not changes or set(changes) - {"scores", "profile"}:
        raise InvalidInput("changes must name scores and/or profile values")
    new_scores, new_profile = changes.get("scores", {}), changes.get("profile", {})
    if not isinstance(new_scores, dict) or not isinstance(new_profile, dict):
        raise InvalidInput("changes.scores and changes.profile must be objects")
    records = parse_scores(body.get("scores"))
    unknown = set(new_scores) - set(records)
    if unknown:
        raise InvalidInput(f"cannot change a dimension without a score: {', '.join(sorted(unknown))}")
    changed = [{**record, "score": new_scores.get(name, record["score"])} for name, record in records.items()]
    profile = body.get("profile")
    if not isinstance(profile, dict):
        raise InvalidInput("profile must be an object")
    result = verdict({**body, "scores": changed, "profile": {**profile, **new_profile}}, run_id)
    return {**result, "hypothetical": True}
