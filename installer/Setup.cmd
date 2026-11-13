@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Writer.ps1"
exit /b %errorlevel%
