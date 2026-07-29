"""Question understanding and the grounding of every figure the chatbot states.

The language model is deliberately switched off in these tests. What is being
checked is that the deterministic layer alone already answers correctly, which
is what guarantees the figures are right whatever the model does.
"""
from datetime import date

import pytest

import nlq
import rag


TODAY = date(2026, 6, 20)


def spec_for(question, user_id=None):
    known = rag._known_merchants(user_id) if user_id else None
    return nlq.parse_query(question, today=TODAY, known_merchants=known)


@pytest.fixture(autouse=True)
def no_language_model(monkeypatch):
    """Force the deterministic path so the assertions test our own logic."""
    monkeypatch.setattr(rag, "_llm_phrase", lambda prompt, system: "")
    monkeypatch.setattr(rag.advisor, "llm_generate", lambda prompt, system="": "")


@pytest.mark.parametrize("question,metric", [
    ("how much did I spend on food", "sum"),
    ("how many transactions did I make", "count"),
    ("average food spend", "average"),
    ("what was my biggest expense", "max"),
    ("list my transport expenses", "list"),
    ("where did my money go", "breakdown"),
    ("compare last month with this month", "compare"),
    ("how can I save money", "advice"),
])
def test_metric_is_recognised(question, metric):
    assert spec_for(question)["metric"] == metric


@pytest.mark.parametrize("question,start,end", [
    ("how much did I spend this month", date(2026, 6, 1), date(2026, 6, 30)),
    ("how much did I spend last month", date(2026, 5, 1), date(2026, 5, 31)),
    ("how much did I spend in May", date(2026, 5, 1), date(2026, 5, 31)),
    ("how much did I spend in May 2026", date(2026, 5, 1), date(2026, 5, 31)),
    ("spending between 1 May and 15 May", date(2026, 5, 1), date(2026, 5, 15)),
])
def test_time_periods_are_understood(question, start, end):
    s = spec_for(question)
    assert s["start"] == start and s["end"] == end


def test_a_question_with_no_period_does_not_invent_one():
    s = spec_for("how much did I spend on food")
    assert s["start"] is None and s["end"] is None
    assert s["period_label"] == "all time"


@pytest.mark.parametrize("question,category", [
    ("how much did I spend on food", "Food & Dining"),
    ("what did I spend on groceries", "Groceries"),
    ("how much on petrol", "Transport"),
    ("how much on electricity bills", "Utilities"),
    ("what are my subscriptions", "Subscriptions"),
    ("how much on clothes", "Shopping"),
])
def test_everyday_words_map_to_categories(question, category):
    assert spec_for(question)["category"] == category


def test_income_questions_look_at_credits():
    assert spec_for("how much did I earn in May")["txn_type"] == "credit"
    assert spec_for("how much did I spend in May")["txn_type"] == "debit"


def test_a_merchant_is_matched_against_the_users_own_data(seeded):
    assert spec_for("how much did I spend on Swiggy", seeded.id)["merchant"] is not None


def test_totals_come_out_of_the_database(seeded):
    s = spec_for("how much did I spend on food in May", seeded.id)
    result = nlq.execute(seeded.id, s)
    assert result["matched"] is True
    assert result["total"] == pytest.approx(980.0)
    assert result["count"] == 2


def test_income_total_for_a_month(seeded):
    result = nlq.execute(seeded.id, spec_for("how much did I earn in May", seeded.id))
    assert result["total"] == pytest.approx(68000.0)


def test_biggest_expense_is_the_largest_row(seeded):
    result = nlq.execute(seeded.id, spec_for("what was my biggest expense in May", seeded.id))
    assert result["rows"][0].amount == pytest.approx(18000.0)


def test_counting_a_month(seeded):
    result = nlq.execute(seeded.id, spec_for("how many transactions did I make in May", seeded.id))
    assert result["count"] == 12


def test_every_rupee_figure_in_an_answer_exists_in_the_data(seeded):
    """No answer may contain a number the database cannot account for."""
    import re
    questions = ["how much did I spend on food in May",
                 "how much did I earn in May",
                 "what was my biggest expense in May",
                 "how much did I spend on groceries in May"]
    for q in questions:
        detail = rag.answer_detailed(seeded.id, q, today=TODAY)
        allowed = {round(float(v)) for v in detail["numbers"].values()
                   if isinstance(v, (int, float))}
        quoted = re.findall(r"Rs\.?\s?([\d,]+)", detail["reply"])
        for figure in quoted:
            assert round(float(figure.replace(",", ""))) in allowed, (
                f"{q}: unexplained figure Rs.{figure}")


def test_answers_stay_readable_with_the_model_switched_off(seeded):
    for q in ["how much did I spend on food in May",
              "what are my subscriptions",
              "where did my money go",
              "how can I save money"]:
        reply = rag.answer(seeded.id, q, today=TODAY)
        assert reply and len(reply) > 20
        assert "None" not in reply and "{" not in reply


def test_an_empty_period_offers_the_nearest_month_that_has_data(seeded):
    reply = rag.answer(seeded.id, "how much did I spend on food this month",
                       today=date(2026, 12, 15))
    assert "nothing recorded" in reply.lower()
    assert "june 2026" in reply.lower()


def test_an_unanswerable_question_says_so_rather_than_guessing(seeded):
    reply = rag.answer(seeded.id, "what is the capital of France", today=TODAY)
    assert "Rs." not in reply or "could not" in reply.lower()


def test_the_guard_rejects_an_invented_figure():
    """A reply quoting a rupee amount that was never computed must be refused."""
    accepted, reason = rag._check_llm_reply("You spent Rs.99,999 on food.", {"total": 4280})
    assert accepted is False
    assert reason in ("invented-figure", "no-verified-figure")


def test_the_guard_rejects_arithmetic_working():
    accepted, _ = rag._check_llm_reply(
        r"Amount per transaction = \frac{4280}{9}", {"total": 4280})
    assert accepted is False


def test_the_guard_rejects_first_person_replies():
    accepted, reason = rag._check_llm_reply("I spent Rs.4,280 on food.", {"total": 4280})
    assert accepted is False and reason == "first-person"


def test_the_guard_accepts_a_faithful_rewrite():
    accepted, _ = rag._check_llm_reply(
        "You spent Rs.4,280 on Food & Dining across 9 transactions.", {"total": 4280})
    assert accepted is True
