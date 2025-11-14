# 🏛️ Berlin Libraries Database Integration

This document outlines the **database population and integration process** for the **Berlin Libraries Dataset**, derived primarily from **OpenStreetMap (OSM)** and enriched with administrative boundaries and contextual metadata.  
It summarizes the **data cleaning, transformation, spatial enrichment**, and the **rationale** behind the final SQL schema design with referential integrity constraints.

---

## 🧹 1. Cleaning, Transformation, and Spatial Mapping Summary

To prepare **148 library records** for reliable database ingestion, several structured data processing steps were executed.

| **Step** | **Action Taken** | **Rationale** |
|-----------|------------------|---------------|
| **Initial Cleaning** | Standardized text casing, unified all `amenity` tags as `'library'`, and replaced empty or placeholder values with proper `NaN` values. | Ensures data consistency and enables accurate enforcement of `NOT NULL` constraints. |
| **Data Transformation** | Consolidated multiple contact fields (`phone:`, `email:`) into `final_phone` and `final_email`; converted `latitude` and `longitude` to `NUMERIC(9, 6)`. | Streamlines the schema and aligns data types with the SQL table definition. |
| **Spatial Mapping (Enrichment)** | Performed a spatial join using PostGIS/GeoPandas to map each library’s coordinates to its corresponding **Berlin district and neighbourhood**, populating the `district_id` field. | Enriches data with administrative context, enabling analysis by district. |
| **Final Quality Check** | Filled the two missing `name` fields with placeholders based on ID/district; verified all `district_id` values conform to the 8-digit ASGS format used in the parent `districts` table. | Guarantees compliance with `NOT NULL` and `FOREIGN KEY` constraints and supports relational integrity. |

---

## ⚙️ 2. Key Assumptions and Caveats

| **Aspect** | **Assumption / Note** |
|-------------|------------------------|
| **Coordinate Accuracy** | OSM-derived `latitude` and `longitude` values are assumed sufficiently accurate for reliable spatial joins with official Berlin district boundaries. |
| **District ID Consistency** | The `district_id` values match the 8-digit **Statutory District Keys (ASGS)** in the parent table `berlin_data.districts`. |
| **Data Completeness** | Two missing `name` values were filled with placeholders. For semantic accuracy, these records may require later manual verification. |

---

## 🧩 3. Rationale for Constraint Design

The final schema uses strong constraints to preserve **data quality**, **relational integrity**, and **referential logic** within the database.

### **Primary Key & Not Null Constraints**
- `PRIMARY KEY (library_id)` ensures uniqueness and prevents duplicate entries.
- `NOT NULL` constraints on key fields (`name`, `district_id`, `latitude`, `longitude`, `postcode`, etc.) guarantee that critical information is always available for spatial and statistical analysis.

### **Foreign Key Constraint**

Links the libraries table to the parent `districts` table:

```sql
CONSTRAINT district_id_fk
    FOREIGN KEY (district_id)
    REFERENCES berlin_data.districts(district_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

---

| **Clause**                                      | **Rationale & Purpose**                                                                                                         |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `REFERENCES berlin_data.districts(district_id)` | Ensures every library record belongs to a valid, existing district — maintaining **referential integrity**.                     |
| `ON DELETE RESTRICT`                            | Prevents deletion of a district if linked libraries exist, avoiding orphaned library records.                                   |
| `ON UPDATE CASCADE`                             | Automatically updates the `district_id` in the libraries table if the parent district key changes, maintaining synchronization. |

---
🗄️ 4. Integration Outcome

After applying all cleaning, enrichment, and validation steps:

✅ 148 libraries successfully matched to valid Berlin districts.

✅ Schema fully aligned with PostgreSQL + PostGIS standards.

✅ Referential integrity enforced through PRIMARY KEY and FOREIGN KEY constraints.

✅ Ready for spatial querying, visualization (QGIS, GeoPandas), and analytics.

---
📂 SQL Schema

CREATE TABLE IF NOT EXISTS berlin_data.libraries (
    library_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    amenity VARCHAR(50) NOT NULL,
    operator_type VARCHAR(50),
    operator VARCHAR(255),
    street VARCHAR(150),
    housenumber VARCHAR(10),
    postcode VARCHAR(10) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(5) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    district_id VARCHAR(8) NOT NULL,
    district VARCHAR(50) NOT NULL,
    neighbourhood VARCHAR(50),
    final_email VARCHAR(255),
    final_phone VARCHAR(50),
    website_url VARCHAR(255),
    opening_hours VARCHAR(255),
    isil_code VARCHAR(50),
    wheelchair_accessible VARCHAR(10),
    toilets_wheelchair VARCHAR(10),
    internet_access VARCHAR(50),
    "level" VARCHAR(10),
    geom_point GEOMETRY(Point, 4326),
    CONSTRAINT district_id_fk
        FOREIGN KEY (district_id)
        REFERENCES berlin_data.districts(district_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
