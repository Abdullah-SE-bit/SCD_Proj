"""POST /verdict answers in the contract, and the ConfigMap holds the documented rules (API-010, SCH-005, M11-003)."""

import json
import re
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "verdict"))

from scd_verdict.app import service  # noqa: E402
from verdict_fixtures import EVIDENCE, PROFILE, scores  # noqa: E402


def validator(name):
    schemas = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "contracts/schemas").glob("*.json")}
    registry = Registry().with_resources((n, Resource.from_contents(s)) for n, s in schemas.items())
    return Draft202012Validator(schemas[name], registry=registry)


def post(**body):
    request = {"scores": list(scores().values()), "profile": PROFILE, "config": {}, "evidence": EVIDENCE, **body}
    return service.handle("POST", "/verdict", json.dumps(request).encode(), {"X-Run-Id": "run-7"})


@pytest.mark.parametrize("body", [{}, {"evidence": []}, {"scores": []}, {"idea_id": "idea_5", "version": 2}])
def test_every_answer_matches_the_verdict_schema(body):
    status, answer = post(**body)
    assert status == 200, answer
    validator("verdict.schema.json").validate(answer)
    assert answer["run_id"] == "run-7"


def test_the_same_request_gets_the_same_answer():
    assert post() == post()


def test_request_config_changes_the_threshold():
    assert post()[1]["verdict"] == "GO"
    assert post(config={"thresholds": {"T_go": 71}})[1]["verdict"] == "PIVOT"


@pytest.mark.parametrize("body", [
    {"scores": "no"}, {"scores": [{"dimension": "risk"}]}, {"profile": {"goal": "fame"}}, {"profile": None},
    {"scores": [scores()["risk"], scores()["risk"]]}, {"scores": [{**scores()["risk"], "score": 6}]},
    {"scores": [{**scores()["risk"], "evidence_ids": []}]}, {"evidence": [{}]}, {"version": 0},
    {"config": {"thresholds": {"T_go": 10}}},
])
def test_bad_requests_get_400(body):
    status, answer = post(**body)
    assert status == 400 and answer["error"]


def test_configmap_packaged_defaults_and_config_file_agree():
    expected = json.loads((ROOT / "config/verdict.defaults.json").read_text(encoding="utf-8"))
    packaged = json.loads((ROOT / "services/verdict/scd_verdict/defaults.json").read_text(encoding="utf-8"))
    manifest = (ROOT / "k8s/verdict-config.yaml").read_text(encoding="utf-8")
    block = re.search(r"verdict\.json: \|\n((?:    .*\n?)+)", manifest)
    assert block and json.loads(block.group(1)) == expected == packaged
