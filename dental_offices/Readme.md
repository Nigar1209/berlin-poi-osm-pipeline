# Dental Offices in Berlin – Data Collection & Analysis

## Overview
This project collects, processes, and analyzes data about dental practices in Berlin.
The focus lies on building a **lightweight, reproducible data pipeline** using openly
available geospatial data.

The primary goal is to obtain a **consistent, enriched, and quality-checked dataset**
of dental offices that can be used for:
    - spatial analysis
    - mapping and visualization
    - comparison with other public health datasets
    - downstream database ingestion or analytics workflows
---

## Project Structure

This project is organized to clearly separate raw data sources, processing logic, and cached artifacts generated during data preparation.

```text
project/
├── scripts/
│   ├── cache/
│   │   └── nominatim_reverse_cache.pkl
│   ├── dental_offices_data_prepocessing.ipynb
│   └── nominatim_reverse_cache.pkl
│
├── sources/
│   ├── Readme.md
│   ├── doctors_202601211553.csv
│   ├── raw_osm_dental_offices_v_01_19_2026.csv
│   └── raw_osm_dental_offices_v_01_19_2026.geojson
│
└── Readme.md
```

### **Directory Overview**
`scripts/`
Contains all data processing logic and intermediate artifacts.
    - `dental_offices_data_prepocessing.ipynb` -> Main notebook responsible for cleaning, normalizing, enriching, and validating dental office data.

`cache/`
Stores cached lookup results to avoid redundant external API calls.
    - `nominatim_reverse_cache.pkl` -> Cached reverse geocoding results (Nominatim) used to improve performance and reproducibility.

`sources/`
Holds all raw and reference data used as inputs for the processing pipeline.
    - `doctors_202601211553.csv` -> Reference dataset containing doctor-related records used to detect and
    remove overlapping identifiers from the dental offices dataset.
    - `raw_osm_dental_offices_v_01_19_2026.csv` -> Raw OpenStreetMap dental office data in tabular format.
    - `raw_osm_dental_offices_v_01_19_2026.geojson` -> Raw OpenStreetMap dental office data including geospatial features.
    - `Readme.md` -> Source-specific documentation describing data provenance and format details.

`Readme.md`
Main project documentation providing an overview of the project goals, data sources, and processing steps.


## Data Sources
### Evaluated Sources

The following data sources were evaluated:

 - OpenStreetMap (amenity=dentist)

 - Berlin Open Data Portal (health and medical facility datasets)

 - KZV Berlin (Kassenzahnärztliche Vereinigung – official registry)

After evaluation, **OpenStreetMap (OSM)** was selected as the primary data source.

OSM is the only source that provides **continuously updated, dynamic data** that can
be accessed programmatically with minimal technical overhead. Data can be retrieved
via standard APIs or extracts without requiring browser automation or additional
infrastructure such as Selenium or WebDriver.

Other sources, while valuable for validation and legal verification, are either
static, updated infrequently, or require complex scraping setups that are outside
the scope of this project.

### OpenStreetMap (OSM)

| Field            | Description                                                                                                     |
|------------------|-----------------------------------------------------------------------------|
| source           | [OpenStreetMap (OSM) - API](https://overpass-api.de/api/interpreter), global crowdsourced geo DB                |
| update_frequency | Monthly / as published                                                                                          |
| data_type        | Dynamic (crowdsourced data accessed via API)                                                                    |
| relevant_fields | name, addr:street, addr:housenumber, addr:postcode, addr:city,<br>level, addr:floor, description, opening_hours,<br>check_date:opening_hours, check_date,<br>healthcare:speciality,<br>wheelchair, wheelchair:description, toilets:wheelchair,<br>phone, contact:website, contact:email, contact:phone, email, url, website,<br>geometry, health_facility:type,<br>health_specialty:oral_surgery, health_specialty:orthodontics, health_specialty:periodontology |
 
| license          | ODbL 1.0 (Open Database License); attribution required, share-alike applies |

## Data Processing – Part 1: Integration & Normalization
1. Data Extraction

Dental offices are fetched from OpenStreetMap using osmnx
with the tag `amenity=dentist` for the geographic boundary of Berlin, Germany.

Both **CSV** and **GeoJSON** snapshots of the raw data are persisted to ensure
full reproducibility and offline inspection.

2. Column Selection & Standardization

Only fields relevant to dental practices, accessibility, contact information,
and geospatial analysis are retained.

OSM-style address tags are normalized into standardized column names
(e.g. `addr:street` → `street`).

3. Speciality Mapping

Dental specialities are derived using a priority-based approach:
    - Use `healthcare:speciality` if populated
    - Otherwise infer speciality from boolean specialty flags
    (`oral_surgery`, `orthodontics`, `periodontology`)
    - Default to `None` if no information is available

Redundant raw specialty columns are dropped after consolidation.

4. Geometry Normalization

All geometries are converted to `point geometries`.
For non-point OSM features (e.g. polygons), representative points are used.

Latitude and longitude are extracted explicitly to support
non-GIS workflows and database storage.

5. Attribute Consolidation

Multiple overlapping OSM attributes are merged into unified fields:

    - Phone numbers (`phone`, `contact:phone`)
    - Email addresses (`email`, `contact:email`)
    - Websites (`website`, `contact:website`, `url`)
    - Accessibility information (wheelchair access, toilets)
    - Check dates (general vs opening hours)

Custom merge logic ensures semantic clarity and avoids data loss.

6. Neighborhood & District Assignment

Each dental office is spatially joined with Berlin neighborhood
(LOR Ortsteile) polygons.

The dataset is enriched with:

    - district
    - neighborhood
    - neighborhood identifier
    - standardized Berlin district IDs

Unmapped districts are explicitly reported for quality control.

7. Identifier Handling & Integrity Checks

OSM identifiers are preserved and normalized as string-based IDs
to ensure database compatibility.

Basic integrity checks verify:

   - total record count
   - uniqueness of identifiers

8. Floor / Level Standardization

Floor information is standardized using locale-specific mappings
(DE / UK / US supported), converting numeric or coded levels into
human-readable formats (e.g. `0` → `EG`, `1` → `1.OG`).

9. Address Enrichment via Reverse Geocoding

Missing address components are enriched using **Nominatim reverse geocoding**.

Key characteristics:

    - strict rate limiting (1 request/second)
    - retry logic with spatial coordinate shifts
    - persistent local caching to minimize API usage
    - fallback handling for incomplete address responses

This step significantly improves address completeness
while respecting public API usage policies.

10. Address Formatting

A standardized, human-readable address string is constructed from:

    - street
    - house number
    - floor
    - postal code
    - city
    - neighborhood

Only records with at least one valid address component are formatted.

1.  Data Quality Overview

The first processing stage concludes with:

    - column and datatype inspection
    - missing value analysis  
    - summary statistics for dataset size and completeness

This provides a clear baseline for subsequent processing steps.

## Licensing Notes

- **OpenStreetMap data** is licensed under the **Open Database License (ODbL 1.0)**
- Attribution to OpenStreetMap contributors is required
- Derived datasets must comply with share-alike provisions