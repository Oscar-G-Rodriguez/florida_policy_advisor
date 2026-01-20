$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root "..")

$venvActivate = Join-Path $repo ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
  & $venvActivate
}

$backendCommand = "cd `"$repo`"; python -m uvicorn app.main:app --reload --port 8000"
$frontendCommand = "cd `"$repo\frontend`"; npm run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "Backend and frontend started. Close the new windows to stop them."
