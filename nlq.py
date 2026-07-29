"""Deterministic natural-language to SQL translation.

Every figure the chatbot states must trace back to a real database query, so
this module never calls a language model. `parse_query` reads the question
with regular expressions and keyword tables and produces a structured spec;
`execute` turns that spec into a SQLAlchemy query scoped to one user and
returns exact totals. A question that cannot be parsed comes back with
`matched=False` so the caller can fall back to semantic retrieval.
"""
import calendar
import re
from datetime import date, timedelta

from sqlalchemy import or_

from models import Transaction

try:
    from classifier import CATEGORIES
except ImportError:
    CATEGORIES = [
        "Income", "Rent", "EMI / Loans", "Insurance", "Investments", "Subscriptions",
        "Food & Dining", "Groceries", "Transport", "Utilities", "Shopping", "Health",
        "Education", "Entertainment", "Travel", "Transfers", "Others",
    ]

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12, "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
_MONTH_ALT = "|".join(sorted(MONTHS.keys(), key=len, reverse=True))

# Everyday words that map onto the 17 canonical categories. Longest keyword
# wins when a question matches more than one entry.
CATEGORY_KEYWORDS = {
    "Income": ["income", "salary", "earning", "stipend", "wages", "payroll"],
    "Rent": ["rent", "landlord", "house rent", "hostel fee", "pg fee"],
    "EMI / Loans": ["emi", "loan", "installment", "instalment", "home loan",
                     "car loan", "personal loan"],
    "Insurance": ["insurance", "premium", "policy"],
    "Investments": ["investment", "invest", "mutual fund", "sip", "stocks",
                     "shares", "fixed deposit", "ppf", "nps"],
    "Subscriptions": ["subscriptions", "subscription", "netflix", "membership",
                       "memberships", "streaming"],
    "Food & Dining": ["food", "eating out", "restaurant", "restaurants",
                       "dining", "swiggy", "zomato", "cafe", "takeaway"],
    "Groceries": ["groceries", "grocery", "vegetables", "supermarket", "kirana"],
    "Transport": ["petrol", "fuel", "diesel", "cab", "taxi", "travel to work",
                   "commute", "transport", "fastag", "metro fare", "bus fare"],
    "Utilities": ["bills", "bill", "electricity", "recharge", "utility",
                   "utilities", "water bill", "gas bill", "broadband",
                   "phone bill"],
    "Shopping": ["shopping", "clothes", "clothing", "apparel"],
    "Health": ["health", "medical", "pharmacy", "medicine", "hospital",
               "doctor", "clinic"],
    "Education": ["education", "tuition", "course fee", "school fee",
                   "college fee", "exam fee"],
    "Entertainment": ["entertainment", "movie", "movies", "cinema", "gaming"],
    "Travel": ["travel", "trip", "vacation", "holiday", "flight", "hotel stay"],
    "Transfers": ["transfer", "transfers", "sent to", "p2p transfer"],
    "Others": ["miscellaneous", "others"],
}

_CREDIT_WORDS = ("earn", "earned", "earning", "salary", "income", "credited",
                  "received", "receipt")
_DEBIT_WORDS = ("spend", "spent", "spending", "expense", "expenses", "cost",
                 "paid", "bought", "purchase")
_DEBIT_DEFAULT_METRICS = {"sum", "average", "max", "min", "breakdown", "compare"}

_MERCHANT_STOPWORDS = {
    "how", "much", "did", "the", "for", "this", "that", "was", "are", "what",
    "show", "list", "give", "total", "amount", "have", "and", "you", "tell",
    "about", "all", "with", "spend", "spent", "last", "week", "weeks",
    "month", "months", "year", "years", "today", "between", "top",
    "categories", "category", "expenses", "expense", "transactions",
    "transaction", "many", "number", "average", "typical", "biggest",
    "largest", "smallest", "cheapest", "compare", "versus", "summary",
    "advice", "tips", "reduce", "save", "saving", "savings", "everything",
    "above", "below", "over", "under", "more", "less", "than", "doing",
    "rate", "make", "makes", "did", "since",
}


