"""LLM provider abstraction + financial advisory.

One interface, three backends:
  - gemini   : Google Gemini REST API (build-now phase)
  - ollama   : local Llama/Mistral via Ollama (final privacy-first phase)
  - fallback : deterministic rule-based advisor (always works, no key/internet)

Switch with LLM_PROVIDER in .env. Migrating to Ollama later = no code change here.
"""
import json
import requests
from config import Config


# --------------------------------------------------------------------------- #
#  Generic LLM call
# --------------------------------------------------------------------------- #
def llm_generate(prompt: str, system: str = "") -> str:
    provider = Config.LLM_PROVIDER

    if provider == "gemini" and Config.GEMINI_API_KEY:
        try:
            return _gemini(prompt, system)
        except Exception as e:
            return _fallback_note(f"(Gemini unavailable: {e})")

    if provider == "ollama":
        try:
            return _ollama(prompt, system)
        except Exception as e:
            return _fallback_note(f"(Ollama unavailable: {e})")

    return ""  # signal caller to use rule-based fallback


def _gemini(prompt, system):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{Config.GEMINI_MODEL}:generateContent?key={Config.GEMINI_API_KEY}")
    full = (system + "\n\n" + prompt) if system else prompt
    payload = {"contents": [{"parts": [{"text": full}]}]}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _ollama(prompt, system):
    r = requests.post(
        f"{Config.OLLAMA_URL}/api/generate",
        json={"model": Config.OLLAMA_MODEL, "prompt": prompt,
              "system": system, "stream": False},
        timeout=120,
    )
    r.raise_for_status()
    return r.json().get("response", "").strip()


def _fallback_note(msg):
    return ""  # empty -> caller falls back to rules


# --------------------------------------------------------------------------- #
#  Advisory
# --------------------------------------------------------------------------- #
ADVISOR_SYSTEM = (
    "You are SmartEdit AI, a personal finance advisor for Indian salaried users. "
    "You give specific, grounded, rupee-level suggestions based ONLY on the data "
    "provided. Reason step by step, then give 3-4 concrete, actionable tips. "
    "Use Rs. for rupees. Be concise and practical. Do not invent numbers."
)


def generate_advice(summary: dict) -> str:
    """summary: {income, expense, savings, savings_rate, top_categories[(cat,amt)], month}"""
    prompt = _advice_prompt(summary)
    out = llm_generate(prompt, ADVISOR_SYSTEM)
    if out:
        return out
    return rule_based_advice(summary)


def _advice_prompt(s):
    cats = "\n".join(f"  - {c}: Rs.{a:,.0f}" for c, a in s.get("top_categories", []))
    return (
        f"Here is the user's finance summary for {s.get('month', 'this month')}:\n"
        f"Total income: Rs.{s.get('income', 0):,.0f}\n"
        f"Total expense: Rs.{s.get('expense', 0):,.0f}\n"
        f"Savings: Rs.{s.get('savings', 0):,.0f} "
        f"(savings rate {s.get('savings_rate', 0):.0f}%)\n"
        f"Top spending categories:\n{cats}\n\n"
        "Analyse this and give specific savings advice with rupee amounts."
    )


def rule_based_advice(s) -> str:
    income = s.get("income", 0)
    expense = s.get("expense", 0)
    savings = s.get("savings", 0)
    rate = s.get("savings_rate", 0)
    cats = s.get("top_categories", [])
    lines = [f"**Summary for {s.get('month', 'this month')}**",
             f"You earned Rs.{income:,.0f} and spent Rs.{expense:,.0f}, "
             f"saving Rs.{savings:,.0f} ({rate:.0f}% of income).", ""]

    if rate < 0:
        lines.append("⚠️ You spent more than you earned this month. The priority is to "
                     "bring expenses below income before anything else.")
    elif rate < 20:
        lines.append("Your savings rate is below the 20% healthy benchmark. Small, "
                     "targeted cuts can close the gap.")
    else:
        lines.append("Good savings rate. Consider directing the surplus into an SIP or RD.")
    lines.append("")
    lines.append("**Where to act:**")

    if cats:
        top_cat, top_amt = cats[0]
        cut = top_amt * 0.20
        lines.append(f"• Your biggest category is **{top_cat}** at Rs.{top_amt:,.0f}. "
                     f"Trimming it by 20% would free about Rs.{cut:,.0f}/month.")
    for c, a in cats[1:3]:
        if c in ("Food & Dining", "Subscriptions", "Shopping", "Entertainment"):
            lines.append(f"• **{c}** (Rs.{a:,.0f}) is discretionary — capping it is the "
                         f"easiest quick win.")
    target = income * 0.20
    if savings < target and income:
        lines.append(f"• To hit a 20% savings rate you'd need to save Rs.{target:,.0f}; "
                     f"you're Rs.{max(0, target - savings):,.0f} short.")
    lines.append("")
    lines.append("_Tip: set up an automatic transfer to savings on salary day so you save "
                 "before you spend._")
    return "\n".join(lines)
