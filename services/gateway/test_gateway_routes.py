"""M1 gateway fixture routes (P01.03a). The verdict is fixture data and has to say so."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from referencing import Registry, Resource
from scd_gateway.app import service

SCHEMAS = Path(__file__).resolve().parents[2] / "contracts" / "schemas"


def validate(body):
    return service.handle("POST", "/validate", json.dumps(body).encode())


def fixture_run():
    status, run = service.handle("GET", "/runs/fixture-run")
    assert status == 200
    return run


def test_validate_starts_the_fixture_run():
    assert validate({"idea": "A study planner for lab groups"}) == (200, {"run_id": "fixture-run"})


@pytest.mark.parametrize("body", [{}, {"idea": ""}, {"idea": "   "}, {"idea": 5}, {"idea": "x" * 2001}])
def test_validate_rejects_a_missing_or_oversized_idea(body):
    assert validate(body)[0] == 400


def test_run_is_labelled_as_fixture_data():
    run = fixture_run()
    assert (run["run_id"], run["status"], run["label"]) == ("fixture-run", "completed", "FIXTURE DATA")
    assert all(s["reason"].startswith("FIXTURE DATA") and s["model"] == "fixture" for s in run["verdict"]["scores"])


def test_fixture_verdict_follows_the_contract():
    schemas = {p.name: json.loads(p.read_text("utf-8")) for p in SCHEMAS.glob("*.schema.json")}
    registry: Registry = Registry().with_resources((n, Resource.from_contents(s)) for n, s in schemas.items())
    verdict = fixture_run()["verdict"]
    Draft202012Validator(schemas["verdict.schema.json"], registry=registry).validate(verdict)
    total = sum(s["score"] * verdict["weights"][s["dimension"]] for s in verdict["scores"]) / 5
    assert total == pytest.approx(verdict["score"])


def test_unknown_run_is_not_found():
    assert service.handle("GET", "/runs/other")[0] == 404