# --------------------------------------------------------------------------- #
#  Date-phrase parsing
# --------------------------------------------------------------------------- #
def _last_day(year, month):
    return date(year, month, calendar.monthrange(year, month)[1])


def _shift_months(d, n):
    month_index = d.month - 1 - n
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _this_month(today):
    start = today.replace(day=1)
    return start, _last_day(today.year, today.month), start.strftime("%B %Y")


def _last_month(today):
    y, m = today.year, today.month - 1
    if m == 0:
        y, m = y - 1, 12
    start = date(y, m, 1)
    return start, _last_day(y, m), start.strftime("%B %Y")


def _this_week(today):
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end, f"week of {start.strftime('%d %b %Y')}"


def _last_week(today):
    this_start = today - timedelta(days=today.weekday())
    start = this_start - timedelta(days=7)
    return start, start + timedelta(days=6), f"week of {start.strftime('%d %b %Y')}"


def _this_year(today):
    return date(today.year, 1, 1), date(today.year, 12, 31), str(today.year)


def _last_year(today):
    y = today.year - 1
    return date(y, 1, 1), date(y, 12, 31), str(y)


def _yesterday(today):
    d = today - timedelta(days=1)
    return d, d, d.strftime("%d %b %Y")


def _today_range(today):
    return today, today, today.strftime("%d %b %Y")


def _month_year_for(month_num, today, explicit_year):
    if explicit_year:
        return int(explicit_year)
    return today.year if month_num <= today.month else today.year - 1


def _in_month(match, today):
    name, year_str = match.group(1), match.group(2)
    month_num = MONTHS[name]
    year = _month_year_for(month_num, today, year_str)
    start = date(year, month_num, 1)
    return start, _last_day(year, month_num), start.strftime("%B %Y")


def _find_simple_periods(q, today):
    """Locate each simple period phrase, in the order it appears in the text."""
    detectors = [
        (r"\bthis\s+month\b", lambda m: _this_month(today)),
        (r"\blast\s+month\b", lambda m: _last_month(today)),
        (r"\bthis\s+week\b", lambda m: _this_week(today)),
        (r"\blast\s+week\b", lambda m: _last_week(today)),
        (r"\bthis\s+year\b", lambda m: _this_year(today)),
        (r"\blast\s+year\b", lambda m: _last_year(today)),
        (r"\byesterday\b", lambda m: _yesterday(today)),
        (r"\btoday\b", lambda m: _today_range(today)),
        (r"\bin\s+(" + _MONTH_ALT + r")\b(?:\s+(\d{4}))?", lambda m: _in_month(m, today)),
    ]
    found = []
    for pattern, handler in detectors:
        for m in re.finditer(pattern, q):
            found.append((m.start(), handler(m)))
    found.sort(key=lambda x: x[0])
    return [item for _, item in found]


def _parse_between_dates(q, today):
    pattern = (r"between\s+(\d{1,2})(?:st|nd|rd|th)?\s+(" + _MONTH_ALT +
               r")(?:\s+(\d{4}))?\s+(?:and|to)\s+(\d{1,2})(?:st|nd|rd|th)?\s+(" +
               _MONTH_ALT + r")(?:\s+(\d{4}))?")
    m = re.search(pattern, q)
    if not m:
        return None
    d1, mo1, y1, d2, mo2, y2 = m.groups()
    month1, month2 = MONTHS[mo1], MONTHS[mo2]
    year1 = _month_year_for(month1, today, y1)
    year2 = int(y2) if y2 else year1
    start = date(year1, month1, int(d1))
    end = date(year2, month2, int(d2))
    label = f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"
    return start, end, label


