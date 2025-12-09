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
