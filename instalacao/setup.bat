@echo off
setlocal
set "PYTHONUTF8=1"
pushd "%~dp0.." || exit /b 1
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "instalacao\install.py" %*
) else (
    python "instalacao\install.py" %*
)
set "installer_exit_code=%errorlevel%"
popd
exit /b %installer_exit_code%