def _parse_financial_year(q, today):
    m = re.search(r"fy\s*'?(\d{4})\s*[-/]\s*(\d{2,4})", q)
    if m:
        y1 = int(m.group(1))
        y2_str = m.group(2)
        y2 = int(y2_str) if len(y2_str) == 4 else (y1 - y1 % 100) + int(y2_str)
        return date(y1, 4, 1), date(y2, 3, 31), f"FY {y1}-{str(y2)[-2:]}"
    if "this financial year" in q or "this fy" in q:
        y = today.year if today.month >= 4 else today.year - 1
        return date(y, 4, 1), date(y + 1, 3, 31), f"FY {y}-{str(y + 1)[-2:]}"
    if "last financial year" in q or "last fy" in q:
        y = (today.year if today.month >= 4 else today.year - 1) - 1
        return date(y, 4, 1), date(y + 1, 3, 31), f"FY {y}-{str(y + 1)[-2:]}"
    return None


def _parse_quarter(q, today):
    m = re.search(r"\bq([1-4])\b", q)
    if not m:
        return None
    qn = int(m.group(1))
    fy_start_year = today.year if today.month >= 4 else today.year - 1
    spans = {1: ((4, 1), (6, 30)), 2: ((7, 1), (9, 30)),
             3: ((10, 1), (12, 31)), 4: ((1, 1), (3, 31))}
    (mo_s, d_s), (mo_e, d_e) = spans[qn]
    year = fy_start_year if qn != 4 else fy_start_year + 1
    start, end = date(year, mo_s, d_s), date(year, mo_e, d_e)
    label = f"Q{qn} FY{str(fy_start_year)[-2:]}-{str(fy_start_year + 1)[-2:]}"
    return start, end, label


def _parse_last_n_months(q, today):
    m = re.search(r"(?:last|past)\s+(\d+)\s+months?", q)
    if not m:
        return None
    n = int(m.group(1))
    start = _shift_months(today, n - 1).replace(day=1)
    return start, today, f"last {n} months"


def _parse_since(q, today):
    m = re.search(r"since\s+(" + _MONTH_ALT + r")(?:\s+(\d{4}))?", q)
    if not m:
        return None
    name, year_str = m.groups()
    month = MONTHS[name]
    year = _month_year_for(month, today, year_str)
    start = date(year, month, 1)
    return start, today, f"since {start.strftime('%B %Y')}"


def _parse_period(q, today):
    for parser in (_parse_between_dates, _parse_financial_year, _parse_quarter,
                   _parse_last_n_months, _parse_since):
        hit = parser(q, today)
        if hit:
            start, end, label = hit
            return start, end, label, None

    phrases = _find_simple_periods(q, today)
    if len(phrases) >= 2:
        (s1, e1, l1), (s2, e2, l2) = phrases[0], phrases[1]
        return s1, e1, l1, {"start": s2, "end": e2, "label": l2}
    if len(phrases) == 1:
        s, e, l = phrases[0]
        return s, e, l, None
    return None, None, "all time", None


# --------------------------------------------------------------------------- #
#  Metric, category, merchant, amount, txn_type detection
# --------------------------------------------------------------------------- #
def _match_metric(q):
    m = re.search(r"top\s+(\d+)", q)
    if m:
        return "breakdown", int(m.group(1))
    if any(p in q for p in (" vs ", "versus", "compare")):
        return "compare", None
    if any(p in q for p in ("how am i doing", "savings rate", "overview",
                            "how is my spending", "how's my spending")):
        return "summary", None
    if any(p in q for p in ("how can i save", "how do i save", "how to save",
                            "save money", "advice", "tips", "reduce my spending",
                            "reduce spending")):
        return "advice", None
    if any(p in q for p in ("breakdown", "where did my money go",
                            "where does my money go", "split")):
        return "breakdown", None
    if any(p in q for p in ("how many", "number of", "count of")):
        return "count", None
    if any(p in q for p in ("average", "typical", "per transaction", "avg")):
        return "average", None
    if any(p in q for p in ("biggest", "largest", "highest", "most expensive",
                            "maximum")):
        return "max", None
    if any(p in q for p in ("smallest", "cheapest", "lowest", "minimum")):
        return "min", None
    if any(p in q for p in ("how much", "total", "spend", "spent", "earn",
                            "earned", "cost of", "paid")):
        return "sum", None
    if any(p in q for p in ("list", "show", "which", "what did i", "what are",
                            "everything")):
        return "list", None
    return "unknown", None


