"""The six rubric files follow the contract and the course wording (RUB-001, DIM-001, DIM-002, VER-002).

Run: python -m pytest rubrics -q
"""

import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]
# Description section 5.1, "5 means"; each anchor 5 starts with this sentence.
MEANING_OF_FIVE = {
    "demand_pain": "Many independent sources show the same strong, recurring problem",
    "competition": "Few or weak direct competitors, so there is room to enter",
    "differentiation": "A clear gap that existing products do not address",
    "feasibility": "Fits the student's hours, skills and compute with margin",
    "risk": "No legal, privacy, safety or platform-dependency concern",
    "learning": "Teaches skills the student wants and shows well on a CV",
}
EVIDENCE_ID = json.loads((ROOT / "contracts/schemas/dimension-score.schema.json").read_text("utf-8"))[
    "properties"]["evidence_ids"]["items"]["pattern"]


def load(dimension):
    return json.loads((ROOT / "rubrics" / f"{dimension}.json").read_text("utf-8"))


def test_there_is_one_file_per_dimension():
    assert sorted(p.stem for p in (ROOT / "rubrics").glob("*.json")) == sorted(MEANING_OF_FIVE)


@pytest.mark.parametrize("dimension", MEANING_OF_FIVE)
def test_rubric(dimension):
    rubric = load(dimension)
    schema = json.loads((ROOT / "contracts/schemas/rubric.schema.json").read_text("utf-8"))
    Draft202012Validator(schema).validate(rubric)
    assert rubric["dimension"] == dimension
    assert rubric["anchors"]["5"].startswith(MEANING_OF_FIVE[dimension])
    assert len(set(rubric["anchors"].values())) == 6, "anchors differ"
    assert rubric["features"] and rubric["output_schema"] == ["score", "confidence", "evidence_ids", "reason"]
    assert sorted(e["expected"]["score"] for e in rubric["examples"]) == [0, 1, 2, 3, 4, 5]


@pytest.mark.parametrize("dimension", MEANING_OF_FIVE)
def test_worked_examples_are_consistent(dimension):
    rubric = load(dimension)
    assert "illustrative" in rubric["note"]
    for example in rubric["examples"]:
        given, expected = example["input"], example["expected"]
        assert sorted(given["features"]) == sorted(rubric["features"]), "every declared feature is shown"
        shown = [card["id"] for card in given["evidence"]]
        assert all(re.match(EVIDENCE_ID, i) and i.startswith("example_") for i in shown)
        # a score without evidence is an abstention, so even level 0 cites the cards it was judged on
        assert expected["evidence_ids"] and set(expected["evidence_ids"]) <= set(shown)
        assert 0 <= expected["confidence"] <= 1 and expected["reason"]
