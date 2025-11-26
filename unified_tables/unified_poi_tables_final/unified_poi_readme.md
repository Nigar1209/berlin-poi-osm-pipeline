# 🗺️ Unified POI Table

A comprehensive data pipeline for consolidating Berlin's Point of Interest (POI) data into a single unified table with spatial indexing and nearest-neighbor analysis.

---

## 📋 Table of Contents

1. [🏗️ Schema Definition](#schema-definition)
2. [🧹 Data Cleaning](#data-cleaning)
3. [🔄 Pipeline Overview](#pipeline-overview)
4. [⚙️ Implementation Details](#implementation-details)

---

## 🏗️ Schema Definition

All tables in the pipeline follow a standardized schema to ensure consistency and compatibility with the unified POI table.

### 📊 Common Column Schema

```sql
id VARCHAR(20) PRIMARY KEY,                 -- Numeric only, no letters
district_id VARCHAR(20) NOT NULL,           -- Mapped from district name
name VARCHAR(200) NOT NULL,                 -- Defaults to 'Unknown' if NULL
latitude DECIMAL(9,6),                      
longitude DECIMAL(9,6), 
geometry VARCHAR,                           -- POINT() format
neighborhood VARCHAR(100),                  -- Joined from neighborhoods table
district VARCHAR(100),                      -- From lor_ortsteile.geojson
neighborhood_id VARCHAR(20),                -- From lor_ortsteile.geojson
CONSTRAINT district_id_fk 
  FOREIGN KEY (district_id)
  REFERENCES berlin_data.districts(district_id) 
  ON DELETE RESTRICT ON UPDATE CASCADE
```

---

## 🧹 Data Cleaning

Before consolidation, all source tables were standardized to meet the common schema requirements.

### 📝 Renaming Tables

Renamed to layer names for clarity:
```sql
ALTER TABLE berlin_source_data.hospitals_refactored RENAME TO hospitals;
```

### 🔤 Renaming Columns

Standardized column naming conventions:
```sql
ALTER TABLE berlin_source_data.food_markets RENAME COLUMN market_id TO id;
```

### 🔢 Data Type Conversions

Corrected inconsistent data types:
```sql
ALTER TABLE berlin_source_data.short_term_listings 
  ALTER COLUMN id TYPE varchar(20) USING id::varchar(20);

ALTER TABLE berlin_source_data.short_term_listings 
  ALTER COLUMN "name" TYPE varchar(200) USING "name"::varchar(200);
```

### ➕ Adding Missing Columns

For tables without latitude/longitude data:
```sql
ALTER TABLE berlin_source_data.bike_lanes ADD latitude varchar NULL;
ALTER TABLE berlin_source_data.bike_lanes ADD longitude varchar NULL;
```

### 🔍 Data Enrichment & Corrections

A dedicated Jupyter notebook (`table_corrections`) handles:
- **🏘️ Missing neighborhood_id**: Joined neighborhood names to the neighborhoods lookup table
- **📍 Missing geometry**: Generated POINT() format from latitude/longitude coordinates
- **🌍 Missing neighborhood/district data**: Used Nominatim API for geocoding and joined to lookup tables
- **🔧 Inconsistent district IDs**: Corrected outdated district numbering
- **📋 Incomplete records**: Recreated short_term_listings table to include name column

---

## 🔄 Pipeline Overview

The unified POI table creation process is implemented in `create_unified_poi_table.py` and consists of five sequential steps.

### 🛠️ Architecture

- **Language**: Python with SQLAlchemy
- **Database**: PostgreSQL with PostGIS
- **Pattern**: Single transaction (`engine.begin()`) for atomicity and performance

---

## ⚙️ Implementation Details

### ✅ Step 1: Validation

Creates an `excluded_tables_log` table to identify invalid tables before processing.

**Validation Checks**:
- ✔️ All required columns present
- ✔️ Correct data types applied
- ✔️ Non-nullable columns contain no NULL values
- ✔️ Primary key constraint on `id` column
- ✔️ Foreign key constraint on `district_id` column

**Process**:
- `all_tables` CTE: Selects all tables except districts and neighborhoods
- `expected_schema` CTE: Defines the standard schema structure
- `missing_columns` CTE: Identifies missing required columns
- `datatype_issues` CTE: Detects incorrect data types
- `null_issues` CTE: Flags NULL values in non-nullable columns
- `pk_issues` CTE: Checks for missing PRIMARY KEY constraints
- `fk_issues` CTE: Checks for missing FOREIGN KEY constraints

Tables failing validation are logged and excluded from processing.

### 📦 Step 2: Table Creation

Creates two tables for the pipeline:

**unified_pois**
```sql
poi_id VARCHAR(50) PRIMARY KEY,             -- [layer_prefix]-[original_id]
name VARCHAR(200),  
layer VARCHAR(100),                         -- Source table name
district_id VARCHAR(20),
district VARCHAR(100),
neighborhood_id VARCHAR(20),
neighborhood VARCHAR(100),
latitude DECIMAL(9,6),
longitude DECIMAL(9,6),
geometry GEOMETRY, 
attributes JSONB,                           -- Non-standard columns
nearest_pois JSONB                          -- Nearest POI per layer
```

**processed_tables_log**
- 📝 Tracks which tables have been successfully added to unified_pois

### 🎯 Step 3: Table Selection

Queries `berlin_source_data` schema to identify valid tables:
- 🚫 Excludes districts and neighborhoods reference tables
- 🚫 Excludes tables in `excluded_tables_log`

### 🔗 Step 4: Data Consolidation & Enrichment

For each valid table:

1. **📊 Data Transformation**
   - Generates unique `poi_id` by concatenating layer prefix and original ID
   - Ensures geometry is in correct SRID (4326)
   - Serializes non-standard columns into JSONB `attributes`

2. **🔀 Union All**
   - Combines all transformed tables into single dataset

3. **🎯 Nearest Neighbor Analysis** (long_term_listings only)
   - For each listing, calculates the nearest POI across all other layers
   - Creates JSONB object with:
     - 🏷️ POI ID, name, and distance
     - 🏠 Street and house number from attributes
   - Populates `nearest_pois` column

4. **💾 Data Insertion**
   - Inserts consolidated POIs into `unified_pois`
   - Logs processed tables in `processed_tables_log`

### 🚀 Step 5: Spatial Indexing

Creates a GIST spatial index on the `geometry` column for optimized spatial queries:

```sql
CREATE INDEX idx_poi_geom ON unified_pois USING GIST (geometry);
```

---

## ⚡ Performance Notes

- ⚡ Single transaction ensures atomicity and minimizes connection overhead
- 🏃 Spatial index enables fast distance-based queries
- 🔧 JSONB attributes provide flexible schema extension
- 📐 Nearest neighbor calculations use PostGIS distance operators for efficiency

---

## 🚀 Usage

```python
python create_unified_poi_table.py
```

The script will:
1. ✅ Validate all source tables
2. ✅ Create fresh unified_pois and logging tables
3. ✅ Process all valid tables
4. ✅ Generate spatial index
5. ✅ Print progress at each step
