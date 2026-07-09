@echo off
REM ============================================================
REM   SmartEdit AI  -  Start the application
REM   Opens http://127.0.0.1:5000 in your browser automatically.
REM ============================================================
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" goto NOSETUP

call ".venv\Scripts\activate.bat"

echo Starting SmartEdit AI ...
echo Opening http://127.0.0.1:5000 in your browser shortly.
echo Keep this window open. Press Ctrl+C here to stop the server.
echo.

REM Open the browser after a short delay while the server boots
start "" cmd /c "timeout /t 5 >nul & start http://127.0.0.1:5000"

python app.py
exit /b 0

:NOSETUP
echo [ERROR] Setup has not been run yet.
echo Please double-click setup.bat first.
echo.
pause
exit /b 1
