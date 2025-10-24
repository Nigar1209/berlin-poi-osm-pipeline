This repository contains the code, data sources, and files used to populate a database with multiple layers of Points of Interest (POIs). Each layer represents a different category or type of POI, allowing for structured, scalable data population. <br>

You can find the current ERD here : [ERD](https://lucid.app/lucidchart/136abd83-b883-43f1-a957-110f5ba18ca7/edit?invitationId=inv_aa66297e-15c3-444c-b8b2-5496c4a9c1c8&page=0_0)

## Automation: Immowelt Hourly Test Workflow

This repo includes a minimal GitHub Actions workflow as a stepping stone towards automating the Immowelt long-term listings scraper.

**Location**
- **File:** `.github/workflows/immowelt-hourly-test.yml`
- **Workflow name (Actions tab):** `immowelt-hourly-test`
- Initially added on branch  
  `393-data-integration-automating-immowelt-scraper-step-2-preliminary-research-on-automation-with-github-actions`

**What it does**
- Provides a **manual trigger** (`workflow_dispatch`) to verify the CI environment.
- Defines an **hourly schedule** (`cron: "17 * * * *"`, UTC).  
  > GitHub runs scheduled workflows **only from the default branch** (usually `main`).  
  > The schedule becomes active after this file is merged into `main`.

**How to run manually (before merge)**
1. Open **Actions → immowelt-hourly-test → Run workflow**.  
2. Select the feature branch above and click **Run**.  
3. The job prints a UTC timestamp so you can confirm execution.

**Next steps**
- Open a PR to `main` (refs `#393`, parent `#392`).  
- After merge, verify the first scheduled run.  
- Add a small Python script that appends a `timestamp` row to a test NeonDB table.  
- Store DB creds as repo secrets in **Settings → Secrets and variables → Actions** (e.g., `NEON_DB_URL`).
