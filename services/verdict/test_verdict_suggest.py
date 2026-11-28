"""What would make this GO (SCR-010, AMB-13)."""

import pytest
from scd_verdict import config as rules
from scd_verdict import engine, sensitivity, suggest
from verdict_fixtures import EVIDENCE, PROFILE, scores

CONFIG = rules.load()


def suggestions(inputs, profile=PROFILE, evidence=EVIDENCE):
    core = engine.decide(inputs, profile, evidence, CONFIG)
    stability = sensitivity.check(core, inputs, profile, evidence, CONFIG)["stability"]
    return suggest.what_would_make_go(core, stability, inputs, profile, evidence, CONFIG)


def test_candidates_go_from_smallest_total_and_prefer_one_dimension():
    ordered = suggest.candidates(scores((4.5, 4.5, 5, 5, 5, 5)))
    assert ordered == [{"demand_pain": 5.0}, {"competition": 5.0}, {"demand_pain": 5.0, "competition": 5.0}]


def test_a_pivot_gets_the_smallest_change_that_reaches_go():
    inputs = scores((3.5, 2.0, 3.0, 3.5, 3.5, 4.5))  # 68.0, PIVOT
    found = suggestions(inputs)[0]
    assert found["new_verdict"] == "GO" and found["new_score"] >= 70 and found["change"].startswith("raise ")
    total = float(found["change"].split(" to ")[1].split()[0]) - float(found["change"].split(" from ")[1].split()[0])
    for values in suggest.candidates(inputs):  # nothing smaller gives a stable GO
        size = sum(v - inputs[d]["score"] for d, v in values.items())
        if size < total - 1e-9:
            changed = suggest.with_scores(inputs, values)
            core = engine.decide(changed, PROFILE, EVIDENCE, CONFIG)
            assert core["verdict"] != "GO" or sensitivity.check(
                core, changed, PROFILE, EVIDENCE, CONFIG)["stability"] == "BORDERLINE"


def test_a_borderline_go_is_told_how_to_become_firmer():
    found = suggestions(scores())[0]
    assert found["new_verdict"] == "GO" and found["new_score"] > 70.5


@pytest.mark.parametrize("inputs", [scores((5,) * 6), scores(risk=None), {}])
def test_nothing_to_suggest_for_a_stable_go_or_missing_evidence(inputs):
    assert suggestions(inputs) == []


def test_too_much_work_says_how_many_hours_to_cut():
    found = suggestions(scores((5,) * 6, feasibility={"features": {"effort_hours": 200}}))
    assert found == [{"change": "cut the build effort by 40 hours, to 160", "new_score": 100.0, "new_verdict": "GO"}]


def test_a_blocker_and_a_duplicate_are_named():
    blocked = suggestions(scores(risk={"features": {"blocker": "no consent"}}))[0]
    assert "no consent" in blocked["change"]
    copied = suggestions(scores(differentiation={"score": 1.0, "features": {"duplicate_product": "Acme"}}))[0]
    assert "Acme" in copied["change"] and copied["new_verdict"] in ("GO", "PIVOT")


def test_no_possible_change_gives_no_suggestion():
    low_confidence_go = scores((0,) * 6)
    strict = rules.load({"thresholds": {"T_go": 100, "floor": 5}})
    core = engine.decide(low_confidence_go, PROFILE, EVIDENCE, strict)
    assert suggest.what_would_make_go(core, "STABLE", low_confidence_go, PROFILE, EVIDENCE, strict) == []


def test_two_students_can_get_different_verdicts_for_the_same_idea():
    large = scores((5,) * 6, feasibility={"features": {"effort_hours": 300}})
    team = {**PROFILE, "team_size": 4}
    assert engine.decide(large, PROFILE, EVIDENCE, CONFIG)["verdict"] == "NO-GO"
    assert engine.decide(large, team, EVIDENCE, CONFIG)["verdict"] == "GO"
