@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"
echo ========================================================
echo   Antigravity Voice Typing - Otomatik Baslatma Kaldir
echo ========================================================
echo.

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_FILE=%STARTUP_DIR%\AntigravityVoiceTyping.vbs"

if exist "%VBS_FILE%" (
    del /f /q "%VBS_FILE%"
    echo [BASARILI] Otomatik baslatma kisayolu kaldirildi.
) else (
    echo [BILGI] Otomatik baslatma zaten kurulu degil.
)

echo.
ping 127.0.0.1 -n 2 >nul
exit /b 0
