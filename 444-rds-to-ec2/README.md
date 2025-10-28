# PostgreSQL Migration Research — RDS → Docker on EC2
*by Alexandra Prot, Data Team · Sub-task of **Chore #11: Provision Core Cloud Infrastructure** (refs #444)*

## 🧭 1) Context & Alignment with Core Infrastructure
This research is part of the **Core Cloud Infrastructure** initiative (Epic #11) led by DevOps. The epic provisions:
- **VPC** with public & private subnets across multiple AZs  
- **RDS PostgreSQL + PostGIS** in a private subnet  
- **Security Groups / NACLs** for controlled traffic  
- **NAT Gateway** for secure outbound from private subnets  
- **Bastion Host** (Elastic IP) for SSH access to private resources  
- Proper **tagging / cost tracking**

My task — **[Data Migration #444] Research: PostgreSQL RDS → Docker on EC2** — evaluates whether we keep managed RDS inside that VPC or migrate to a self-managed PostgreSQL container on EC2 (still within the same secure network architecture).

## 🧩 2) My Objective
I am evaluating:
- Feasibility/benefits of moving PostgreSQL from **RDS** to **Docker on EC2**  
- Operational, performance, and security risks within the multi-AZ VPC  
- How this integrates with DevOps deliverables:
  - **Private Subnets:** EC2 with Docker-Postgres
  - **NAT Gateway:** outbound for packages & S3 backups
  - **Security Groups:** inbound only from Bastion + App SG
  - **Bastion Host:** single admin entry (SSH/psql)
  - **Tagging:** `Team=Data, Service=PostgresDocker, Env=Dev/Prod`

## ⚙️ 3) Plan — What I’m Delivering Step by Step
| Phase | My Deliverable | Linked Infra Element |
|------|-----------------|----------------------|
| **1. Research Summary** | RDS vs EC2+Docker, pros/cons, risk matrix | Aligns with RDS plan |
| **2. Migration Scenarios** | Offline (pg_dump/pg_restore) & Online (DMS/Logical Replication) | NAT + Private Subnets |
| **3. Data Artifacts** | Schema dump, migration scripts, validation SQLs | RDS ↔ EC2 |
| **4. Test Environment** | EC2 (private), encrypted gp3 EBS, Dockerized Postgres | SG rules + Bastion |
| **5. Docs & Monitoring** | Playbook, DR plan, Grafana dashboards & alerts | Core Monitoring Stack |

## 🧠 4) Key Findings (TL;DR)
- **Stay on RDS** for lowest operational risk (SLA, Multi-AZ, automated PITR).  
- **Move to EC2+Docker** only if we need custom extensions/tuning/cost control or experimental data pipelines.  
- If migrating, we must own: **Patroni HA**, **pgBackRest/WAL-G** backups (PITR), **KMS/IAM/SG** hardening, **Prometheus/Grafana**, and a tested **DR/PITR** runbook.

## ⚠️ 5) Risks & Mitigation
| Category | Risk | Mitigation |
|---------|------|------------|
| Data | WAL gaps / broken backups | Continuous archiving + scheduled test-restore |
| Security | SG/NACL mistakes, no encryption | Private subnets, KMS, Secrets Manager |
| Operations | Manual patching → downtime | Maintenance window + replica promotion |
| Performance | Not enough IOPS | EBS **gp3/io2** + I/O monitoring |
| HA | No auto-failover | **Patroni** cluster in private subnets |

## 🧰 6) Tools & Integration
| Purpose | Tool | Integration Point |
|--------|------|-------------------|
| Backups | **pgBackRest / WAL-G** | S3 via NAT (outbound only) |
| HA/Failover | **Patroni + PgBouncer** | EC2 in AZ-A/B (private) |
| Monitoring | **Prometheus + Grafana** | Exporters + CloudWatch |
| Migration | **AWS DMS / pg_dump / pg_restore** | RDS → EC2 via private SG rules |
| Security | **KMS / IAM / Secrets Manager** | Encrypted EBS + secret rotation |

## 📋 7) Next Steps (from me)
- [ ] Add `docs/data-migration-rds-to-ec2/migration_to_ec2_docker.md` (offline/online paths)  
- [ ] Add `docs/data-migration-rds-to-ec2/sql/validation_queries.sql` (row counts, aggregates)  
- [ ] (Opt) `docs/data-migration-rds-to-ec2/docker-compose.yml` (official postgres image, PGDATA on EBS)  
- [ ] (Opt) `docs/data-migration-rds-to-ec2/infra/ec2_postgres_example.tf` (tiny Terraform snippet)  
- [ ] Run a test restore RDS → Docker Postgres in a private subnet (through Bastion) and report
