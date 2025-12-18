# Berlin Kindergartens Data Pipeline

This repository contains scripts to extract and transform kindergarten data in Berlin, Germany.

## Current Data Sources

### 1. OpenStreetMap (Implemented)

- **Source**: [OpenStreetMap Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)
- **Format**: CSV (`kindergartens_berlin_raw_osm.csv`)
- **Update Frequency**: Real-time (OSM is continuously updated)
- **Fields Extracted**: 
  - `id`: OSM element ID
  - `name`: Kindergarten name
  - `address`: Combined street address
  - `latitude`, `longitude`: Geographic coordinates
  - `postcode`: ZIP code
  - `city`: District/city name
  - `operator`: Operating organization

## Potential Future Sources

### 2. Senatsverwaltung für Bildung, Jugend und Familie (SenBJF)

- **Official Source**: [Berlin.de Kitadaten](https://www.berlin.de/sen/jugend/familie-und-kinder/kindertagesbetreuung/kitas/)
- **Direct Data Link**: [Kita-Finder Berlin](https://www.berlin.de/sen/jugend/familie-und-kinder/kindertagesbetreuung/kitas/liste-der-kitas/)
- **Format**: Excel (`berlin_kitas_raw.xlsx`)
- **Update Frequency**: Annual (typically released each summer)
- **Key Fields**:
  - `name`: Kindergarten name
  - `address`: Full address with street and number
  - `capacity`: Number of available spots
  - `provider`: Operating organization
  - `district`: Official Berlin district
  - `contact`: Phone/email
  - `concept`: Educational approach

### 3. Berlin District Boundaries

- **Source**: [Berlin Open Data](https://daten.berlin.de/)
- **Direct Download**: [Bezirksgrenzen GeoJSON](https://fbinter.stadt-berlin.de/fb/berlin/service_intern.jsp?id=s_lor_bezirksgrenzen@senstadt&type=FEED)
- **Format**: GeoJSON
- **Use Case**: Spatial analysis and district mapping

## Implementation Roadmap

### Current Implementation

1. **OSM Extraction**:
   ```bash
   python scripts/extract_kindergartens_osm.py


kindergartens-data-modelling

This step details the research and planning for integrating Berlin kindergarten data. The primary data source is OpenStreetMap (OSM) via the Overpass API, chosen for its reliability and accessibility after initial attempts with the Berlin Open Data WFS failed.

1.1 Data Source and Modelling
Source: OpenStreetMap data, accessed through the Overpass API. This source is dynamic and updated regularly by the OSM community.

Data Type: Dynamic, providing real-time geographical data.

Key Columns: The raw data will provide id, name, latitude, longitude, address components (street, housenumber, postcode), and operator.

Planned Schema: A new table named kindergartens will be created with the following columns: id, name, address, district, zip_code, latitude, longitude, provider, capacity, age_groups, created_at, and updated_at.

Connection to Existing Tables: The latitude and longitude will be used for a spatial join with a neighborhoods table.

1.2 Transformation Plan
The raw OSM data will undergo the following transformations:

Combining Address: The street and housenumber fields will be merged into a single address column.

Mapping Columns: The OSM operator field will be mapped to the provider column in the final schema.

Handling Missing Data: Missing values in name, address, and zip_code will be filled with 'Unknown'.

Timestamps: created_at and updated_at columns will be added to track data freshness.

Step 2: Data Transformation
Branch Name: kindergartens-data-transformation

This step involves writing the Python script to transform the raw OSM data into a clean, normalized format that matches the planned schema. This script is purely for data processing and does not interact with the database.

2.1 Transformation Logic
Tool: A Python script (/scripts/transform_kindergartens.py) using the pandas library.

Input: The raw CSV file (/sources/kindergartens_berlin_raw_osm.csv).

Output: A cleaned CSV file (/data/kindergartens_berlin_cleaned.csv).

2.2 

Loading Data
The previously cleaned dataset is loaded into a Pandas DataFrame.

Column Normalization

Column names are standardized (lowercase, underscores).

Leading/trailing spaces are removed.

Handling Missing Values

All missing fields are filled with "Unknown" (or replaced using postal code mapping for districts).

Address & Postal Code Standardization

Postal codes are normalized to 5-digit strings.

Addresses are cleaned (removing redundant "Berlin" suffix).

Coordinate Checks

Ensures latitude and longitude are numeric.

Rows with coordinates outside Berlin boundaries (lat: 52.3–52.7, lon: 13.1–13.7) are flagged.

Neighborhood / District Assignment

Districts (Bezirk) assigned using postal code mapping.

Optional enrichment via reverse geocoding using Nominatim API for missing districts.

Contact Details Normalization

Website, phone, and email fields are stripped of whitespace and standardized.

Final Quality Checks

Duplicate rows removed.

All numeric and string columns validated.

Total row count confirmed.

Timestamps

created_at and updated_at columns added to track the transformation timestamp.

Saving Final Dataset

Final CSV saved as kindergartens_berlin_final.csv.

Assumptions
Postal codes are assumed to map uniquely to a district; if unknown, district is filled via geocoding.

Missing contact info is filled with "Unknown".

Coordinates outside Berlin are excluded from analysis.

Reverse geocoding uses a 1-second delay per request to avoid API limits.

How to Run
Ensure all dependencies are installed:

bash
Copy
Edit
pip install pandas geopy
Place the latest raw data in /kindergartens/sources/.

Open kindergardens_data_transformation.ipynb and run all cells sequentially.

The final dataset will be saved as kindergartens_berlin_final.csv.



Key Operations:

Reading the raw data.

Combining address components.

Renaming the operator column to provider.

Filling NaN values.

Adding created_at and updated_at timestamps.

Creating new columns for capacity and age_groups with placeholder values, as this data is not consistently available from OSM.


