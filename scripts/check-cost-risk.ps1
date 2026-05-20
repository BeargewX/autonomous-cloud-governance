$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$TerraformDir = Join-Path $Root "terraform"
$TerraformFiles = Get-ChildItem -Path $TerraformDir -Recurse -Filter "*.tf" | Select-Object -ExpandProperty FullName

Write-Host "Static cost-risk check"
Write-Host "Project: $Root"
Write-Host ""

$Findings = @()

if (Select-String -Path $TerraformFiles -Pattern "aws_nat_gateway" -ErrorAction SilentlyContinue) {
  $Findings += "[HIGH] NAT Gateway found. This is usually paid hourly plus data processing."
}
else {
  $Findings += "[OK] No NAT Gateway resource found."
}

if (Select-String -Path $TerraformFiles -Pattern "aws_eip|enable_public_ipv4" -ErrorAction SilentlyContinue) {
  $Findings += "[WATCH] Public IPv4/EIP is configurable. Keep enable_public_ipv4=false when not doing a live demo."
}

if (Select-String -Path $TerraformFiles -Pattern "aws_flow_log|enable_vpc_flow_logs" -ErrorAction SilentlyContinue) {
  $Findings += "[WATCH] VPC Flow Logs are configurable. Keep enable_vpc_flow_logs=false for lowest CloudWatch Logs usage."
}

if (Select-String -Path $TerraformFiles -Pattern "cpu_credits\s*=\s*var.ec2_cpu_credits" -ErrorAction SilentlyContinue) {
  $Findings += "[OK] EC2 T3 CPU credits are controlled by ec2_cpu_credits."
}
else {
  $Findings += "[WARN] EC2 CPU credit mode was not found."
}

if (Select-String -Path $TerraformFiles -Pattern "billing_mode\s*=\s*`"PAY_PER_REQUEST`"" -ErrorAction SilentlyContinue) {
  $Findings += "[OK] DynamoDB uses PAY_PER_REQUEST."
}

$Findings | ForEach-Object { Write-Host $_ }

Write-Host ""
Write-Host "Recommended after-demo state:"
Write-Host "  enable_public_ipv4=false"
Write-Host "  enable_vpc_flow_logs=false"
Write-Host "  enable_public_ssh=false"
Write-Host "  ec2_cpu_credits=standard"
