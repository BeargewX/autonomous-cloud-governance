param(
  [switch]$StopEc2,
  [switch]$Destroy,
  [switch]$Yes
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "Cleanup helper for Autonomous Cloud Governance"
Write-Host ""
Write-Host "Safe options:"
Write-Host "  -StopEc2   Stop the EC2 demo instance through AWS CLI."
Write-Host "  -Destroy   Run terraform destroy from terraform/."
Write-Host ""

if (-not $StopEc2 -and -not $Destroy) {
  Write-Host "No action selected. Examples:"
  Write-Host "  .\scripts\cleanup-after-demo.ps1 -StopEc2"
  Write-Host "  .\scripts\cleanup-after-demo.ps1 -Destroy"
  exit 0
}

if (-not $Yes) {
  $Answer = Read-Host "This can stop or destroy AWS resources. Type YES to continue"
  if ($Answer -ne "YES") {
    Write-Host "Cancelled."
    exit 0
  }
}

if ($StopEc2) {
  $InstanceId = $env:EC2_INSTANCE_ID
  if (-not $InstanceId) {
    $InstanceId = Read-Host "Enter EC2 instance id"
  }

  aws ec2 stop-instances --instance-ids $InstanceId --region ap-southeast-1
}

if ($Destroy) {
  Push-Location (Join-Path $Root "terraform")
  try {
    terraform destroy
  }
  finally {
    Pop-Location
  }
}
