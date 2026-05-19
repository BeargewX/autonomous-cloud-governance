# Autonomous Cloud Governance Platform

ระบบ Cloud Governance อัตโนมัติ ที่สามารถซ่อมแซมตัวเองได้ พร้อม FinOps และ Compliance

## โครงสร้างโปรเจค

```
├── app/                    # Flask Web Application
│   ├── app.py
│   ├── requirements.txt
│   └── tests/
├── terraform/              # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       └── infrastructure/ # VPC, EC2, RDS, ALB, Auto Scaling
├── lambda/                 # Self-healing Lambda functions
├── playbooks/              # Ansible Playbooks
├── dashboards/             # Grafana Dashboards
└── docs/                   # Documentation
```

## Tech Stack

- **Cloud:** AWS (VPC, EC2, RDS, Lambda, DynamoDB, SNS)
- **IaC:** Terraform + Terraform Cloud
- **App:** Python Flask
- **Monitoring:** CloudWatch + Grafana
- **CI/CD:** GitHub Actions
