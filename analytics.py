"""Reporting maths for dashboards, the tracker and the chatbot.

Every aggregation the UI needs — monthly summaries, trend series, recurring
subscription detection, budget tracking and deterministic spending insights —
is computed here from the Transaction table, so app.py, rag.py and the
templates all read the same numbers from a single source.
"""
import calendar
import re
import statistics
from collections import Counter, defaultdict
from datetime import date

from classifier import CATEGORIES
from models import db, Transaction, Budget

SAVINGS_BENCHMARK_PCT = 20.0

# Categories where a repeated charge is a standing commitment the user has
# signed up to, rather than ordinary day-to-day spending.
RECURRING_CATEGORIES = ("Subscriptions", "Utilities", "Insurance",
                        "EMI / Loans", "Rent", "Investments")


# --------------------------------------------------------------------------- #
#  Shared helpers
# --------------------------------------------------------------------------- #
def _month_bounds(year, month):
    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    return start, end


def _build_summary(txns, label, start, end):
    """Fold a list of transactions into the shared summary shape.

    An empty list falls out of every branch as zero, so this doubles as the
    empty-data path for month_summary and period_summary alike.
    """
    income = expense = 0.0
    cat_totals = defaultdict(float)
    for t in txns:
        if t.txn_type == "credit":
            income += t.amount
        else:
            expense += t.amount
            cat_totals[t.category] += t.amount
    savings = income - expense
    rate = (savings / income * 100.0) if income else 0.0
    top = sorted(cat_totals.items(), key=lambda kv: (-kv[1], _category_rank(kv[0])))
    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "savings": round(savings, 2),
        "savings_rate": round(rate, 2),
        "top_categories": [(c, round(a, 2)) for c, a in top],
        "category_totals": {c: round(a, 2) for c, a in cat_totals.items()},
        "month": label,
        "start": start,
        "end": end,
        "txn_count": len(txns),
    }


def _merchant_label(txn):
    """Prefer the stored merchant column; fall back to a normalised description."""
    if txn.merchant:
        return txn.merchant
    source_text = txn.description or txn.raw_description or "Unknown"
    return _normalise_merchant(source_text)


def _normalise_merchant(text):
    cleaned = re.sub(r"[^A-Za-z0-9& ]", " ", text or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    words = cleaned.split(" ")
    label = " ".join(words[:2]).title() if words and words[0] else ""
    return label or "Unknown"


def _category_rank(category):
    """Canonical position of a category, used only to break amount ties
    deterministically instead of relying on dict iteration order."""
    return CATEGORIES.index(category) if category in CATEGORIES else len(CATEGORIES)


# --------------------------------------------------------------------------- #
#  Summaries
# --------------------------------------------------------------------------- #
def available_months(user_id):
    """Distinct (year, month) pairs the user has transactions in, newest first."""
    rows = (db.session.query(Transaction.date)
            .filter(Transaction.user_id == user_id, Transaction.date.isnot(None))
            .all())
    months = sorted({(d.year, d.month) for (d,) in rows}, reverse=True)
    return months


def month_summary(user_id, ref=None):
    """Summary for the calendar month containing ``ref``.

    If that month has no data, falls back to the most recent month that
    does — a fresh statement upload rarely lands in the current calendar
    month, so the dashboard should not show an empty screen by default.
    """
    ref = ref or date.today()
    months = available_months(user_id)
    target = (ref.year, ref.month)
    if months and target not in months:
        target = months[0]
    if not months:
        label = date(ref.year, ref.month, 1).strftime("%B %Y")
        return _build_summary([], label, None, None)

    start, end = _month_bounds(*target)
    txns = (Transaction.query
            .filter(Transaction.user_id == user_id,
                    Transaction.date >= start, Transaction.date <= end)
            .all())
    return _build_summary(txns, start.strftime("%B %Y"), start, end)


def period_summary(user_id, start=None, end=None, label=None):
    """Summary for an arbitrary date range, open-ended on either side."""
    query = Transaction.query.filter(Transaction.user_id == user_id)
    if start:
        query = query.filter(Transaction.date >= start)
    if end:
        query = query.filter(Transaction.date <= end)
    txns = query.all()

    if label is None:
        if start and end:
            label = f"{start.isoformat()} to {end.isoformat()}"
        elif start:
            label = f"Since {start.isoformat()}"
        elif end:
            label = f"Until {end.isoformat()}"
        else:
            label = "All time"
    return _build_summary(txns, label, start, end)


# --------------------------------------------------------------------------- #
#  Trend series
# --------------------------------------------------------------------------- #
def trends(user_id):
    """Daily (last 30 days with data), monthly and weekday credit/debit series."""
    txns = Transaction.query.filter_by(user_id=user_id).all()
    daily = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    monthly = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    weekday = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})
    wd_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for t in txns:
        if not t.date:
            continue
        daily[t.date.isoformat()][t.txn_type] += t.amount
        monthly[t.date.strftime("%Y-%m")][t.txn_type] += t.amount
        weekday[wd_names[t.date.weekday()]][t.txn_type] += t.amount

    daily_sorted = sorted(daily.items())[-30:]
    monthly_sorted = sorted(monthly.items())
    return {
        "daily": {
            "labels": [d for d, _ in daily_sorted],
            "credit": [round(v["credit"], 2) for _, v in daily_sorted],
            "debit": [round(v["debit"], 2) for _, v in daily_sorted],
        },
        "monthly": {
            "labels": [m for m, _ in monthly_sorted],
            "credit": [round(v["credit"], 2) for _, v in monthly_sorted],
            "debit": [round(v["debit"], 2) for _, v in monthly_sorted],
        },
        "weekday": {
            "labels": wd_names,
            "debit": [round(weekday[w]["debit"], 2) for w in wd_names],
        },
    }


