# 🎭 Theatres in Berlin

A geospatial data modeling  that maps and analyzes all **theatres and cinemas in Berlin** by combining **OpenStreetMap**, **Wikidata**, and **Berlin LOR (Lebensweltlich orientierte Räume)** datasets.

---

## 🧩 Project Overview

This project creates a unified, clean, and SQL-ready dataset of cultural venues in Berlin.  
It brings together multiple open data sources and organizes them into a single pipeline that:

- Extracts **theatres and cinemas** from **OpenStreetMap (OSM)**  
- Enriches with **Wikidata** properties such as capacity, operator, and genre  
- Integrates **district and neighborhood data** from Berlin’s official LOR boundaries  
- Produces structured outputs for analytics, visualization, or database integration  

---



## ⚙️ Data Pipeline

### 1️⃣ Fetch OpenStreetMap data
Use `osmnx` to extract all features tagged as `amenity=theatre` or `amenity=cinema` within Berlin’s boundaries:

```python
import osmnx as ox

tags = {"amenity": ["theatre", "cinema"]}
berlin_poly = ox.geocode_to_gdf("Berlin, Germany").geometry.iloc[0]
theaters_osm_raw = ox.features_from_polygon(berlin_poly, tags)
```


### 2️⃣ Clean and normalize OSM data
Standardize address and contact fields, normalize text, and ensure consistent coordinate reference (EPSG:4326).  
Missing address parts (`street`, `postcode`, etc.) are handled gracefully.

Output → `/source/theatres_berlin_osm_clean.geojson`

---

### 3️⃣ Fetch Wikidata data
Using `SPARQLWrapper` to query **Wikidata** for theatre and cinema entities located in Berlin.

Example query:
```python
SELECT ?item ?itemLabel ?coordinate_location ?capacity
WHERE {
  ?item wdt:P31 wd:Q24354.   # theatre
  ?item wdt:P131 wd:Q64.     # Berlin
  OPTIONAL { ?item wdt:P1083 ?capacity. }
  OPTIONAL { ?item wdt:P625 ?coordinate_location. }
}
```

Output →`/source/theatres_berlin_wiki_clean.geojson`

---

### 4️⃣ Merge OSM + Wikidata + LOR
Spatially join the cleaned datasets and append administrative context:

```python
merged = osm.merge(wikidata, on="name_key", how="left")
merged = gpd.sjoin(merged, lor_neighborhoods, how="left", predicate="within")
merged = gpd.sjoin(merged, lor_districts, how="left", predicate="within")
```

Output →  `/source/theatres_berlin_enriched.geojson`


---

### 5️⃣ Database Schema

```sql
CREATE TABLE theatres_berlin (
    theater_id         VARCHAR(64) PRIMARY KEY,
    name               VARCHAR(255) NOT NULL,
    name_key           VARCHAR(255),
    place_type         VARCHAR(50),
    operator           VARCHAR(255),
    opening_hours      VARCHAR(255),
    wheelchair         VARCHAR(50),
    screen             INTEGER,
    website            VARCHAR(255),
    phone              VARCHAR(100),
    email              VARCHAR(255),
    addr_full          VARCHAR(255),
    addr_street        VARCHAR(255),
    addr_housenumber   VARCHAR(50),
    addr_postcode      VARCHAR(20),
    district_id        VARCHAR(10),
    district           VARCHAR(255),
    neighborhood_id    VARCHAR(10),
    neighborhood       VARCHAR(255),
    wikidata_id        VARCHAR(50),
    lon                FLOAT,
    lat                FLOAT,
    geometry           GEOMETRY(Point, 4326)
);
```

---

## 🧰 Environment Setup

### 1. Create and activate the environment
```bash
conda create -n theatres python=3.11 geopandas osmnx sparqlwrapper shapely pandas
conda activate theatres
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

**Example `requirements.txt`:**
```
geopandas
osmnx
SPARQLWrapper
pandas
shapely
numpy
openpyxl
sqlalchemy
```

---

## 📊 Outputs

| File                                 | Description                                                                           |
| ------------------------------------ | ------------------------------------------------------------------------------------- |
| File                                        | Description                                                                               |
| ------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `lor_berlin_full.geojson`                   | LOR administrative boundaries (raw/full Berlin polygons).                                 |
| `lor_berlin_full_clean.geojson`             | Cleaned/standardized LOR boundaries (normalized fields, CRS=EPSG:4326).                   |
| `lor_ortsteile.geojson`                     | LOR **Ortsteile** (sub-district) polygons for neighborhood/district joins.                |
| `theatres_berlin_osm_clean.csv`             | Cleaned OSM theatres/cinemas — attributes only (no geometry column).                      |
| `theatres_berlin_osm_clean.geojson`         | Cleaned OSM theatres/cinemas with geometry (WGS84) for GIS/mapping.                       |
| `theatres_berlin_wiki_clean.csv`            | Cleaned Wikidata entities (keys like `wikidata_id`, `name_key`, selected WD properties).  |
| `theatres_berlin_wiki_clean.geojson`        | Same Wikidata clean set with geometry.                                                    |
| `theatres_berlin_enriched.csv`              | **Merged** OSM + Wikidata ; tabular export (no geometry).                 |
| `theatres_berlin_enriched.geojson`          | **Merged** OSM + Wikidata with geometry ; ready for maps.               |
| `theatres_berlin_enriched_district.csv`     | Enriched dataset with **district-level** assignment (CSV). Useful for district analytics. |
| `theatres_berlin_enriched_district.geojson` | Enriched dataset with **district-level** assignment + geometry (GeoJSON).                 |
| `theaters_berlin_db_ready.csv`              | Final curated, **schema-aligned** export (CSV) for database import (no geometry column).  |
| `theaters_berlin_db_ready.geojson`          | Same **DB-ready** dataset with geometry (GeoJSON), CRS=EPSG:4326.                         |



---

## 📜 License

**Data sources:**
- [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)
- [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page)


All data is licensed under **ODbL / CC-BY-SA**, respecting original source terms.

 

