param(
  [ValidateSet("mock", "aws")]
  [string]$Mode = "mock",
  [int]$Port = 5000
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$AppDir = Join-Path $Root "app"
$VenvPython = Join-Path $AppDir ".venv\Scripts\python.exe"

function Resolve-Python {
  if (Test-Path $VenvPython) {
    return $VenvPython
  }

  $candidates = @("py", "python", "python3")
  foreach ($candidate in $candidates) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) {
      return $cmd.Source
    }
  }

  throw "Python was not found. Install Python 3.11+ or create app/.venv first."
}

$Python = Resolve-Python

if (-not (Test-Path $VenvPython)) {
  Push-Location $AppDir
  try {
    & $Python -m venv .venv
    & $VenvPython -m pip install -r requirements.txt
  }
  finally {
    Pop-Location
  }
}

$env:APP_MODE = $Mode
$env:DB_PATH = Join-Path $env:TEMP "cloud-governance-data.db"
$env:PORT = "$Port"

Write-Host "Starting Flask API in $Mode mode on http://127.0.0.1:$Port"
Write-Host "APP_MODE=$env:APP_MODE"

Push-Location $AppDir
try {
  & $VenvPython app.py
}
finally {
  Pop-Location
}
