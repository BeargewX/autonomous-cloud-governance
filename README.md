# Autonomous Cloud Governance Platform

> ระบบ Cloud Governance อัตโนมัติที่ซ่อมแซมตัวเอง จัดการค่าใช้จ่าย และ monitor ทุกอย่างได้ในหน้าจอเดียว

![Status](https://img.shields.io/badge/status-active-success)
![AWS](https://img.shields.io/badge/AWS-ap--southeast--1-orange)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-black)
![Cost](https://img.shields.io/badge/cost-free%20tier-green)

---

## ปัญหาที่โปรเจคนี้แก้

| ปัญหา | วิธีแก้แบบเดิม | วิธีแก้ของโปรเจคนี้ |
|---|---|---|
| ระบบล่มตอนดึก | รอ engineer ตื่น | ซ่อมตัวเองภายใน 60 วินาที |
| ค่า Cloud บวมโดยไม่รู้ตัว | รู้ตอนปลายเดือน | ตรวจและแจ้งเตือนอัตโนมัติทุกคืน |
| Security config ผิดพลาด | audit ทีหลัง | Compliance check อัตโนมัติ |
| ดูหลาย dashboard | เปิดหลาย tab | Desktop App เดียวจบทุกอย่าง |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Layer 4: Governance Dashboard               │
│   Electron Desktop App · Real-time · Email alerts   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│         Layer 3: FinOps Engine                      │
│  Cost Anomaly · S3 Lifecycle · Weekly Report        │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│         Layer 2: Self-Healing Engine                │
│   CloudWatch · EventBridge · Lambda · Ansible       │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│         Layer 1: Infrastructure                     │
│   VPC · EC2 · Flask · DynamoDB · SNS · CloudWatch   │
└─────────────────────────────────────────────────────┘
```

---

## Live Demo

Flask App รันอยู่ที่ `http://13.228.240.37:5000`

| Endpoint | Description |
|---|---|
| `/` | System status |
| `/health` | Health check |
| `/api/cpu` | Real-time CPU จาก CloudWatch |
| `/api/incidents` | Incidents จาก DynamoDB |
| `/api/status` | EC2 instance state |
| `/api/lambda-stats` | Lambda invocation stats |

---

## Tech Stack

| Category | Technology |
|---|---|
| Cloud | AWS (VPC, EC2, Lambda, DynamoDB, SNS, CloudWatch, EventBridge) |
| IaC | Terraform + Terraform Cloud |
| Backend | Python Flask |
| Desktop App | Electron + Node.js |
| CI/CD | GitHub Actions |
| Config Mgmt | Ansible |
| Region | ap-southeast-1 (Singapore) |

---

## โครงสร้าง Repository

```
autonomous-cloud-governance/
├── .github/workflows/
│   └── deploy.yml              # CI/CD: test → plan → deploy
├── app/
│   ├── app.py                  # Flask + real AWS API endpoints
│   ├── requirements.txt
│   └── tests/test_app.py
├── electron-app/               # Desktop monitoring app
│   ├── main.js
│   ├── preload.js
│   └── index.html
├── lambda/
│   ├── self_healing.py         # ซ่อมระบบอัตโนมัติ
│   ├── finops.py               # ตรวจ idle resources
│   ├── cost_anomaly.py         # ตรวจ cost anomaly
│   ├── s3_lifecycle.py         # จัดการ S3 lifecycle
│   └── weekly_report.py        # รายงานประจำสัปดาห์
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/infrastructure/
│       ├── main.tf             # VPC, Subnets, Security Groups
│       ├── ec2.tf              # EC2, EIP, DynamoDB, SNS
│       └── lambda.tf           # Lambda + EventBridge rules
├── playbooks/                  # Ansible automation
│   ├── site.yml
│   └── roles/
│       ├── base/
│       ├── app/
│       ├── monitoring/
│       └── compliance/
└── dashboards/
    └── governance-dashboard.json
```

---

## Self-Healing Demo

```bash
# หยุด EC2 แล้วดูว่าระบบซ่อมตัวเองได้ไหม
aws ec2 stop-instances --instance-ids i-0327c7e7774cbc046 --region ap-southeast-1

# รอ 60 วินาที แล้วเช็ค — ควรกลับมา running อัตโนมัติ
aws ec2 describe-instances \
  --instance-ids i-0327c7e7774cbc046 \
  --region ap-southeast-1 \
  --query "Reservations[0].Instances[0].State.Name"

# ดู incident log ที่ DynamoDB บันทึกไว้
aws dynamodb scan \
  --table-name cloud-governance-incident-log \
  --region ap-southeast-1
```

---

## Quick Start

```bash
git clone https://github.com/BeargewX/autonomous-cloud-governance.git
cd autonomous-cloud-governance

# Deploy infrastructure
cd terraform
terraform init
terraform apply

# Run Flask app locally
cd ../app
pip install -r requirements.txt
python app.py

# Run Electron Desktop App
cd ../electron-app
npm install
npm start
```

---

## Progress

**Phase 1 — Infrastructure** ✅
- [x] VPC + Subnets + Security Groups + VPC Flow Logs
- [x] EC2 t3.micro + Elastic IP + Flask App
- [x] DynamoDB incident log + SNS alerts
- [x] CloudWatch CPU alarm

**Phase 2 — Self-Healing** ✅
- [x] Lambda self-healing (CPU high + EC2 stopped)
- [x] EventBridge rules + triggers
- [x] Ansible playbooks (base, app, monitoring, compliance)
- [x] Incident logging + email alerts

**Phase 3 — FinOps** ✅
- [x] Lambda FinOps (idle resource detection)
- [x] Cost Anomaly Detection
- [x] S3 Lifecycle policies
- [x] Weekly Report via email

**Phase 4 — Dashboard** ✅
- [x] Flask API endpoints (CPU, status, incidents, lambda stats)
- [x] Electron Desktop App (real-time data)
- [x] GitHub Actions CI/CD pipeline

---

## Resume Bullet Points

```
• Architected Autonomous Cloud Governance Platform on AWS with 4-layer
  self-healing architecture using Terraform IaC, reducing manual ops to zero

• Built event-driven self-healing engine (CloudWatch → EventBridge → Lambda)
  with mean recovery time under 60 seconds, logging all incidents to DynamoDB

• Implemented FinOps pipeline detecting idle resources and cost anomalies
  with automated nightly checks and weekly email reports via SNS

• Delivered Electron desktop monitoring app with real-time AWS metrics
  and full CI/CD pipeline via GitHub Actions (test → plan → deploy)
```

---

*Region: ap-southeast-1 · Free Tier · $0.00/month · May 2026*
