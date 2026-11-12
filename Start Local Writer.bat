@echo off
cd /d "%~dp0"
python --version >nul 2>&1
if errorlevel 1 (
    echo Python was not found. Install it only if you choose to do so.
    pause
    exit /b 1
)
python app\server.py --open
set "writer_exit_code=%errorlevel%"
echo.
if not "%writer_exit_code%"=="0" (
    echo Writer ^& Translator stopped with an error. Review the message above.
) else (
    echo Writer ^& Translator has stopped. You can close this window.
)
pause
exit /b %writer_exit_code%
