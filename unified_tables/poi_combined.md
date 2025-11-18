# Unified Points of Interest (POI) Table

## Proposed Table Structure

| Column Name     | Key                                  | Data Type             | Description                                                   | Example |
|-----------------|--------------------------------------|-----------------------|---------------------------------------------------------------|---------|
| poi_id          | Primary Key                          | varchar(50)           | Unique identifier (e.g., source + original id)                | `bank_28968292` |
| name            |                                      | varchar(255)          | Name of the place                                             | `Berliner Volksbank` |
| layer           |                                      | varchar(100)          | General category (bank, dental office, gallery, etc.)         | `bank` |
| district_id     | Foreign Key → districts(district_id) | varchar(20)           | Identifier of parent district                                 | `11001001` |
| district        |                                      | varchar(100)          | Name of the district                                          | `Mitte` |
| neighborhood_id |                                      | varchar(20)           | Neighborhood identifier                                       | `0105` |
| neighborhood    |                                      | varchar(100)          | Name of the neighborhood                                      | `Moabit` |
| latitude        |                                      | float8                | Geographic latitude                                           | `52.4866675` |
| longitude       |                                      | float8                | Geographic longitude                                          | `13.319723` |
| geometry        |                                      | geometry(Point, 4326) | Geometry column (WGS84)                                       | `POINT(13.319723 52.4866675)` |
| attributes      |                                      | jsonb                 | Additional info from source tables stored as JSON             | `{"operator":"nan","wheelchair":true,"opening_hours":"mo-fr 10:00-16:00"}` |

---

## Common Columns
- `poi_id`
- `name`
- `district_id`
- `district`
- `neighborhood_id`
- `neighborhood`
- `latitude`
- `longitude`

---

## Columns to Create 
- `layer` → derived from table name  
- `geometry` → `geometry(Point, 4326)`  
- `attributes` → JSON with columns not common across all tables  

---

## Standard Rules for Table Creation (have to exist)
- **Table name**: must be the layer name only (used in `layer` column for grouping).  
- **poi_id**: unique row identifier, starting with first 3 letters of layer name + underscore + number (e.g., `gal_012345`).  
- **name**: must exist; rows with missing/unknown names should be removed.  
- Only `district_id` and `neighborhood_id` are required as links to their respective tables.  
- `latitude` and `longitude` must always be present.  

---

## JSON Attributes Column
- **Exclude**: street, postal code, house number.  
- **Consider retaining**: Wikidata references, website info, contact numbers.  

---

## Example Schema

![Schema Example](/layered-data-engineering/unified_tables/poi_schema.png)

---
## Code snippets

### Show the names of tables that are only Points of Interest
```sql
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'berlin_source_data'
    AND table_type = 'BASE TABLE'
    AND table_name NOT ILIKE '%stat%'
```

### Loop through above list and show top 5 rows of each table
- Helps to look for any column columns
```sql
for table in poi_tables_df['table_name']:
    print(f"\n--- {table} ---")
    preview_query = f"SELECT * FROM berlin_source_data.{table} LIMIT 5;"
    df = pd.read_sql(text(preview_query), engine)
    display(df)
```
### Example of the tables
![alt text](/layered-data-engineering/unified_tables/poi_tables.png)

### Look for common columns
- Created columns staing TRUE or FALSE if the column exists
```sql
 WITH tables AS (
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'berlin_source_data'
        AND table_type = 'BASE TABLE'
        AND table_name NOT ILIKE '%test%' AND table_name NOT ILIKE '%stat%'
  ),
  cols AS (
      SELECT table_name, column_name
      FROM information_schema.columns
      WHERE table_schema = 'berlin_source_data'
  )
  SELECT t.table_name,
        -- check for each required pattern
        bool_or(c.column_name ILIKE '%id%' AND c.column_name != 'district_id') AS has_id,
        bool_or(c.column_name ILIKE '%name%' OR c.column_name ILIKE '%station%' OR c.column_name ILIKE '%district%' ) AS has_name,
        bool_or(c.column_name ='district_id') AS has_district_id,
        bool_or(c.column_name ILIKE '%hood_id%') AS has_neighborhood_id,
        bool_or(c.column_name ILIKE '%lat%')  AS has_lat,
        bool_or(c.column_name ILIKE '%lon%')  AS has_lon,
        bool_or(c.column_name ILIKE '%geom%')  AS has_geom
  FROM tables t
  LEFT JOIN cols c ON t.table_name = c.table_name
  GROUP BY t.table_name
  ORDER BY t.table_name;
```

