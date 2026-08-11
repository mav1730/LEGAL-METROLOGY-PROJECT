# Prefer D: runtime (venv + Playwright browsers + DB)
$DStart = "D:\legal-metrology\scripts\start-backend.ps1"
if (Test-Path $DStart) {
    & $DStart
} else {
    Write-Host "D: setup missing — using system Python (C:)."
    Set-Location $PSScriptRoot\backend
    py -3 run.py
}
