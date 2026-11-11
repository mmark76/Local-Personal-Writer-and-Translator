@echo off
cd /d "%~dp0"
python --version >nul 2>&1
if errorlevel 1 (
    echo Python was not found. Install it only if you choose to do so.
    pause
    exit /b 1
)
python app\server.py --open
echo.
echo Application stopped.
pause
