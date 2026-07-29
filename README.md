# SmartEdit AI — Personal Finance Web App

An intelligent personal finance manager for Indian salaried users. Upload a bank
statement (PDF, CSV or Excel) or add entries manually. SmartEdit AI reads every
transaction, works out what each cryptic narration actually was, shows where the
money went, models your salary and tax, and answers questions in plain English —
all on your own computer, with no account and no internet connection needed.

## Getting started on Windows

1. Double-click **`setup.bat`** and wait. It installs everything and downloads the
   language model that runs on this machine. This happens once and takes a few
   minutes, since about 1.5 GB is fetched.
2. Double-click **`run.bat`**. The browser opens at http://127.0.0.1:5000.
3. Register an account, then upload `sample_data/sample_statement.csv` to see the
   dashboard populate.

Nothing else needs configuring. There is no API key to obtain and no service to
sign up for.

## Features

- **Statement import** — CSV, Excel and PDF, across SBI, HDFC, ICICI, Axis, Kotak,
  PNB and other Indian layouts. Finds the real header row beneath the account
  preamble, handles `1,23,456.00`, resolves credit against debit from a Dr/Cr
  column, a suffix, the sign, or the movement in the running balance, and falls
  back to reading the text line by line when a PDF has no ruled table.
- **Transaction classification** — 17 categories from an India-aware rule engine,
  with a character n-gram model for narrations the rules cannot place. Payment
  rails are tested last, so a UPI payment to Swiggy is Food & Dining rather than
  an anonymous transfer.
- **Duplicate protection** — re-uploading a statement you already imported adds
  nothing, matched on a transaction fingerprint.
- **Dashboard** — income, expenses, savings and savings rate, a category
  breakdown, a month-on-month trend and a savings advisory.
- **View / Database** — filter, search, re-categorise inline, delete, export CSV.
  Rows the classifier was unsure about are flagged for review.
- **Tracker** — daily, monthly and weekday credit-against-debit charts.
- **Salary & Tax** — Indian CTC structure with Basic, HRA, PF, gratuity and
  professional tax; HRA exemption; both regimes for FY 2025-26 including the
  Section 87A rebate with marginal relief; and a side-by-side regime comparison.
- **Goals & Budget** — savings goals with a projection against your actual
  monthly surplus, and per-category monthly limits.
- **Insights** — deterministic observations that always quote real figures,
  including recurring commitments and what they cost you over a year.
- **Assistant** — ask questions such as "how much did I spend on groceries in
  June" or "what are my subscriptions" and get an exact answer.

## How the assistant keeps its numbers right

Every rupee figure comes from a SQL aggregate, never from the language model. A
question is parsed into a structured query using regular expressions, the query is
executed against your transactions, and only then is the finished sentence handed
to the model to be reworded. A guard discards the model's reply and uses the
original sentence if it quotes a figure that was never computed, shows arithmetic
working, or drifts in tone. Lists, breakdowns and period comparisons skip the
model entirely.

## Configuration

Settings live in `.env`, created for you by `setup.bat`. `LLM_PROVIDER` selects
how answers are phrased:

- `local` (default) — a quantised Qwen2.5 1.5B model running through llama.cpp on
  your CPU. Nothing leaves the machine.
- `ollama` — use a model served by a local Ollama instance instead.
- `gemini` — use the Gemini API, which requires your own key in `GEMINI_API_KEY`.
- `fallback` — skip the language model altogether. Answers and advice are still
  produced, from the deterministic engine.

`SMARTEDIT_DATABASE_URI` moves the data file somewhere other than the default
`smartedit.db` beside the application.

Every optional component degrades quietly. Without llama.cpp the built-in advisor
answers; without sentence-transformers the assistant retrieves by keyword; the
application still starts either way.

## Running the tests

```bash
.venv\Scripts\python.exe -m pytest
```

172 tests cover statement parsing, classification, the tax model, analytics,
question grounding, access control and every page. They run against a scratch
database and never touch `smartedit.db`.

## Project structure

```
app.py            Flask routes
models.py         SQLAlchemy models and in-place schema upgrade
parser.py         Statement parsing for CSV, Excel and PDF
classifier.py     Transaction categorisation, merchant naming, payment rails
analytics.py      Summaries, trends, recurring commitments, insights, budgets
salary.py         Indian CTC, HRA exemption, both tax regimes, goal projection
nlq.py            Questions to structured queries, executed as SQL
advisor.py        Provider chain and the rule-based savings advisory
rag.py            Embeddings, cosine retrieval and the grounded answer pipeline
llm_local.py      Quantised GGUF model on the CPU through llama.cpp
templates/        Server-rendered pages
static/           Theme and a local copy of Chart.js
sample_data/      Example statements in four bank layouts
data/             Classifier training corpus and persisted model
tools/            First-run setup and sample generation
tests/            Automated test suite
docs/             Diagrams, report, presentation and knowledge-transfer guide
```
