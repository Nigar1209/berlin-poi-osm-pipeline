# Veterinary Clinics – Berlin

This directory contains the new **Vet Clinics in Berlin** data layer.

The goal of this layer is to build a clean, well-documented dataset of veterinary clinics in Berlin that can be used for:
- search and discovery of vet clinics,
- neighborhood- and district-level context,
- coverage and accessibility analysis.

## Directory structure

- `sources/`  
  Raw input data and documentation for all external data sources (OSM, LOR / Ortsteile, etc.).

- `cache/`  
  Intermediate files and temporary outputs produced during exploration and modelling
  (e.g. CSV exports from notebooks). These files are **not** considered final
  database-ready tables.

- `01_vet_clinics_osm_lor_join.ipynb`  
  Jupyter notebook that:
  - loads the raw OSM snapshot of vet clinics in Berlin,
  - loads the Berlin LOR (Ortsteile) polygons,
  - performs a spatial join to assign each clinic to a LOR, district, and neighborhood,
  - exports a first `v0` CSV dataset with coordinates and spatial context.

## Data flow (current status)

1. **Raw sources**  
   - `sources/raw_osm_berlin_vet_clinics_20251209.geojson`  
     Main OSM snapshot of vet clinics in Berlin (tag `amenity = veterinary`), downloaded via Overpass Turbo.

   - `sources/raw_osm_berlin_vet_clinics_2025-09-25.csv`  
     Older OSM export kept only for comparison and QA (not used as the primary source).

   - `sources/raw_berlin_lor_ortsteile.geojson`  
     Berlin LOR (Lebensweltlich orientierte Räume) polygons, used to assign clinics to districts and neighborhoods.

2. **Notebook processing**  
   The notebook `01_vet_clinics_osm_lor_join.ipynb`:
   - reads the OSM GeoJSON and the LOR GeoJSON,
   - checks and aligns the CRS (EPSG:4326 / WGS84),
   - selects relevant LOR attributes (`gml_id`, `BEZIRK`, `OTEIL`),
   - runs a spatial join (`within`) to assign each clinic to a LOR polygon,
   - renames LOR attributes to `lor_id`, `district_name`, `neighborhood_name`,
   - adds explicit `lat` / `lon` columns from the geometry,
   - exports an intermediate `v0` CSV.

3. **Intermediate output (v0)**  
   - `cache/vets_osm_berlin_with_lor_20251209_v0.csv`  
     First enriched vet clinics dataset with district and neighborhood context.  
     This file is used for further cleaning, normalization, and mapping to the final
     database schema in subsequent steps.
