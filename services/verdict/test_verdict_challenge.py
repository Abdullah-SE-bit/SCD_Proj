"""Challenge steps and caps (SCR-007)."""

import copy

import pytest
from scd_verdict import challenge, engine
from scd_verdict import config as rules
from verdict_fixtures import EVIDENCE, PROFILE, scores

CONFIG = rules.load()


def objections(dimension, count):
    return [{"dimension": dimension, "reason": f"objection {n}"} for n in range(count)]


@pytest.mark.parametrize("count, score, confidence", [(1, 3.5, 0.62), (2, 3.0, 0.52), (3, 3.0, 0.52), (9, 3.0, 0.52)])
def test_each_objection_costs_half_a_point_up_to_one(count, score, confidence):
    adjusted, changes = challenge.apply(scores(), objections("feasibility", count), CONFIG)
    assert adjusted["feasibility"]["score"] == score
    assert adjusted["feasibility"]["confidence"] == pytest.approx(confidence)
    assert (changes[0]["objections"], changes[0]["counted"]) == (count, min(count, 2))


def test_scores_and_confidence_stop_at_zero():
    inputs = scores(risk={"score": 0.2, "confidence": 0.05})
    adjusted, _ = challenge.apply(inputs, objections("risk", 2), CONFIG)
    assert (adjusted["risk"]["score"], adjusted["risk"]["confidence"]) == (0.0, 0.0)


def test_only_challenged_dimensions_with_a_score_change_and_the_input_is_kept():
    inputs = scores(learning=None)
    before = copy.deepcopy(inputs)
    adjusted, changes = challenge.apply(inputs, objections("learning", 2) + objections("competition", 1), CONFIG)
    assert [c["dimension"] for c in changes] == ["competition"] and inputs == before
    assert adjusted["risk"] == before["risk"]


def test_a_challenge_can_change_the_verdict():
    adjusted, _ = challenge.apply(scores(), objections("feasibility", 1), CONFIG)
    result = engine.decide(adjusted, PROFILE, EVIDENCE, CONFIG)
    assert (result["verdict"], result["score"]) == ("PIVOT", 68.0)
