# SmartEdit AI — Setup Guide (Client VM)

This guide gets SmartEdit AI running on a fresh Windows machine in a few minutes.

---

## 1. Prerequisites (install once)

You only need **Python**. The app is 100% Python — **Node.js is NOT required** to run it.

| Software | Version | Why |
|----------|---------|-----|
| **Python** | **3.12.x** (tested on 3.12.10) | Runs the whole application |
| Git (optional) | latest | Only if cloning from GitHub instead of ZIP |

### Install Python — pick ONE method

**A. Command line (fastest, Windows 10/11):**
Open **Command Prompt** or **PowerShell as Administrator** and run:

```
winget install -e --id Python.Python.3.12
```

Close and reopen the terminal afterwards so `python` is on PATH.

**B. Manual download:**
Get Python 3.12.10 from
https://www.python.org/downloads/release/python-31210/
Run the installer and **tick “Add python.exe to PATH”** on the first screen.

**Verify:**
```
python --version
```
You should see `Python 3.12.x`.

*(Optional)* Install Git if you plan to `git clone`:
```
winget install -e --id Git.Git
```

---

## 2. Get the project

**Option A — ZIP (recommended for the client):**
1. Go to the GitHub repo.
2. Click the green **`<> Code`** button → **Download ZIP**.
3. Right-click the ZIP → **Extract All…** to a folder like `C:\SmartEditAI`.

**Option B — Git clone:**
```
git clone https://github.com/Vickey-vijay/finance-trcker.git
```

---

## 3. One-click setup

Inside the extracted folder, **double-click `setup.bat`**.

It will:
1. Check Python is installed.
2. Create a virtual environment (`.venv`).
3. Install the core dependencies.
4. Offer to install the optional local RAG engine (large PyTorch download — you can skip it).
5. Create a `.env` file from the template (**no API key inside**).

> Prefer the command line? From the project folder:
> ```
> setup.bat
> ```

---

## 4. Add your Gemini API key

1. Open the newly created **`.env`** file in Notepad.
2. Find this line and paste your key after the `=`:
   ```
   GEMINI_API_KEY=your_key_here
   ```
   (Get a free key at https://aistudio.google.com/app/apikey)
3. Save and close.

> If you leave the key blank, the app still runs using the built-in **offline
> fallback** advisor and chat — nothing crashes, you just don’t get Gemini’s
> natural-language answers.

---

## 5. Run the app

**Double-click `run.bat`** (or run `run.bat` from the terminal).

- It starts the server and opens **http://127.0.0.1:5000** in your browser.
- Keep the black window open while using the app.
- To stop: press **Ctrl + C** in that window, or just close it.

---

## 6. First use

1. Click **Create an account** and register.
2. On the empty dashboard, upload **one month** of a bank statement — try the
   included `sample_data/sample_statement.csv` first.
3. Explore **Dashboard → View/Database → Tracker → AI Chat**.
4. In chat, ask e.g. *“How much did I spend on Amazon?”* or *“How can I save more?”*

---

## 7. Switching to a fully local AI (later)

To run with no cloud at all, install **Ollama** (https://ollama.com), then in `.env`:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3
```
Pull the model once with `ollama pull llama3`, then `run.bat`. No other change needed.

---

## 8. Troubleshooting

| Problem | Fix |
|--------|-----|
| `'python' is not recognized` | Python not on PATH — reinstall and tick “Add to PATH”, reopen terminal. |
| `setup.bat` closes instantly | Run it from a terminal to read the error, or ensure you extracted the ZIP (don’t run from inside the zip). |
| Port 5000 already in use | Close the old window, or edit the last line of `app.py` to use another port. |
| Chat gives short answers | Add your `GEMINI_API_KEY` to `.env`, then restart `run.bat`. |
| Want semantic RAG | `pip install -r requirements-optional.txt` inside the activated `.venv`. |
