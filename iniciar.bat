@echo off
setlocal
set "PYTHONUTF8=1"
pushd "%~dp0" || exit /b 1
if not exist ".venv\Scripts\python.exe" (
    echo Ambiente ausente. Execute instalacao\setup.bat. >&2
    popd
    exit /b 1
)
".venv\Scripts\python.exe" "run.py" %*
set "app_exit_code=%errorlevel%"
popd
exit /b %app_exit_code%
