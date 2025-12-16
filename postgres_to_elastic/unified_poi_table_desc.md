# Unified POIS Table for Berlin Layers

## Objective
- Combine multiple Berlin spatial data layers into:
  - One unified table for **Points of Interest (POI)**
- Designed for use in **PostgreSQL/PostGIS** and **Elasticsearch**
- Tables must include:
  - Geometry column
  - Common standardized columns
  - Additional attributes stored as JSON

## Data Types
- **Points of Interest (POI):** places such as banks, post offices, schools, and parks
- Spatial queries on POI table should leverage **R‑Tree/GiST indexing**


## Proposed Table Structure: Points of Interest (POI)

| Column Name     | Key                                | Data Type             | Description                                                   | Example |
|-----------------|------------------------------------|-----------------------|---------------------------------------------------------------|---------|
| poi_id          | Primary Key                        | varchar(50)           | Unique identifier (e.g., source + original id)                | `bank_28968292` |
| name            |                                    | varchar(255)          | Name of the place                                             | `Berliner Volksbank` |
| layer           |                                    | varchar(100)          | General category (bank, dental office, gallery, etc.)         | `bank` |
| district_id     | Foreign Key → districts(district_id) | varchar(20)          | Identifier of parent district                                 | `11001001` |
| district        |                                    | varchar(100)          | Name of the district                                          | `Mitte` |
| neighborhood_id |                                    | varchar(20)           | Neighborhood identifier                                       | `0105` |
| neighborhood    |                                    | varchar(100)          | Name of the neighborhood                                      | `Moabit` |
| latitude        |                                    | float8                | Geographic latitude                                           | `52.4866675` |
| longitude       |                                    | float8                | Geographic longitude                                          | `13.319723` |
| geometry        |                                    | geometry(Point, 4326) | Geometry column (WGS84)                                       | `POINT(13.319723 52.4866675)` |
| attributes      |                                    | jsonb                 | Additional info from source tables stored as JSON             | `{"operator":"nan","wheelchair":true,"opening_hours":"mo-fr 10:00-16:00"}` |
| nearest_pos     |                                      | jsonb.                | Showing nearest layer to long term listing                    | `{"bank": {"id":"ban-1915389761","name": "sparkasse","address": {"street": "otto-suhr-allee","house_number": null},"distance": 1011.56046421}` |
---
