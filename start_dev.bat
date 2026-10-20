@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_dev.ps1" %*
if errorlevel 1 (
  echo.
  echo Startup failed. Read the message above before closing this window.
  pause
  exit /b 1
)
endlocal
