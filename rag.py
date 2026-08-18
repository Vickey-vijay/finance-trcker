"""Retrieval-augmented chatbot.

Every question is first tried as a structured query: `nlq.parse_query` reads
the question, `nlq.execute` runs a real SQLAlchemy aggregate scoped to the
user, and that is where every rupee figure in an answer originates. Semantic
search (sentence-transformer embeddings, cosine similarity, cached as JSON in
SQLite) only supplies supporting transactions for context, and only takes
over the whole answer when the question cannot be turned into a query. The
language model's sole job is to restate an already-computed fact in a more
natural sentence; a guard inspects its reply and discards it in favour of the
deterministic sentence whenever it invents or recomputes a number.
"""
import json
import math
import re
from datetime import date

from models import db, Transaction, Embedding
from config import Config
import advisor
import llm_local
import nlq
from nlq import CATEGORIES

try:
    import numpy as _np
    _NUMPY_OK = True
except Exception:
    _NUMPY_OK = False

# --------------------------------------------------------------------------- #
#  Embedding model (lazy-loaded; optional dependency)
# --------------------------------------------------------------------------- #
_model = None
_MODEL_OK = None


def _get_model():
    global _model, _MODEL_OK
    if _MODEL_OK is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            _MODEL_OK = True
        except Exception:
            _MODEL_OK = False
    return _model


def embed_text(text: str):
    model = _get_model()
    if not model:
        return None
    vec = model.encode(text or "", normalize_embeddings=True)
    return [float(x) for x in vec]


def index_transaction(txn) -> None:
    """Compute and store the embedding for one transaction."""
    parts = [txn.description or "", txn.category or "", txn.txn_type or ""]
    if txn.amount is not None:
        parts.append(f"Rs.{txn.amount:,.0f}")
    merchant = getattr(txn, "merchant", None)
    if merchant:
        parts.append(merchant)
    vec = embed_text(" ".join(p for p in parts if p))
    if vec is None:
        return
    if txn.embedding:
        txn.embedding.vector = json.dumps(vec)
    else:
        db.session.add(Embedding(transaction_id=txn.id, vector=json.dumps(vec)))


def reindex_all(user_id) -> int:
    """Rebuild the embedding for every transaction of one user."""
    txns = Transaction.query.filter_by(user_id=user_id).all()
    for t in txns:
        index_transaction(t)
    db.session.commit()
    return len(txns)


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _cosine_batch(qvec, vectors):
    if _NUMPY_OK:
        q = _np.array(qvec, dtype=float)
        m = _np.array(vectors, dtype=float)
        qn = q / (float(_np.linalg.norm(q)) or 1.0)
        norms = _np.linalg.norm(m, axis=1, keepdims=True)
        mn = m / (norms + 1e-12)
        return (mn @ qn).tolist()
    return [_cosine(qvec, v) for v in vectors]


# --------------------------------------------------------------------------- #
#  Retrieval
# --------------------------------------------------------------------------- #
def retrieve(user_id, query, k=8):
    """Return the top-K transactions most relevant to the query text."""
    txns = Transaction.query.filter_by(user_id=user_id).all()
    qvec = embed_text(query)
    if qvec is None:
        return _keyword_retrieve(query, txns, k)

    scored_txns, vectors = [], []
    for t in txns:
        if t.embedding and t.embedding.vector:
            try:
                vectors.append(json.loads(t.embedding.vector))
                scored_txns.append(t)
            except Exception:
                continue
    if not vectors:
        return _keyword_retrieve(query, txns, k)

    scores = _cosine_batch(qvec, vectors)
    ranked = sorted(zip(scores, scored_txns), key=lambda x: x[0], reverse=True)
    return [t for _, t in ranked[:k]]


def _keyword_retrieve(query, txns, k):
    words = re.findall(r"[a-zA-Z]{3,}", (query or "").lower())
    scored = []
    for t in txns:
        text = f"{t.description} {t.category}".lower()
        score = sum(1 for w in words if w in text)
        if score:
            scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:k]]


def _known_merchants(user_id):
    txns = Transaction.query.filter_by(user_id=user_id).all()
    names = set()
    for t in txns:
        for val in (getattr(t, "merchant", None), t.description, t.raw_description):
            if val:
                names.add(val)
    return list(names)


