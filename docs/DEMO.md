# Demo Script

This demo has two modes:

- Mock mode: safest and free. Use it to show the dashboard and API without AWS calls.
- Live AWS mode: use it only when you want to prove the real cloud integration.

## Before Demo

Check repo state:

```powershell
git status
```

Run static safety checks:

```powershell
.\scripts\check-cost-risk.ps1
```

## Mock Mode Demo

Terminal 1:

```powershell
.\scripts\start-local.ps1 -Mode mock
```

Terminal 2:

```powershell
.\scripts\demo-health-check.ps1 -BaseUrl http://127.0.0.1:5000
.\scripts\start-dashboard.ps1 -BaseUrl http://127.0.0.1:5000
```

Say:

"This is the free local mode. It proves the application flow and dashboard without keeping AWS resources open."

Show:

- `/health`
- `/api/status`
- `/api/cpu`
- `/api/incidents`
- `/api/governance-score`
- `/api/policy-checks`
- `/api/drift`
- `/api/incident-priority`
- Electron dashboard

## Live AWS Demo

Use this only when the EC2 app endpoint is intentionally running:

```powershell
.\scripts\demo-health-check.ps1 -BaseUrl http://13.228.240.37:5000
.\scripts\start-dashboard.ps1 -BaseUrl http://13.228.240.37:5000
```

Show:

- Terraform Cloud successful run
- AWS EC2 instance
- Lambda functions
- EventBridge rules
- DynamoDB incident table
- CloudWatch alarm or Lambda metrics
- Electron dashboard connected to the live endpoint

Say:

"The same dashboard can run against mock data or the live AWS environment. That keeps the project usable without spending money every time."

Then show the assistant report:

```powershell
.\scripts\export-report.ps1 -BaseUrl http://127.0.0.1:5000
```

Say:

"The system is not just observing cloud resources. It produces an actionable engineer report with risk, drift, priority, and next steps."

## Architecture Story

1. GitHub Actions validates code.
2. Terraform Cloud provisions AWS.
3. EC2 hosts the Flask governance API.
4. CloudWatch and EventBridge detect operational events.
5. Lambda performs self-healing and FinOps actions.
6. DynamoDB stores evidence.
7. Electron displays the governance view.

## Closing

"The project is now demo-ready and cost-aware: local mode is free, live mode proves the cloud workflow, and the after-demo checklist reduces billing risk."

## After Demo

Run:

```powershell
.\scripts\check-cost-risk.ps1
```

Then decide whether to:

- stop EC2
- disable public IPv4
- disable VPC Flow Logs
- destroy the stack
