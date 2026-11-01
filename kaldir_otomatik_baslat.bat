@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET_VBS=%STARTUP_DIR%\AntigravityVoiceTyping.vbs"

echo ========================================================
echo   Antigravity Voice Typing - Otomatik Baslatma Kaldir
echo ========================================================
echo.

if exist "%TARGET_VBS%" (
    del /f /q "%TARGET_VBS%"
    if not exist "%TARGET_VBS%" (
        echo [BASARILI] Startup baslaticisi silindi:
        echo   %TARGET_VBS%
        echo Artik bilgisayar acilisinda otomatik baslamayacak.
    ) else (
        echo [HATA] Startup baslaticisi silinemedi! Dosya kilitli olabilir.
        exit /b 1
    )
) else (
    echo [BILGI] Startup klasorunde kurulu AntigravityVoiceTyping.vbs bulunamadi.
    echo Zaten otomatik baslatma aktif degil.
)

exit /b 0
