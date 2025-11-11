# Government Offices in Berlin - Data Transformation & Schema Design

## 📋 Project Overview

This project transforms raw OpenStreetMap (OSM) data of government and administrative offices in Berlin into a clean, structured dataset ready for database integration. The process includes data fetching, cleaning, geocoding, spatial enrichment, and schema design.

**Final Output:** 419 government offices with complete geographic and administrative information

---

## 🗂️ Project Structure

```
/scripts
  └── government_offices_data_transformation.ipynb
  └── README.md
/sources
  └── lor_ortsteile.geojson (Berlin districts/neighborhoods)
```

---

## 🔄 Data Pipeline

### 1. **Data Discovery & Fetching**
- **Source:** OpenStreetMap via OSMnx library
- **Query Tags:** `office=government`, `office=administrative`, `amenity=townhall`, `amenity=public_building`, `office=employment_agency`
- **Initial Result:** 441 entries with 177 columns
- **Filter:** Focused on German administrative offices (Bürgeramt, Finanzamt, etc.)

### 2. **Data Consolidation**
- **Column Merging:** Consolidated duplicate information across sparse OSM columns
  - `name` ← `name:de`, `name:en`, `official_name`
  - `opening_hours` ← `opening_hours:signed`
  - `website` ← `contact:website`
  - `phone_number` ← `contact:phone`, `phone`
  - `email` ← `contact:email`

### 3. **Standardization**
- **Column Mapping:** Renamed OSM columns to schema-aligned names (e.g., `addr:street` → `street`)
- **Structure:** Reduced from 177 to 16 core columns
- **Naming Convention:** snake_case format

### 4. **Geo-Enrichment**
- **Source:** Berlin LOR (Lebensweltlich Orientierte Räume) - `lor_ortsteile.geojson`
- **Process:** Spatial join to assign district/neighborhood to each office
- **Added Fields:**
  - `district` (12 Berlin districts)
  - `neighborhood` (97 neighborhoods)
  - `district_id` (8-digit official codes)
  - `neighborhood_id`
- **Data Quality:** Removed 21 offices outside boundaries or without names (441 → 420 rows)

### 5. **Coordinate Extraction**
- Extracted `latitude` and `longitude` from Point geometries
- Set `coordinate_type` to 'point'
- **Coverage:** 100% coordinate availability

### 6. **Address Construction**
- **Strategy 1:** Reverse geocoding via Nominatim API (63.8% success - 268 offices)
- **Strategy 2:** Fallback construction from components (74.5% success - 313 offices)
- **Final Coverage:** 89.5% (376/420 offices have complete addresses)
- **Format:** `"Street Housenumber, Postal_code City"`

### 7. **Geospatial Validation**
- **CRS:** Verified EPSG:4326 (WGS84)
- **Geometry Validation:** Fixed 1 multipart geometry (420 → 421 rows)
- **Duplicate Removal:**
  - Exact duplicates by `office_id`: 421 → 420 rows
  - Near-duplicates (within 10m): 420 → 419 rows
- **Final Status:** All valid, single-part Point geometries

---

## 📊 Final Dataset

### Statistics
- **Total Records:** 419 government offices
- **Total Columns:** 19
- **CRS:** EPSG:4326 (WGS84)
- **Geometry Type:** Point (100%)

### Data Completeness

| Completeness Level | Fields | Count |
|-------------------|--------|-------|
| **High (≥70%)** | office_id, office_name, district, neighborhood, district_id, neighborhood_id, address, postal_code, city, geometry | 10 |
| **Medium (40-70%)** | latitude, longitude, coordinate_type, website, office_type, wheelchair_accessible | 6 |
| **Low (<40%)** | opening_hours, phone_number, email | 3 |

---

## 🗄️ Database Schema

### Table: `government_offices_in_berlin`

**Design Decision:** Single table structure (optimal for 419 records)

#### Schema Highlights
- **Primary Key:** `office_id` (BIGINT)
- **Foreign Keys:** `district_id` → `berlin_districts(district_id)`
- **NOT NULL Fields:** office_id, office_name, district_id, neighborhood_id, district, neighborhood, geometry
- **Spatial Index:** PostGIS-enabled `GEOMETRY(Point, 4326)`
- **Audit Trail:** `created_at`, `updated_at` timestamps

#### Indexes
```sql
CREATE INDEX idx_district_id ON government_offices_in_berlin(district_id);
CREATE INDEX idx_neighborhood_id ON government_offices_in_berlin(neighborhood_id);
CREATE INDEX idx_office_type ON government_offices_in_berlin(office_type);
CREATE INDEX idx_postal_code ON government_offices_in_berlin(postal_code);
CREATE SPATIAL INDEX idx_geometry ON government_offices_in_berlin(geometry);
```

---

## 🛠️ Technologies Used

- **Python Libraries:**
  - `pandas` - Data manipulation
  - `geopandas` - Geospatial operations
  - `osmnx` - OpenStreetMap data fetching
  - `shapely` - Geometry handling
  - `geopy` - Reverse geocoding (Nominatim)

- **Data Sources:**
  - OpenStreetMap (OSM)
  - Berlin Open Data Portal (LOR boundaries)

---

## 📁 Column Reference

| Column | Type | Description | Completeness |
|--------|------|-------------|--------------|
| office_id | BIGINT | Unique OSM identifier | 100% |
| office_name | VARCHAR(255) | Official office name | 100% |
| office_type | VARCHAR(100) | Office classification | 53.2% |
| address | TEXT | Full address string | 89.5% |
| postal_code | VARCHAR(10) | 5-digit postal code | 73.0% |
| city | VARCHAR(100) | City (default: Berlin) | 72.8% |
| district | VARCHAR(100) | District name | 100% |
| neighborhood | VARCHAR(100) | Neighborhood name | 100% |
| district_id | VARCHAR(10) | 8-digit district code | 100% |
| neighborhood_id | VARCHAR(10) | Neighborhood identifier | 100% |
| phone_number | VARCHAR(50) | Contact phone | 33.9% |
| email | VARCHAR(255) | Contact email | 16.0% |
| website | VARCHAR(500) | Official website | 62.1% |
| opening_hours | TEXT | Service hours | 39.4% |
| wheelchair_accessible | VARCHAR(20) | Accessibility info | 45.1% |
| latitude | FLOAT | Latitude (WGS84) | 63.7% |
| longitude | FLOAT | Longitude (WGS84) | 63.7% |
| coordinate_type | VARCHAR(50) | Geometry type | 63.7% |
| geometry | GEOMETRY | PostGIS Point | 100% |

---

## 🎯 Key Achievements

✅ Consolidated 441 raw OSM entries into 419 validated records  
✅ 89.5% address completion through dual-strategy geocoding  
✅ 100% geographic assignment (district/neighborhood)  
✅ Spatially validated geometries (EPSG:4326)  
✅ Production-ready database schema with indexes  
✅ Complete audit trail with timestamps  

---

## 🚀 Next Steps

1. Create `berlin_districts` reference table
2. Execute CREATE TABLE statement
3. Import cleaned dataset (419 rows)
4. Validate spatial queries and index performance
5. Plan data enrichment for low-completeness fields (phone, email, opening_hours)

---

## 📝 License & Attribution

- **Data Source:** OpenStreetMap contributors (ODbL)
- **Administrative Boundaries:** Berlin Open Data Portal
- **Geocoding:** Nominatim (OpenStreetMap Foundation)

---

**Last Updated:** 11.11.2025  