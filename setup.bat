@echo off
REM ============================================================
REM   SmartEdit AI  -  One-click Setup (Windows)
REM   Creates a virtual environment, installs dependencies,
REM   and prepares a .env file (WITHOUT any API key).
REM ============================================================
setlocal
cd /d "%~dp0"

echo(
echo ============================================================
echo    SmartEdit AI  -  Setup
echo ============================================================
echo(

REM --- 1. Check Python is installed ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found on this system.
    echo Please install Python 3.12 from:
    echo     https://www.python.org/downloads/release/python-31210/
    echo During install, TICK "Add python.exe to PATH".
    echo Then run setup.bat again.
    echo(
    pause
    exit /b 1
)
for /f "delims=" %%v in ('python --version') do echo Found %%v

REM --- 2. Create virtual environment ---
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment (.venv) ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Could not create the virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists - reusing it.
)

REM --- 3. Activate and install dependencies ---
call ".venv\Scripts\activate.bat"
echo Upgrading pip ...
python -m pip install --upgrade pip >nul
echo Installing core dependencies (this may take a few minutes) ...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed. Check your internet connection.
    pause
    exit /b 1
)

REM --- 4. Optional: local semantic RAG (large download) ---
echo(
choice /c YN /m "Install OPTIONAL local RAG engine (large ~2GB PyTorch download)"
if errorlevel 2 (
    echo Skipping optional RAG. The chatbot will use keyword + exact-total search with Gemini.
) else (
    echo Installing optional RAG dependencies ...
    pip install -r requirements-optional.txt
)

REM --- 5. Create .env from template (NO API key inside) ---
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo(
    echo Created .env from template.
    echo   ^>^> IMPORTANT: open .env and paste your GEMINI_API_KEY, then save.
) else (
    echo .env already exists - leaving it untouched.
)

echo(
echo ============================================================
echo   Setup complete!
echo   1. Open .env and add your GEMINI_API_KEY
echo   2. Double-click run.bat to start the app
echo ============================================================
echo(
pause
endlocal
