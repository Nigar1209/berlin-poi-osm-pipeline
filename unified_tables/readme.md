# Draft: Unified Tables for Berlin Layers

## Objective
- Combine multiple Berlin spatial data layers into:
  - One unified table for **Points of Interest (POI)**
  - One unified table for **Statistics**
- Designed for use in **PostgreSQL/PostGIS** and **Elasticsearch**
- Tables must include:
  - Geometry column
  - Common standardized columns
  - Additional attributes stored as JSON

### Data Types
- **Points of Interest (POI):** places such as banks, post offices, schools, and parks
- **Statistics (Stats):** crime or population statistics
- Spatial queries on POI table should leverage **R‑Tree/GiST indexing**

---

## Deliverables

### Proposed Table Structure: Points of Interest (POI)

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
---

### Proposed Table Structure: Statistics
*(to be defined — pending schema decisions)*

---

## Indexing Strategy

### R‑Tree / GiST Index
PostgreSQL with PostGIS supports GiST indexes, which behave like R‑Trees.

```sql
CREATE INDEX idx_poi_geom
ON point_of_interest
USING GIST (geometry);
```
- Without an index, Postgres scans the entire table
- With GiST, bounding box queries (ST_DWithin, ST_Intersects) are much faster

### Example Query
Find all parks within 1 km of Alexanderplatz:
```sql
SELECT name
FROM poi_combined
WHERE category = 'park'
  AND ST_DWithin(
    geometry,
    ST_SetSRID(ST_MakePoint(13.4132, 52.5219), 4326),
    1000
  );
```
### Architecture Overview
🔄 Kafka
- Purpose: Transport layer for updates/events from Postgres → Elasticsearch
- Benefit: Decouples ingestion from query. If you later add more consumers (e.g., analytics, monitoring), Kafka already provides the stream.
- Note: Kafka itself doesn’t index or query — it’s just the reliable pipe.

🔍 Elasticsearch
- Purpose: User‑facing search
- Strengths: Full‑text queries, geo_point/geo_shape queries for "what's nearby"
- Trade‑off: Less precise than PostGIS for complex geometries, but faster for “nearby” queries
- Benefit: Fast, scalable, user‑friendly search API. Perfect for your layers app where someone asks “What cafés are near Alexanderplatz?”

⚡ Cost‑Effective Workflow
- Postgres: Maintain geometry + R‑Tree index for accuracy.
- Kafka: Stream changes downstream
- Elasticsearch: Provide user‑friendly search (text + location).

### In summary
- Heavy spatial logic (precise geometry) stays in Postgres.
- Elasticsearch handles the “nearby” queries at scale with lower latency.
- Kafka keeps everything in sync without tight coupling.

### Practical Tips
- Store geometry in Postgres for accuracy
- Store lat/long in Elasticsearch as geo_point for fast “nearby” queries
- Push simplified geometries into Elasticsearch as geo_shape if polygon queries are needed (e.g., “inside this district”),
- Kafka ensures smooth, real‑time sync between systems

### Recommendations
- Keep Statistics separate from Points of Interest (different schemas)
- Create two unified tables:
    - `poi_combined` 
    - `statistics_combined`



