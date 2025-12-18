Berlin Kindergartens Data Pipeline
This repository contains scripts to extract and transform kindergarten data in Berlin, Germany.

Current Data Sources
1. OpenStreetMap (Implemented)
Source: OpenStreetMap Overpass API
Format: CSV (kindergartens_berlin_raw_osm.csv)
Update Frequency: Real-time (OSM is continuously updated)
Fields Extracted:
id: OSM element ID
name: Kindergarten name
address: Combined street address
latitude, longitude: Geographic coordinates
postcode: ZIP code
city: District/city name
operator: Operating organization
Potential Future Sources
2. Senatsverwaltung für Bildung, Jugend und Familie (SenBJF)
Official Source: Berlin.de Kitadaten
Direct Data Link: Kita-Finder Berlin
Format: Excel (berlin_kitas_raw.xlsx)
Update Frequency: Annual (typically released each summer)
Key Fields:
name: Kindergarten name
address: Full address with street and number
capacity: Number of available spots
provider: Operating organization
district: Official Berlin district
contact: Phone/email
concept: Educational approach
3. Berlin District Boundaries
Source: Berlin Open Data
Direct Download: Bezirksgrenzen GeoJSON
Format: GeoJSON
Use Case: Spatial analysis and district mapping
Implementation Roadmap
Current Implementation
OSM Extraction:
python scripts/extract_kindergartens_osm.py

kindergartens-data-modelling

This step details the research and planning for integrating Berlin kindergarten data. The primary data source is OpenStreetMap (OSM) via the Overpass API, chosen for its reliability and accessibility after initial attempts with the Berlin Open Data WFS failed.

1.1 Data Source and Modelling Source: OpenStreetMap data, accessed through the Overpass API. This source is dynamic and updated regularly by the OSM community.

Data Type: Dynamic, providing real-time geographical data.

Key Columns: The raw data will provide id, name, latitude, longitude, address components (street, housenumber, postcode), and operator.

Planned Schema: A new table named kindergartens will be created with the following columns: id, name, address, district, zip_code, latitude, longitude, provider, capacity, age_groups, created_at, and updated_at.

Connection to Existing Tables: The latitude and longitude will be used for a spatial join with a neighborhoods table.

1.2 Transformation Plan The raw OSM data will undergo the following transformations:

Combining Address: The street and housenumber fields will be merged into a single address column.

Mapping Columns: The OSM operator field will be mapped to the provider column in the final schema.

Handling Missing Data: Missing values in name, address, and zip_code will be filled with 'Unknown'.

Timestamps: created_at and updated_at columns will be added to track data freshness.

Step 2: Data Transformation Branch Name: kindergartens-data-transformation

This step involves writing the Python script to transform the raw OSM data into a clean, normalized format that matches the planned schema. This script is purely for data processing and does not interact with the database.

2.1 Transformation Logic Tool: A Python script (/scripts/transform_kindergartens.py) using the pandas library.

Input: The raw CSV file (/sources/kindergartens_berlin_raw_osm.csv).

Output: A cleaned CSV file (/data/kindergartens_berlin_cleaned.csv).

Key Operations:

Reading the raw data.

Combining address components.

Renaming the operator column to provider.

Filling NaN values.

Adding created_at and updated_at timestamps.

Creating new columns for capacity and age_groups with placeholder values, as this data is not consistently available from OSM.
