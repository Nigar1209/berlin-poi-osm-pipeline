# Veterinary Clinics – Berlin

This directory contains the new **Vet Clinics in Berlin** data layer.

The goal of this layer is to build a clean, well-documented dataset of veterinary
clinics in Berlin that can be used by the application for:

- search and discovery of vet clinics,
- neighborhood- and district-level context,
- coverage and accessibility analysis.

## Directory structure

- `sources/`  
  Raw input data and documentation for all external data sources
  (OSM, LOR / Ortsteile, etc.).

- `cache/`  
  Intermediate files and temporary outputs produced during exploration and modelling
  (e.g. CSV exports from notebooks). These files are **not** considered final
  database-ready tables, but are used as inputs for later steps.

- `01_vet_clinics_osm_lor_join.ipynb`  
  Jupyter notebook that:
  - loads the raw OSM snapshot of vet clinics in Berlin (`amenity = veterinary`),
  - loads the Berlin LOR (Ortsteile) polygons,
  - performs a spatial join to assign each clinic to a LOR, district, and neighborhood,
  - adds latitude/longitude coordinates,
  - exports a first **v0** CSV dataset with spatial context and key OSM attributes.

- `02_vet_clinics_cleaning_and_normalization.ipynb`  
  Jupyter notebook that:
  - loads the v0 CSV from `cache/`,
  - cleans and normalizes key fields (clinic name, address, district, neighborhood),
  - aggregates contact information (phone, email, website),
  - exposes opening hours and derives a simple `operating_days` label,
  - derives basic `services_offered` (currently based on the OSM `emergency` flag),
  - builds an `accessibility_features` field from wheelchair tags,
  - applies a fallback strategy for missing clinic names (using `operator` or address),
  - maps the data into a target schema suitable for the app / DB layer,
  - exports a **v1 cleaned CSV** in `cache/`.

## Data flow

1. **Raw sources**

   - `sources/raw_osm_berlin_vet_clinics_20251209.geojson`  
     OSM snapshot of `amenity = veterinary` in Berlin (downloaded via Overpass Turbo).

   - `sources/raw_osm_berlin_vet_clinics_2025-09-25.csv`  
     Older OSM export kept for QA / comparison (not used as primary source).

   - `sources/raw_berlin_lor_ortsteile.geojson`  
     Berlin LOR (Lebensweltlich orientierte Räume) polygons, used to assign clinics
     to districts and neighborhoods.

2. **Spatial join and enrichment (v0)**

   `01_vet_clinics_osm_lor_join.ipynb`:

   - reads the OSM GeoJSON and the LOR GeoJSON,
   - aligns CRS (EPSG:4326 / WGS84),
   - selects LOR attributes (`gml_id`, `BEZIRK`, `OTEIL`),
   - runs a spatial join (`within`) to assign each clinic to a LOR polygon,
   - renames LOR attributes to `lor_id`, `district_name`, `neighborhood_name`,
   - adds `lat` / `lon` from geometry,
   - exports **v0**:

     - `cache/vets_osm_berlin_with_lor_20251209_v0.csv`.

3. **Cleaning and normalization (v1)**

   `02_vet_clinics_cleaning_and_normalization.ipynb`:

   - loads `cache/vets_osm_berlin_with_lor_20251209_v0.csv`,
   - builds `df_clean` with the schema:

     - `clinic_name`
     - `address`
     - `district`
     - `neighborhood`
     - `services_offered`
     - `operating_days`
     - `operating_hours`
     - `contact_info`
     - `latitude`
     - `longitude`
     - `accessibility_features`
     - `data_source`

   - fills missing clinic names using:
     - `name` when available,
     - otherwise `operator`,
     - otherwise `"Veterinary clinic - <address>"`,
     - otherwise `"Veterinary clinic (name missing)"`,
   - aggregates contact information and accessibility details,
   - exports **v1**:

     - `cache/vet_clinics_berlin_clean_20251209_v1.csv`.

