RECYCLING POINTS IN BERLIN
OpenStreetMap Data Extraction, Normalization & Enrichment
=========================================================

This project extracts, cleans, and normalizes recycling location data
for Berlin from OpenStreetMap (OSM) into an analysis-ready GeoDataFrame.

The notebook is designed to handle highly heterogeneous OSM metadata
while preserving data provenance and avoiding inferred or fabricated
information.


PROJECT GOALS
-------------

- Extract all amenity=recycling locations in Berlin from OpenStreetMap
- Interpret granular recycling:* tags into explicit material categories
- Normalize noisy, overlapping OSM metadata into user-facing fields
- Preserve ambiguity where data is unclear
- Produce a clean, structured GeoDataFrame suitable for analysis or APIs


DESIGN PRINCIPLES
-----------------

- No invented data – only explicit OSM tags are used
- Structured tags are preferred over free text
- Fallback logic is explicit and ranked
- Human readability without semantic loss
- Reproducibility over live API calls


DATA SOURCE
-----------

Primary source:
- OpenStreetMap (via OSMnx)

OSM tag used:
- amenity=recycling

Geographic scope:
- Berlin, Germany

To avoid repeated API calls and ensure reproducibility, the raw OSM
extract is persisted locally and reused throughout the notebook.


DEPENDENCIES
------------

Required Python packages:

- osmnx
- geopandas
- pandas
- numpy

Install via:
pip install osmnx geopandas pandas numpy


PROJECT STRUCTURE
-----------------

.
├── scripts/
│   └── recycling_points_berlin.ipynb
├── sources/
│   ├── raw_recycling_points.geojson
│   ├── raw_recycling_points.csv
│   ├── final_recycling_points_with_district.geojson
│   └── final_recycling_points_with_district.csv
└── README.txt


PROCESSING PIPELINE OVERVIEW
----------------------------

1) DATA EXTRACTION (ONE-TIME)

- Query OpenStreetMap for amenity=recycling features in Berlin
- Persist results as GeoJSON and CSV
- All further analysis loads from disk to ensure reproducibility


2) RECYCLING TAG INTERPRETATION

OpenStreetMap models recycling using hierarchical tags:

- recycling:<item>            -> acceptance (yes / no / customers)
- recycling:<item>:<subtype>  -> material details (e.g. glass color)

Derived output fields:

- accepted_recycling_items
- not_accepted_recycling_items
- other_recycling_items

Design guarantees:
- Order of tags is preserved
- Subtype detail is not collapsed
- No acceptance is inferred from ambiguous tags


3) COLUMN GROUPING STRATEGY

OSM metadata is grouped by semantic purpose rather than raw tag name.

Groups:

1. Identity
2. Geometry
3. Name & Operator
4. Address
5. Contact
6. Website
7. Recycling Types
8. Accessibility
9. Opening & Access Times
10. Metadata / Notes

Each group is:
- Explored independently
- Normalized using group-specific rules
- Collapsed into user-facing fields


NORMALIZATION HIGHLIGHTS
------------------------

NAME RESOLUTION

Produces:
- display_name   : best human-readable label
- name_metadata  : all name/operator variants with provenance
- entity_type    : classification hints (e.g. man_made, operator:type)

Priority order:
name -> short_name -> localized name -> operator (fallback)

Entity types are never used to invent names.


ADDRESS CONSTRUCTION

Primary structured address built from:
- addr:street
- addr:housenumber
- addr:postcode
- addr:suburb

Fallback logic (explicit precision → coverage tradeoff):
1. ref
2. description
3. position

Final field:
- full_address


CONTACT NORMALIZATION

All phone and email variants are merged into:
- contact_combined

Original provenance is preserved via prefixed labels.


WEBSITE NORMALIZATION

Rules:
- Preserve existing URL schemes
- Assume https:// only when scheme is missing
- Leave missing values untouched

Final field:
- website_combined


ACCESSIBILITY MODELING

Core accessibility fields:
- wheelchair_access
- access_restriction
- floor_level
- unit_count

Derived summaries:
- physical_obstacles
- environmental_features
- accessibility_features

All accessibility information is derived strictly from explicit OSM tags.
Missing values are treated as unknown, not negative.


FINAL OUTPUT
------------

The final GeoDataFrame contains:

- Geometry (points / polygons)
- Clean identity fields
- Human-readable address
- Explicit recycling material acceptance
- Accessibility summaries
- Contact and website information

All raw OSM noise and redundant columns are removed.


FINAL DATASET OVERVIEW (SCHEMA SUMMARY)
=====================================

