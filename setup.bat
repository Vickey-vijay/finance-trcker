@echo off
REM ============================================================
REM   SmartEdit AI  -  one-click setup for Windows
REM   Installs everything the application needs. Nothing else
REM   has to be configured afterwards.
REM ============================================================
setlocal
cd /d "%~dp0"
title SmartEdit AI - Setup

echo.
echo ============================================================
echo    SmartEdit AI - Setup
echo.
echo    This installs the application and its on-device AI.
echo    It downloads about 1.5 GB the first time, so it can
echo    take a few minutes. You only need to do this once.
echo ============================================================
echo.

REM --- 1. Locate Python -------------------------------------------------
set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if not defined PY (
    python --version >nul 2>&1
    if not errorlevel 1 set "PY=python"
)
if not defined PY goto NOPYTHON
for /f "delims=" %%v in ('%PY% --version 2^>^&1') do echo Using %%v

REM --- 2. Virtual environment -------------------------------------------
if exist ".venv\Scripts\python.exe" goto HAVEVENV
echo Creating the application environment ...
%PY% -m venv .venv
if errorlevel 1 goto VENVFAIL
:HAVEVENV
set "VPY=.venv\Scripts\python.exe"

REM --- 3. Core libraries -------------------------------------------------
echo.
echo Installing core components ...
"%VPY%" -m pip install --upgrade pip --quiet --disable-pip-version-check
"%VPY%" -m pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 goto PIPFAIL

REM --- 4. On-device AI ---------------------------------------------------
REM Both come from prebuilt CPU wheels, so no compiler is required.
echo Installing the on-device AI engine ...
"%VPY%" -m pip install --only-binary=:all: llama-cpp-python==0.3.34 ^
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu ^
    --quiet --disable-pip-version-check
if errorlevel 1 echo    (skipped - the built-in advisor will be used instead)

echo Installing the search engine used by the assistant ...
"%VPY%" -m pip install torch==2.9.1 --index-url https://download.pytorch.org/whl/cpu ^
    --quiet --disable-pip-version-check
if errorlevel 1 echo    (skipped - keyword search will be used instead)
"%VPY%" -m pip install sentence-transformers==5.1.2 --quiet --disable-pip-version-check
if errorlevel 1 echo    (skipped - keyword search will be used instead)

REM --- 5. Models, settings and database ---------------------------------
echo.
"%VPY%" tools\first_run_setup.py
if errorlevel 1 goto PREPFAIL

echo.
echo ============================================================
echo   Setup complete.
echo   Double-click  run.bat  to start SmartEdit AI.
echo ============================================================
echo.
pause
exit /b 0

:NOPYTHON
echo.
echo [Setup cannot continue] Python is not installed on this computer.
echo.
echo   1. Go to https://www.python.org/downloads/
echo   2. Download Python 3.12 and run the installer
echo   3. On the first screen, tick "Add python.exe to PATH"
echo   4. Once it finishes, double-click setup.bat again
echo.
pause
exit /b 1

:VENVFAIL
echo.
echo [Setup cannot continue] The application environment could not be created.
echo Check that you have permission to write to this folder.
echo.
pause
exit /b 1

:PIPFAIL
echo.
echo [Setup cannot continue] The core components could not be installed.
echo Check your internet connection and run setup.bat again.
echo.
pause
exit /b 1

:PREPFAIL
echo.
echo [Setup finished with warnings] Some optional components are missing.
echo SmartEdit AI will still start and work. Run setup.bat again later
echo to complete them.
echo.
pause
exit /b 0
