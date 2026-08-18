@echo off
REM ============================================================
REM   SmartEdit AI  -  start the application
REM   Opens the app in your browser automatically.
REM ============================================================
setlocal
cd /d "%~dp0"
title SmartEdit AI

if not exist ".venv\Scripts\python.exe" goto NOSETUP

echo.
echo ============================================================
echo    SmartEdit AI is starting.
echo.
echo    Your browser will open at http://127.0.0.1:5000
echo    Keep this window open while you use the app.
echo    Press Ctrl+C here when you want to stop it.
echo ============================================================
echo.

REM Open the browser once the server actually answers, rather than after a
REM fixed delay that can be shorter than the app's real startup time.
start "" /min "%~dp0tools\open_browser.bat"

".venv\Scripts\python.exe" app.py
if errorlevel 1 goto CRASHED
exit /b 0

:NOSETUP
echo.
echo SmartEdit AI has not been installed yet.
echo Please double-click  setup.bat  first, then run this again.
echo.
pause
exit /b 1

:CRASHED
echo.
echo SmartEdit AI stopped unexpectedly. The messages above explain why.
echo If the port is already in use, close any other copy of the app and retry.
echo.
pause
exit /b 1