def category_breakdown(user_id, start=None, end=None):
    """Debit totals by category, descending, for the given (optional) range."""
    query = Transaction.query.filter(Transaction.user_id == user_id,
                                     Transaction.txn_type == "debit")
    if start:
        query = query.filter(Transaction.date >= start)
    if end:
        query = query.filter(Transaction.date <= end)

    totals = defaultdict(lambda: [0.0, 0])
    for t in query.all():
        totals[t.category][0] += t.amount
        totals[t.category][1] += 1
    rows = [(cat, round(amount, 2), count) for cat, (amount, count) in totals.items()]
    rows.sort(key=lambda r: (-r[1], _category_rank(r[0])))
    return rows


def top_merchants(user_id, start=None, end=None, limit=10):
    """Highest-spend merchants, descending, for the given (optional) range."""
    query = Transaction.query.filter(Transaction.user_id == user_id,
                                     Transaction.txn_type == "debit")
    if start:
        query = query.filter(Transaction.date >= start)
    if end:
        query = query.filter(Transaction.date <= end)

    totals = defaultdict(lambda: [0.0, 0])
    for t in query.all():
        label = _merchant_label(t)
        totals[label][0] += t.amount
        totals[label][1] += 1
    rows = [(m, round(amount, 2), count) for m, (amount, count) in totals.items()]
    rows.sort(key=lambda r: r[1], reverse=True)
    return rows[:limit]


