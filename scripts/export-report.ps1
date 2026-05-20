param(
  [string]$BaseUrl = "http://127.0.0.1:5000",
  [string]$OutputPath = "reports\governance-report.md"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$FullOutputPath = Join-Path $Root $OutputPath
$OutputDir = Split-Path -Parent $FullOutputPath

if (-not (Test-Path $OutputDir)) {
  New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$Report = Invoke-RestMethod -Uri "$BaseUrl/api/report" -TimeoutSec 10
$Report.markdown | Set-Content -LiteralPath $FullOutputPath -Encoding UTF8

Write-Host "Governance report written to $FullOutputPath"
