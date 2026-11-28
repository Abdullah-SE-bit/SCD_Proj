"""Repository and service layers of M2 against a migrated database (M2-001, M2-005, SCH-002)."""

import json
from pathlib import Path

import pytest
from scd_profile import repositories as repo
from scd_profile.app import ready
from scd_profile.migrate import migrate
from scd_profile.services import Invalid, NotFound, ProfileService

EXAMPLES = Path(__file__).resolve().parents[2] / "contracts" / "schemas" / "examples"


def example(name):
    return json.loads((EXAMPLES / name).read_text("utf-8"))


@pytest.fixture
def database(empty_database):
    migrate(empty_database)
    return empty_database


@pytest.fixture
def service(database):
    return ProfileService(database)


def new_user(database, email="a@example.org"):
    with database.transaction() as tx:
        return repo.add_user(tx, email, "not-a-real-hash")


def test_users_are_found_by_email_and_emails_are_unique(database):
    user_id = new_user(database)
    with database.transaction() as tx:
        assert repo.user_by_email(tx, "a@example.org")["id"] == user_id
        assert repo.user_by_email(tx, "nobody@example.org") is None
    with pytest.raises(Exception, match="(?i)unique"):
        new_user(database)


def test_profile_round_trip_raises_the_version_on_each_save(database, service):
    user_id = new_user(database)
    with pytest.raises(NotFound):
        service.profile(user_id)
    profile = example("student-profile.valid.json") | {"user_id": user_id}
    assert service.save_profile(user_id, profile) == profile | {"version": 1}
    assert service.save_profile(user_id, profile | {"hours_per_week": 4.5})["version"] == 2
    assert service.profile(user_id)["hours_per_week"] == 4.5


@pytest.mark.parametrize("change", [
    {"hours_per_week": -1}, {"hours_per_week": 169}, {"hours_per_week": "10"}, {"hours_per_week": True},
    {"weeks_available": 1.5}, {"team_size": 0}, {"compute": "cluster"}, {"goal": "fun"},
    {"skills": "python"}, {"skills": [""]}, {"interests": [1]}, {"user_id": "someone-else"}, {"extra": 1},
])
def test_invalid_profiles_are_rejected_and_not_stored(database, service, change):
    user_id = new_user(database)
    with pytest.raises(Invalid):
        service.save_profile(user_id, example("student-profile.valid.json") | {"user_id": user_id} | change)
    with pytest.raises(NotFound):
        service.profile(user_id)


def test_a_missing_field_is_rejected(database, service):
    user_id = new_user(database)
    profile = example("student-profile.valid.json") | {"user_id": user_id}
    del profile["goal"]
    with pytest.raises(Invalid, match="goal"):
        service.save_profile(user_id, profile)


def test_ideas_keep_every_version_for_their_owner_only(database, service):
    owner, other = new_user(database), new_user(database, "b@example.org")
    idea = service.create_idea(owner, "Link checker", "Checks README links", "own")
    assert idea["version"] == 1
    assert service.revise_idea(owner, idea["idea_id"], "Checks README links in CI")["version"] == 2
    with pytest.raises(NotFound):
        service.revise_idea(other, idea["idea_id"], "not mine")
    with pytest.raises(Invalid):
        service.create_idea(owner, "  ", "text", "own")
    with pytest.raises(Invalid):
        service.create_idea(owner, "title", "text", "copied")
    with database.transaction() as tx:
        assert [v["version"] for v in repo.versions_of(tx, idea["idea_id"])] == [1, 2]
        assert [i["title"] for i in repo.ideas_of(tx, owner)] == ["Link checker"]
        assert repo.ideas_of(tx, other) == []


def test_a_verdict_is_stored_whole_with_its_dimension_scores(database, service):
    idea = service.create_idea(new_user(database), "Link checker", "Checks links", "own")
    document = example("verdict.valid.json")
    with database.transaction() as tx:
        repo.save_verdict(tx, idea["version_id"], document)
    with database.transaction() as tx:
        [stored] = repo.verdicts_of(tx, idea["version_id"])
        assert stored["document"] == document and stored["verdict"] == document["verdict"]
        scores = repo.scores_of(tx, stored["id"])
    assert len(scores) == len(document["scores"])
    assert scores[0]["evidence"] == sorted(document["scores"], key=lambda s: s["dimension"])[0]["evidence_ids"]


def test_a_failed_unit_of_work_stores_nothing(database, service):
    idea = service.create_idea(new_user(database), "Link checker", "Checks links", "own")
    broken = example("verdict.valid.json")
    broken["scores"] = broken["scores"][:1] * 2  # the same dimension twice
    with pytest.raises(Exception, match="(?i)unique"), database.transaction() as tx:
        repo.save_verdict(tx, idea["version_id"], broken)
    with database.transaction() as tx:
        assert repo.verdicts_of(tx, idea["version_id"]) == []


def test_run_records_and_conversations(database, service):
    idea = service.create_idea(new_user(database), "Link checker", "Checks links", "generated")
    with database.transaction() as tx:
        repo.record_approval(tx, "run_1", "expensive_search", "declined")
        repo.index_run(tx, "run_1", 0.02, 3.5, "running")
        repo.index_run(tx, "run_1", 0.05, 8.0, "completed")
        repo.save_turns(tx, idea["idea_id"], [{"role": "user", "text": "hi"}])
        repo.save_turns(tx, idea["idea_id"], [{"role": "user", "text": "hello"}])
    with database.transaction() as tx:
        assert [a["decision"] for a in repo.approvals_of(tx, "run_1")] == ["declined"]
        assert repo.run_index(tx, "run_1") == {"run_id": "run_1", "cost": pytest.approx(0.05),
                                               "latency": pytest.approx(8.0), "status": "completed"}
        assert repo.turns_of(tx, idea["idea_id"]) == [{"role": "user", "text": "hello"}]
        assert repo.turns_of(tx, "other") == []


def test_ready_needs_a_reachable_database_when_one_is_configured(database):
    def unreachable():
        raise OSError("no route")

    assert ready(None)
    assert ready(database)
    assert not ready(type(database)(unreachable))