def _match_category(q, known_categories):
    cats = known_categories or CATEGORIES
    best_cat, best_len = None, 0
    for cat in cats:
        if cat.lower() in q and len(cat) > best_len:
            best_cat, best_len = cat, len(cat)
        for kw in CATEGORY_KEYWORDS.get(cat, []):
            if kw in q and len(kw) > best_len:
                best_cat, best_len = cat, len(kw)
    return best_cat


def _match_merchant(q, known_merchants):
    if not known_merchants:
        return None
    q_tokens = set(re.findall(r"[a-z0-9]{3,}", q)) - _MERCHANT_STOPWORDS
    best_term, best_len = None, 0
    for cand in known_merchants:
        if not cand:
            continue
        cand_tokens = re.findall(r"[a-z0-9]{3,}", cand.lower())
        if not cand_tokens:
            continue
        if len(cand_tokens) >= 2:
            phrase = " ".join(cand_tokens)
            if phrase in q and len(phrase) > best_len:
                best_term, best_len = phrase, len(phrase)
        for t in cand_tokens:
            if t in q_tokens and len(t) > best_len:
                best_term, best_len = t, len(t)
    return best_term.title() if best_term else None


def _match_txn_type(q, metric):
    if any(w in q for w in _CREDIT_WORDS):
        return "credit"
    if any(w in q for w in _DEBIT_WORDS):
        return "debit"
    if metric in _DEBIT_DEFAULT_METRICS:
        return "debit"
    return None


def _match_amount_range(q):
    min_amt = max_amt = None
    m = re.search(r"(?:above|over|more than|greater than|exceeding)\s*(?:rs\.?)?\s*([\d,]+)", q)
    if m:
        min_amt = float(m.group(1).replace(",", ""))
    m = re.search(r"(?:below|under|less than)\s*(?:rs\.?)?\s*([\d,]+)", q)
    if m:
        max_amt = float(m.group(1).replace(",", ""))
    if min_amt is None and max_amt is None:
        m = re.search(r"between\s*(?:rs\.?)?\s*([\d,]+)\s*(?:and|to|-)\s*(?:rs\.?)?\s*([\d,]+)", q)
        if m:
            a, b = float(m.group(1).replace(",", "")), float(m.group(2).replace(",", ""))
            min_amt, max_amt = min(a, b), max(a, b)
    return min_amt, max_amt


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
def parse_query(question, today=None, known_categories=None, known_merchants=None) -> dict:
    today = today or date.today()
    raw = question or ""
    q = raw.lower().strip()

    start, end, period_label, compare_to = _parse_period(q, today)
    metric, top_n = _match_metric(q)
    category = _match_category(q, known_categories)
    merchant = _match_merchant(q, known_merchants)
    txn_type = _match_txn_type(q, metric)
    min_amount, max_amount = _match_amount_range(q)

    return {
        "metric": metric, "txn_type": txn_type, "category": category,
        "merchant": merchant, "start": start, "end": end,
        "period_label": period_label, "top_n": top_n, "compare_to": compare_to,
        "raw": raw, "min_amount": min_amount, "max_amount": max_amount,
    }


def _merchant_condition(term):
    like = f"%{term}%"
    conditions = [Transaction.description.ilike(like)]
    if hasattr(Transaction, "raw_description"):
        conditions.append(Transaction.raw_description.ilike(like))
    if hasattr(Transaction, "merchant"):
        conditions.append(Transaction.merchant.ilike(like))
    return or_(*conditions)


def _scoped_query(user_id, spec):
    q = Transaction.query.filter_by(user_id=user_id)
    if spec.get("txn_type"):
        q = q.filter(Transaction.txn_type == spec["txn_type"])
    if spec.get("category"):
        q = q.filter(Transaction.category == spec["category"])
    if spec.get("merchant"):
        q = q.filter(_merchant_condition(spec["merchant"]))
    if spec.get("start"):
        q = q.filter(Transaction.date >= spec["start"])
    if spec.get("end"):
        q = q.filter(Transaction.date <= spec["end"])
    if spec.get("min_amount") is not None:
        q = q.filter(Transaction.amount >= spec["min_amount"])
    if spec.get("max_amount") is not None:
        q = q.filter(Transaction.amount <= spec["max_amount"])
    return q


