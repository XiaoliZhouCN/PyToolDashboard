@echo off
setlocal EnableDelayedExpansion
rem Dashboard launcher.
rem Args:
rem   1) project_root (optional): target project root. Defaults to current working directory.
rem   2) dashboard_args... (optional): extra arguments passed to the dashboard entry.
rem Behavior:
rem   - No args: run against current working directory with default "host" action.
rem   - To pass dashboard args while using current directory, call: dashboard.bat . <dashboard_args...>
rem Env:
rem   - PYTHON_EXE (optional): Python executable path. If unset, prefer repo .venv, then fallback to "python".

set "SCRIPT_DIR=%~dp0"

for %%I in ("%SCRIPT_DIR%..") do set "PYTOOL_REPO=%%~fI"

if not defined PYTHON_EXE (
  if exist "%PYTOOL_REPO%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PYTOOL_REPO%\.venv\Scripts\python.exe"
  ) else (
    set "PYTHON_EXE=python"
  )
)

if "%~1"=="" (
  set "PROJECT_ROOT=%CD%"
  goto project_root_ready
)

set "PROJECT_ROOT=%~1"

:project_root_ready

if not exist "%PROJECT_ROOT%" (
  echo Project root not found: %PROJECT_ROOT%
  exit /b 3
)

if not "%~1"=="" shift
set "DASHBOARD_ARGS="
:collect_args
if "%~1"=="" goto args_ready
set "DASHBOARD_ARGS=!DASHBOARD_ARGS! "%~1""
shift
goto collect_args

:args_ready
if not defined DASHBOARD_ARGS (
  set "DASHBOARD_ARGS=host"
)

pushd "%PROJECT_ROOT%"
%PYTHON_EXE% "%PYTOOL_REPO%\dashboard\src\ptd_dashboard\app\main.py" !DASHBOARD_ARGS! --project-root "%PROJECT_ROOT%"
set "EXIT_CODE=%ERRORLEVEL%"
popd

exit /b %EXIT_CODE%
