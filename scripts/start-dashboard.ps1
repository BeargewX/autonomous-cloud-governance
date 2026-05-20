param(
  [string]$BaseUrl = "http://127.0.0.1:5000"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$ElectronDir = Join-Path $Root "electron-app"

$env:DASHBOARD_BASE_URL = $BaseUrl

Write-Host "Starting Electron dashboard"
Write-Host "DASHBOARD_BASE_URL=$env:DASHBOARD_BASE_URL"

Push-Location $ElectronDir
try {
  if (-not (Test-Path "node_modules")) {
    npm install
  }

  npm start
}
finally {
  Pop-Location
}
