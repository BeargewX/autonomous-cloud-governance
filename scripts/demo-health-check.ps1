param(
  [string]$BaseUrl = "http://127.0.0.1:5000"
)

$ErrorActionPreference = "Stop"

$Endpoints = @(
  "/health",
  "/",
  "/metrics",
  "/api/status",
  "/api/cpu",
  "/api/incidents",
  "/api/lambda-stats",
  "/api/governance-score",
  "/api/policy-checks",
  "/api/drift",
  "/api/incident-priority",
  "/api/report",
  "/api/assistant-summary"
)

Write-Host "Checking $BaseUrl"

foreach ($Endpoint in $Endpoints) {
  $Url = "$BaseUrl$Endpoint"
  try {
    $Response = Invoke-RestMethod -Uri $Url -TimeoutSec 10
    $Mode = if ($Response.mode) { $Response.mode } else { "n/a" }
    Write-Host "[OK] $Endpoint mode=$Mode"
  }
  catch {
    Write-Host "[FAIL] $Endpoint $($_.Exception.Message)"
    exit 1
  }
}

Write-Host "All demo endpoints responded."