| Column Name                   | Data Type | Summary                                              |
|------------------------------|-----------|------------------------------------------------------|
| id                           | int64     | Internal feature identifier                          |
| source                       | string    | Data source provenance identifier                    |
| landuse                      | string    | Land use classification from OSM                     |
| geometry                     | geometry  | Spatial geometry (Point or Polygon)                  |
| accepted_recycling_items     | object    | Explicitly accepted recycling materials              |
| not_accepted_recycling_items | object    | Explicitly rejected recycling materials              |
| display_name                 | object    | Best human-readable name                             |
| name_metadata                | object    | All name/operator variants with provenance           |
| entity_type                  | object    | Entity classification hints                          |
| full_address                 | string    | Constructed human-readable address                   |
| contact_combined             | object    | Aggregated contact information                       |
| website_combined             | object    | Aggregated website URLs                              |
| access_restriction           | string    | Explicit access limitations                          |
| wheelchair_access            | string    | Wheelchair accessibility (explicit tagging only)     |
| physical_obstacles           | string    | Explicitly tagged physical barriers                  |
| environmental_features       | string    | Environmental or structural features                 |
| floor_level                  | Float64   | Floor or level information                           |
| unit_count                   | Int64     | Number of recycling units or containers              |
| accessibility_features      | string    | Aggregated accessibility-related features            |
| availability_info            | string    | Opening times or availability information            |
| is_operational               | boolean   | Operational status if explicitly tagged              |
| district                     | object    | Administrative district                              |
| neighborhood                 | object    | Neighborhood or locality                             |
| neighborhood_id                  | object    | Neighborhood or locality identifier                   |
| district_id                  | object    | Administrative district identifier                   |


FINAL DATASET SCHEMA
===================

The final dataset is a GeoDataFrame where each row represents a single
recycling location extracted from OpenStreetMap.

Data types reflect Pandas / GeoPandas dtypes after normalization.
Missing values represent unknown or unspecified information, not false
or negative assertions.


CORE IDENTIFIERS & GEOMETRY
--------------------------

id
  Type: int64
  Description:
  Stable internal identifier for each recycling feature.

source
  Type: string
  Description:
  Data source identifier. Used to track provenance of the feature
  (e.g. OpenStreetMap).

landuse
  Type: string
  Description:
  Land use classification from OSM, if present. May be null if not tagged.

geometry
  Type: geometry
  Description:
  GeoPandas geometry (Point or Polygon) representing the spatial location
  of the recycling feature.


RECYCLING MATERIAL ACCEPTANCE
-----------------------------

accepted_recycling_items
  Type: object (list-like)
  Description:
  Explicit list of recycling materials accepted at this location,
  derived from recycling:* = yes tags. Subtypes (e.g. glass color)
  are preserved.

not_accepted_recycling_items
  Type: object (list-like)
  Description:
  Explicit list of recycling materials not accepted at this location,
  derived from recycling:* = no tags.

Note:
Materials not listed in either field should be interpreted as unknown,
not implicitly accepted or rejected.


NAME & ENTITY METADATA
---------------------

display_name
  Type: object (string)
  Description:
  Best human-readable name for the recycling location, resolved using
  prioritized OSM name tags and explicit fallbacks.

name_metadata
  Type: object (dictionary-like)
  Description:
  Collection of all available name- and operator-related tags with
  provenance preserved.

entity_type
  Type: object (string)
  Description:
  Classification hints describing the nature of the entity
  (e.g. man_made, operator:type). Not used to infer names.


ADDRESS & LOCATION CONTEXT
--------------------------

full_address
  Type: string
  Description:
  Human-readable address constructed from structured address tags,
  with explicit fallbacks when structured data is missing.

district
  Type: object (string)
  Description:
  Administrative district within Berlin, if available.

neighborhood
  Type: object (string)
  Description:
  Neighborhood or locality name, if available.

neighborhood_id
  Type: object (string)
  Description:
  Identifier associated with the neighborhood, when present.

district_id
  Type: object (string)
  Description:
  Identifier associated with the administrative district, when present.


CONTACT & WEB INFORMATION
-------------------------

contact_combined
  Type: object (string)
  Description:
  Aggregated contact information (phone, email, etc.), with original
  OSM tag provenance preserved via labels.

website_combined
  Type: object (string)
  Description:
  Aggregated website URLs associated with the location. URL schemes are
  preserved or normalized when missing.


ACCESSIBILITY & ACCESS CONTROL
------------------------------

access_restriction
  Type: string
  Description:
  Access limitations such as private, customers-only, or restricted use,
  derived from explicit OSM access tags.

wheelchair_access
  Type: string
  Description:
  Wheelchair accessibility status as explicitly tagged in OSM
  (e.g. yes, no, limited). Missing values indicate unknown accessibility.

physical_obstacles
  Type: string
  Description:
  Explicitly tagged physical barriers or obstacles affecting access.

environmental_features
  Type: string
  Description:
  Environmental or structural features relevant to accessibility
  (e.g. covered, indoor, underground).

floor_level
  Type: Float64
  Description:
  Floor or level information when explicitly tagged. Nullable.

unit_count
  Type: Int64
  Description:
  Number of recycling units or containers, if explicitly specified.

accessibility_features
  Type: string
  Description:
  Aggregated summary of accessibility-related features derived strictly
  from explicit OSM tags.


OPERATIONAL STATUS & AVAILABILITY
--------------------------------

availability_info
  Type: string
  Description:
  Information about opening times, access hours, or availability
  conditions, when explicitly provided.

is_operational
  Type: boolean
  Description:
  Indicates whether the recycling location is operational, based on
  explicit OSM lifecycle or status tags. Null indicates unknown status.


DATA TYPE NOTES
---------------

- object columns may contain strings, lists, or dictionary-like structures
- string columns use Pandas string dtype where normalization was possible
- Nullable integer and float types (Int64, Float64) preserve missing values
- geometry column uses GeoPandas geometry dtype

No column encodes inferred or assumed information.


NOTES & LIMITATIONS
-------------------

- OSM data quality varies by contributor
- Missing tags are treated as NA, not false
- Local recycling rules cannot be inferred
- Results reflect OSM state at extraction time

