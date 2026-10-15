$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$onWindows = [System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT
$relativePython = if ($onWindows) { '.venv/Scripts/python.exe' } else { '.venv/bin/python' }
$python = Join-Path $PSScriptRoot $relativePython
if (-not (Test-Path -LiteralPath $python)) { throw 'Crie a .venv local com instalacao/setup.bat (Windows) ou bash instalacao/setup.sh (Linux).' }
Push-Location $PSScriptRoot
try { & $python (Join-Path $PSScriptRoot 'run.py') @args; $resultCode = $LASTEXITCODE }
finally { Pop-Location }
exit $resultCode
