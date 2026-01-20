$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root "..")

$venvActivate = Join-Path $repo ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
  & $venvActivate
}

Set-Location $repo
python -m app.data.refresh
