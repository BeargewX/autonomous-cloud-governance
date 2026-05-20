# Demo Script

This script is optimized for a 5-10 minute project presentation.

## Before The Demo

Run these checks first:

```powershell
cd "D:\BG\Cloud Engineer\autonomous-cloud-governance"
git status
```

```powershell
cd terraform
terraform output
```

Open the backend health endpoint:

```text
http://13.228.240.37:5000/health
```

Expected response:

```json
{"status":"ok"}
```

Start the desktop app:

```powershell
cd ..\electron-app
npm start
```

## Storyline

### 1. Problem

"Cloud teams often react to incidents and cost problems after they happen. This project turns the cloud environment into an automated governance platform that can monitor, respond, and keep evidence."

### 2. Architecture

Show the block diagram and describe the four layers:

- Infrastructure: VPC, EC2, DynamoDB, SNS, CloudWatch
- Self-healing: EventBridge and Lambda respond to alarms or EC2 state changes
- FinOps: scheduled Lambda checks cost and lifecycle opportunities
- Governance dashboard: Flask API and Electron UI show operational status

### 3. Deployment

Show:

- GitHub Actions workflow
- Terraform Cloud successful run
- AWS resources created by Terraform

Key line to say:

"The infrastructure is not manually clicked together. It is reproducible through Terraform Cloud."

### 4. Live Backend

Open:

```text
http://13.228.240.37:5000
http://13.228.240.37:5000/api/status
http://13.228.240.37:5000/api/incidents
```

Explain:

- `/api/status` reads EC2 status from AWS
- `/api/incidents` reads incident history from DynamoDB
- `/api/cpu` reads CloudWatch metrics

### 5. Dashboard

Open the Electron app and show:

- EC2 state
- CPU usage
- Lambda invocation counts
- Incident log
- Infrastructure summary

Key line to say:

"This is the operations cockpit for the governance platform."

### 6. Self-Healing Evidence

Show one of these:

- DynamoDB incident item
- CloudWatch alarm or EventBridge rule
- Lambda logs for `cloud-governance-self-healing`
- A previous EC2 stop or CPU alarm recovery

Key line to say:

"The important part is not just detecting a problem. The platform records what happened and what action was taken."

### 7. FinOps Evidence

Show:

- `cloud-governance-finops`
- `cloud-governance-cost-anomaly`
- `cloud-governance-s3-lifecycle`
- EventBridge schedules

Key line to say:

"FinOps runs as scheduled automation, so cost governance becomes continuous instead of a month-end manual task."

## Closing

Use this summary:

"This project demonstrates a complete cloud engineering workflow: CI/CD, infrastructure as code, monitoring, self-healing, cost governance, evidence logging, and a dashboard for operations. The core platform is working; the next stage is improving security, multi-account support, and richer remediation policies."

## Post-Demo Cost Check

After the demo, verify:

- EC2 instance is still intended to run
- CloudWatch log groups do not have excessive retention
- EventBridge schedules are expected
- Elastic IP is attached
- Terraform Cloud state matches AWS
