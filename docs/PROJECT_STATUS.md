# Project Status

Status: demo ready

Date: May 2026

## Completed

- Terraform Cloud remote deployment
- Modular Terraform infrastructure
- VPC, public/private subnets, route tables, security groups
- EC2 application host
- Flask API service
- DynamoDB incident log table
- SNS alerts topic
- CloudWatch metrics and alarm integration
- EventBridge rules for self-healing triggers
- Lambda functions for self-healing and FinOps flows
- Electron desktop dashboard
- GitHub Actions CI/CD workflow

## Verified Demo Flows

- Terraform apply completes successfully
- Flask health endpoint responds
- EC2 status can be read through the API
- CPU data can be requested from CloudWatch
- Incidents can be read from DynamoDB
- Lambda stats can be read from CloudWatch
- Electron app can consume the Flask API

## Evidence To Capture

For final submission, capture screenshots of:

- Block diagram
- GitHub Actions workflow run
- Terraform Cloud successful apply
- AWS EC2 instance
- DynamoDB incident table
- Lambda functions
- CloudWatch alarm or metrics
- EventBridge rules
- Electron dashboard

## Known Notes

- The HCP Terraform workspace may warn about `db_password` if that variable still exists in Terraform Cloud. It is not used by the current Terraform root module and can be removed from the workspace variables.
- `electron-app/node_modules` is currently present in the repository history. A future cleanup should remove it from git tracking and rely on `package-lock.json` plus `npm install`.
- The Electron app points to the current Elastic IP in `electron-app/preload.js`. If the IP changes, update `BASE_URL`.

## Next Improvement Candidates

- Move environment-specific IDs and URLs into config files or deployment outputs
- Add API authentication for dashboard endpoints
- Add least-privilege IAM review
- Add richer remediation policies and dry-run mode
- Add CloudWatch dashboard import automation
- Add end-to-end tests for API responses
- Remove tracked `node_modules`
- Add release screenshots and architecture images to `docs/`
