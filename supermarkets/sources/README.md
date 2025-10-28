# 📂 Data Sources for Supermarkets Database

This folder contains the raw and enriched datasets used to populate the `supermarkets` table in the PostgreSQL database.

## 📄 File Overview

### ✅ `supermarkets_raw.csv`
- **Source**: OpenStreetMap (OSM)
- **Content**: Raw export of supermarket POIs in Berlin.
- **Fields**: Includes name, address, coordinates, brand, and limited metadata.
- **Usage**: Used as the starting point for data cleaning and enrichment.

---

### 🗺️ `supermarkets_raw.geojson`
- **Source**: Converted version of the CSV with spatial geometry.
- **Content**: Same as `supermarkets_raw.csv`, but in GeoJSON format.
- **Usage**: Used for spatial joins with neighborhood boundaries.

---

### 🗺️ `lor_ortsteile.geojson`
- **Source**: Berlin’s official administrative boundaries (LOR Ortsteile).
- **Content**: Polygon boundaries of districts and neighborhoods.
- **Usage**: Used to assign each supermarket to a neighborhood/district based on its coordinates.

---

### 📄 `final_supermarkets_with_district.csv`
- **Content**: Fully cleaned and enriched supermarket data.
- **Includes**: Spatial joins, standardized fields, and linked `district_id` and `neighborhood_id`.
- **Usage**: Final dataset used for populating the `supermarkets` database table.

---

## 📝 Notes
- All datasets are UTF-8 encoded.
- The final CSV aligns with the schema in the database and includes foreign key references to the `districts` and `neighborhoods` tables.
