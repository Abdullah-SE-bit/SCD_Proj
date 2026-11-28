"""Score, confidence, threshold and floor edges (SCR-001, SCR-003 to SCR-006, SCR-011 first figure)."""

import pytest
from scd_verdict import config as rules
from scd_verdict import scoring

CONFIG = rules.load()
PORTFOLIO = CONFIG["weights"]["portfolio"]
WORKED = (3.5, 2.0, 3.0, 4.0, 3.5, 4.5)


def scores(values=WORKED, confidence=0.7):
    return {d: {"score": v, "confidence": confidence, "evidence_ids": ["a#c0"], "features": {}}
            for d, v in zip(rules.DIMENSIONS, values, strict=True)}


def test_worked_example_scores_70_5():
    assert scoring.weighted_score(scores(), PORTFOLIO) == 70.5


@pytest.mark.parametrize("value, expected", [(0, 0.0), (5, 100.0), (2.5, 50.0), (3.5, 70.0)])
def test_equal_scores_scale_to_100(value, expected):
    for weights in CONFIG["weights"].values():
        assert scoring.weighted_score(scores([value] * 6), weights) == expected


@pytest.mark.parametrize("score, verdict", [
    (70.000001, "GO"), (70, "GO"), (69.999999, "PIVOT"), (50.000001, "PIVOT"), (50, "PIVOT"), (49.999999, "NO-GO"),
])
def test_threshold_edges(score, verdict):
    assert scoring.threshold_verdict(score, [], CONFIG) == verdict


def test_floor_breach_turns_go_into_pivot_but_never_lifts_a_no_go():
    assert scoring.threshold_verdict(90, ["risk"], CONFIG) == "PIVOT"
    assert scoring.threshold_verdict(40, ["risk"], CONFIG) == "NO-GO"


@pytest.mark.parametrize("value, breaches", [(1.4999, ["competition"]), (1.5, []), (1.5001, [])])
def test_floor_edge(value, breaches):
    assert scoring.below_floor(scores((4, value, 4, 4, 4, 4)), CONFIG) == breaches


def test_learning_has_no_floor():
    assert scoring.below_floor(scores((4, 4, 4, 4, 4, 0)), CONFIG) == []


def test_weakest_prefers_a_floor_breach_then_fixed_order():
    assert scoring.weakest(scores((4, 4, 4, 1.0, 4, 0.5)), CONFIG) == "feasibility"
    assert scoring.weakest(scores((3, 2, 2, 4, 4, 4)), CONFIG) == "competition"
    assert scoring.weakest({}, CONFIG) is None


def test_confidence_formula():
    assert scoring.confidence(scores(confidence=0.7), 4, CONFIG) == pytest.approx(0.7 * 0.7 + 0.3 * 0.8)
    assert scoring.confidence(scores(confidence=1.0), 50, CONFIG) == 1.0  # sources are capped at 5


def test_confidence_exactly_on_the_minimum_is_not_below_it():
    value = (CONFIG["confidence"]["minimum"] - 0.3 * 0.6) / 0.7
    assert scoring.confidence(scores(confidence=value), 3, CONFIG) == CONFIG["confidence"]["minimum"]
