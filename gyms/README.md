# 🏋️‍♂️ Berlin Gyms Data Pipeline

This repository contains all scripts, notebooks, and data sources for the **ETL pipeline to extract, clean, enrich, spatially join, and import gyms and fitness studio data for Berlin** as part of the [layered-populate-data-pool-da](../) project.

---

## 🚦 Workflow Overview

1. create a .env with your credentials for the dev database on AWS
2. **Extract gyms** from OpenStreetMap (OSM) using the Overpass API  
3. **Clean, normalize, and spatially join** OSM data to Berlin's districts and neighborhoods  
4. **Produce final, database-ready CSV** (including district & neighborhood foreign keys)  
5. **Import gyms** into a Postgres/PostGIS (or NeonDB) database  
6. **QA validation:** Automated SQL-based checks for completeness, duplicates, spatial coverage

**See [`scripts/README.md`](./scripts/README.md) for detailed descriptions of each script and workflow step.**

---

## 📁 Directory Structure

```text
gyms/
├── scripts/
│   ├── 1_get_osm_gyms.py                # Download gyms from OSM (Overpass API)
│   ├── 2_gyms_data_transformation.py    # Clean, enrich, and spatial join (can also be .ipynb)
│   ├── 3_import_gyms_to_neondb.py       # Import cleaned gyms into NeonDB/Postgres
│   ├── 3_1_test.py                      # Data QA & validation checks after import
│   ├── 4_import_gyms_to_layereddb.py    # Import to local PostGIS/dev database
│   ├── MAPPING_OSM_GYM_TABLE.md         # Full OSM→DB field mapping/specification
│   └── requirements.txt                 # Python dependencies
├── sources/
│   ├── berlin_districts.geojson         # Official Berlin district boundaries
│   ├── berlin_neighborhood.geojson      # Official neighborhood (Ortsteil) boundaries
│   ├── gyms_osm_berlin_<date>.csv       # Raw OSM gym export (timestamped)
│   ├── gyms_with_district_and_neighborhood.csv # Cleaned, enriched gyms with spatial info
│   ├── gyms_db_ready_final.csv          # Final import-ready dataset
│   └── README.md                        # Documentation for all source files
└── README.md                            # This file

---

## 🚀 Quickstart: Run the Gyms ETL Pipeline

```bash
# (Optional, but recommended) Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all required dependencies
pip install -r gyms/scripts/requirements.txt

# 1️⃣ Download gyms from OSM Overpass API
python gyms/scripts/1_get_osm_gyms.py

# 2️⃣ Clean, transform, and spatially join data (Python script or Jupyter Notebook)
python gyms/scripts/2_gyms_data_transformation.py

# 3️⃣ Import gyms into your database
python gyms/scripts/3_import_gyms_to_neondb.py

# 4️⃣ (Optional) Run QA/validation checks after import
python gyms/scripts/3_1_test.py

# import to dev database:
python gyms/scripts/4_import_gyms_to_layereddb.py
---

🗺️ Data Sources

OpenStreetMap (OSM):
All gyms, fitness studios, and yoga venues for Berlin, queried via the Overpass API.

GeoJSON boundaries:
Official Berlin district (berlin_districts.geojson) and neighborhood (berlin_neighborhood.geojson) polygons for spatial enrichment.

---

🧩 Field Mapping & Schema

See scripts/MAPPING_OSM_GYM_TABLE.md
 for a detailed column-by-column field mapping (OSM → DB).

Target table: gyms
(The schema is fully defined in the transformation scripts and import scripts.)

---

📝 Notes

The scripts/Backup/ folder is excluded from GitHub and used only for local/legacy backups.

All cleaning, enrichment, and spatial join logic is fully documented in code and notebooks.

This pipeline is fully reproducible: re-run the scripts with new OSM data any time for a fresh import.

Intermediate and output files are described in sources/README.md

---

**copy in your .env-file and insert your credentials**
'''
DB_USER_layereddb=your_username
DB_PASS_layereddb=your_passwort
'''

