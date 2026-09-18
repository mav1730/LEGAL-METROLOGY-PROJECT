# Start backend + dashboard without an AI assistant.
# Run from the project folder:  .\START-EVERYTHING.ps1

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
if (-not $Root) { $Root = Get-Location }

Write-Host ""
Write-Host "Legal Metrology checker — starting both programs"
Write-Host "Project: $Root"
Write-Host ""

# 1) Backend (D: venv if present — that Python has the NER model)
$backendScript = Join-Path $Root "start-backend.ps1"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $backendScript
)

Write-Host "Waiting for API on http://127.0.0.1:5000/api/health ..."
$ok = $false
for ($i = 1; $i -le 40; $i++) {
    Start-Sleep -Seconds 2
    try {
        $h = Invoke-RestMethod "http://127.0.0.1:5000/api/health" -TimeoutSec 2
        if ($h.ok) {
            $ok = $true
            Write-Host ""
            Write-Host "API is up."
            Write-Host ("  ner_available   = " + $h.ner_available)
            Write-Host ("  extractor_mode  = " + $h.extractor_mode)
            if (-not $h.ner_available) {
                Write-Host "  WARNING: NER is OFF. You are probably on system Python, not D:\legal-metrology\venv."
                Write-Host "  Close the backend window and run: D:\legal-metrology\scripts\start-backend.ps1"
            }
            break
        }
    } catch {
        Write-Host ("  try " + $i + "/40 ...")
    }
}
if (-not $ok) {
    Write-Host "API did not start. Read the backend PowerShell window for the error."
    Write-Host "Common cause: D:\legal-metrology\venv missing. Run D:\legal-metrology\scripts\setup-d-drive.ps1"
    exit 1
}

# 2) Frontend
$frontendScript = Join-Path $Root "start-frontend.ps1"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", $frontendScript
)

Write-Host "Waiting for dashboard on http://127.0.0.1:5173/ ..."
$ui = $false
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-WebRequest "http://127.0.0.1:5173/" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $ui = $true; break }
    } catch {
        Write-Host ("  try " + $i + "/30 ...")
    }
}

Write-Host ""
if ($ui) {
    Write-Host "Dashboard is up."
} else {
    Write-Host "Dashboard not answering yet. Check the frontend PowerShell window (npm install may still be running)."
}

Write-Host ""
Write-Host "Open these in Chrome:"
Write-Host "  Dashboard  http://127.0.0.1:5173/"
Write-Host "  DemoMart   http://127.0.0.1:5000/demo/"
Write-Host "  Health     http://127.0.0.1:5000/api/health"
Write-Host ""
Write-Host "First scans: honey URL (regex) then golden-grain-atta-5kg (NER)."
Write-Host "Full story: docs\01-what-is-this.md  through  docs\05-demo-script-and-limits.md"
Write-Host "Leave both PowerShell windows open. Closing them stops the site."
Write-Host ""
