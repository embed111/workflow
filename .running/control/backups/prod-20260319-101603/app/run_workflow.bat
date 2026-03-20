@echo off
setlocal
set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%scripts\start_workflow_env.ps1" -Environment prod -OpenBrowser
endlocal
