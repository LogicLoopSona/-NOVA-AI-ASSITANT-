@echo off
title NOVA - AutoStart Setup
echo NOVA ko Windows Startup mein add kar rahe hain (silent mode)...
echo.

set "SCRIPT_DIR=%~dp0"
set "TARGET=%SCRIPT_DIR%Start_NOVA_Silent.vbs"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\NOVA.lnk"

powershell -NoProfile -Command ^
  "$WshShell = New-Object -ComObject WScript.Shell;" ^
  "$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%');" ^
  "$Shortcut.TargetPath = '%TARGET%';" ^
  "$Shortcut.WorkingDirectory = '%SCRIPT_DIR%';" ^
  "$Shortcut.Description = 'NOVA Voice Assistant';" ^
  "$Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo.
    echo Done! Ab jab bhi tum laptop on karogi / login karogi,
    echo NOVA khud-ba-khud chalu ho jayegi — sirf circle GUI dikhega,
    echo koi kaali terminal window nahi.
    echo.
    echo Isse hatana ho toh Uninstall_AutoStart.bat chala dena.
) else (
    echo.
    echo Kuch gadbad hui, shortcut nahi ban paya.
)

echo.
pause
