# Veterinary Clinics – Berlin

This directory contains the new vet clinics data layer for Berlin.

The goal of this layer is to provide a clean, well-documented dataset of veterinary clinics in Berlin, suitable for use in the application (search layer, coverage analysis, and neighborhood-level context).

## Data sources (high-level)

- **Primary source:**  
  OpenStreetMap, vet clinics tagged as `amenity = veterinary` within the administrative boundary of Berlin.  
  Main snapshot file: `sources/raw_osm_berlin_vet_clinics_20251209.geojson` (GeoJSON exported via Overpass Turbo).

- **Spatial reference:**  
  Berlin LOR (Lebensweltlich orientierte Räume) neighborhood / district boundaries.  
  File: `sources/raw_berlin_lor_ortsteile.geojson`.  
  Used to assign each clinic to a district (Bezirk) and neighborhood (Ortsteil).

- **Historical / QA snapshot:**  
  Older OSM export kept for comparison and quality checks:  
  `sources/raw_osm_berlin_vet_clinics_2025-09-25.csv` (not used as the main source).

The cleaning and modelling steps from these raw files to the final table are documented in the corresponding Jupyter notebooks in this directory.
