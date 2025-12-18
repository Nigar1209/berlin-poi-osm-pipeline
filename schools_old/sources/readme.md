- deleted the other stuff as asked
- `berlin_schools.csv`: reworked CSV version of school points now with extracted added `longitude` and `latitude` columns for two decimals
- `school_inside_inductions.gpkg`: Full polygon layer of school induction zones, provided as GeoPackage
- `school_inside_inductions`: Folder with extracted `.shp`, `.shx`, `.dbf` files from the same zone layer


---

## 🔄 Transformation Plan

1. **QGIS-Based Preprocessing**:
   - Extracted geodata layers from source GeoPackages and `.shp` files.
   - Added `longitude` and `latitude` columns via geometry field calculator.
   - Performed **spatial joins** between school points and induction zone polygons using *"inside a zone"* (contains) overlay type.

2. **Exported Outputs**:
   - Results were exported as `.csv` (point data) and `.gpkg` / `.shp` (zones).
   - All geometry data preserved in **WGS84** (EPSG:4326) for PostGIS compatibility.

---

## 🔧 Notes on Compatibility

- All geodata is prepared for use with **PostGIS**.
- Coordinate reference system: **EPSG:4326 (WGS84)**
- Geometry types: `Point` (schools), `Polygon` (zones)

---

✅ Step 2: Data Transformation – Documentation Overview
🔀 Scope of this Step

This step focuses purely on preparing clean, normalized school data for insertion into the database. No data is written to PostGIS yet — all processing happens locally in script form.
📁 Files Added

    scripts/transform_schools.py: Python script for transforming raw school data

    output/schools_transformed.csv: Cleaned output file ready for import

    (Optional) scripts/README.md: Overview of transformation logic

🛠 Transformation Logic Summary

    Load raw input

        File: sources/berlin_schools_with_lonlat.csv

        Origin: Extracted from QGIS, manually joined with school induction zones

    Schema normalization

        Renamed columns to snake_case (e.g., Name → school_name, Lat → latitude) maybe overthink some ost in trasnlation stuff of english names for private schools.

        Ensured types are consistent (float for coordinates, string for names/types)

    Data quality checks

        checking entries with missing coordinates or school names

        cleaning empty values in students/teachers values

        Verified all coordinates are in EPSG:4326 (WGS84) format

      

    Output

        Saved cleaned data as schools_transformed.csv in output/

        File is ready for ingestion into PostGIS schema as defined in Step 1.2

🔗 What This Connects To

The transformed dataset  will include all the headers seen in the table:

    neighborhood as our planned constant for everyone

    quaretrs (subdistricts?) unsure how i should name them 
    
    bsn 

    school_name

    latitude, longitude (evtl lon,lat)

    s....

    These fields will later link to:

        🏘️ neighborhoods (via spatial relationship)

        🏫 school_induction_zones (already joined in QGIS)

✅ Notes for Reviewer

    No further transformation needed on zone polygons — spatial join already done in QGIS (preserved in GPKG)

    Output is fully aligned with planned schema

    PostGIS insert logic will follow in Step 3 (schools-populating-db)