def _empty_result(spec):
    return {"kind": spec.get("metric", "unknown"), "total": 0.0, "count": 0,
            "average": 0.0, "rows": [], "breakdown": [],
            "label": spec.get("period_label", "all time"), "compare": None,
            "matched": False}


def execute(user_id, spec) -> dict:
    metric = spec.get("metric", "unknown")
    result = _empty_result(spec)
    if metric in ("unknown", "advice"):
        return result

    query = _scoped_query(user_id, spec)

    if metric == "sum":
        rows = query.all()
        total = sum(r.amount for r in rows)
        result.update(total=round(total, 2), count=len(rows), rows=rows[:50], matched=True)

    elif metric == "count":
        result.update(count=query.count(), matched=True)

    elif metric == "average":
        rows = query.all()
        total = sum(r.amount for r in rows)
        avg = total / len(rows) if rows else 0.0
        result.update(total=round(total, 2), count=len(rows), average=round(avg, 2), matched=True)

    elif metric == "max":
        row = query.order_by(Transaction.amount.desc()).first()
        if row:
            result.update(total=round(row.amount, 2), count=1, rows=[row])
        result["matched"] = True

    elif metric == "min":
        row = query.order_by(Transaction.amount.asc()).first()
        if row:
            result.update(total=round(row.amount, 2), count=1, rows=[row])
        result["matched"] = True

    elif metric == "list":
        rows = query.all()
        total = sum(r.amount for r in rows)
        ordered = sorted(rows, key=lambda r: r.date or date.min, reverse=True)
        result.update(rows=ordered[:50], count=len(rows), total=round(total, 2), matched=True)

    elif metric == "breakdown":
        rows = query.all()
        totals, counts = {}, {}
        for r in rows:
            key = r.category or "Others"
            totals[key] = totals.get(key, 0.0) + r.amount
            counts[key] = counts.get(key, 0) + 1
        breakdown = sorted(((c, round(a, 2), counts[c]) for c, a in totals.items()),
                           key=lambda x: x[1], reverse=True)
        top_n = spec.get("top_n")
        if top_n:
            breakdown = breakdown[:top_n]
        result.update(breakdown=breakdown, total=round(sum(totals.values()), 2),
                      count=len(rows), matched=True)

    elif metric == "summary":
        rows = _scoped_query(user_id, {**spec, "txn_type": None}).all()
        income = sum(r.amount for r in rows if r.txn_type == "credit")
        expense = sum(r.amount for r in rows if r.txn_type == "debit")
        n_income = sum(1 for r in rows if r.txn_type == "credit")
        n_expense = sum(1 for r in rows if r.txn_type == "debit")
        savings = income - expense
        rate = (savings / income * 100) if income else 0.0
        result.update(
            breakdown=[("Income", round(income, 2), n_income),
                      ("Expense", round(expense, 2), n_expense)],
            total=round(savings, 2), average=round(rate, 2),
            count=len(rows), matched=True,
        )

    elif metric == "compare":
        primary_rows = query.all()
        total1 = sum(r.amount for r in primary_rows)
        ct = spec.get("compare_to") or {}
        spec2 = dict(spec)
        spec2["start"], spec2["end"] = ct.get("start"), ct.get("end")
        second_rows = _scoped_query(user_id, spec2).all()
        total2 = sum(r.amount for r in second_rows)
        delta = total2 - total1
        pct = (delta / total1 * 100) if total1 else (100.0 if total2 else 0.0)
        result["compare"] = {
            "first": {"label": spec.get("period_label"), "total": round(total1, 2),
                      "count": len(primary_rows)},
            "second": {"label": ct.get("label"), "total": round(total2, 2),
                      "count": len(second_rows)},
            "delta": round(delta, 2), "pct_change": round(pct, 1),
        }
        result.update(total=round(total1, 2), count=len(primary_rows), matched=True)

    return result
