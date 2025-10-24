
# 🧩 Immowelt Daily Fetch — Deployment via AWS Lambda + EventBridge

This document describes how to deploy and schedule the **Immowelt data-fetch pipeline** securely using **AWS Lambda** and **EventBridge**.  
The script collects daily long-term rental listings from Immowelt and writes them to the PostgreSQL database.

---

## 🚀 Overview

**Goal:**  
Automate the daily data-fetch pipeline in a secure, serverless environment.

**Tech Stack:**  
- AWS Lambda (Python)
- AWS EventBridge (Scheduler)
- AWS Secrets Manager (DB credentials)
- AWS CloudWatch (Logs)
- PostgreSQL (Target database)

👉 Implementation scaffold: [`long-term-listings/lambda/`](./long-term-listings/lambda/)

---

### 🌐 Networking Notes
- Lambda runs **inside the VPC** (private subnet) → outbound via **NAT gateway**.
- Use an **S3 Gateway VPC Endpoint** (free) if reading/writing S3 from inside the VPC.
- Enforce DB TLS (e.g., `sslmode=verify-full`); consider **RDS Proxy + IAM authentication** for production setups.

---

### 💸 Cost Snapshot (Lambda)
- 512 MB for 10 s ≈ **$0.000085 per run**
- 1 × per day ≈ **$0.0026 / month** • 100 × per day ≈ **$0.25 / month**
- For short data-fetch jobs, costs are effectively negligible.

---


## 🧩 Step 1 — Preparation

1. **Confirm AWS access**
   Check the status create and manage:
   - Lambda functions  
   - Secrets Manager secrets  
   - EventBridge rules  

   ### 🔑 AWS Login (SSO, QA)
```bash
### 🔑 AWS Login (SSO, QA)
```bash
aws sso login --profile ReadOnlyAccess-489962060388
aws sts get-caller-identity
```

3. **Package the script**  
   Creating a ZIP file with main script and dependencies:
   ```bash
   zip -r function.zip main.py requirements.txt
Check requirements.txt
Include only the required libraries:
psycopg2-binary
requests
pandas

```markdown
### ✅ QA Test Plan (what I’ll validate)
- Lambda runs in QA VPC (private subnet) and reaches the internet via NAT.
- Writes to **QA PostgreSQL** succeed.
- Total runtime < **15 minutes** (otherwise consider ECS Fargate).
- No duplicates thanks to **UPSERT**; counts are logged.
- CloudWatch logs show clean run (no connection errors).
```
**Promote to prod** once all the above are green (same Terraform module, prod vars).

---

## 🔐 Step 2 — Database Credentials (Secrets Manager)

**AWS Secrets Manager → Store a new secret** 
   - Other type of secret.
   - PostgreSQL connection details:
host
port
database
user
password
Name the secret:
```immowelt-db-secret```

---

## ☁️ Step 3 — AWS Lambda Function

1. **AWS Lambda → Create Function**  
2. Settings:
   - **Runtime:** Python 3.11  
   - **Function name:** `immowelt-daily-fetch`
3. **Upload** `function.zip` package.  
4. Configure the function:
   - **Memory:** 512 MB (increase if needed)  
   - **Timeout:** 10–15 minutes  
5. Environment variables:
   ```bash
   SECRET_NAME=immowelt-db-secret

---

## 🌐 Step 4 — Database Connectivity (VPC)

Сonnect Lambda  to the PostgreSQL database.
- **If using AWS RDS:**  
Attach the Lambda to the same **VPC**, **Subnet**, and **Security Group** as the RDS instance.  
- **If using an external database:**  
Configure a **VPN / SSH tunnel** or **whitelist the Lambda’s public IP** for secure access.

---

## ⏰ Step 5 — Scheduling (EventBridge)
Open EventBridge → Rules → Create Rule.
Set:
Schedule pattern:
   ```bash
   cron(0 2 * * ? *)   # every day at 02:00 UTC
```
Target: Lambda function `immowelt-daily-fetch`
Save the rule.
✅ Lambda runs automatically every day.

---

## 📜 Step 6 — Logs & Monitoring

1. Open **CloudWatch → Logs → Log groups**.  
2. Locate your log group:
   ```bash
   /aws/lambda/immowelt-daily-fetch

- **Verifing:
The Lambda runs successfully
No database connection errors
Data is inserted correctly into PostgreSQL

---

## 🔁 Step 7 

Add UPSERT logic (to avoid duplicate rows)
Log the number of inserted/updated records
When multiple pipelines or dependencies appear →
migrate to AWS Managed Airflow (MWAA) for orchestration.

---

### ✅ Quick Summary
Step	Action	AWS Service
1	Prepare script & dependencies	Local
2	Store DB credentials securely	Secrets Manager
3	Create Lambda function
4	Connect to database (VPC)	VPC / RDS
5	Schedule daily job	EventBridge
6	Monitor execution	CloudWatch

---

## ⚖️ Pros & Cons of Using AWS Lambda

### ✅ Pros
- Fully serverless — no infrastructure management  
- Integrated with AWS ecosystem (Secrets Manager, EventBridge, CloudWatch)  
- Easy to scale horizontally for multiple pipelines  
- Cost-efficient for small daily jobs (pay only for execution time)
