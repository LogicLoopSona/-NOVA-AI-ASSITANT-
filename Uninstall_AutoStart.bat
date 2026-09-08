@echo off
title NOVA - Remove AutoStart
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\NOVA.lnk"

if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo NOVA ab auto-start nahi hogi. Manually Start_Sona.bat se chalani hogi.
) else (
    echo NOVA autostart mein setup nahi thi, kuch karne ki zaroorat nahi.
)
echo.
pause
