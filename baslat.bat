@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0baslat.ps1"

if "%~1"=="" (
    ping 127.0.0.1 -n 2 >nul
)
exit /b %ERRORLEVEL%
