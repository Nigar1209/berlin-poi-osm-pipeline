

<img width="1206" height="747" alt="Screenshot 2025-11-13 at 9 37 11 PM" src="https://github.com/user-attachments/assets/324c22a7-3481-41e2-abb5-cf33ed7035f9" />


### 🏡 1. Data Source — Immowelt

* **Immowelt** is the source website where real estate listings are scraped.
* The scraper script (likely written in Python) extracts listing details such as:
  - Price
  - Address
  - Description

---

### ⚙️ 2. GitHub Actions — Automation and Scraping

* A **GitHub Action** is scheduled (daily or weekly) to:

  1. **Run the scraping script** to collect the latest listings from Immowelt.
  2. **Transform and save the data** into a **Parquet file** (a compact, columnar format ideal for analytics).
  3. **Upload the Parquet file to AWS S3** for persistent storage.

* This ensures the scraping and storage process runs automatically without manual intervention.

---

### ☁️ 3. AWS Infrastructure (Provisioned by Terraform)

* **Terraform** defines and deploys the required AWS infrastructure:

  - **S3 bucket**: Stores scraped Parquet files
  - **Lambda function**: Processes and inserts data
  - **PostgreSQL database**: Hosted via AWS RDS or similar

* Infrastructure is version-controlled, reproducible, and easy to maintain.

---

### 📦 4. S3 — Data Storage

* Each time the GitHub Action runs, it **uploads a new Parquet file** to S3.
* Each file represents a snapshot of scraped listings (daily/weekly).

---

### 🧠 5. AWS Lambda — Data Sync Logic

* The **Lambda function** is triggered (either on a schedule or by S3 upload event) and performs:

  1. **Read the new Parquet file** from S3.
  2. **Load the data** and compare against existing records in **PostgreSQL** (`berlin_source_data` table).
  3. **Identify new listings** or changes (e.g., new property IDs).
  4. **Append only new rows** to PostgreSQL to avoid duplicates.

---

### 🗃️ 6. PostgreSQL — Central Data Repository

* The **PostgreSQL database** (`berlin_source_data`) holds the curated listings.
* Over time, it accumulates a historical record for downstream analytics, dashboards, or data science work.

---

### 🔄 Summary Flow

1. **GitHub Action** → Scrapes Immowelt → Saves Parquet → Uploads to **S3**  
2. **AWS Lambda** → Reads Parquet → Compares with **PostgreSQL** → Appends new listings  
3. **Terraform** → Manages AWS infrastructure for S3, Lambda, and PostgreSQL

