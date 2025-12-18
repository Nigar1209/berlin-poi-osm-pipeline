# SQL Workflow for Geospatial Data

The scraper outputs a clean CSV with composite IDs and lat/long coordinates.
All geospatial data (geometry, district, neighborhood) is added via SQL.

## Step 1: Load CSV to Staging Table

```sql
-- Create staging table from CSV structure
CREATE TABLE staging.long_term_listings_staging (
    id VARCHAR PRIMARY KEY,
    url TEXT,
    name TEXT,
    type VARCHAR(50),
    first_tenant VARCHAR(10),
    price_euro INTEGER,
    number_of_rooms DECIMAL(3,1),
    surface_m2 DECIMAL(6,2),
    floor INTEGER,
    street TEXT,
    house_number VARCHAR(10),
    postal_code INTEGER,
    city VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    geocode_source VARCHAR(20)  -- nominatim, postal_fallback, or failed
);

-- Load CSV (using psql or your preferred method)
\COPY staging.long_term_listings_staging FROM 'immowelt_listings.csv' WITH CSV HEADER;
```

## Step 2: Add Geospatial Data

```sql
-- Insert to final table with geospatial data
INSERT INTO staging.long_term_listings_staging_postgis (
    id, url, name, type, first_tenant, price_euro,
    number_of_rooms, surface_m2, floor,
    street, house_number, postal_code, city,
    latitude, longitude, geocode_source,
    geometry, address, district_id, district, neighborhood_id, neighborhood
)
SELECT
    src.id,
    src.url,
    src.name,
    src.type,
    src.first_tenant,
    src.price_euro,
    src.number_of_rooms,
    src.surface_m2,
    src.floor,
    src.street,
    src.house_number,
    src.postal_code,
    src.city,
    src.latitude,
    src.longitude,
    src.geocode_source,
    -- Create geometry from coordinates
    ST_AsText(ST_SetSRID(ST_MakePoint(src.longitude, src.latitude), 4326)) AS geometry,
    -- Build address from components
    src.street || ' ' || src.house_number || ', ' || src.postal_code || ' ' || src.city AS address,
    -- Spatial joins for district
    d.district_id,
    d.district,
    -- Spatial joins for neighborhood
    n.neighborhood_id,
    n.neighborhood
FROM staging.long_term_listings_staging AS src
LEFT JOIN berlin_source_data.districts AS d
    ON ST_Contains(d.geometry, ST_SetSRID(ST_MakePoint(src.longitude, src.latitude), 4326))
LEFT JOIN berlin_source_data.neighborhoods AS n
    ON ST_Contains(n.geometry, ST_SetSRID(ST_MakePoint(src.longitude, src.latitude), 4326))
WHERE src.latitude IS NOT NULL
  AND src.longitude IS NOT NULL;
```

## Benefits

✅ **Separation of concerns**: Scraper focuses on data extraction, SQL handles geospatial logic
✅ **Proven SQL**: Uses your existing, working SQL script
✅ **Flexibility**: Easy to adjust geospatial joins without touching scraper
✅ **Simplicity**: Scraper is 26% smaller (628 lines vs 853)
✅ **Robustness**: Enhanced geocoding with retries ensures high success rate
