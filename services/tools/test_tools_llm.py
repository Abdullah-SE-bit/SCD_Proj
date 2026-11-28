"""POST /llm with recorded-style answers: no network and no real key (budget, validation, secrecy)."""

import json

import pytest
from scd_tools import llm
from tools_fakes import Network, ok

ENV = {"HOSTED_LLM_API_KEY": "test-key", "HOSTED_LLM_MODEL": "test-model"}
BODY = {"messages": [{"role": "user", "content": "x" * 300}], "max_tokens": 100}


def answer(tokens=50, text="hello"):
    return ok(json.dumps({"model": "test-model", "choices": [{"message": {"content": text}}],
                          "usage": {"total_tokens": tokens}}))


def proxy(*replies, env=ENV, run_cap=1000, day_cap=10_000):
    network = Network(*replies)
    return llm.Proxy(network.send, network.resolve, env, llm.Budget(run_cap, day_cap)), network


def test_a_call_goes_to_the_provider_with_the_key_and_counts_tokens():
    model, network = proxy(answer(80))
    result = model.complete({**BODY, "json": True}, "run-1")
    assert (result["content"], result["run_tokens_used"]) == ("hello", 80)
    call = network.calls[0]
    assert (call["host"], call["target"]) == ("api.groq.com", "/openai/v1/chat/completions")
    assert call["headers"]["Authorization"] == "Bearer test-key"
    assert json.loads(call["body"])["response_format"] == {"type": "json_object"}
    assert "test-key" not in json.dumps(result)


@pytest.mark.parametrize("env", [{}, {"HOSTED_LLM_API_KEY": "k"},
                                 {**ENV, "HOSTED_LLM_BASE_URL": "https://evil.example/v1"},
                                 {**ENV, "HOSTED_LLM_BASE_URL": "http://api.groq.com/openai/v1"}])
def test_unconfigured_or_foreign_provider_sends_nothing(env):
    model, network = proxy(env=env)
    with pytest.raises(llm.Unavailable):
        model.complete(BODY, "run-1")
    assert network.calls == []


@pytest.mark.parametrize("body", [
    {}, {"messages": []}, {"messages": [{"role": "tool", "content": "a"}]}, {"messages": [{"role": "user"}]},
    {**BODY, "max_tokens": 0}, {**BODY, "max_tokens": 10_000}, {**BODY, "temperature": 5},
    {"messages": [{"role": "user", "content": "a" * 70_000}]},
])
def test_bad_requests(body):
    model, network = proxy()
    with pytest.raises(llm.Invalid):
        model.complete(body, "run-1")
    assert network.calls == []


def test_the_run_budget_stops_calls_before_they_are_sent():
    model, network = proxy(answer(900), answer(10), run_cap=1000)
    model.complete(BODY, "run-1")
    with pytest.raises(llm.OverBudget, match="run"):
        model.complete(BODY, "run-1")
    assert len(network.calls) == 1
    model.complete(BODY, "run-2")  # another run has its own budget


def test_the_daily_budget_covers_all_runs_and_resets_next_day():
    days = ["monday"]
    network = Network(answer(900), answer(10))
    model = llm.Proxy(network.send, network.resolve, ENV, llm.Budget(5000, 1000, lambda: days[0]))
    model.complete(BODY, "run-1")
    with pytest.raises(llm.OverBudget, match="daily"):
        model.complete(BODY, "run-2")
    days[0] = "tuesday"
    model.complete(BODY, "run-2")


@pytest.mark.parametrize("reply", [ok("{}", status=429, **{"retry-after": "7"}), ok("{}", status=500),
                                   ConnectionError("api.groq.com: TimeoutError")])
def test_a_failed_call_is_reported_and_not_charged(reply):
    model, _ = proxy(reply)
    with pytest.raises(llm.ProviderError):
        model.complete(BODY, "run-1")
    assert model.budget.day_used == 0


def test_an_unreadable_answer_is_charged_in_full():
    model, _ = proxy(ok("not json"))
    with pytest.raises(llm.ProviderError, match="understood"):
        model.complete(BODY, "run-1")
    assert model.budget.day_used == 200