# --------------------------------------------------------------------------- #
#  Deterministic sentence building (never depends on the LLM)
# --------------------------------------------------------------------------- #
def _period_suffix(spec):
    label = spec.get("period_label") or "all time"
    return "" if label == "all time" else f" in {label}"


def _deterministic_sentence(spec, result):
    kind = result["kind"]
    period_txt = _period_suffix(spec)
    subject = spec.get("merchant") or spec.get("category") or "that"

    if kind == "sum":
        if result["count"] == 0:
            return f"I could not find any transactions for {subject}{period_txt}."
        verb = "earned" if spec.get("txn_type") == "credit" else "spent"
        return (f"You {verb} Rs.{result['total']:,.0f} on {subject}{period_txt} "
               f"across {result['count']} transaction(s).")

    if kind == "count":
        return f"You made {result['count']} transaction(s){period_txt}."

    if kind == "average":
        if result["count"] == 0:
            return f"There is no data to average for {subject}{period_txt}."
        return (f"Your average transaction on {subject}{period_txt} is "
               f"Rs.{result['average']:,.0f} across {result['count']} transaction(s).")

    if kind == "max":
        if not result["rows"]:
            return f"I could not find a transaction for that{period_txt}."
        r = result["rows"][0]
        return (f"Your biggest expense{period_txt} was Rs.{r.amount:,.0f} "
               f"on {r.description} ({r.date}).")

    if kind == "min":
        if not result["rows"]:
            return f"I could not find a transaction for that{period_txt}."
        r = result["rows"][0]
        return (f"Your smallest transaction{period_txt} was Rs.{r.amount:,.0f} "
               f"on {r.description} ({r.date}).")

    if kind == "list":
        if not result["rows"]:
            return f"I could not find any transactions for that{period_txt}."
        lines = [f"Here are those transactions{period_txt}:"]
        for r in result["rows"][:10]:
            lines.append(f"- {r.date} - {r.description} - Rs.{r.amount:,.0f} ({r.category})")
        if result["count"] > 10:
            lines.append(f"...and {result['count'] - 10} more, totalling Rs.{result['total']:,.0f}.")
        return "\n".join(lines)

    if kind == "breakdown":
        if not result["breakdown"]:
            return f"There is no spending data to break down{period_txt}."
        lines = [f"Here is where your money went{period_txt}:"]
        for label, amt, cnt in result["breakdown"]:
            lines.append(f"- {label}: Rs.{amt:,.0f} ({cnt} transaction(s))")
        return "\n".join(lines)

    if kind == "compare":
        c = result["compare"]
        if not c:
            return "I could not compare those two periods."
        delta = c["delta"]
        direction = "more" if delta > 0 else "less" if delta < 0 else "the same as"
        return (f"You spent Rs.{c['first']['total']:,.0f} in {c['first']['label']} and "
               f"Rs.{c['second']['total']:,.0f} in {c['second']['label']} - that is "
               f"Rs.{abs(delta):,.0f} {direction} ({c['pct_change']:+.1f}%).")

    if kind == "summary":
        income = next((a for lbl, a, _ in result["breakdown"] if lbl == "Income"), 0.0)
        expense = next((a for lbl, a, _ in result["breakdown"] if lbl == "Expense"), 0.0)
        savings = income - expense
        rate = (savings / income * 100) if income else 0.0
        label = spec.get("period_label") or "this period"
        return (f"For {label}, you earned Rs.{income:,.0f} and spent Rs.{expense:,.0f}, "
               f"saving Rs.{savings:,.0f} ({rate:.0f}% of income).")

    return "I could not work out an answer to that from your transactions."


def _extract_numbers(result):
    numbers = {}
    if result.get("total") is not None:
        numbers["total"] = round(result["total"], 2)
    if result.get("average"):
        numbers["average"] = round(result["average"], 2)
    if result.get("count") is not None:
        numbers["count"] = result["count"]
    for label, amt, _cnt in result.get("breakdown", []):
        numbers[f"breakdown:{label}"] = round(amt, 2)
    if result.get("compare"):
        c = result["compare"]
        numbers["compare:first"] = c["first"]["total"]
        numbers["compare:second"] = c["second"]["total"]
        numbers["compare:delta"] = c["delta"]
    for r in result.get("rows", [])[:10]:
        numbers[f"row:{r.id}"] = round(r.amount, 2)
    return numbers


