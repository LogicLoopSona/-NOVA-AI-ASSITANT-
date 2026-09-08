@echo off
title NOVA - One-Click Setup
echo ============================================
echo   NOVA Setup — laptop on hote hi khud khulegi
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
set "TARGET=%SCRIPT_DIR%Start_NOVA_Silent.vbs"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\NOVA.lnk"

echo [1/2] Autostart set kar rahe hain...
powershell -NoProfile -Command ^
  "$WshShell = New-Object -ComObject WScript.Shell;" ^
  "$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%');" ^
  "$Shortcut.TargetPath = '%TARGET%';" ^
  "$Shortcut.WorkingDirectory = '%SCRIPT_DIR%';" ^
  "$Shortcut.Description = 'NOVA Voice Assistant';" ^
  "$Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo       Done — ab har laptop start/login pe NOVA khud chalu hogi.
) else (
    echo       Kuch gadbad hui, autostart set nahi hua. Baaki bhi try karte hain.
)

echo.
echo [2/2] NOVA ko abhi launch kar rahe hain...
start "" wscript.exe "%TARGET%"

echo       Done — NOVA ka circle window kuch second mein khulega.
echo.
echo Yeh window band kar sakti ho, NOVA alag se chalti rahegi.
echo.
pause
