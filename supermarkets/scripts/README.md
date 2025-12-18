# ⚙️ Data Scripts for Supermarkets Project

This folder contains scripts used to process, clean, and insert supermarket data into the database.

## 📜 Script Overview

### 🧪 `supermarkets-data-transforming.ipynb`
- **Purpose**: Main notebook for data preparation and transformation.
- **Steps**:
  1. Load raw supermarket data from `/sources/`
  2. Clean and standardize fields (e.g. brand, address, opening hours)
  3. Perform spatial join with `lor_ortsteile.geojson` to assign districts and neighborhoods
  4. Export final dataset to `final_supermarkets_with_district.csv`

---

### 📁 `cache/`
- **Purpose**: Temporary storage for intermediate files or backups during processing.
- **Note**: This folder is optional and can be excluded from version control (`.gitignore`).

---

## 🛠️ Requirements

Ensure your environment has the following packages installed:
- `pandas`
- `geopandas`
- `sqlalchemy`
- `psycopg2`
- `shapely`
- `notebook` (for Jupyter)

Install all requirements using:

```bash
pip install -r requirements.txt