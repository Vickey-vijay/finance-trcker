"""LLM provider chain and financial advisory.

Four backends can answer a prompt: the local quantized model (llama.cpp), a
self-hosted Ollama server, Google Gemini, or nothing at all. Config.LLM_PROVIDER
picks which one is tried first; the remaining backends act as a fallback
chain. When every backend is unavailable or returns nothing, the caller
always has `rule_based_advice`, a deterministic advisor that never depends on
a network call or a model file.
"""
import re

import requests

from config import Config
import llm_local

ADVISOR_SYSTEM = (
    "You are SmartEdit AI, a personal finance advisor for Indian salaried users. "
    "You give specific, grounded, rupee-level suggestions based ONLY on the data "
    "provided. Give exactly 3 short, concrete tips, one line each, as a plain "
    "hyphen list. No markdown headings, no bold text, no code blocks. Use Rs. "
    "for rupees. Stay under 120 words in total. Do not invent numbers."
)

# The advice reply is longer than a one-line chat answer but still has to
# finish inside a demo-friendly time budget on CPU-only inference, so it is
# capped well below the general chat/advice ceiling in Config.CHAT_MAX_TOKENS.
_ADVICE_MAX_TOKENS = 220

_CHAINS = {
    "local": ["local", "ollama", "gemini"],
    "ollama": ["ollama", "local", "gemini"],
    "gemini": ["gemini", "local", "ollama"],
    "fallback": [],
}


def _chain_for(provider):
    return _CHAINS.get(provider, _CHAINS["local"])


# --------------------------------------------------------------------------- #
#  Provider calls
# --------------------------------------------------------------------------- #
def _try_local(prompt, system):
    max_tokens = min(Config.CHAT_MAX_TOKENS, _ADVICE_MAX_TOKENS)
    return llm_local.generate(prompt, system=system, max_tokens=max_tokens, temperature=0.3)