# --------------------------------------------------------------------------- #
#  LLM phrasing, with a guard against invented or recomputed figures
# --------------------------------------------------------------------------- #
CHAT_SYSTEM = (
    "You rewrite a given financial fact as one short sentence addressed to the user "
    "as 'you'. Never write in the first person. Do not add, remove, or recompute any "
    "number. Use Rs. for rupees. Reply with exactly one plain sentence and nothing else."
)

# Only single-figure answers are handed to the language model. Anything that
# lists rows or compares two periods is returned exactly as computed, because a
# small model reliably garbles multi-part results.
_PHRASEABLE_METRICS = {"sum", "count", "average"}

_LATEX_MARKERS = ("\\frac", "\\[", "\\text{", "$$", "\\times", "\\cdot")
_WORKING_PHRASES = ("calculat", "we need to", "step 1", "step-by-step",
                    "let's compute", "let us compute", "first, we")
# The model tends to answer as though it were the account holder, or to open
# with congratulations. Both read badly in a finance report, so they are refused.
_FIRST_PERSON = (" i spent", " i earned", " i paid", " i have spent", " i've spent",
                 "i spent ", "i earned ", "my spending", "my income", " we spent")
_CHATTY_OPENERS = ("congrat", "wow", "hey there", "great job", "well done",
                   "awesome", "fantastic", "amazing")


def _check_llm_reply(raw, numbers):
    """Return (accepted, reason). Rejects anything that looks computed or invented."""
    text = (raw or "").strip()
    if not text:
        return False, "empty"
    if any(marker in text for marker in _LATEX_MARKERS):
        return False, "latex"
    lowered = text.lower()
    if any(phrase in lowered for phrase in _WORKING_PHRASES):
        return False, "shows-working"
    if any(phrase in " " + lowered for phrase in _FIRST_PERSON):
        return False, "first-person"
    if any(lowered.startswith(opener) for opener in _CHATTY_OPENERS):
        return False, "chatty-opener"
    sentence_ends = len(re.findall(r"[.!?](?:\s|$)", text))
    if len(text) > 400 or sentence_ends > 3:
        return False, "too-long"

    allowed = {round(float(v)) for v in numbers.values() if isinstance(v, (int, float))}
    if not allowed:
        return True, "no-figures-to-check"
    mentioned = [int(tok.replace(",", "")) for tok in re.findall(r"\d[\d,]*", text)
                if len(tok.replace(",", "")) >= 2]
    if not any(m in allowed for m in mentioned):
        return False, "no-verified-figure"
    rupee_figures = re.findall(r"Rs\.?\s?([\d,]+(?:\.\d+)?)", text, re.IGNORECASE)
    for rf in rupee_figures:
        if round(float(rf.replace(",", ""))) not in allowed:
            return False, "invented-figure"
    return True, "ok"


def _llm_phrase(prompt, system):
    """Route through the local model with tuned, fast decoding when it is the
    configured provider; otherwise use the shared provider chain."""
    if Config.LLM_PROVIDER == "local":
        text = llm_local.generate(prompt, system=system, max_tokens=130,
                                  temperature=0.2, stop=["\n\n"])
        if text:
            return text
    return advisor.llm_generate(prompt, system)


def _phrase_with_llm(deterministic, numbers, result, spec=None):
    if not numbers or result.get("count", 0) == 0:
        return deterministic, "sql"
    if spec and spec.get("metric") not in _PHRASEABLE_METRICS:
        return deterministic, "sql"
    prompt = (
        f"FACT: {deterministic}\n\n"
        "Rewrite the FACT above as one sentence addressed to the user as 'you'. "
        "Do not add, remove, or recompute any number. Do not show any working."
    )
    raw = _llm_phrase(prompt, CHAT_SYSTEM)
    accepted, _reason = _check_llm_reply(raw, numbers)
    if accepted:
        return raw.strip(), "sql+llm"
    return deterministic, "sql"


