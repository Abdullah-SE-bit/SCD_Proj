"""/verdict with objections and /whatif, over the contract (API-010, SCR-007, SCR-009, SCR-010)."""

import json

import pytest
from test_verdict_contract import EVIDENCE, PROFILE, post, scores, service, validator


def whatif(changes, **body):
    request = {"scores": list(scores().values()), "profile": PROFILE, "config": {}, "evidence": EVIDENCE,
               "changes": changes, **body}
    return service.handle("POST", "/whatif", json.dumps(request).encode(), {})


def test_the_worked_example_card():
    answer = post()[1]
    assert (answer["verdict"], answer["stability"], answer["score"]) == ("GO", "BORDERLINE", 70.5)
    assert "feasibility weight 25 to 20" in [f["change"] for f in answer["flips"]]
    assert answer["what_would_make_go"][0]["new_verdict"] == "GO"
    validator("verdict.schema.json").validate(answer)


def test_raising_competition_gives_73_5():
    status, answer = whatif({"scores": {"competition": 3.0}})
    assert (status, answer["score"], answer["verdict"], answer["hypothetical"]) == (200, 73.5, "GO", True)
    validator("verdict.schema.json").validate(answer)


def test_accepted_objections_lower_the_score_and_are_listed():
    answer = post(accepted_objections=[{"dimension": "feasibility", "reason": "needs a paid GPU"}])[1]
    assert (answer["verdict"], answer["score"]) == ("PIVOT", 68.0)
    assert answer["adjustments"][0]["dimension"] == "feasibility"
    assert answer["scores"][3]["score"] == 3.5
    validator("verdict.schema.json").validate(answer)


def test_fewer_hours_fail_the_feasibility_gate_in_a_whatif():
    assert whatif({"profile": {"hours_per_week": 2}})[1]["verdict"] == "NO-GO"


@pytest.mark.parametrize("changes", [None, {}, {"weights": {}}, {"scores": {"nonsense": 1}}, {"scores": 3},
                                     {"scores": {"risk": 9}}, {"profile": {"goal": "fame"}}])
def test_bad_whatif_requests(changes):
    assert whatif(changes)[0] == 400


@pytest.mark.parametrize("objections", [[{}], [{"dimension": "risk"}], "x"])
def test_bad_objections(objections):
    assert post(accepted_objections=objections)[0] == 400