def _try_ollama(prompt, system):
    r = requests.post(
        f"{Config.OLLAMA_URL}/api/generate",
        json={"model": Config.OLLAMA_MODEL, "prompt": prompt,
              "system": system, "stream": False},
        timeout=Config.LLM_TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("response", "").strip()


def _try_gemini(prompt, system):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{Config.GEMINI_MODEL}:generateContent?key={Config.GEMINI_API_KEY}")
    full = (system + "\n\n" + prompt) if system else prompt
    payload = {"contents": [{"parts": [{"text": full}]}]}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _ollama_reachable():
    try:
        r = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False


_PROVIDER_FN = {"local": _try_local, "ollama": _try_ollama, "gemini": _try_gemini}


def llm_generate(prompt: str, system: str = "") -> str:
    """Walk the provider chain for Config.LLM_PROVIDER, return "" if all fail."""
    for name in _chain_for(Config.LLM_PROVIDER):
        if name == "gemini" and not Config.GEMINI_API_KEY:
            continue
        try:
            out = _PROVIDER_FN[name](prompt, system)
        except Exception:
            out = ""
        if out:
            return out
    return ""


def provider_status() -> dict:
    """Which backend is currently active, for the UI footer."""
    chain = _chain_for(Config.LLM_PROVIDER)
    active, detail = "rules", "Deterministic rule-based advisor (no LLM configured)."
    for name in chain:
        if name == "local" and llm_local.status()["ready"]:
            active, detail = "local", llm_local.status()["detail"]
            break
        if name == "ollama" and _ollama_reachable():
            active = "ollama"
            detail = f"Ollama model {Config.OLLAMA_MODEL} at {Config.OLLAMA_URL}"
            break
        if name == "gemini" and Config.GEMINI_API_KEY:
            active = "gemini"
            detail = f"Google Gemini ({Config.GEMINI_MODEL})"
            break
    return {"active": active, "detail": detail, "chain": chain}


# --------------------------------------------------------------------------- #
#  Advisory
# --------------------------------------------------------------------------- #
def generate_advice(summary: dict, user_id=None) -> str:
    """summary: the dict shape returned by analytics.month_summary/period_summary."""
    grounded = rule_based_advice(summary, user_id=user_id)
    out = llm_generate(_advice_prompt(summary), ADVISOR_SYSTEM)
    if out and advice_is_grounded(out, summary):
        return out
    return grounded


def advice_is_grounded(text, summary):
    """Check that every rupee figure quoted in the advice traces back to the
    user's own totals, or to one of the round percentage cuts the advisor is
    allowed to suggest. Anything else means the model has done its own sums."""
    base = [summary.get("income", 0), summary.get("expense", 0), summary.get("savings", 0)]
    base += [amount for _category, amount in summary.get("top_categories", [])]
    allowed = set()
    for value in base:
        try:
            value = abs(float(value))
        except (TypeError, ValueError):
            continue
        for fraction in (1.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.50, 0.75):
            allowed.add(round(value * fraction))
    for quoted in re.findall(r"Rs\.?\s?([\d,]+(?:\.\d+)?)", text, re.IGNORECASE):
        amount = round(float(quoted.replace(",", "")))
        if amount and not any(abs(amount - a) <= max(1, a * 0.02) for a in allowed):
            return False
    return True


def _advice_prompt(s):
    cats = "\n".join(f"  - {c}: Rs.{a:,.0f}" for c, a in s.get("top_categories", []))
    return (
        f"Here is the user's finance summary for {s.get('month', 'this period')}:\n"
        f"Total income: Rs.{s.get('income', 0):,.0f}\n"
        f"Total expense: Rs.{s.get('expense', 0):,.0f}\n"
        f"Savings: Rs.{s.get('savings', 0):,.0f} "
        f"(savings rate {s.get('savings_rate', 0):.0f}%)\n"
        f"Top spending categories:\n{cats}\n\n"
        "Analyse this and give specific savings advice with rupee amounts."
    )


def rule_based_advice(s, user_id=None) -> str:
    income = s.get("income", 0)
    expense = s.get("expense", 0)
    savings = s.get("savings", 0)
    rate = s.get("savings_rate", 0)
    cats = s.get("top_categories", [])
    lines = [f"Summary for {s.get('month', 'this period')}",
             f"You earned Rs.{income:,.0f} and spent Rs.{expense:,.0f}, "
             f"saving Rs.{savings:,.0f} ({rate:.0f}% of income).", ""]

    if income and expense > income:
        lines.append("You spent more than you earned this period. The priority is to "
                     "bring expenses below income before anything else.")
    elif rate < 20:
        lines.append("Your savings rate is below the 20% healthy benchmark. Small, "
                     "targeted cuts can close the gap.")
    else:
        lines.append("Good savings rate. Consider directing the surplus into an SIP or RD.")
    lines.append("")
    lines.append("Where to act:")

    if cats:
        top_cat, top_amt = cats[0]
        cut = top_amt * 0.20
        lines.append(f"- Your biggest category is {top_cat} at Rs.{top_amt:,.0f}. "
                     f"Trimming it by 20% would free about Rs.{cut:,.0f}/month.")
    for c, a in cats[1:3]:
        if c in ("Food & Dining", "Subscriptions", "Shopping", "Entertainment"):
            lines.append(f"- {c} (Rs.{a:,.0f}) is discretionary, so capping it is the "
                         f"easiest quick win.")

    subs_line = _subscriptions_line(user_id or s.get("user_id"))
    if subs_line:
        lines.append(subs_line)

    target = income * 0.20
    if savings < target and income:
        lines.append(f"- To hit a 20% savings rate you'd need to save Rs.{target:,.0f}; "
                     f"you're Rs.{max(0, target - savings):,.0f} short.")
    lines.append("")
    lines.append("Tip: set up an automatic transfer to savings on salary day so you save "
                 "before you spend.")
    return "\n".join(lines)


def _subscriptions_line(user_id):
    """Concrete rupee-per-year cost of the user's recurring subscriptions, when known."""
    if not user_id:
        return None
    try:
        from analytics import recurring_subscriptions
        subs = recurring_subscriptions(user_id)
    except Exception:
        return None
    monthly_subs = [x for x in subs if x.get("cadence") == "monthly"]
    if not monthly_subs:
        return None
    annual_total = sum(x.get("annual_cost", 0) for x in monthly_subs)
    names = ", ".join(x["merchant"] for x in monthly_subs[:4])
    return (f"- You are paying Rs.{annual_total:,.0f} a year for these "
           f"{len(monthly_subs)} subscriptions: {names}.")
