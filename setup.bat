@echo off
REM ============================================================
REM   SmartEdit AI  -  One-click Setup (Windows)
REM   Creates a virtual environment, installs dependencies,
REM   and prepares a .env file (WITHOUT any API key).
REM ============================================================
setlocal
cd /d "%~dp0"

echo.
echo ============================================================
echo    SmartEdit AI  -  Setup
echo ============================================================
echo.

REM --- 1. Check Python is installed ---
python --version >nul 2>&1
if errorlevel 1 goto NOPYTHON
for /f "delims=" %%v in ('python --version') do echo Found %%v

REM --- 2. Create virtual environment ---
if exist ".venv\Scripts\activate.bat" goto HAVEVENV
echo Creating virtual environment .venv ...
python -m venv .venv
if errorlevel 1 goto VENVFAIL
:HAVEVENV

REM --- 3. Activate and install dependencies ---
call ".venv\Scripts\activate.bat"
echo Upgrading pip ...
python -m pip install --upgrade pip >nul
echo Installing core dependencies. This may take a few minutes ...
pip install -r requirements.txt
if errorlevel 1 goto PIPFAIL

REM --- 4. Optional: local semantic RAG (large download) ---
echo.
choice /c YN /m "Install OPTIONAL local RAG engine - large PyTorch download"
if errorlevel 2 goto SKIPRAG
echo Installing optional RAG dependencies ...
pip install -r requirements-optional.txt
:SKIPRAG

REM --- 5. Create .env from template (NO API key inside) ---
if exist ".env" goto HAVEENV
copy ".env.example" ".env" >nul
echo.
echo Created .env from template.
echo    IMPORTANT: open .env and paste your GEMINI_API_KEY, then save.
goto DONE
:HAVEENV
echo .env already exists - leaving it untouched.

:DONE
echo.
echo ============================================================
echo   Setup complete!
echo   1. Open .env and add your GEMINI_API_KEY
echo   2. Double-click run.bat to start the app
echo ============================================================
echo.
pause
exit /b 0

:NOPYTHON
echo [ERROR] Python was not found on this system.
echo Install Python 3.12 from https://www.python.org/downloads/
echo During install, TICK "Add python.exe to PATH", then run setup.bat again.
echo.
pause
exit /b 1

:VENVFAIL
echo [ERROR] Could not create the virtual environment.
echo.
pause
exit /b 1

:PIPFAIL
echo [ERROR] Dependency installation failed. Check your internet connection.
echo.
pause
exit /b 1
