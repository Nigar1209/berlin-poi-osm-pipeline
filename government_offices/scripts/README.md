# Berlin Government Offices Data Pipeline

A comprehensive data transformation pipeline that fetches, cleans, enriches, and structures government and administrative office data for Berlin, Germany using OpenStreetMap and official Berlin municipal sources.

## 📋 Overview

This project creates a production-ready dataset of **436 unique government offices** in Berlin by combining OpenStreetMap data with official Berlin administrative boundaries. The pipeline handles data discovery, cleaning, geospatial enrichment, and schema standardization for database integration.

## 🎯 Key Features

- **Automated Data Fetching**: Uses OSMnx to query OpenStreetMap for government offices
- **Smart Deduplication**: Removes exact and near-duplicate entries (within 10m)
- **Geospatial Enrichment**: Links offices to official Berlin districts and neighborhoods
- **Data Consolidation**: Merges sparse OSM columns into structured attributes
- **Schema Standardization**: Outputs database-ready format with 19 standardized columns
- **Quality Validation**: Ensures geometric integrity and CRS compliance (EPSG:4326)

## 🛠️ Tech Stack

```python
pandas          # Data manipulation
geopandas       # Geospatial operations
shapely         # Geometry handling
osmnx           # OpenStreetMap queries
requests        # HTTP requests
json            # JSON processing
```

## 📊 Data Pipeline

```
┌─────────────────┐
│  OSM Data Fetch │  ← Query government offices via OSMnx
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Initial Dataset │  ← 441 offices, 177 columns (highly sparse)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Cleaning   │  ← Consolidate columns, merge duplicates
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Schema Mapping  │  ← Standardize to 17-column structure
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Geo-Enrichment  │  ← Spatial join with Berlin districts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Quality Checks  │  ← Remove out-of-bounds, fix geometries
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Final Dataset   │  ← 436 unique offices, ready for DB
└─────────────────┘
```

## 📁 Project Structure

```
├── scripts/
│   └── government_offices_data_transformation.ipynb
│   └── README.md   
├── sources/
    ├── lor_ortsteile.geojson              # Berlin district boundaries
    └── README.MD

```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install required packages
pip install pandas geopandas shapely osmnx requests
```

### 2. Run the Pipeline

```python
# Open and run the notebook
jupyter notebook scripts/government_offices_data_transformation.ipynb
```

### 3. Output

The pipeline generates a clean GeoDataFrame with 436 offices containing:
- **Address data**: street, housenumber, postal_code, city
- **Contact info**: phone_number, email, website, opening_hours
- **Administrative**: district, neighborhood, district_id, neighborhood_id
- **Geospatial**: latitude, longitude, geometry (Point)
- **Accessibility**: wheelchair_accessible

## 📐 Database Schema

### Table: `government_offices_in_berlin`

```sql
CREATE TABLE government_offices_in_berlin (
    -- Primary Key
    office_id               BIGINT PRIMARY KEY,
    
    -- Foreign Keys
    district_id             VARCHAR(10) NOT NULL,
    neighborhood_id         VARCHAR(10),
    
    -- Office Information
    office_name             VARCHAR(255),
    office_type             VARCHAR(100),
    
    -- Address Information
    street                  VARCHAR(255),
    housenumber             VARCHAR(20),
    postal_code             VARCHAR(10),
    city                    VARCHAR(100) DEFAULT 'Berlin',
    district                VARCHAR(100),
    neighborhood            VARCHAR(100),
    
    -- Contact Information
    phone_number            VARCHAR(50),
    email                   VARCHAR(255),
    website                 VARCHAR(500),
    opening_hours           TEXT,
    wheelchair_accessible   VARCHAR(20),
    
    -- Geospatial Information
    latitude                FLOAT,
    longitude               FLOAT,
    coordinate_type         VARCHAR(50),
    geometry                GEOMETRY(Point, 4326),
    
    -- Indexes
    INDEX idx_district_id (district_id),
    INDEX idx_office_type (office_type),
    SPATIAL INDEX idx_geometry (geometry)
);
```

## 🧹 Data Quality Summary

| Stage | Records | Action |
|-------|---------|--------|
| Initial OSM Fetch | 441 | Raw OpenStreetMap data |
| Spatial Filter | 437 | Removed out-of-bounds offices |
| Geometry Fix | 438 | Exploded multipart geometry |
| Exact Deduplication | 437 | Removed identical office_ids |
| Near Deduplication | **436** | Removed offices within 10m |

## 🔑 Key Design Decisions

### Single Table Architecture
- ✅ **Chosen**: Single unified table for all office types
- **Reasoning**: 436 offices is manageable, simplifies queries, maintains consistency
- ❌ **Rejected**: Multiple tables by office type (unnecessary complexity)

### Data Consolidation Strategy
Sequential column merging for sparse OSM data:
- `name` ← `name:de`, `name:en`, `official_name`
- `opening_hours` ← `opening_hours:signed`
- `website` ← `contact:website`
- `phone_number` ← `contact:phone`, `phone`
- `email` ← `contact:email`

### Geospatial Standards
- **CRS**: EPSG:4326 (WGS84) - global standard
- **Geometry Type**: Point (validated and cleaned)
- **Coordinate Precision**: Float (sufficient for Berlin)

## 📊 Data Sources

1. **OpenStreetMap** (via OSMnx)
   - Government offices tagged with `office=government`, `amenity=townhall`, etc.
   - German-specific names (Bürgeramt, Finanzamt, etc.)

2. **Berlin Open Data**
   - Official administrative boundaries (`lor_ortsteile.geojson`)
   - District and neighborhood identifiers

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows PEP 8 style guidelines
- Geospatial operations maintain CRS consistency
- New features include data quality checks

## 📄 License

This project uses data from OpenStreetMap (ODbL) and Berlin Open Data (CC BY).

## 📧 Contact

For questions or issues, please open a GitHub issue.

---

**Last Updated**: November 2025  
**Dataset Version**: 1.0  
**Record Count**: 436 unique government offices