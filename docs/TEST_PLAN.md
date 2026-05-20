# Test Plan

Use this checklist after each meaningful change.

## 1. Local Mock Mode

```powershell
.\scripts\start-local.ps1 -Mode mock
```

In another terminal:

```powershell
.\scripts\demo-health-check.ps1 -BaseUrl http://127.0.0.1:5000
```

Expected:

- all endpoints return `[OK]`
- responses include `mode=mock`
- no AWS credentials required
- assistant endpoints return score, policies, drift, incident priority, and report data

## 2. Electron Dashboard

```powershell
.\scripts\start-dashboard.ps1 -BaseUrl http://127.0.0.1:5000
```

Expected:

- dashboard opens
- status is healthy
- CPU chart has mock values
- incident log shows demo records
- no encoding errors

## 3. Terraform Static Checks

```powershell
.\scripts\check-cost-risk.ps1
cd terraform
terraform fmt -check -recursive
terraform validate
```

Expected:

- no NAT Gateway
- public IPv4 is configurable
- VPC Flow Logs are configurable
- Terraform validates

## 4. Live AWS Mode

Only run when you intentionally want a live demo:

```powershell
.\scripts\demo-health-check.ps1 -BaseUrl http://13.228.240.37:5000
```

Expected:

- `/health` returns ok
- `/api/status` returns the EC2 state
- `/api/incidents` returns DynamoDB incident data
- `/api/cpu` returns CloudWatch CPU data

## 5. After Demo

Run:

```powershell
.\scripts\check-cost-risk.ps1
```

Then decide:

- stop EC2
- disable public IPv4
- disable VPC Flow Logs
- destroy the stack if no longer needed

## 6. Assistant Report

With the local API running:

```powershell
.\scripts\export-report.ps1 -BaseUrl http://127.0.0.1:5000
```

Expected:

- `reports/governance-report.md` is created
- report includes score, recommended actions, drift checks, and incident priority
