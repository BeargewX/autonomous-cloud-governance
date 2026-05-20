# Project Status

Status: demo-ready and free-first

Date: May 2026

## Completed

- Terraform Cloud remote deployment
- Modular Terraform infrastructure
- VPC, subnets, route tables, security groups
- EC2 application host
- Flask API service
- Mock/local API mode
- DynamoDB incident log table
- SNS alerts topic
- CloudWatch metrics and alarm integration
- EventBridge rules for self-healing triggers
- Lambda functions for self-healing and FinOps flows
- Electron desktop dashboard
- Configurable dashboard backend URL
- GitHub Actions CI/CD workflow
- Cost safety documentation
- Test/demo scripts
- Governance scorecard
- Policy checks
- Drift detector
- Incident prioritizer
- Markdown report generator

## Free-First Improvements

- `APP_MODE=mock` is the local default
- dashboard defaults to `http://127.0.0.1:5000`
- public IPv4 is controlled by `enable_public_ipv4`
- public SSH is controlled by `enable_public_ssh`
- VPC Flow Logs are controlled by `enable_vpc_flow_logs`
- EC2 T3 CPU credits are set to `standard`
- `terraform/free.tfvars.example` documents the after-demo low-cost posture

## Verified Locally

- Python files compile
- Electron preload/main JavaScript syntax passes
- Terraform format check passes
- Terraform validate passes
- PowerShell scripts parse
- Cost-risk script runs
- Dashboard static preview has no encoding errors

## Still To Verify On Your Machine

- `.\scripts\start-local.ps1 -Mode mock`
- `.\scripts\demo-health-check.ps1 -BaseUrl http://127.0.0.1:5000`
- `.\scripts\start-dashboard.ps1 -BaseUrl http://127.0.0.1:5000`
- `.\scripts\export-report.ps1 -BaseUrl http://127.0.0.1:5000`
- GitHub Actions after push
- Terraform Cloud plan after commit
- Live AWS endpoint when intentionally enabled

## Known Notes

- Public IPv4/EIP can still cost money while the live endpoint is enabled.
- The HCP Terraform workspace may warn about `db_password` if that variable remains in Terraform Cloud.
- `electron-app/node_modules` is currently present in git history; future cleanup should remove it from tracking and rely on `package-lock.json`.

## Recommended Next Improvements

- Improve GitHub Actions deployment so it copies the latest Flask app code to EC2 before restart.
- Add API authentication before exposing real operational controls.
- Add AWS Budget resources or documented manual budget setup.
- Add screenshots to `docs/`.
- Remove tracked `node_modules`.