# --------------------------------------------------------------------------- #
#  Recurring subscriptions
# --------------------------------------------------------------------------- #
def recurring_subscriptions(user_id):
    """Merchants that look like a recurring subscription or bill.

    Only categories that represent a standing commitment are considered. A
    supermarket visited every week is a habit, not a subscription, and listing
    it here would bury the charges the user has actually forgotten about.

    A merchant qualifies once its debits appear in at least two distinct
    calendar months at a similar amount (within 15% of the median, which
    absorbs the odd price rise). The median gap between those matching
    charges gives the cadence, and the annual cost extrapolates the median
    amount by that cadence so it reads like a yearly cost the user can
    compare against their subscription budget.
    """
    txns = (Transaction.query
            .filter(Transaction.user_id == user_id, Transaction.txn_type == "debit")
            .filter(Transaction.category.in_(RECURRING_CATEGORIES))
            .order_by(Transaction.date)
            .all())

    groups = defaultdict(list)
    for t in txns:
        if not t.date:
            continue
        groups[_merchant_label(t)].append(t)

    results = []
    for merchant, items in groups.items():
        amounts = [t.amount for t in items]
        median_amount = statistics.median(amounts)
        if median_amount <= 0:
            continue

        band = [t for t in items if abs(t.amount - median_amount) <= 0.15 * median_amount]
        band_months = {(t.date.year, t.date.month) for t in band}
        if len(band_months) < 2:
            continue

        band_dates = sorted(t.date for t in band)
        gaps = [(band_dates[i + 1] - band_dates[i]).days for i in range(len(band_dates) - 1)]
        gaps = [g for g in gaps if g > 0]
        median_gap = statistics.median(gaps) if gaps else None

        # Standing commitments are billed monthly, quarterly or yearly. Reading
        # a weekly rhythm into them inflates the annual figure absurdly, which
        # happens whenever two statements covering the same period are loaded,
        # so the cadence is decided on how many distinct months are involved
        # rather than on the raw gap between charges.
        span_months = max(1, len(band_months))
        per_month = len(band_dates) / span_months
        if median_gap is not None and median_gap >= 350:
            cadence = "yearly"
        elif median_gap is not None and 85 <= median_gap <= 95:
            cadence = "quarterly"
        elif per_month >= 0.75:
            cadence = "monthly"
        else:
            cadence = "irregular"

        if cadence == "monthly":
            annual_cost = median_amount * 12
        elif cadence == "yearly":
            annual_cost = median_amount
        elif cadence == "quarterly":
            annual_cost = median_amount * 4
        else:
            # With no clear rhythm the rate is estimated from how often the
            # charge appeared, then held to a monthly equivalent. Extrapolating
            # a short, dense run straight to a year overstates the cost wildly.
            span_days = (band_dates[-1] - band_dates[0]).days or 1
            occurrence_rate_per_day = len(band_dates) / span_days
            annual_cost = min(median_amount * occurrence_rate_per_day * 365,
                              median_amount * 12)

        category = Counter(t.category for t in band).most_common(1)[0][0]
        results.append({
            "merchant": merchant,
            "amount": round(median_amount, 2),
            "occurrences": len(band_dates),
            "cadence": cadence,
            "last_seen": band_dates[-1],
            "annual_cost": round(annual_cost, 2),
            "category": category,
        })

    results.sort(key=lambda r: r["annual_cost"], reverse=True)
    return results


# --------------------------------------------------------------------------- #
#  Trend chart / budgets
# --------------------------------------------------------------------------- #
def month_over_month(user_id, months=6):
    """Income/expense/savings for the last N months with data, oldest first."""
    available = available_months(user_id)[:months]
    rows = []
    for (year, mon) in reversed(available):
        start, end = _month_bounds(year, mon)
        summary = period_summary(user_id, start=start, end=end,
                                 label=start.strftime("%B %Y"))
        rows.append({
            "month": f"{year:04d}-{mon:02d}",
            "label": summary["month"],
            "income": summary["income"],
            "expense": summary["expense"],
            "savings": summary["savings"],
        })
    return rows


def budget_status(user_id, ref=None):
    """Each budget the user has set against what they actually spent this month."""
    budgets = Budget.query.filter_by(user_id=user_id).all()
    if not budgets:
        return []
    summary = month_summary(user_id, ref=ref)
    spent_by_category = summary["category_totals"]

    rows = []
    for b in budgets:
        spent = spent_by_category.get(b.category, 0.0)
        pct = (spent / b.monthly_limit * 100.0) if b.monthly_limit else 0.0
        rows.append({
            "category": b.category,
            "limit": round(b.monthly_limit, 2),
            "spent": round(spent, 2),
            "pct": round(pct, 2),
            "over": spent > b.monthly_limit,
        })
    return rows