# --------------------------------------------------------------------------- #
#  Advice and semantic fallback
# --------------------------------------------------------------------------- #
def _fallback_summary(user_id):
    from collections import defaultdict
    txns = Transaction.query.filter_by(user_id=user_id).all()
    months = sorted({(t.date.year, t.date.month) for t in txns if t.date}, reverse=True)
    target = months[0] if months else None
    income = expense = 0.0
    cats = defaultdict(float)
    for t in txns:
        if target and t.date and (t.date.year, t.date.month) == target:
            if t.txn_type == "credit":
                income += t.amount
            else:
                expense += t.amount
                cats[t.category or "Others"] += t.amount
    savings = income - expense
    label = date(target[0], target[1], 1).strftime("%B %Y") if target else "this month"
    return {"income": income, "expense": expense, "savings": savings,
            "savings_rate": (savings / income * 100) if income else 0.0,
            "top_categories": sorted(cats.items(), key=lambda x: x[1], reverse=True),
            "category_totals": dict(cats), "month": label,
            "start": None, "end": None, "txn_count": len(txns)}


def _advice_response(user_id, spec):
    try:
        from analytics import month_summary
        summary = month_summary(user_id)
    except Exception:
        summary = _fallback_summary(user_id)
    # generate_advice already refuses any wording whose rupee figures cannot be
    # traced back to this summary, so whichever it returns is grounded.
    grounded = advisor.rule_based_advice(summary, user_id=user_id)
    reply = advisor.generate_advice(summary, user_id=user_id)
    engine = "rules" if reply == grounded else "sql+llm"
    # The month's own totals, reported so a caller can check them the same way
    # it checks any other answer. Figures the advice derives from these, such as
    # an annualised standing charge, stay the responsibility of the guard above.
    numbers = {"income": round(summary.get("income", 0.0), 2),
               "expense": round(summary.get("expense", 0.0), 2),
               "savings": round(summary.get("savings", 0.0), 2)}
    for category, amount in summary.get("top_categories", []):
        numbers[f"category:{category}"] = round(amount, 2)
    return {"reply": reply or grounded, "engine": engine, "sources": [],
            "spec": spec, "numbers": numbers}


def _advice_figures_ok(text, summary):
    base = [summary.get("income", 0), summary.get("expense", 0),
            summary.get("savings", 0)]
    base += [amt for _cat, amt in summary.get("top_categories", [])]
    base.append(summary.get("income", 0) * 0.20)
    allowed = set()
    for value in base:
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        for fraction in (1.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.50):
            allowed.add(round(abs(value) * fraction))
    quoted = re.findall(r"Rs\.?\s?([\d,]+(?:\.\d+)?)", text, re.IGNORECASE)
    for q in quoted:
        amount = round(float(q.replace(",", "")))
        if amount and not any(abs(amount - a) <= max(1, a * 0.02) for a in allowed):
            return False
    return True


def _semantic_answer(sources):
    """Answer from retrieved rows alone, returning the figures it is allowed to quote.

    The third value is the same kind of ledger the structured path builds, so a
    caller can check every rupee figure in the reply against it either way.
    """
    if not sources:
        reply = ("I could not find transactions matching that. Try naming a category, "
                 "merchant, or time period, for example 'how much did I spend on food "
                 "last month'.")
        return reply, "rules", {}

    numbers = {f"row:{t.id}": round(t.amount, 2) for t in sources}
    lines = ["RELEVANT TRANSACTIONS:"]
    for t in sources:
        lines.append(f"- {t.date} | {t.description} | {t.txn_type} "
                     f"Rs.{t.amount:,.0f} | {t.category}")
    context = "\n".join(lines)
    prompt = (f"{context}\n\nUsing only the transactions above, answer in one or two "
             "sentences. Do not invent a rupee figure that is not listed above.")
    raw = _llm_phrase(prompt, CHAT_SYSTEM)
    accepted, _reason = _check_llm_reply(raw, numbers)
    if accepted:
        return raw.strip(), "semantic+llm", numbers

    listing = ["Here are the most relevant transactions I found:"]
    for t in sources[:6]:
        listing.append(f"- {t.date} - {t.description} - {t.txn_type} "
                       f"Rs.{t.amount:,.0f} ({t.category})")
    return "\n".join(listing), "rules", numbers


