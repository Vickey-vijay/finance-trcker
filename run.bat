@echo off
REM ============================================================
REM   SmartEdit AI  -  Start the application
REM   Opens http://127.0.0.1:5000 in your browser automatically.
REM ============================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Setup has not been run yet.
    echo Please double-click setup.bat first.
    echo(
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

REM Warn if the API key has not been added yet
findstr /c:"GEMINI_API_KEY=" ".env" | findstr /v /c:"GEMINI_API_KEY=$" >nul 2>&1
if errorlevel 1 (
    echo [NOTE] GEMINI_API_KEY appears empty in .env.
    echo The app will still run using the offline fallback advisor + chat.
    echo Add your key to .env for full AI answers.
    echo(
)

echo Starting SmartEdit AI ...
echo Opening http://127.0.0.1:5000 in your browser shortly.
echo (Keep this window open. Press Ctrl+C here to stop the server.)
echo(

REM Open the browser after a short delay while the server boots
start "" cmd /c "timeout /t 5 >nul & start http://127.0.0.1:5000"

python app.py

endlocal
