"""Reporting maths, data isolation between users and empty-data safety."""
from datetime import date

import pytest

import analytics
from models import db, User, Transaction
from conftest import add_txn


def test_month_summary_adds_up(seeded):
    s = analytics.month_summary(seeded.id, ref=date(2026, 5, 15))
    assert s["income"] == pytest.approx(68000.0)
    assert s["expense"] == pytest.approx(42339.0)
    assert s["savings"] == pytest.approx(s["income"] - s["expense"])
    assert s["savings_rate"] == pytest.approx(s["savings"] / s["income"] * 100, abs=0.01)
    assert s["month"] == "May 2026"
    assert s["txn_count"] == 12


def test_category_totals_only_count_spending(seeded):
    s = analytics.month_summary(seeded.id, ref=date(2026, 5, 15))
    assert "Income" not in s["category_totals"]
    assert s["category_totals"]["Rent"] == pytest.approx(18000.0)
    assert sum(s["category_totals"].values()) == pytest.approx(s["expense"])


def test_top_categories_are_ordered_by_size(seeded):
    top = analytics.month_summary(seeded.id, ref=date(2026, 5, 15))["top_categories"]
    assert top[0][0] == "Rent"
    assert [a for _c, a in top] == sorted((a for _c, a in top), reverse=True)


def test_an_empty_month_falls_back_to_the_latest_month_with_data(seeded):
    """A user opening the app in a quiet month should still see their figures."""
    s = analytics.month_summary(seeded.id, ref=date(2026, 12, 1))
    assert s["month"] == "June 2026"
    assert s["txn_count"] > 0


def test_period_summary_respects_its_bounds(seeded):
    s = analytics.period_summary(seeded.id, date(2026, 5, 1), date(2026, 5, 10))
    assert s["txn_count"] == 8
    assert s["income"] == pytest.approx(68000.0)


def test_available_months_are_newest_first(seeded):
    assert analytics.available_months(seeded.id) == [(2026, 6), (2026, 5)]


def test_trends_series_are_aligned(seeded):
    t = analytics.trends(seeded.id)
    for block in ("daily", "monthly"):
        assert len(t[block]["labels"]) == len(t[block]["credit"]) == len(t[block]["debit"])
    assert len(t["weekday"]["labels"]) == len(t["weekday"]["debit"]) == 7
    assert t["monthly"]["labels"] == ["2026-05", "2026-06"]


def test_month_over_month_reads_oldest_first(seeded):
    rows = analytics.month_over_month(seeded.id, months=6)
    assert [r["month"] for r in rows] == sorted(r["month"] for r in rows)
    assert rows[-1]["label"] == "June 2026"


def test_recurring_payments_are_standing_commitments_only(seeded):
    found = analytics.recurring_subscriptions(seeded.id)
    merchants = {r["merchant"] for r in found}
    assert any("Netflix" in m for m in merchants)
    assert not any("Swiggy" in m for m in merchants), "a takeaway habit is not a subscription"
    for row in found:
        assert row["annual_cost"] <= row["amount"] * 12 + 0.01, "annual cost over-extrapolated"
        assert row["cadence"] in ("monthly", "quarterly", "yearly", "irregular")


def test_top_merchants_are_ranked(seeded):
    rows = analytics.top_merchants(seeded.id, limit=5)
    assert rows
    assert [a for _m, a, _c in rows] == sorted((a for _m, a, _c in rows), reverse=True)


def test_insights_quote_real_figures(seeded):
    items = analytics.spending_insights(seeded.id)
    assert items
    for item in items:
        assert item["severity"] in ("good", "warn", "info")
        assert item["title"] and item["detail"]


def test_one_user_never_sees_another_users_money(app_ctx):
    a = User(name="A", email="a@x.com", password_hash="x")
    b = User(name="B", email="b@x.com", password_hash="x")
    db.session.add_all([a, b])
    db.session.commit()
    add_txn(a.id, date(2026, 5, 1), "SALARY CREDIT ACME", 90000.0, "credit")
    add_txn(a.id, date(2026, 5, 2), "UPI-SWIGGY-OKAXIS-1", 500.0, "debit")
    add_txn(b.id, date(2026, 5, 1), "SALARY CREDIT OTHER", 40000.0, "credit")
    db.session.commit()

    sa = analytics.month_summary(a.id, ref=date(2026, 5, 1))
    sb = analytics.month_summary(b.id, ref=date(2026, 5, 1))
    assert sa["income"] == pytest.approx(90000.0)
    assert sb["income"] == pytest.approx(40000.0)
    assert sb["expense"] == 0


@pytest.mark.parametrize("call", [
    lambda uid: analytics.month_summary(uid),
    lambda uid: analytics.period_summary(uid),
    lambda uid: analytics.trends(uid),
    lambda uid: analytics.category_breakdown(uid),
    lambda uid: analytics.top_merchants(uid),
    lambda uid: analytics.recurring_subscriptions(uid),
    lambda uid: analytics.month_over_month(uid),
    lambda uid: analytics.budget_status(uid),
    lambda uid: analytics.spending_insights(uid),
    lambda uid: analytics.available_months(uid),
])
def test_a_brand_new_account_never_raises(user, call):
    call(user.id)


def test_budget_status_flags_an_overspend(seeded):
    from models import Budget
    db.session.add(Budget(user_id=seeded.id, category="Rent", monthly_limit=10000.0))
    db.session.commit()
    rows = {r["category"]: r for r in analytics.budget_status(seeded.id, ref=date(2026, 5, 15))}
    assert rows["Rent"]["over"] is True
    assert rows["Rent"]["spent"] == pytest.approx(18000.0)
    assert rows["Rent"]["pct"] > 100


def test_duplicate_uploads_are_detected_by_fingerprint(seeded):
    existing = Transaction.query.filter_by(user_id=seeded.id).first()
    repeat = Transaction.make_fingerprint(
        seeded.id, existing.date, existing.amount, existing.txn_type, existing.raw_description)
    assert repeat == existing.fingerprint


def test_fingerprints_differ_when_anything_differs(seeded):
    existing = Transaction.query.filter_by(user_id=seeded.id).first()
    changed = Transaction.make_fingerprint(
        seeded.id, existing.date, existing.amount + 1, existing.txn_type, existing.raw_description)
    assert changed != existing.fingerprint