def _retry_latest_month(user_id, spec, result):
    """Re-run an empty period query against the newest month holding data."""
    from calendar import monthrange
    rows = (Transaction.query.filter_by(user_id=user_id)
            .filter(Transaction.date.isnot(None))
            .order_by(Transaction.date.desc()).first())
    if not rows or not rows.date:
        return spec, result, ""
    year, month = rows.date.year, rows.date.month
    if spec.get("start") and (spec["start"].year, spec["start"].month) == (year, month):
        return spec, result, ""
    asked = spec.get("period_label") or "that period"
    widened = dict(spec)
    widened["start"] = date(year, month, 1)
    widened["end"] = date(year, month, monthrange(year, month)[1])
    widened["period_label"] = date(year, month, 1).strftime("%B %Y")
    retried = nlq.execute(user_id, widened)
    if not retried["matched"] or retried.get("count", 0) == 0:
        return spec, result, ""
    prefix = (f"There is nothing recorded for {asked} yet, so here is "
              f"{widened['period_label']} instead. ")
    return widened, retried, prefix


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #
_MONEY_WORDS = re.compile(
    r"\b(spend|spent|spending|cost|costs|paid|pay|payment|payments|earn|earned|"
    r"earning|earnings|income|salary|save|saved|saving|savings|money|rupee|rupees|"
    r"rs|transaction|transactions|expense|expenses|expensive|budget|bank|account|"
    r"upi|bill|bills|balance|credit|debit|purchase|purchases|buy|bought|"
    r"subscription|subscriptions|cheap|afford|much|many|total)\b", re.I)


def _is_about_money(question, spec):
    """Whether the question refers to the user's finances at all.

    Retrieval always hands back its nearest few rows however unrelated the
    question is, so without this check something the application simply cannot
    answer comes back as a list of arbitrary transactions. Saying so plainly is
    more use to the reader than a confident-looking non-answer.
    """
    # A date on its own is not enough: "what is the weather today" parses to a
    # period without being a question about money at all.
    if spec.get("category") or spec.get("merchant"):
        return True
    return bool(_MONEY_WORDS.search(question or ""))


def answer_detailed(user_id, question, today=None) -> dict:
    known_merchants = _known_merchants(user_id)
    spec = nlq.parse_query(question, today=today, known_categories=list(CATEGORIES),
                           known_merchants=known_merchants)

    if spec["metric"] == "advice":
        return _advice_response(user_id, spec)

    result = nlq.execute(user_id, spec)
    prefix = ""

    # A question about "this month" asked before the month has any entries would
    # otherwise return nothing useful, so the search widens to the most recent
    # month that does hold transactions and the answer says so.
    if result["matched"] and result.get("count", 0) == 0 and spec.get("start"):
        spec, result, prefix = _retry_latest_month(user_id, spec, result)

    sources = retrieve(user_id, question, k=8)

    if result["matched"]:
        deterministic = _deterministic_sentence(spec, result)
        numbers = _extract_numbers(result)
        reply, engine = _phrase_with_llm(deterministic, numbers, result, spec)
        reply = prefix + reply
        source_rows = result["rows"] or sources
        return {"reply": reply, "engine": engine,
                "sources": [t.to_dict() for t in source_rows[:8]],
                "spec": spec, "numbers": numbers}

    if not _is_about_money(question, spec):
        reply = ("I could not answer that one. I only know about the transactions in "
                 "your own account, so try asking something like 'how much did I spend "
                 "on food last month' or 'what are my biggest expenses'.")
        return {"reply": reply, "engine": "rules", "sources": [],
                "spec": spec, "numbers": {}}

    reply, engine, numbers = _semantic_answer(sources)
    return {"reply": reply, "engine": engine,
            "sources": [t.to_dict() for t in sources[:8]],
            "spec": spec, "numbers": numbers}


def answer(user_id, question, today=None) -> str:
    return answer_detailed(user_id, question, today=today)["reply"]
