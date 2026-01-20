$ErrorActionPreference = "Stop"

$exe = Join-Path $env:LOCALAPPDATA "Programs\FloridaPolicyAdvisor\FloridaPolicyAdvisor.exe"
if (-not (Test-Path $exe)) {
  throw "Executable not found at $exe"
}

$proc = Start-Process -FilePath $exe -PassThru
Start-Sleep -Seconds 4
$status = (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health).StatusCode
Stop-Process -Id $proc.Id -Force
Write-Output $status
