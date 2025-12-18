# 🏋️‍♂️ Gyms Data Layer – Scripts Overview

This directory contains the scripts and notebooks for fetching, transforming, spatially joining, and importing **Berlin gym locations** into the database as part of the Data Foundation (EPIC 2).

---

## **Project Workflow & File Structure**

### `gyms/scripts/1_get_osm_gyms.py`

**Purpose:**
Fetches raw gym data for Berlin from [OpenStreetMap](https://www.openstreetmap.org/) using the Overpass API and exports it as a CSV.

* **Input:** None (fetches directly from OSM)
* **Output:** `gyms/sources/gyms_osm_berlin_<date>.csv`
* **Key Steps:**

  * Downloads gym POIs for Berlin.
  * Stores all available attributes, coordinates, and tags.

---

### `gyms/scripts/2_gyms_data_transformation.ipynb`

**Purpose:**
Cleans, transforms, and enriches the raw OSM gym data, assigning each gym a district and (optionally) a neighborhood, and outputs a ready-to-import CSV.

* **Input:**

  * `gyms/sources/gyms_osm_berlin_<date>.csv` (from Script 1)
  * `gyms/sources/berlin_districts.geojson` (for district assignment)
  * `gyms/sources/berlin_neighborhood.geojson` (for neighborhood assignment, optional)
* **Output:** `gyms/sources/gyms_with_district.csv`
* **Key Steps:**

  * Cleans and normalizes OSM gym data (column mapping, fixing address, types, missing values, etc.)
  * Performs **spatial join** using GeoPandas to assign each gym to its corresponding district (and optionally neighborhood).
  * Prepares all fields to match the final DB schema, including correct data types and column order.
  * Exports the final, validated CSV for database import.

---

### `gyms/scripts/3_import_gyms_to_postgres.py`

**Purpose:**
Imports the cleaned and enriched gym data into your target PostgreSQL/PostGIS database.

* **Input:** `gyms/sources/gyms_with_district.csv`
* **Database Table:** `gyms` (schema and constraints defined in the script)
* **Key Steps:**

  * Reads the CSV, cleans up leftover/duplicate columns.
  * **Truncates the `gyms` table** before each import (all previous data will be lost!).
  * Ensures data types and columns match the table structure.
  * Inserts data in chunks for memory safety.
  * (Optionally) adds and updates a geometry column for PostGIS spatial features.
* **Caution:**

  * Edit your DB credentials at the top of the script before running.
  * The import script assumes the district foreign key table (usually `test_berlin_data.districts`) already exists in your DB.

---

## **Full End-to-End Pipeline (How to Run)**

1. **Download latest gyms from OSM:**

   ```
   python gyms/scripts/1_get_osm_gyms.py
   ```
2. **Clean, enrich, and spatially join data in Jupyter Notebook:**

   * Open `gyms/scripts/2_gyms_data_transformation.ipynb` in Jupyter.
   * Run all cells to produce a clean `gyms_with_district.csv`.
3. **Import into Postgres DB:**

   ```
   python gyms/scripts/3_import_gyms_to_postgres.py
   ```

   * **All existing data in the `gyms` table will be deleted on each run!**

---

## **Key Field Mapping & Schema**

| OSM Field        | DB Field           | Example               | Notes                                  |
| ---------------- | ------------------ | --------------------- | -------------------------------------- |
| name             | name               | "McFit Tempelhof"     |                                        |
| leisure/sport    | type               | "fitness_centre/yoga" | Use "leisure" if present, else "sport" |
| addr:street      | street             | "Sonnenallee"         |                                        |
| addr:housenumber | housenumber        | "123"                 |                                        |
| addr:postcode    | postcode           | "12045"               |                                        |
| phone            | phone_number       | "+49 30 123456"       |                                        |
| osm_id           | gym_id             | 308190832             | Becomes primary key in DB              |
| latitude/lon     | latitude/longitude | 52.4923/13.4247       |                                        |
| (assigned)       | district_id        | 11004004              | From spatial join with districts       |
| (assigned)       | neighborhood       | "Prenzlauer Berg"     | From spatial join with neighborhoods   |

**Full DB table:**

```sql
CREATE TABLE IF NOT EXISTS gyms (
    gym_id VARCHAR(20) PRIMARY KEY,
    district_id VARCHAR(20),
    name VARCHAR(200),
    address VARCHAR(200),
    postal_code VARCHAR(10),
    phone_number VARCHAR(50),
    email VARCHAR(100),
    coordinates VARCHAR(200),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    neighborhood VARCHAR(100),
    district VARCHAR(100),
    CONSTRAINT district_id_fk FOREIGN KEY (district_id)
        REFERENCES test_berlin_data.districts(district_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
```

---

## **Quality Checks & Validation**

* No duplicate rows.
* All gyms have valid coordinates in Berlin.
* Row counts align with raw source and CSV.
* All key columns match expected names/types.
* All foreign keys and spatial joins work as intended.
* Final notebook includes Markdown documentation and explains all key steps, mappings, and assumptions.

---

## **Further Information**

* See [`MAPPING_OSM_GYM_TABLE.md`](../MAPPING_OSM_GYM_TABLE.md) for a detailed field mapping and transformation strategy.
* The data transformation pipeline is **fully reproducible**. To update the DB, simply rerun all steps in order with new OSM data.

---

**Contact:**
[Last update: 2025-09-26]

---

**Ready for further data layer integration and frontend use!**
