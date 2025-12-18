  Lakes in Berlin — Sources (Data Overview)

This folder contains all input, intermediate, and final datasets used to build the Berlin Lakes data layer.
The data comes from two main sources:

OpenStreetMap (OSM) — waterbodies in Berlin

Dämeritzsee in-situ measurements — historical water-parameter recordings

All files here were cleaned, standardized, and harmonized through the notebook
lakes/scripts/lakes_data_transformation.ipynb.

📁 File Descriptions
1. osm_berlin_lakes_raw.json

Raw Overpass API response containing all tagged waterbodies within the Berlin bounding box.
This is the unprocessed source file downloaded directly from Overpass.

2. osm_berlin_lakes.geojson

Converted raw OSM data transformed into GeoJSON format.
Includes only polygons with valid geometry and tagging information.

3. berlin_lakes_clean.geojson

Cleaned and standardized OSM lake dataset.
Key features:

normalized column names

removed unnamed lakes

computed centroids

added area in hectares (using metric CRS)

4. demeritzsee.csv

Raw in-situ water measurements for the Dämeritzsee (various water physics and chemistry parameters).
This file contains formatting inconsistencies and redundant rows.

5. demeritzsee_clean.csv

Cleaned version of the in-situ dataset:

standardized column names

removed empty and duplicate rows

fixed formatting issues in the header

6. berlin_lakes_summary.csv

Summary table of all Berlin lakes without geometry.
Useful for analytics, dashboards, and lightweight pipelines.
Includes metadata fields:

lake name & tags

centroid coordinates

area

data source

last update timestamp

7. lakes_berlin_unified.geojson

Final unified GeoJSON dataset combining:

cleaned OSM lakes

in-situ data indicator for Dämeritzsee

metadata columns added during processing

This is the main file consumed by downstream layers.

🔧 Processing Notebook

All transformations, cleaning steps, and exports are implemented in:

lakes/scripts/lakes_data_transformation.ipynb
