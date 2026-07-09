# SmartEdit AI — Technical Approach & Design Document

**Project:** SmartEdit AI — An Intelligent Personal Finance Web App for Indian Salaried Users
**Client:** Shyam Sundar
**Document purpose:** Define and verify the full technical approach before implementation.
**Date:** June 2026

---

## 1. Goal in one line

Upload a bank statement (PDF/CSV) or add entries manually → the system reads, classifies, and stores every transaction → the dashboard shows where the money went → an AI chatbot + advisory answers questions and suggests savings, grounded in the user's *actual* data.

---

## 2. Chosen stack (decided with client)

| Layer | Choice | Why |
|---|---|---|
| Backend | **Python + Flask** | Simple, easy to demo and explain in a viva; pairs naturally with PDF/NLP libraries |
| Database | **SQLite (SQLAlchemy ORM)** | Zero-config, single file, perfect for a single-machine demo; easy to migrate to Postgres later |
| Frontend | **Server-rendered HTML + vanilla JS + Chart.js** | Minimalist white/blue theme, no build step, reliable |
| Statement parsing | **pdfplumber** (PDF) + **pandas** (CSV) | Handles tabular extraction across Indian bank layouts |
| Classification | **Rule-based keyword matching + fallback** | Fast, interpretable, India-aware (UPI/NEFT/NACH/POS) |
| AI advisory + chat | **Gemini API now → Ollama later** (one config switch) | Free tier, strong reasoning; modular `LLMProvider` abstraction |
| RAG retrieval | **sentence-transformers (all-MiniLM-L6-v2) + cosine similarity** | Free, offline, matches the client's sketch (embed → symmetric search → retrieve) |

**Design principle:** every external dependency (Gemini, embeddings) has a graceful **offline fallback** so the app always runs in a demo, even with no API key and no internet.

---

## 3. Architecture (6 modules)

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (white/blue UI)                  │
│  Login · Register · Dashboard · Add · View · Tracker · Chat  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────────┐
│                       Flask Application                       │
│                                                              │
│  1. Auth (register/login, session, password hashing)         │
│  2. Statement Parser  (pdfplumber / pandas)                  │
│  3. Transaction Classifier  (rule engine → category)         │
│  4. Analytics  (monthly summary, category split, trends)     │
│  5. AI Advisory  (LLMProvider → Gemini/Ollama + fallback)    │
│  6. RAG Chatbot  (embeddings + cosine retrieval → LLM)       │
└───────────────────────────┬─────────────────────────────────┘
                            │ SQLAlchemy
┌───────────────────────────▼─────────────────────────────────┐
│                     SQLite database                          │
│   users · transactions · embeddings · chat_history          │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Database schema

**users**: id, name, email (unique), password_hash, created_at
**transactions**: id, user_id (FK), date, description, raw_description, amount, txn_type (credit/debit), category, source (upload/manual), created_at
**embeddings**: id, transaction_id (FK), vector (BLOB / JSON of floats) — used by the RAG search
**chat_history**: id, user_id (FK), role (user/assistant), message, created_at

---

## 5. Statement parsing pipeline

1. Detect file type by extension (`.pdf` / `.csv`).
2. **CSV**: read with pandas; auto-map common column names (Date, Description/Narration/Particulars, Debit, Credit, Amount, Withdrawal, Deposit).
3. **PDF**: `pdfplumber` extracts tables page by page; rows are normalised into (date, description, amount, type).
4. Normalise: parse dates (multiple Indian formats), coerce amounts, infer credit vs debit from Debit/Credit columns or sign.
5. Each parsed row → classifier → category → saved to `transactions` → embedded for RAG.

**Edge cases handled:** mixed date formats, comma thousands separators (₹1,23,456.00), blank rows, multi-line descriptions, separate debit/credit columns vs single signed amount.

---

## 6. Transaction classification (India-aware)

Hybrid rule engine over the raw description string. Keyword → category map covering:
Food (SWIGGY, ZOMATO, restaurant), Groceries (BIGBASKET, RELIANCE, DMART), Transport (UBER, OLA, IRCTC, FUEL), Subscriptions (NETFLIX, PRIME, SPOTIFY, HOTSTAR), Utilities (ELECTRICITY, RECHARGE, BROADBAND), Shopping (AMAZON, FLIPKART, MYNTRA), EMI/Loans (EMI, LOAN, ACH), Insurance (LIC, PREMIUM, POLICY), Rent (RENT), Transfers (UPI, NEFT, IMPS to person), Income (SALARY, CREDIT, INTEREST), Health, Education, Entertainment, Others.
Method markers (UPI/NEFT/NACH/POS/IMPS) are detected and stored for reporting. Unknown strings → "Others" and are flagged for the (future) ML classifier. Users can re-categorise manually in the View tab.

---

## 7. AI advisory

`advisor.generate_advice(summary)` builds a chain-of-thought prompt from the categorised monthly summary + month-on-month trend and calls the active `LLMProvider`.
- **Gemini**: `gemini-1.5-flash` via REST, key from `GEMINI_API_KEY`.
- **Ollama** (later): same interface, `llama3`/`mistral` at `localhost:11434`.
- **Fallback** (no key/offline): a deterministic rule-based advisor that still produces specific rupee-level suggestions (top category, discretionary cap, savings-rate nudge) so demos never break.

---

## 8. RAG chatbot (matches client's sketch)

```
User question ──embed──> query vector
                              │ cosine similarity (symmetric search)
Stored transactions ──embed──> transaction vectors
                              ▼
                  top-K most relevant transactions
                              │
        (+ aggregate stats e.g. SUM where merchant LIKE 'AMAZON')
                              ▼
                 context injected into LLM prompt
                              ▼
                    grounded natural-language answer
```

- Embeddings: `all-MiniLM-L6-v2` (384-dim), computed once per transaction and cached in `embeddings`.
- Retrieval: cosine similarity between query vector and all transaction vectors → top-K.
- **Hybrid grounding:** for quantitative questions ("how much on Amazon last month") we also run a direct SQL aggregate so numbers are exact, not hallucinated. Retrieved rows + aggregates → LLM → answer.
- **Fallback:** if embeddings/LLM unavailable, keyword SQL search answers factual queries directly.

---

## 9. Feasibility check ✅

- **Flask + SQLite + pdfplumber + pandas + sentence-transformers** — all mature, pip-installable, run locally. ✔
- **Gemini free tier** supports text generation + embeddings via REST. ✔
- **Offline fallbacks** mean the app is fully demoable with no API key. ✔
- **Cosine-similarity RAG** over a few hundred transactions is instant on CPU. ✔
- **Migration to Ollama** = swap one provider class; interface unchanged. ✔

Conclusion: the design is feasible, minimalist, and matches every requirement (upload PDF/CSV, manual add, categorise, dashboard, tracker, RAG chat, white/blue UI). Proceeding to implementation.

---

## 10. Pages delivered

Login · Register · Dashboard (this-month income/expense/savings + category chart + recent) · Add Entry (credit/debit manual) · View / Database (filterable transaction table, editable category) · Tracker (daily/weekly/monthly credit vs debit charts) · Chat (RAG assistant).
