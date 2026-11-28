"""Gate edges (GAT-002 to GAT-005) and configuration validation."""

import json

import pytest
from scd_verdict import config as rules
from scd_verdict import gates

CONFIG = rules.load()
PROFILE = {"hours_per_week": 10, "weeks_available": 8, "team_size": 2}  # 160 hours


def record(score=3.0, ids=("a#c0",), **features):
    return {"score": score, "confidence": 0.7, "evidence_ids": list(ids), "features": features}


def item(n, source, url=None):
    return {"evidence_id": f"c{n}#c0", "source": source, "url": url or f"https://example.org/{n}"}


@pytest.mark.parametrize("sources, platforms, outcome",
                         [(3, 2, "pass"), (2, 2, "fail"), (3, 1, "fail"), (0, 0, "fail"), (9, 3, "pass")])
def test_evidence_gate_edges(sources, platforms, outcome):
    assert gates.evidence_gate(sources, platforms, CONFIG)[0] == outcome


def test_sources_are_distinct_cited_cards():
    scores = {"risk": record(ids=["c1#c0", "c2#c0", "c3#c0"])}
    evidence = [item(1, "hackernews"), item(2, "github", "https://example.org/1/"), item(3, "github"),
                item(4, "producthunt")]  # card 2 repeats card 1's URL; card 4 is not cited
    assert gates.count_sources(scores, evidence) == (2, 2)


@pytest.mark.parametrize("effort, outcome", [(159.5, "pass"), (160, "pass"), (160.5, "fail"), (None, "unknown"),
                                             ("40", "unknown"), (True, "unknown"), (-1, "unknown")])
def test_feasibility_gate_edges(effort, outcome):
    assert gates.feasibility_gate({"feasibility": record(effort_hours=effort)}, PROFILE)[0] == outcome


def test_feasibility_failure_states_the_gap():
    assert "short by 40 hours" in gates.feasibility_gate({"feasibility": record(effort_hours=200)}, PROFILE)[1]


def test_risk_gate_names_the_blocker():
    outcome, reason = gates.risk_gate({"risk": record(blocker="scrapes a site that forbids it")})
    assert outcome == "fail" and "scrapes a site that forbids it" in reason
    assert gates.risk_gate({"risk": record()})[0] == "pass"
    assert gates.risk_gate({})[0] == "unknown"


@pytest.mark.parametrize("score, product, outcome",
                         [(2.5, "Acme", "fail"), (3.0, "Acme", "pass"), (3.5, "Acme", "pass"), (0.0, None, "pass")])
def test_duplicate_gate_edges(score, product, outcome):
    result, reason = gates.duplicate_gate({"differentiation": record(score, duplicate_product=product)}, CONFIG)
    assert result == outcome and (outcome == "pass" or "Acme" in reason)


def test_duplicate_gate_without_a_score_does_not_pass():
    assert gates.duplicate_gate({}, CONFIG)[0] == "unknown"


@pytest.mark.parametrize("overrides", [
    {"thresholds": {"T_go": 40}}, {"thresholds": {"floor": 9}}, {"thresholds": {"T_go": float("nan")}},
    {"weights": {"startup": {"demand_pain": 100}}}, {"weights": {"portfolio": dict.fromkeys(rules.DIMENSIONS, 20)}},
    {"nonsense": {}}, {"floor_dimensions": []}, [1],
])
def test_bad_configuration_is_refused(overrides):
    with pytest.raises(rules.InvalidInput):
        rules.load(overrides)


def test_a_config_file_changes_the_rules(tmp_path, monkeypatch):
    changed = json.loads(rules.DEFAULTS.read_text(encoding="utf-8"))
    changed["thresholds"]["T_go"] = 80
    path = tmp_path / "verdict.json"
    path.write_text(json.dumps(changed), encoding="utf-8")
    monkeypatch.setenv("VERDICT_CONFIG", str(path))
    assert rules.load()["thresholds"]["T_go"] == 80
    path.unlink()
    with pytest.raises(OSError):
        rules.load()  # a named but missing file is an error, never a silent fallback
