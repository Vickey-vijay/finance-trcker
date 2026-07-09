"""RAG chatbot.

Flow (matches the project sketch):
  question --embed--> query vector
  transactions --embed--> stored vectors
  cosine similarity (symmetric search) --> top-K relevant transactions
  + exact SQL aggregates for quantitative questions
  --> context injected into the LLM --> grounded answer

Embeddings: sentence-transformers (all-MiniLM-L6-v2), cached in the DB.
Falls back to keyword search + rule answers if the model/LLM is unavailable.
"""
import json
import math
import re
from datetime import date

from models import db, Transaction, Embedding
from advisor import llm_generate

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


def index_transaction(txn: Transaction):
    """Compute + store the embedding for one transaction."""
    vec = embed_text(f"{txn.description} {txn.category} {txn.txn_type} {txn.amount}")
    if vec is None:
        return
    if txn.embedding:
        txn.embedding.vector = json.dumps(vec)
    else:
        db.session.add(Embedding(transaction_id=txn.id, vector=json.dumps(vec)))


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


# --------------------------------------------------------------------------- #
#  Retrieval
# --------------------------------------------------------------------------- #
def retrieve(user_id: int, query: str, k: int = 8):
    """Return top-K transactions most relevant to the query (cosine search)."""
    qvec = embed_text(query)
    txns = Transaction.query.filter_by(user_id=user_id).all()
    if qvec is None:
        return _keyword_retrieve(query, txns, k)

    scored = []
    for t in txns:
        if t.embedding and t.embedding.vector:
            try:
                v = json.loads(t.embedding.vector)
                scored.append((_cosine(qvec, v), t))
            except Exception:
                continue
    if not scored:
        return _keyword_retrieve(query, txns, k)
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:k]]


def _keyword_retrieve(query, txns, k):
    words = [w for w in re.findall(r"[a-zA-Z]{3,}", query.lower())]
    scored = []
    for t in txns:
        text = f"{t.description} {t.category}".lower()
        score = sum(1 for w in words if w in text)
        if score:
            scored.append((score, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:k]]


# --------------------------------------------------------------------------- #
#  Exact aggregates (so numbers are never hallucinated)
# --------------------------------------------------------------------------- #
def keyword_aggregate(user_id: int, query: str):
    """If the user names a merchant/category, compute exact totals via SQL."""
    q = query.lower()
    tokens = re.findall(r"[a-zA-Z]{3,}", q)
    stop = {"how", "much", "did", "spend", "spent", "the", "for", "this", "last",
            "month", "what", "was", "are", "show", "list", "give", "total", "amount",
            "have", "and", "you", "tell", "about", "all", "with"}
    terms = [t for t in tokens if t not in stop]
    results = []
    for term in terms:
        rows = (Transaction.query
                .filter_by(user_id=user_id)
                .filter(Transaction.description.ilike(f"%{term}%"))
                .all())
        if rows:
            total = sum(r.amount for r in rows if r.txn_type == "debit")
            if total > 0:
                results.append((term, total, len(rows)))
    return results


# --------------------------------------------------------------------------- #
#  Chatbot answer
# --------------------------------------------------------------------------- #
def _quick_summary(user_id):
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
                cats[t.category] += t.amount
    savings = income - expense
    label = date(target[0], target[1], 1).strftime("%B %Y") if target else "this month"
    return {"income": income, "expense": expense, "savings": savings,
            "savings_rate": (savings / income * 100) if income else 0,
            "top_categories": sorted(cats.items(), key=lambda x: x[1], reverse=True),
            "month": label}


CHAT_SYSTEM = (
    "You are SmartEdit AI's finance assistant. Answer the user's question using ONLY "
    "the transaction context provided. Use exact figures from the AGGREGATES section "
    "when present. Use Rs. for rupees. If the data does not contain the answer, say so. "
    "Be concise and friendly."
)


def answer(user_id: int, question: str) -> str:
    txns = retrieve(user_id, question, k=8)
    aggs = keyword_aggregate(user_id, question)

    ctx_lines = []
    if aggs:
        ctx_lines.append("AGGREGATES (exact totals of debits matching your words):")
        for term, total, n in aggs:
            ctx_lines.append(f"  - '{term}': Rs.{total:,.0f} across {n} transaction(s)")
    ctx_lines.append("\nRELEVANT TRANSACTIONS:")
    for t in txns:
        ctx_lines.append(f"  - {t.date} | {t.description} | {t.txn_type} "
                         f"Rs.{t.amount:,.0f} | {t.category}")
    context = "\n".join(ctx_lines) if txns or aggs else "No matching transactions found."

    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    out = llm_generate(prompt, CHAT_SYSTEM)
    if out:
        return out
    return _rule_answer(user_id, question, txns, aggs)


def _rule_answer(user_id, question, txns, aggs):
    q = question.lower()
    if any(w in q for w in ("save", "saving", "budget", "advice", "reduce",
                            "cut", "spend less", "improve")):
        try:
            from advisor import rule_based_advice
            summary = _quick_summary(user_id)
            return rule_based_advice(summary)
        except Exception:
            pass
    if aggs:
        parts = []
        for term, total, n in aggs:
            parts.append(f"You spent **Rs.{total:,.0f}** on "
                         f"'{term}' across {n} transaction(s).")
        return " ".join(parts)
    if txns:
        lines = ["Here are the most relevant transactions I found:"]
        for t in txns[:6]:
            lines.append(f"• {t.date} — {t.description} — {t.txn_type} "
                         f"Rs.{t.amount:,.0f} ({t.category})")
        return "\n".join(lines)
    return ("I couldn't find transactions matching that. Try naming a merchant or "
            "category, e.g. 'how much did I spend on Amazon?'")
