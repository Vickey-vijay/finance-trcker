# SmartEdit AI — Personal Finance Web App

An intelligent personal finance manager for Indian salaried users. Upload a bank
statement (PDF/CSV) or add entries manually — SmartEdit AI reads, classifies, and
stores every transaction, shows where your money went, and answers questions through
a RAG-powered AI chatbot.

## Features
- **Login / Register** — secure sessions, hashed passwords
- **Upload statements** — PDF (pdfplumber) and CSV (pandas), Indian bank layouts
- **Manual add** — log credit/debit with auto category detection
- **AI categorisation** — India-aware rule engine (UPI/NEFT/NACH/POS)
- **Dashboard** — month income/expense/savings, category doughnut, AI advisory
- **View / Database** — filterable table, re-categorise inline, delete
- **Tracker** — daily / monthly / weekday credit-vs-debit charts
- **AI Chat** — RAG over your transactions (sentence-transformers + cosine search)

## Quick start
```bash
cd SmartEditAI
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then add your GEMINI_API_KEY (optional)
python app.py
```
Open http://localhost:5000 , register, and upload `sample_data/sample_statement.csv`.

## AI configuration
Set `LLM_PROVIDER` in `.env`:
- `fallback` — works offline, no key (rule-based advisor + keyword chat)
- `gemini` — add `GEMINI_API_KEY` (free key: https://aistudio.google.com/app/apikey)
- `ollama` — run `ollama serve` locally (final privacy-first version)

The provider is the **only** thing that changes between the demo (Gemini) and the
final local (Ollama) build — all other code stays the same.

## Project structure
```
app.py          Flask routes + analytics
models.py       SQLAlchemy models (User, Transaction, Embedding, ChatHistory)
parser.py       PDF/CSV statement parsing
classifier.py   India-aware transaction categorisation
advisor.py      LLM provider abstraction + savings advisory
rag.py          Embeddings + cosine retrieval + chatbot
templates/      White/blue minimalist UI
static/css/     Theme
sample_data/    Example statement
docs/           Approach doc, diagrams, report, presentation, KT guide
```