![alt text](/layered-data-engineering/unified_tables/poi_common_columns.png)

### Create the point_of_interest table and insert the rows
- Using Union to join the tables before inserting (not sure if Union is needed or can just append exch table to the main table)
```sql
DROP TABLE IF EXISTS point_of_interest CASCADE;

CREATE TABLE point_of_interest (
    poi_id TEXT PRIMARY KEY,
    name TEXT,
    layer TEXT, -- 'galleries' or 'museums'
    district_id TEXT,
    district TEXT,
    neighborhood_id TEXT,
    neighborhood TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    geometry geometry(Point, 4326),
    attributes JSONB
);

INSERT INTO point_of_interest (poi_id, name, layer, district_id, district, neighborhood_id, neighborhood,
                 latitude, longitude, geometry, attributes)
SELECT
    CONCAT(SUBSTRING('galleries' FROM 1 FOR 3), '-', g.id) AS poi_id,
    g.name,
    'galleries' AS layer,
    g.district_id,
    d.district AS district,
    g.neighborhood_id,
    n.neighborhood AS neighborhood,
    g.latitude,
    g.longitude,
    ST_SetSRID(ST_MakePoint(g.longitude, g.latitude), 4326) AS geometry,
    to_jsonb(g) - 'id' - 'name' - 'district_id' - 'neighborhood_id'
                 - 'latitude' - 'longitude' - 'geometry' - 'street' - 'house_number' - 'postal_code' - 'wikipedia' AS attributes
FROM berlin_source_data.galleries g
JOIN berlin_source_data.districts d ON g.district_id = d.district_id
JOIN berlin_source_data.neighborhoods n ON g.neighborhood_id = n.neighborhood_id

UNION ALL

SELECT
    CONCAT(SUBSTRING('museums' FROM 1 FOR 3), '-', m.id) AS poi_id,
    m.name,
    'museums' AS layer,
    m.district_id,
    d.district AS district,
    m.neighborhood_id,
    n.neighborhood AS neighborhood,
    m.latitude,
    m.longitude,
    ST_SetSRID(ST_MakePoint(m.longitude, m.latitude), 4326) AS geometry,
    to_jsonb(m) - 'id' - 'name' - 'district_id' - 'neighborhood_id'
                 - 'latitude' - 'longitude' - 'geometry' - 'street' - 'house_number' - 'postal_code' - 'wikipedia' AS attributes
FROM berlin_source_data.museums m
JOIN berlin_source_data.districts d ON m.district_id = d.district_id
JOIN berlin_source_data.neighborhoods n ON m.neighborhood_id = n.neighborhood_id;
```
### Show top 5 rows of table (change Geometry to POINT format)
```sql
SELECT poi_id,
    name,
    layer,
    district_id,
    district,
    neighborhood_id,
    neighborhood,
    latitude,
    longitude,
     ST_AsText(geometry) AS geom_wkt,
    attributes
FROM point_of_interest 
LIMIT 5;
```
![alt text](/layered-data-engineering/unified_tables/poi_final.png)


### Things to look at
- What data do we need in the attributes column, what can we drop off
- Have some odd tables eg: district_level_aggreagted or land_prices - what do we do with these?
- 2 different theaters tables, one says final can we remove the otehr one?
- Need to set a standard format for future tables (see above)
- As some columns have different naming conventions this will need to be corrected before adding rows to unified table (eg id and name)
- Need to remove the rows that dont have a name, so NULL or Unknown
- Some tables are missing lattitude and longitude, need to fix before adding to unified table
- Some tables are missing id column, need to fix before adding to unified table
