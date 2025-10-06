#  Clubs & Social Activities in Berlin — Research, Modelling & Data Transformation and Test Loading into PostgreSQL

##  Goal
- Build a dataset of clubs and social activities in Berlin.
- Clean and filter data from OpenStreetMap.
- Normalize the attributes to match a planned database schema.
- Perform a **test load into PostgreSQL** (`test_berlin_data` schema).

---

##  Process Overview

### 1. Library Imports & Configuration
- **Main libraries:** `pandas`, `geopandas`, `osmnx`, `sqlalchemy`, `psycopg2`, `shapely`.
- Configured PostgreSQL connection via **SQLAlchemy + psycopg2**.

---

### 2. Data Collection from OpenStreetMap (OSM)
- Queried **OpenStreetMap** with `osmnx.features_from_place("Berlin, Germany", tags={...})`.
- **Extracted features** using tags:
    - `club=*`
    - `leisure=*`
    - `sport=*`
    - `amenity=*`
- **Filtering Applied:**
    - **Excluded** categories: theaters, bars, cafes, pubs, restaurants, night_clubs.

---

### 3. Data Cleaning & Preparation
- **Selected and standardized attributes:**
    - `club_id`, `name`, `club`, `leisure`, `sport`, `amenity`,
    - `street`, `housenumber`, `postcode`,
    - `website`, `phone`, `email`, `opening_hours`,
    - `wheelchair`, `geometry`
- **Coordinate Calculation:** Calculated coordinates (`latitude`, `longitude`) from `geometry`.
- **Geospatial Join (Enrichment):** Joined with **districts and neighborhoods** (`lor_ortsteile.geojson`) to add:
    - `district`, `district_id`, `neighborhood`, `neighborhood_id`.

---

### 4. Address Enrichment & Validation
- **Missing Data:** Initial OSM data contained many `NULL` values in `street` and `housenumber`.
- **Enrichment Test:** **Nominatim reverse geocoding** was tested to build a `full_address` and fill missing values.
- **Data Validation:**
    - Checked **string lengths** per column to define correct SQL column sizes (VARCHAR length, TEXT fields, etc.).
    - Adjusted schema accordingly (e.g., longer fields for `website`, `full_address`, `opening_hours`).

---

### 5. Database Schema (Planned)
```sql
CREATE TABLE IF NOT EXISTS test_berlin_data.clubs (
    club_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200),
    club VARCHAR(100),
    leisure VARCHAR(100),
    sport VARCHAR(100),
    amenity VARCHAR(100),
    street VARCHAR(200),
    housenumber VARCHAR(50),
    postcode VARCHAR(20),
    website VARCHAR(250),
    phone VARCHAR(100),
    email VARCHAR(150),
    opening_hours TEXT,
    wheelchair VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    district VARCHAR(100),
    neighborhood_id VARCHAR(100),
    neighborhood VARCHAR(100),
    full_address TEXT,
    district_id VARCHAR(100),
    geometry TEXT, 	-- stored as Well-Known Text (WKT)
    CONSTRAINT district_id_fk FOREIGN KEY (district_id)
        REFERENCES test_berlin_data.districts(district_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
```

---
### **6. Test Loading into PostgreSQL**
- **Geometry Conversion:** `shapely Point` objects were converted into **WKT (Well-Known Text)** strings so they could be inserted into the `TEXT` column.
- **Loading:** The transformed `DataFrame` was loaded into PostgreSQL with the `.to_sql()` method.
- **Verification:** The data insertion into `test_berlin_data.clubs` was verified as correct.

---

## **Current Status**
- Data successfully **extracted, filtered, and normalized**.
- First **test load into PostgreSQL completed** and verified.
