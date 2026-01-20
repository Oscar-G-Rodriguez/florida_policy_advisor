$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root "..")

& (Join-Path $repo "scripts\build_single_app.ps1")

$iss = Join-Path $repo "installer\FloridaPolicyAdvisor.iss"
$inno = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $inno) {
  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if ($winget) {
    Write-Host "Installing Inno Setup..."
    winget install --id JRSoftware.InnoSetup --accept-source-agreements --accept-package-agreements
    $inno = Get-Command iscc -ErrorAction SilentlyContinue
  }
}
if (-not $inno) {
  throw "Inno Setup not found. Install it from https://jrsoftware.org/isinfo.php and re-run."
}

iscc $iss
Write-Host "Installer built at dist\FloridaPolicyAdvisor-Setup.exe"
