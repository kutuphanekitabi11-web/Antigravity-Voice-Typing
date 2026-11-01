@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET_VBS=%STARTUP_DIR%\AntigravityVoiceTyping.vbs"

set "BAT_PATH="
for %%I in ("%~dp0baslat.bat") do set "BAT_PATH=%%~sI"
if "%BAT_PATH%"=="" set "BAT_PATH=C:\Users\eGe\Vault\300-PR~1\ANTIGR~1\baslat.bat"

echo ========================================================
echo   Antigravity Voice Typing - Otomatik Baslatma Kurulumu
echo ========================================================
echo.

if not exist "%STARTUP_DIR%" mkdir "%STARTUP_DIR%" 2>nul

> "%TARGET_VBS%" (
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo WshShell.Run chr^(34^) ^& "%BAT_PATH%" ^& chr^(34^), 0, False
    echo Set WshShell = Nothing
)

if exist "%TARGET_VBS%" (
    echo [BASARILI] Startup baslaticisi kuruldu!
    echo   Konum: %TARGET_VBS%
    echo   Hedef: %BAT_PATH%
    echo.
    echo Bilgisayar acildiginda Voice Typing sessizce arka planda calisacak.
) else (
    echo [HATA] VBS baslaticisi olusturulamadi!
    exit /b 1
)

exit /b 0
