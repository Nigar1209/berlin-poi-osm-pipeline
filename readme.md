# 🧭 Lakes in Berlin – Data Transformation & Preprocessing

This notebook focuses on cleaning and transforming data for the Berlin lakes project.  
The goal was to standardize the different datasets (OSM water polygons and in-situ measurements) and prepare clean outputs for database integration.

---

## 🔹 Input Files
- **osm_berlin_lakes.geojson** – all Berlin waterbodies from OpenStreetMap  
- **demeritzsee.csv** – measurement data for Dämeritzsee (temperature, pH, oxygen, etc.)

---

## 🔹 Main Steps
1. Loaded the OSM and CSV data using GeoPandas and Pandas.  
2. Filtered out non-lake features and removed empty or duplicate entries.  
3. Converted coordinate system to WGS 84 (EPSG:4326) and calculated area and centroid.  
4. Cleaned and renamed columns to match the unified schema.  
5. Combined results into clean GeoJSON and CSV outputs.  
6. Added metadata such as `data_source`, `lake_name`, and `last_updated`.  
7. Checked data quality and exported the final results.

---

## 🔹 Output Files
- **berlin_lakes_summary.csv** – cleaned data without geometry  
- **lakes_berlin_unified.geojson** – standardized dataset with geometry  
- *(optional)* **demeritzsee_clean.csv** – processed water-quality data  
- *(optional)* **daemeritzsee_polygon.geojson** – lake polygon extracted from OSM

---

## 🔹 Unified Schema
| Column | Description |
|--------|--------------|
| lake_name | Name of the lake or waterbody |
| geometry | Polygon geometry (EPSG:4326) |
| centroid_lat | Latitude of centroid |
| centroid_lon | Longitude of centroid |
| water_type | Type of waterbody (lake, pond, reservoir) |
| area_ha | Surface area in hectares |
| max_depth_m | Maximum depth (if available) |
| has_public_access | Boolean, public access yes/no |
| swimming_allowed | Boolean, swimming allowed yes/no |
| data_source | Data origin |
| last_updated | Timestamp of last update |

---

## 🔹 Summary
All geometry data were validated, duplicates removed, and coordinate references standardized.  
The cleaned dataset is now ready for integration into the unified database structure.

---

**Prepared by:** Robert Sesazi  
**Branch:** `lakes-data-modelling-rs2`  
**Date:** November 2025