# --------------------------------------------------------------------------- #
#  Spending insights
# --------------------------------------------------------------------------- #
def spending_insights(user_id):
    """Deterministic, figure-backed observations about the current month.

    Every sentence quotes a number computed from the user's own rows —
    nothing here is generic advice, so it can be shown next to the LLM
    advisor as a fact-checked companion to it.
    """
    current = month_summary(user_id)
    if current["txn_count"] == 0:
        return []

    insights = []
    months = available_months(user_id)
    target = (current["start"].year, current["start"].month) if current["start"] else None

    prev_summary = None
    if target and target in months:
        idx = months.index(target)
        if idx + 1 < len(months):
            py, pm = months[idx + 1]
            pstart, pend = _month_bounds(py, pm)
            prev_summary = period_summary(user_id, start=pstart, end=pend,
                                          label=pstart.strftime("%B %Y"))

    if prev_summary and prev_summary["expense"] > 0:
        delta = current["expense"] - prev_summary["expense"]
        pct = delta / prev_summary["expense"] * 100.0
        driver = None
        if current["category_totals"]:
            diffs = {cat: amt - prev_summary["category_totals"].get(cat, 0.0)
                     for cat, amt in current["category_totals"].items()}
            driver = max(diffs, key=diffs.get) if diffs else None
        direction = "up" if delta > 0 else "down"
        detail = (f"Spending is {direction} Rs.{abs(delta):,.0f} ({abs(pct):.1f}%) "
                 f"versus {prev_summary['month']}.")
        if driver:
            detail += f" {driver} moved the most."
        insights.append({
            "title": f"Month-on-month spend {direction}",
            "detail": detail,
            "severity": "warn" if delta > 0 else "good",
        })

    if current["expense"] > 0 and current["category_totals"]:
        top_cat, top_amt = max(current["category_totals"].items(), key=lambda kv: kv[1])
        share = top_amt / current["expense"] * 100.0
        if share > 30:
            insights.append({
                "title": f"{top_cat} dominates spending",
                "detail": (f"{top_cat} is Rs.{top_amt:,.0f}, {share:.1f}% of this month's "
                          f"Rs.{current['expense']:,.0f} spend."),
                "severity": "warn",
            })

    start, end = current["start"], current["end"]
    debit_txns = []
    if start and end:
        debit_txns = (Transaction.query
                      .filter(Transaction.user_id == user_id, Transaction.txn_type == "debit",
                              Transaction.date >= start, Transaction.date <= end)
                      .all())

    if debit_txns:
        weekend = sum(t.amount for t in debit_txns if t.date.weekday() >= 5)
        weekday_amt = sum(t.amount for t in debit_txns if t.date.weekday() < 5)
        insights.append({
            "title": "Weekend versus weekday spend",
            "detail": (f"Weekend spend is Rs.{weekend:,.0f} against Rs.{weekday_amt:,.0f} "
                      f"on weekdays this month."),
            "severity": "info",
        })

        biggest = max(debit_txns, key=lambda t: t.amount)
        insights.append({
            "title": "Largest transaction this month",
            "detail": f"Rs.{biggest.amount:,.0f} at {biggest.description} on {biggest.date.isoformat()}.",
            "severity": "info",
        })

        total_days = (end - start).days + 1
        spend_days = {t.date for t in debit_txns}
        zero_days = total_days - len(spend_days)
        insights.append({
            "title": "Days without spending",
            "detail": f"{zero_days} of {total_days} days this month had zero recorded spend.",
            "severity": "good" if zero_days > total_days / 2 else "info",
        })

        food_orders = [t for t in debit_txns if t.category == "Food & Dining"]
        if food_orders:
            insights.append({
                "title": "Food delivery orders",
                "detail": (f"{len(food_orders)} food and dining transactions totalling "
                          f"Rs.{sum(t.amount for t in food_orders):,.0f} this month."),
                "severity": "info",
            })

    subs = recurring_subscriptions(user_id)
    if subs:
        total_annual = sum(s["annual_cost"] for s in subs)
        insights.append({
            "title": "Recurring commitments",
            "detail": (f"{len(subs)} standing charges detected, from rent and EMI to "
                      f"subscriptions, costing about Rs.{total_annual:,.0f} a year."),
            "severity": "warn",
        })

    if current["income"] > 0:
        rate = current["savings_rate"]
        if rate < SAVINGS_BENCHMARK_PCT:
            insights.append({
                "title": "Savings rate below benchmark",
                "detail": f"Savings rate is {rate:.1f}% this month, below the 20% benchmark.",
                "severity": "warn",
            })
        else:
            insights.append({
                "title": "Savings rate on target",
                "detail": f"Savings rate is {rate:.1f}%, at or above the 20% benchmark.",
                "severity": "good",
            })

    return insights[:8]
