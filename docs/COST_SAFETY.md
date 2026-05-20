# Cost Safety Guide

This project follows a free-first rule: use local/mock mode by default, enable live AWS only for tests or demos, and clean up after.

## Biggest Cost Risks

| Item | Risk | What to do |
|---|---|---|
| Public IPv4 / Elastic IP | Charged hourly by AWS | Keep `enable_public_ipv4=false` when not doing a live demo |
| NAT Gateway | Paid hourly plus data processing | Do not add NAT Gateway for this student/demo version |
| EC2 | Free only within account limits | Stop or destroy after demo if you do not need it |
| CloudWatch Logs | Can grow over time | Keep VPC Flow Logs off unless demoing governance logs |
| T3 unlimited CPU credits | Can charge when CPU bursts | Use `ec2_cpu_credits="standard"` |

## Default Working Modes

### Free Local Mode

Use this for development and UI testing:

```powershell
.\scripts\start-local.ps1 -Mode mock
.\scripts\start-dashboard.ps1 -BaseUrl http://127.0.0.1:5000
```

This mode does not call AWS.

### Live AWS Demo Mode

Use this only when you want to show real AWS integration:

```powershell
.\scripts\start-local.ps1 -Mode aws
.\scripts\start-dashboard.ps1 -BaseUrl http://13.228.240.37:5000
```

## Terraform Free Settings

For the lowest-cost after-demo state, review:

```text
terraform/free.tfvars.example
```

Then run a plan intentionally:

```powershell
cd terraform
terraform plan -var-file=free.tfvars.example
```

Do not apply until you understand what will change. Disabling public IPv4 can break the public endpoint.

## AWS Console Checklist

Before and after demo:

- Billing dashboard has no unexpected cost
- AWS Budget alert exists at a low threshold, such as 1 USD
- EC2 instance is stopped or intentionally running
- Elastic IP/public IPv4 is removed or intentionally active
- VPC Flow Logs are off unless needed
- CloudWatch log retention is short

## Recommended Budget Alerts

Create AWS Budgets alerts:

- Actual cost greater than 1 USD
- Forecasted cost greater than 3 USD

This is the one guardrail I would always keep on.
