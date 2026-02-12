# OSM Table Generator Configuration

This directory contains the foundational configuration files for a dynamic, metadata-driven OpenStreetMap (OSM) data pipeline. By utilizing these JSON configurations, the system can automatically generate PostgreSQL tables and fetch specific spatial layers from the Overpass API without requiring hardcoded logic for every new category.

## ⚠️ Important Note
**This module is currently configuration-only.** This task focuses on establishing the schema definitions and table metadata. It does **not** yet include the Airflow DAG implementation or the Python logic for data extraction.

---

## Configuration Files

### 1. core_columns.json
This file defines the "Skeleton" of every table in the database. 
- **must_columns**: Essential fields for database integrity, including the primary key (`id` as `VARCHAR`) and PostGIS spatial data (`geometry`).
- **common_columns**: Metadata that is consistently available across most Berlin OSM layers, such as Names, Coordinates (DECIMAL), District/Neighborhood info, and standardized Address details.

### 2. osm_tables.json
This file defines the specific "Layers" (e.g., Bakeries, Hospitals, Museums) we want to extract.
- **table_name**: The target table name in the database (lowercase, snake_case).
- **tags**: An array of OSM keys and values defining the search criteria. 
    - Multiple objects in the array are treated as an **AND** operation (e.g., `shop=bakery` AND `bakery=yes`).
    - An array of values (e.g., `["hotel", "hostel"]`) is treated as an **OR** operation.
- **unique_columns**: Fields specific only to that layer, defined with their appropriate PostgreSQL data types.

---

## How to add a new table in the future
To extend the pipeline to a new data layer (e.g., "Cinemas"):
1. Open `config/osm_tables.json`.
2. Append a new object to the `tables` array:
   ```json
   {
     "table_name": "cinemas",
     "tags": [{ "key": "amenity", "value": "cinema" }],
     "unique_columns": [
       { "name": "screens", "type": "INTEGER" },
       { "name": "cinema_type", "type": "VARCHAR(50)" }
     ]
   }