Set-Location $PSScriptRoot\frontend
if (-not (Test-Path node_modules)) { npm install }
Write-Host "Starting dashboard on http://127.0.0.1:5173"
npm run dev
