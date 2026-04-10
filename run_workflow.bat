@echo off
setlocal
set "EXIT_CODE=0"
for %%I in ("%~dp0..") do set "WORKSPACE_PARENT=%%~fI"
pushd "%WORKSPACE_PARENT%" >nul 2>nul
if errorlevel 1 (
    echo [workflow-start] failed to switch to workspace parent: %WORKSPACE_PARENT%
    set "EXIT_CODE=1"
    goto :done
)
set "PUSHD_OK=1"
set "PM_ROOT=%CD%\workflow"
set "DEFAULT_DEVELOPER_ID=pm-main"
set "DEVELOPER_ID=%WORKFLOW_DEVELOPER_ID%"
if not defined DEVELOPER_ID set "DEVELOPER_ID=%DEFAULT_DEVELOPER_ID%"
set "WORKSPACE_START=%PM_ROOT%\.repository\%DEVELOPER_ID%\scripts\start_workflow_env.ps1"
set "DEPLOYED_START=%PM_ROOT%\.running\prod\scripts\start_workflow_env.ps1"
set "WORKSPACE_LAUNCH=%PM_ROOT%\.repository\%DEVELOPER_ID%\scripts\launch_workflow.ps1"

if exist "%WORKSPACE_START%" (
    set "TARGET_SCRIPT=%WORKSPACE_START%"
    set "TARGET_MODE=workspace-supervisor"
) else if exist "%DEPLOYED_START%" (
    set "TARGET_SCRIPT=%DEPLOYED_START%"
    set "TARGET_MODE=deployed"
) else if exist "%WORKSPACE_LAUNCH%" (
    set "TARGET_SCRIPT=%WORKSPACE_LAUNCH%"
    set "TARGET_MODE=workspace"
) else (
    echo [workflow-start] launch script not found.
    echo [workflow-start] expected one of:
    echo   %DEPLOYED_START%
    echo   %WORKSPACE_LAUNCH%
    set EXIT_CODE=1
    goto :done
)

if /I "%TARGET_MODE%"=="workspace-supervisor" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%TARGET_SCRIPT%" -Environment prod -SkipBackfill -OpenBrowser
) else if /I "%TARGET_MODE%"=="deployed" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%TARGET_SCRIPT%" -Environment prod -SkipBackfill -OpenBrowser
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%TARGET_SCRIPT%" -OpenBrowser
)
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo [workflow-start] failed with exit code %EXIT_CODE%.
    if not defined WORKFLOW_NO_PAUSE_ON_FAIL pause
)

:done
if defined PUSHD_OK popd >nul 2>nul
endlocal & exit /b %EXIT_CODE%
