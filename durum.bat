@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0durum.ps1"

if "%~1"=="" (
    echo.
    echo Devam etmek icin bir tusa basiniz...
    pause >nul
)
exit /b 0
