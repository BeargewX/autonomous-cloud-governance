# Cloud Engineer Assistant

This project is no longer only a dashboard. It now includes a lightweight Cloud Engineer Assistant that runs in free local mode by default.

## Goals

- identify cost risks before they become bills
- highlight security and reliability problems
- detect drift-like conditions without enabling paid governance services
- prioritize incidents
- generate a readable governance report

## Endpoints

| Endpoint | Purpose |
|---|---|
| `/api/governance-score` | Overall and category scores for cost, security, reliability, and operations |
| `/api/policy-checks` | Free-first policy checks and recommended actions |
| `/api/drift` | Lightweight drift detector based on expected vs observed posture |
| `/api/incident-priority` | Incident severity and next-action ranking |
| `/api/report` | Markdown governance report |
| `/api/assistant-summary` | Combined assistant payload for integrations |

## Free-First Design

The assistant does not require AWS Config, Security Hub, Cost Optimization Hub, or any new paid service.

Default mode:

```powershell
.\scripts\start-local.ps1 -Mode mock
```

Live AWS mode is optional and should be used only for demos:

```powershell
.\scripts\start-local.ps1 -Mode aws
```

## What It Checks

- public IPv4/EIP risk
- public SSH exposure
- NAT Gateway presence
- VPC Flow Logs cost exposure
- T3 CPU credit mode
- unauthenticated dashboard API
- broad IAM policy warning
- EC2 running state
- CPU alarm status
- Lambda error status
- incident evidence availability

## Report Export

Start local mode, then run:

```powershell
.\scripts\export-report.ps1 -BaseUrl http://127.0.0.1:5000
```

The report is written to:

```text
reports/governance-report.md
```
