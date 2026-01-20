<#
RALPH loop runner for Windows (PowerShell)

Usage:
  powershell -ExecutionPolicy Bypass -File .\ralph.ps1 -MaxIterations 25

Assumes:
  - Claude Code CLI is available as `claude`
  - PRD.md, plan.md, PROMPT.md, activity.md exist in repo root
#>

param(
  [Parameter(Mandatory=$true)][int]$MaxIterations
)

$ErrorActionPreference = 'Continue'

function WriteBanner([string]$text) {
  Write-Host "========================================="
  Write-Host $text
  Write-Host "========================================="
}

WriteBanner "RALPH — Florida Workforce Stability Policy Advisor (MVP)"
Write-Host ("Started: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-Host ("MaxIterations: " + $MaxIterations)
Write-Host ""

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Host "ERROR: Claude Code CLI (claude) was not found on PATH."
  Write-Host "Fix: install Claude Code CLI, then re-run this script."
  exit 2
}

if (-not (Test-Path -Path "PROMPT.md")) {
  Write-Host "ERROR: PROMPT.md not found in current directory."
  exit 2
}

for ($i = 1; $i -le $MaxIterations; $i++) {
  WriteBanner ("Iteration " + $i + " / " + $MaxIterations)

  $prompt = Get-Content -Path "PROMPT.md" -Raw

  # Run Claude with the stable prompt. Any writes/commands are governed by .claude/settings.json.
  $result = (claude -p $prompt --output-format text 2>&1 | Out-String)

  Write-Host $result

  if ($result -match "<promise>COMPLETE</promise>") {
    WriteBanner "COMPLETE"
    Write-Host ("Finished: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
    Write-Host "Next steps:"
    Write-Host "  1) Run tests:  python -m pytest"
    Write-Host "  2) Run app:    python -m app.main"
    Write-Host "  3) Open UI:    http://127.0.0.1:8000"
    exit 0
  }

  Start-Sleep -Seconds 2
}

WriteBanner "MAX ITERATIONS REACHED"
Write-Host ("Finished: " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-Host "Review activity.md and plan.md to see what remains."
Write-Host "Re-run with additional iterations if needed."
exit 1
