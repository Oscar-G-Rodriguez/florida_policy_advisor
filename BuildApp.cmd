@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0\scripts\build_installer.ps1"
endlocal
