# SmartEdit AI — Setup Guide (Windows)

This gets SmartEdit AI running on a fresh Windows machine. There is no account to
create, no API key to obtain, and no cloud service involved.

---

## 1. Prerequisite: Python

Python is the only thing you need to install yourself. Node.js is not required to
run the application.

| Software | Version | Why |
|----------|---------|-----|
| **Python** | **3.12.x** (tested on 3.12.10) | Runs the whole application |
| Git (optional) | latest | Only if cloning instead of downloading a ZIP |

### Install Python — pick one

**A. Command line (Windows 10/11):** open Command Prompt or PowerShell **as
Administrator** and run:

```
winget install -e --id Python.Python.3.12
```

Close and reopen the terminal afterwards so `python` is on PATH.

**B. Manual download:** get Python 3.12.10 from
https://www.python.org/downloads/release/python-31210/ and **tick "Add python.exe
to PATH"** on the installer's first screen.

Verify with:

```
python --version
```

You should see `Python 3.12.x`.

---

## 2. Get the project

**Option A — ZIP:**
1. Open the GitHub repository.
2. Click the green **`<> Code`** button, then **Download ZIP**.
3. Right-click the ZIP, choose **Extract All…**, and extract to a short path such
   as `C:\SmartEditAI`. Do not run anything from inside the ZIP itself.

**Option B — Git clone:**

```
git clone https://github.com/Vickey-vijay/finance-trcker.git
```

---

## 3. One-click setup

Inside the folder, **double-click `setup.bat`** and leave it running.

It will:
1. Find Python and create a private environment (`.venv`) for the application.
2. Install the core components.
3. Install the on-device AI engine from prebuilt packages, so no compiler or
   build tools are needed.
4. Download the language model that runs on this machine, showing a progress bar.
5. Prepare the settings file, the transaction classifier and the database.

**This downloads about 1.5 GB once**, most of it the language model, so allow a
few minutes on a reasonable connection. Every later run starts instantly.

If any optional component cannot be installed, setup says so and continues. The
application still works — it simply uses its built-in advisor and keyword search
instead of the on-device model.

---

## 4. Run the app

**Double-click `run.bat`.**

- The server starts and your browser opens at **http://127.0.0.1:5000**.
- Keep the black window open while you use the app.
- To stop, press **Ctrl + C** in that window, or close it.

---

## 5. First use

1. Click **Create an account** and register. The account exists only on this
   machine.
2. On the empty dashboard, upload a statement. Start with the included
   `sample_data/sample_statement.csv`, or try `hdfc_statement.csv`,
   `icici_statement.csv` or `axis_statement.csv` to see different bank layouts
   being read.
3. Work through **Dashboard → View/Database → Tracker → Insights**.
4. Enter your CTC on **Salary & Tax** to see your take-home and a comparison of
   the two tax regimes.
5. On **AI Chat**, try:
   - *How much did I spend on groceries in June?*
   - *What are my subscriptions?*
   - *What was my biggest expense?*
   - *Compare last month with this month*
   - *How can I save money?*

---

## 6. Settings

Settings live in `.env`, which setup creates for you. You do not need to edit it.

`LLM_PROVIDER` controls how answers are worded:

| Value | Behaviour |
|-------|-----------|
| `local` (default) | Quantised Qwen2.5 1.5B model on your own CPU. Nothing leaves the machine. |
| `ollama` | Use a model served by a local Ollama instance. |
| `gemini` | Use the Gemini API. Requires your own key in `GEMINI_API_KEY`. |
| `fallback` | No language model at all. Answers and advice still work. |

The figures in every answer are computed from your transactions by the
application itself, not by the language model, so they are the same whichever
provider is selected. Only the phrasing changes.

To keep the data file somewhere else, set `SMARTEDIT_DATABASE_URI`, for example
`sqlite:///D:/finance/smartedit.db`.

---

## 7. Where your data lives

Everything stays on this computer:

- `smartedit.db` — your transactions, salary profile, goals and chat history
- `models/` — the downloaded language model
- `uploads/` — statements you have uploaded

To start completely fresh, close the app and delete `smartedit.db`. It is
recreated empty on the next launch.

---

## 8. Troubleshooting

| Problem | Fix |
|--------|-----|
| `'python' is not recognized` | Python is not on PATH. Reinstall and tick "Add python.exe to PATH", then reopen the terminal. |
| `setup.bat` closes instantly | Run it from a terminal to read the message, and make sure you extracted the ZIP rather than running from inside it. |
| Setup says the model could not be downloaded | Re-run `setup.bat`; it resumes and skips whatever is already done. The app works in the meantime. |
| Port 5000 already in use | Close the other copy of the app, or change the port on the last line of `app.py`. |
| A statement will not import | Check it is a CSV, Excel or PDF exported from your bank. Scanned image PDFs cannot be read. If the PDF is password protected, the app will ask for the password. |
| Charts are blank | Do a hard refresh with Ctrl + F5. Chart.js is served from the application, so no internet is needed. |
| Answers are short and plain | The on-device model is not installed or not downloaded. Re-run `setup.bat`. Figures stay correct either way. |