## Known limitations and next steps

- `services_offered` is currently limited to emergency information based on the
  OSM `emergency` tag. More detailed services (surgery, specialist care, etc.)
  would require enrichment from additional sources.

- `operating_days` is derived using simple heuristics on the `opening_hours`
  string and should be treated as indicative, not authoritative.

- Ratings, reviews and quality scores are not included; they are out of scope
  for this open-data-based layer in the current iteration.

## Concrete files used in this layer

### 1. OSM vet clinics snapshot (GeoJSON)

- **File**: `raw_osm_berlin_vet_clinics_20251209.geojson`
- **Origin**: OpenStreetMap (Overpass Turbo export of `amenity = veterinary` within the Berlin bounding box).
- **Update frequency**: OSM is updated continuously by contributors; this file is a static snapshot as of 2025-12-09.
- **Data type**: Dynamic source, captured here as a static GeoJSON snapshot.
- **Relevant fields**:
  - `name`
  - `addr:street`, `addr:housenumber`, `addr:postcode`, `addr:city`
  - `phone`, `contact:phone`
  - `email`, `contact:email`
  - `website`, `contact:website`
  - `opening_hours`
  - `operator`
  - `wheelchair`, `wheelchair:description`
  - `emergency`
  - geometry (point location)

### 2. OSM vet clinics snapshot (CSV, older export)

- **File**: `raw_osm_berlin_vet_clinics_2025-09-25.csv`
- **Origin**: OpenStreetMap (Overpass Turbo export of `amenity = veterinary`).
- **Update frequency**: Same as above (OSM is continuously updated); this file is an older static snapshot.
- **Data type**: Dynamic source, captured as a static CSV snapshot.
- **Role**: Kept for QA and comparison only (not used as the primary data source in the current pipeline).
- **Relevant fields**: Similar to the GeoJSON snapshot (OSM tags for amenity, name, address, contact, opening_hours, etc.).

### 3. Berlin LOR / Ortsteile polygons

- **File**: `raw_berlin_lor_ortsteile.geojson`
- **Origin**: Berlin Open Data portal (Lebensweltlich orientierte Räume – LOR / Ortsteile).
- **Update frequency**: Updated by the city when administrative boundaries or LOR definitions change
  (typically low-frequency, e.g. when new official boundaries are published).
- **Data type**: Static geospatial dataset (polygons).
- **Relevant fields**:
  - `gml_id` (used as `lor_id`)
  - `BEZIRK` (district name)
  - `OTEIL` (neighborhood / Ortsteil name)
  - `geometry` (polygon boundaries used for spatial join with vet clinic points)

  ## Planned DB schema – `berlin_data.vet_clinics_table`

The vet clinics layer will eventually be loaded into a dedicated table that follows
the common POI schema used across the project.

**Table name**: `berlin_data.vet_clinics_table`

### Core columns (shared POI schema)

These columns follow the common POI schema provided in the project guidelines:

- `id VARCHAR(20) PRIMARY KEY`  
  Numeric-only internal identifier, assigned during ETL (no letters).

- `district_id VARCHAR(20) NOT NULL`  
  Foreign key to `berlin_data.districts(district_id)`, derived from the
  `district` name.

- `name VARCHAR(200) NOT NULL`  
  Clinic name, mapped from the cleaned `clinic_name` field. Defaults to
  `"Unknown"` if null.

- `latitude DECIMAL(9,6)`  
  Latitude in WGS84, mapped from the cleaned dataset.

- `longitude DECIMAL(9,6)`  
  Longitude in WGS84, mapped from the cleaned dataset.

- `geometry VARCHAR`  
  Point geometry stored as a string in `POINT(<lon> <lat>)` format.

- `neighborhood VARCHAR(100)`  
  Neighborhood (Ortsteil) name, mapped from the LOR join.

- `district VARCHAR(100)`  
  District name, mapped from the LOR join.

