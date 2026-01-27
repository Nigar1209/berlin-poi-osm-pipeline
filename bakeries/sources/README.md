# Bakeries – Data Sources & Transformation (Berlin)

## Project Overview

This project documents the data sourcing, extraction, transformation, and preparation
of bakery location data for Berlin, with the goal of producing a clean,
analysis-ready dataset enriched with district-level spatial context.

The project starts from data source identification and proceeds through a complete
Python-based transformation pipeline implemented in a Jupyter Notebook.
----------------------------------------------------------------------------------------------
# Data Sources

## 1. OpenStreetMap (OSM)

### Source and Origin
Identified via the OpenStreetMap public website (https://www.openstreetmap.org) by manually
searching for bakeries in Berlin and inspecting individual map points.
Tag definitions and usage were verified using the official OpenStreetMap Wiki.
Data access is handled programmatically via OSMnx / Overpass API.

### Update Frequency
Continuous (community-maintained)

### Data Type
Dynamic

### Relevant Fields
- Unique OSM ID
- Name
- Shop type
- Address (street, house number, postcode)
- Latitude
- Longitude
- Opening hours
- Sunday opening (where available)
- Brand / chain name (if available)

### Tagging Notes
Bakeries are primarily tagged as:

- shop=bakery

Additional tags observed during manual inspection include:
- `shop=pastry` (pastry-focused bakeries)
- `bakery=yes` (used inconsistently)
- Combination with `amenity=cafe` for bakery–café hybrids

These variations will need to be handled during data normalization.

### Planned Use
Primary source for bakery locations and spatial analysis.

### License
ODbL (Open Database License)

---

## 2. Berlin Open Data Portal (daten.berlin.de)

### Source and Origin
Identified through manual searches on the official Berlin Open Data Portal
(https://daten.berlin.de) using keywords such as “Bäckerei”, “Einzelhandel”,
“Lebensmittel”, and “Nahversorgung”.
Data is provided through downloadable datasets published by the city administration.

### Update Frequency
Varies by dataset (often yearly or irregular updates)

### Data Type
Mostly static or periodically updated datasets

### Relevant Fields (dataset-dependent)
- Business name
- Business category
- Address
- District
- Registration or activity status

### Planned Use
Secondary source for validation and enrichment, particularly for:
- Official business registration confirmation
- Cross-checking addresses and existence of bakeries

### License
Typically CC-BY (varies by dataset)

---

## 3. Bakery Chain Store Locators (Official Websites)

### Source and Origin
Identified via official websites of major bakery chains operating in Berlin.
Store locator pages were found by manually searching for known bakery chains and reviewing
their publicly available location listings.
Data is accessed through company websites rather than a centralized dataset or API.

### Update Frequency
Irregular, maintained by the respective companies

### Data Type
Dynamic

### Relevant Fields
- Bakery name
- Brand / chain name
- Address
- Opening hours
- Store status

### Planned Use
Used to verify and classify bakeries as chain-based versus artisanal/local businesses.

### License
No explicit open data license; data should be used cautiously and mainly for verification.

---

## 4. Business Directories (e.g. Gelbe Seiten, Google Maps)

### Source and Origin
Identified through common business directory platforms and online mapping services.
These sources were found by manually searching for bakeries in Berlin to cross-check
existing locations and operational status.

### Update Frequency
Frequent, platform-managed updates

### Data Type
Dynamic

### Relevant Fields
- Business name
- Address
- Contact information
- Operating status

### Planned Use
Supplementary source for:
- Verifying whether bakeries are still active
- Cross-checking address and opening information

### License
Proprietary; not suitable as a primary data source.

----------------------------------------------------------------------------------------------

# Data Extraction & Transformation

All data extraction and transformation steps are implemented in:

## Notebook: bakeries_transformation.ipynb

## Tools & Libraries

- Python

- Pandas

- GeoPandas

- OSMnx

- Shapely

The notebook executes the full pipeline from raw OSM data to finalized datasets.
----

# Key Transformations Applied

- Extraction of bakery-related POIs from OpenStreetMap

- Filtering and normalization of bakery-related tags

- Standardization of address fields

- Conversion to GeoDataFrame for spatial operations

- Spatial join with Berlin district boundaries

- Deduplication and basic data quality checks

- Feature engineering:

  - bakery_type (e.g. bakery, pastry)

  - is_chain (boolean)

  - brand_name

- Separation of spatial and non-spatial outputs
----------------------------------------------------------------------------------------------

# Final Datasets

1. Tabular Dataset

File: bakeries_berlin.csv
Description: Cleaned, non-spatial bakery dataset
Granularity: One row per bakery location

2. Spatial Dataset

File: bakeries_berlin.geojson
Description: GeoJSON version including geometry for mapping and spatial analysis
Coordinate System: WGS84 (latitude / longitude)
----------------------------------------------------------------------------------------------

# Final Schema (Key Fields)

| Column Name    | Description                          |
| -------------- | ------------------------------------ |
| `name`         | Bakery name                          |
| `bakery_type`  | Normalized bakery category           |
| `is_chain`     | Chain vs. independent indicator      |
| `brand_name`   | Chain brand name (if applicable)     |
| `street`       | Street name                          |
| `house_number` | House number                         |
| `postal_code`  | Postal code                          |
| `district`     | Berlin district (spatially assigned) |
| `latitude`     | Latitude                             |
| `longitude`    | Longitude                            |
| `geometry`     | Point geometry (GeoJSON only)        |
---------------------------------------------------------------------------------------------

# Data Quality Notes & Assumptions

- OpenStreetMap data is community-maintained; completeness varies by area

- Bakery classification is based on OSM tags and observed brand patterns

- Chain detection may not capture small or regional chains consistently

- Opening hours are incomplete and not fully standardized
----------------------------------------------------------------------------------------------

# Reproducibility

To reproduce the datasets:

 1. Install required Python libraries

 2. Run bakeries_transformation.ipynb top to bottom

 3. Output files will be generated in the sources/ directory


## Summary

OpenStreetMap will serve as the primary data source due to its coverage, structure,
and open licensing. Additional sources will be used selectively for validation,
classification, and data quality improvement.
