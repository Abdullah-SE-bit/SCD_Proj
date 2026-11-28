"""The sensitivity runs and the worked example of Description 5.4 (SCR-008, SCR-009, SCR-011, AMB-24)."""

import pytest
from scd_verdict import config as rules
from scd_verdict import engine, sensitivity
from verdict_fixtures import EVIDENCE, PROFILE, scores

CONFIG = rules.load()
PORTFOLIO = CONFIG["weights"]["portfolio"]


def check(inputs, evidence=EVIDENCE):
    core = engine.decide(inputs, PROFILE, evidence, CONFIG)
    return core, sensitivity.check(core, inputs, PROFILE, evidence, CONFIG)


@pytest.mark.parametrize("dimension", rules.DIMENSIONS)
@pytest.mark.parametrize("factor", [1.2, 0.8])
def test_a_shifted_weight_keeps_the_total_and_the_proportions(dimension, factor):
    shifted = sensitivity.shift_weight(PORTFOLIO, dimension, factor)
    assert sum(shifted.values()) == pytest.approx(100)
    assert shifted[dimension] == pytest.approx(PORTFOLIO[dimension] * factor)
    others = [d for d in rules.DIMENSIONS if d != dimension]
    ratios = [shifted[d] / PORTFOLIO[d] for d in others]
    assert ratios == pytest.approx([ratios[0]] * 5)


def test_a_dimension_holding_all_the_weight_cannot_move():
    weights = {**dict.fromkeys(rules.DIMENSIONS, 0), "risk": 100}
    assert sensitivity.shift_weight(weights, "risk", 0.8) == weights


def test_fourteen_runs_twelve_weights_and_two_scores():
    runs = sensitivity.runs(scores(), PROFILE, EVIDENCE, CONFIG)
    assert len(runs) == 14
    assert sum(" weight " in r["change"] for r in runs) == 12
    # confidences tie, so the lowest score is moved: competition 2.0
    assert [r["change"] for r in runs[12:]] == ["competition score 2 to 3", "competition score 2 to 1"]


def test_the_least_confident_score_wins_over_the_lowest():
    assert sensitivity.least_confident(scores(learning={"confidence": 0.4})) == "learning"


def test_worked_example_numbers():
    """70.5, then 69.9 with feasibility 25 to 20; 73.5 with competition 3.0, then 73.1 under the same change."""
    core, result = check(scores())
    assert (core["verdict"], core["score"]) == ("GO", 70.5)
    flip = next(r for r in result["flips"] if r["change"] == "feasibility weight 25 to 20")
    assert (flip["verdict"], round(flip["score"], 1)) == ("PIVOT", 69.9)
    better = scores((3.5, 3.0, 3.0, 4.0, 3.5, 4.5))
    assert check(better)[0]["score"] == 73.5
    lower = next(r for r in sensitivity.runs(better, PROFILE, EVIDENCE, CONFIG)
                 if r["change"] == "feasibility weight 25 to 20")
    assert (lower["verdict"], round(lower["score"], 1)) == ("GO", 73.1)


def test_worked_example_is_borderline_and_lists_what_flips_it():
    _, result = check(scores())
    assert result["stability"] == "BORDERLINE"
    weight_flips = [r["change"] for r in result["flips"] if " weight " in r["change"]]
    assert weight_flips == ["competition weight 15 to 18", "feasibility weight 25 to 20", "learning weight 20 to 16"]
    # AMB-24: the document's 3 covers the weight runs; by its own rules the score run also flips
    assert result["sensitivity"] == {"runs": 14, "flipped": 4}


def test_a_clear_result_is_stable():
    _, result = check(scores((5,) * 6))
    assert (result["stability"], result["sensitivity"], result["flips"]) == ("STABLE", {"runs": 14, "flipped": 0}, [])


def test_score_runs_stay_within_zero_and_five():
    runs = sensitivity.runs(scores((5,) * 6), PROFILE, EVIDENCE, CONFIG)
    assert runs[12]["change"] == "demand_pain score 5 to 5"


@pytest.mark.parametrize("inputs, evidence", [
    (scores(), EVIDENCE[:1]), (scores(feasibility={"features": {"effort_hours": 900}}), EVIDENCE),
    (scores(risk=None), EVIDENCE), (scores(confidence=0.1), EVIDENCE), ({}, []),
])
def test_verdicts_that_never_reached_scoring_have_no_runs(inputs, evidence):
    assert check(inputs, evidence)[1]["sensitivity"] == {"runs": 0, "flipped": 0}
