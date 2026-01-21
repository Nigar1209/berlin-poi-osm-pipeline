# Bakeries – Data Sources (Berlin)

This document describes the identified data sources for bakeries in Berlin.
The focus of this step is to document where bakery data can be found, how it is accessed,
how often it is updated, and how it can later be integrated into the existing database
structure (districts, neighborhoods, and points of interest).

This step does not include data extraction or transformation yet.

---

## 1. OpenStreetMap (OSM)

### Source and Origin
Identified via the OpenStreetMap public website (https://www.openstreetmap.org) by manually
searching for bakeries in Berlin and inspecting individual map points.
Tag definitions and usage were verified using the official OpenStreetMap Wiki.
The data is accessible via regional downloads (e.g. Geofabrik) and APIs such as Overpass in later stages.

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

### Notes on Tagging
Bakeries in OpenStreetMap are primarily tagged as:
- `shop=bakery`

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

---

## Planned Transformation and Normalization (Next Steps)

- Consolidate bakery records from multiple sources
- Normalize shop types (bakery, pastry, bakery–café)
- Classify bakeries as artisanal or chain-based
- Link bakery locations to districts and neighborhoods
- Standardize opening hours and Sunday opening indicators

---

## Summary

OpenStreetMap will serve as the primary data source due to its coverage, structure,
and open licensing. Additional sources will be used selectively for validation,
classification, and data quality improvement.
