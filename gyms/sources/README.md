# 📂 gyms/sources – Source Data Overview

This folder contains all **raw, reference, and intermediate data files** used and generated during the Berlin gyms data pipeline.

---

## **Contents & Structure**

| File Name                                    | Type     | Description                                                                                  |
|-----------------------------------------------|----------|----------------------------------------------------------------------------------------------|
| `berlin_districts.geojson`                   | GeoJSON  | Berlin district boundaries, for spatial join assigning each gym to a district                |
| `berlin_neighborhood.geojson`                | GeoJSON  | Berlin neighborhood ("Ortsteil") boundaries, for more granular spatial assignment (optional) |
| `gyms_osm_berlin_<date>.csv`                 | CSV      | Raw gym export from OSM Overpass API (Script 1), date = extraction day                      |
| `gyms_with_district_and_neighborhood.csv`     | CSV      | Cleaned, transformed, spatially joined data (district + neighborhood assigned, Script 2)    |
| `gyms_db_ready_final.csv`                    | CSV      | Final DB-ready CSV, matches DB schema exactly (Script 3)                                    |
| `README.md`                                  | Markdown | This file: overview and file documentation                                                   |

---

## **Data Lifecycle & Pipeline**

1. **Raw Download (Script 1):**
   - `gyms_osm_berlin_<date>.csv`
   - All Berlin gyms (fitness, yoga, etc.) fetched from OSM, all available tags and coordinates.

2. **Spatial Enrichment & Cleaning (Script 2):**
   - `berlin_districts.geojson` & `berlin_neighborhood.geojson` are used to assign district and (optionally) neighborhood to each gym.
   - `gyms_with_district_and_neighborhood.csv`
   - Data is normalized, types mapped, all fields aligned to DB schema.

3. **Database Import Preparation (Script 3):**
   - `gyms_db_ready_final.csv`
   - Output is a **1:1 match** for the target database, ready for ETL import.

---

## **How are these files generated?**

- All files are produced by running the pipeline scripts in `/gyms/scripts/`.
- The process is **fully reproducible**; simply re-run the scripts to refresh with new data or update outputs.

**For detailed workflow instructions, see the [README in the scripts folder](../scripts/README.md).**

---

## **GeoJSON Reference Files**

### `berlin_districts.geojson`
- Polygons for Berlin's districts (Bezirke)
- Key properties:  
  - `Gemeinde_name` (district name, e.g. "Reinickendorf")
  - `Schluessel_gesamt` (unique district ID, used as FK in DB)
- Used for assigning gyms to a district via spatial join

### `berlin_neighborhood.geojson`
- Polygons for Berlin's neighborhoods (Ortsteile)
- Key properties:  
  - `spatial_name` or `OTEIL` (neighborhood ID, e.g. "0101")
  - `spatial_alias` (neighborhood name, e.g. "Mitte")
  - `BEZIRK` (parent district)
- Used for assigning gyms to neighborhoods (optional, for more detail)

---

## **CSV Data Files**

### `gyms_osm_berlin_<YYYY-MM-DD>.csv`
- Raw export from OSM Overpass API
- All gym-related tags, POI fields, coordinates
- Input for cleaning & transformation

### `gyms_with_district_and_neighborhood.csv`
- Cleaned, normalized, and spatially joined data (district, neighborhood assigned)
- All fields mapped and ready for import prep

### `gyms_db_ready_final.csv`
- Final output: columns, types, and rows exactly match the target DB table
- Import directly with SQL/ETL scripts

---

## **FAQ**

- **Can I delete or overwrite these files?**  
  Yes! Just re-run the ETL scripts in sequence to regenerate everything.

- **How do I refresh with new gyms data?**  
  Run `1_get_osm_gyms.py`, then the rest of the scripts as usual.

- **What do I need for DB import?**  
  Only the final file (`gyms_db_ready_final.csv`) is needed for a clean import; other files are intermediate or reference data.

---

## **Notes**

- All files use UTF-8 encoding and WGS84/EPSG:4326 unless noted otherwise.
- Large/intermediate/backup files should not be pushed to git (see `.gitignore`).

---

_Last updated: 2025-10-06_
