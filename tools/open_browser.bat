@echo off
REM Started minimized by run.bat while the server is still starting up.
REM Polls the app instead of guessing a fixed delay: a fixed wait that is
REM too short opens the browser before Flask is listening, and the client
REM sees a browser connection error even though the app is fine seconds
REM later. Falls back to opening anyway after 40 tries so the browser is
REM never left unopened if curl is unavailable or something is genuinely
REM wrong with the server.
REM Both tools are called by full path, because a machine with Git or similar
REM on its PATH can otherwise pick up different versions of them.
REM The pause between attempts uses ping rather than timeout: timeout refuses
REM to run at all when its input is redirected, which is exactly how this file
REM is started, and it would print an error on every pass.
setlocal
set "URL=http://127.0.0.1:5000"
set "CURL=%SystemRoot%\System32\curl.exe"
set "WAIT=%SystemRoot%\System32\ping.exe -n 2 127.0.0.1"
for /l %%i in (1,1,40) do (
    "%CURL%" -s -o nul --max-time 1 "%URL%" >nul 2>&1
    if not errorlevel 1 (
        start "" "%URL%"
        exit /b 0
    )
    %WAIT% >nul 2>&1
)
start "" "%URL%"
exit /b 0
