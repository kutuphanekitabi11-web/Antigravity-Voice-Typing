@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"

echo ========================================================
echo   Antigravity Voice Typing - Surec Durdurucu
echo ========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0durdur.ps1"

if "%~1"=="" (
    echo.
    timeout /t 2 >nul
)
exit /b 0
