"""Decision order, gate precedence and abstention (FLW-001, GAT-001, SCR-006, AMB-09, U10)."""

import copy

import pytest
from scd_verdict import config as rules
from scd_verdict import engine
from verdict_fixtures import EVIDENCE, PROFILE, scores

CONFIG = rules.load()
PERFECT = (5,) * 6


def decide(inputs, evidence=EVIDENCE):
    return engine.decide(inputs, PROFILE, evidence, CONFIG)


def test_worked_example_is_go():
    result = decide(scores())
    assert (result["verdict"], result["score"], result["abstained"]) == ("GO", 70.5, [])
    assert set(result["gates"].values()) == {"pass"}


@pytest.mark.parametrize("override, word", [
    ({"feasibility": {"features": {"effort_hours": 900}}}, "short by 740 hours"),
    ({"risk": {"features": {"blocker": "collects medical data without consent"}}}, "medical data"),
    ({"differentiation": {"score": 2.5, "features": {"duplicate_product": "Acme Planner"}}}, "Acme Planner"),
])
def test_a_failed_gate_is_no_go_even_with_a_perfect_score(override, word):
    result = decide(scores(PERFECT, **override))
    assert result["verdict"] == "NO-GO" and word in result["reasons"][0]


def test_the_evidence_gate_comes_first():
    result = decide(scores(PERFECT, risk={"features": {"blocker": "x"}}), evidence=EVIDENCE[:2])
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE" and "2 independent sources" in result["reasons"][0]


def test_gates_are_decided_in_order():
    both = scores(feasibility={"features": {"effort_hours": 900}}, risk={"features": {"blocker": "x"}})
    assert "hours" in decide(both)["reasons"][0]


@pytest.mark.parametrize("dimension", ["demand_pain", "competition", "differentiation", "feasibility", "risk"])
def test_an_abstaining_floor_dimension_gives_insufficient_evidence_and_is_named(dimension):
    result = decide(scores(PERFECT, **{dimension: None}))
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE" and result["abstained"] == [dimension]
    assert dimension.split("_")[0] in " ".join(result["reasons"])


def test_abstaining_learning_rescales_the_weights_and_lowers_confidence():
    full, partial = decide(scores(PERFECT)), decide(scores(PERFECT, learning=None))
    assert partial["verdict"] == "GO" and partial["score"] == 100.0
    assert partial["confidence"] < full["confidence"]
    assert partial["abstained"] == ["learning"]


def test_low_confidence_abstains_even_with_a_perfect_score():
    result = decide(scores(PERFECT, confidence=0.2))
    assert result["verdict"] == "INSUFFICIENT_EVIDENCE" and "confidence" in result["reasons"][0]


def test_no_scores_at_all():
    result = decide({}, evidence=[])
    assert (result["verdict"], result["score"], result["weakest_dimension"]) == ("INSUFFICIENT_EVIDENCE", 0.0, None)


def test_floor_breach_gives_pivot_naming_the_dimension():
    result = decide(scores((5, 1.0, 5, 5, 5, 5)))
    assert (result["verdict"], result["weakest_dimension"]) == ("PIVOT", "competition")


def test_same_input_same_output_and_input_untouched():
    inputs = scores()
    before = copy.deepcopy(inputs)
    assert all(decide(inputs) == decide(inputs) for _ in range(50))
    assert inputs == before
