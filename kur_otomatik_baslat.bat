@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"
echo ========================================================
echo   Antigravity Voice Typing - Otomatik Baslatma Kurucu
echo ========================================================
echo.

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_FILE=%STARTUP_DIR%\AntigravityVoiceTyping.vbs"
set "BAT_FILE=%~dp0baslat.bat"

echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_FILE%"
echo WshShell.Run """%BAT_FILE%"" silent", 0, False >> "%VBS_FILE%"

if exist "%VBS_FILE%" (
    echo [BASARILI] Otomatik baslatma kuruldu!
    echo Bilgisayar her acildiginda Voice Typing arka planda baslayacaktir.
) else (
    echo [HATA] Kisayol olusturulamadi!
)

echo.
ping 127.0.0.1 -n 3 >nul
exit /b 0
