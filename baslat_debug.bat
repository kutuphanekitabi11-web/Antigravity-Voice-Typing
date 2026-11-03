@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"
title Antigravity Voice Typing - Canli Konsol

echo ========================================================
echo       Antigravity Global Voice Typing (Canli Konsol)
echo ========================================================
echo.
echo Loglar bu ekranda anlik gorunecektir.
echo Alt + V tusuna basarak dikteyi test edebilirsin.
echo Cikmak icin bu konsol penceresini kapatman yeterlidir.
echo.

python app.py
echo.
echo Uygulama kapandi.
pause
