$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root "..")

& (Join-Path $repo "scripts\build_single_app.ps1")

$iss = Join-Path $repo "installer\FloridaPolicyAdvisor.iss"
$npx = Get-Command npx -ErrorAction SilentlyContinue
if ($npx) {
  Write-Host "Building installer via innosetup-compiler (npx)..."
  npx --yes innosetup-compiler $iss
} else {
  $inno = Get-Command iscc -ErrorAction SilentlyContinue
  if (-not $inno) {
    throw "Inno Setup not found and npx is unavailable. Install Node.js or Inno Setup and re-run."
  }
  iscc $iss
}
Write-Host "Installer built at dist\FloridaPolicyAdvisor-Setup.exe"
