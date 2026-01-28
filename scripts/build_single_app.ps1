$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root "..")

# Build frontend (bundled into backend)
Push-Location (Join-Path $repo "frontend")
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  throw "npm is required to build the frontend"
}
$env:VITE_API_BASE = ""
$env:VITE_REQUIRE_API = "true"
if (-not (Test-Path "node_modules")) {
  npm install
}
npm run build
Pop-Location

# Copy frontend build into app/static
$staticDir = Join-Path $repo "app\static"
if (Test-Path $staticDir) {
  Remove-Item -Recurse -Force $staticDir
}
Copy-Item -Recurse (Join-Path $repo "frontend\dist") $staticDir

# Ensure output folders exist
$distDir = Join-Path $repo "dist"
if (-not (Test-Path $distDir)) {
  New-Item -ItemType Directory -Path $distDir | Out-Null
}

# Build single-file executable
$python = Join-Path $repo ".venv\Scripts\python.exe"
$pyArgs = @()
if (-not (Test-Path $python)) {
  $python = "py"
  $pyArgs = @("-3.12")
}

Push-Location $repo
& $python @pyArgs -m pip install -r requirements.txt
& $python @pyArgs -m pip install pyinstaller
& $python @pyArgs -m PyInstaller --onefile --name FloridaPolicyAdvisor --collect-all webview --hidden-import webview.platforms.edgechromium --add-data "app\static;app\static" --add-data "data;data" --add-data "outputs;outputs" app\packaged.py
Pop-Location

Write-Host "Built dist\FloridaPolicyAdvisor.exe"