- `neighborhood_id VARCHAR(20)`  
  LOR-based neighborhood identifier (mapped from the LOR `gml_id` / `lor_id`).

The `district_id` column will be constrained as:

    ```sql
    CONSTRAINT vet_clinics_district_fk
     FOREIGN KEY (district_id)
     REFERENCES berlin_data.districts(district_id)
     ON DELETE RESTRICT
     ON UPDATE CASCADE;

### Vet-clinics-specific columns

Additional columns are specific to the vet clinics layer. They do not have  
global constraints but follow consistent naming and data types:

- **`address VARCHAR(255)`**  
  Full address string, composed from OSM `addr:street`, `addr:housenumber`,  
  `addr:postcode`, `addr:city`.

- **`services_offered TEXT`**  
  Free-text description of services. In the current version this mainly  
  reflects emergency services derived from the OSM `emergency` tag  
  (e.g. `"emergency"`), but can be extended with more detailed categories.

- **`operating_days VARCHAR(50)`**  
  Simple label describing operating days (e.g. `"Mon–Fri"`, `"Mon–Sun"`),  
  derived using heuristics from the `opening_hours` string.

- **`operating_hours VARCHAR(200)`**  
  Human-readable opening hours string, mapped directly from OSM  
  `opening_hours` where available.

- **`contact_info TEXT`**  
  Aggregated contact information, combining `phone`, `email` and `website`  
  fields from OSM (`phone`, `contact:phone`, `email`, `contact:email`,  
  `website`, `contact:website`).

- **`accessibility_features TEXT`**  
  Accessibility-related notes, currently derived from OSM `wheelchair` and  
  `wheelchair:description` tags.

- **`data_source VARCHAR(200)`**  
  Provenance of the record, e.g. `"OSM amenity=veterinary, Berlin, snapshot 2025-12-09"`.

- **`source_osm_id VARCHAR(50)`**  
  Original OSM element identifier (e.g. `"node/..."`, `"way/..."`), mapped  
  from the OSM `id` / `@id` field in the v0 dataset for traceability.


---

### Relationship with the cleaned CSV (`v1`)

The cleaned CSV produced by  
`02_vet_clinics_cleaning_and_normalization.ipynb`  
(`cache/vet_clinics_berlin_clean_20251209_v1.csv`) provides most of the  
content for this schema:

- `name` ⇐ `clinic_name`  
- `address` ⇐ `address`  
- `district` ⇐ `district`  
- `neighborhood` ⇐ `neighborhood`  
- `services_offered` ⇐ `services_offered`  
- `operating_days` ⇐ `operating_days`  
- `operating_hours` ⇐ `operating_hours`  
- `contact_info` ⇐ `contact_info`  
- `latitude` ⇐ `latitude`  
- `longitude` ⇐ `longitude`  
- `accessibility_features` ⇐ `accessibility_features`  
- `data_source` ⇐ `data_source`  


---

### Columns populated during the DB loading step (not in this notebook)

The following fields belong to the final table schema but are created later  
during ETL into the database:

- **`id`** – numeric-only primary key.  
- **`district_id`** – via join to `berlin_data.districts` using the district name.  
- **`neighborhood_id`** – via join to the LOR / neighborhoods reference table  
  (from LOR `gml_id` / `lor_id`).  
- **`geometry`** – constructed as `POINT(longitude latitude)` in WGS84.  
- **`source_osm_id`** – copied from the OSM `id` / `@id` in the v0 dataset.  

## Address Enrichment via Reverse Geocoding

This pipeline enriches missing veterinary clinic addresses using Nominatim reverse geocoding based on latitude and longitude.

The process:
- Targets only rows with missing address and valid coordinates
- Respects Nominatim API usage policies with rate limiting
- Is fully reproducible and suitable for CI / automated pipelines
- Leaves values as NULL when no address can be resolved

This ensures higher data completeness while maintaining reproducibility and ingestion standards.
