# Transformation Plan for Berlin Schools Data Layer

This directory contains the data model and transformation logic for the Berlin schools data layer.  
It builds on the source documentation in `schools/sources/README.md` and defines the target schema and high-level transformation steps.

## 1. Goal

Thats a clean, query-friendly schools table for Berlin that:

- uses a consistent column schema across layers.
- links to existing districts and neighbourhoods.
- exposes meaningful attributes for analysis (school type, address, accessibility, languages, etc.)

---

## 2. Target table schema (logical)

This is the logical schema.

### 2.1 Core columns (common pattern)

These columns follow the common column schema used across the project.

| Column name       | Type (logical) | Required | Description |
|-------------------|----------------|----------|-------------|
| `id`              | string         | yes      | Primary key. |
| `district_id`     | string         | yes      | Second key to the Berlin districts table. |
| `district_name`   | string         | yes      | District name. |
| `neighborhood_id` | string         | no       | Foreign key to a neighbourhood table. |
| `neighborhood`    | string         | no       | Name of the neighbourhood / LOR / planning area. |
| `name`            | string         | yes      | School name. |
| `latitude`        | numeric        | no       | Latitude of the school (WGS84). |
| `longitude`       | numeric        | no       | Longitude of the school (WGS84). |
| `geometry`        | geometry/text  | no       | Geometry representation (e.g. POINT(lat, lon) or polygon as text/geometry). |

### 2.2 Address & ownership

| Column name        | Type (logical) | Required | Description |
|--------------------|----------------|----------|-------------|
| `street`           | string         | no       | Street name. |
| `house_number`     | string         | no       | House number. |
| `postal_code`      | string         | no       | Postal code. |
| `city`             | string         | no       | City. |
| `ownership`        | string         | no       | Ownership category. |
| `official_school_id` | string       | no       | Official school ID from Berlin administration. |

### 2.3 School type & educational profile

| Column name         | Type (logical) | Required | Description |
|---------------------|----------------|----------|-------------|
| `school_type`       | string         | yes      | High-level school type. |
| `school_subtype`    | string         | no       | Specific sub-type of schools. |
| `grades_offered`    | string         | no       | Range of grades. |
| `is_primary`        | boolean        | no       | Has school primary education. |
| `is_secondary`      | boolean        | no       | Is school lower/upper secondary education. |
| `is_vocational`     | boolean        | no       | Is school vocational. |
| `is_special_needs`  | boolean        | no       | Has special needs / inclusive schools. |
| `languages`         | string         | no       | Comma-separated list of main instruction languages. |
| `has_all_day_program` | boolean      | no       | Has school offers all-day programmes (Ganztag). |

### 2.4 Accessibility & contact

| Column name               | Type (logical) | Required | Description |
|---------------------------|----------------|----------|-------------|
| `is_barrier_free`         | boolean        | no       | Is barrier-free / wheelchair accessible. |
| `accessibility_notes`     | string         | no       | Notes about accessibility. |
| `phone`                   | string         | no       | Contact phone number. |
| `email`                   | string         | no       | Contact email address. |
| `website`                 | string         | no       | Official school website. |

### 2.5 Provenance & technical fields

| Column name            | Type (logical) | Required | Description |
|------------------------|----------------|----------|-------------|
| `primary_source`       | string         | yes      | Main source key. |
| `source_ids`           | string         | no       | Comma-separated list of original IDs from different sources (for cross-reference). |
| `last_source_update`   | date/datetime  | no       | Date when the source record was last updated. |
| `last_ingested_at`     | date/datetime  | no       | Timestamp when this record was last ingested into this layer. |
| `is_active`            | boolean        | no       | Is Active. |

---

## 3. High-level transformation plan

This section describes how plan to derive the target schema from the sources documented in `schools/sources/README.md`.

### 3.1 Primary source

- Use OSM_SCHOOLS as the primary source for school locations.
- Extract from OSM:
  - geometry and coordinates.
  - school name.
  - address information (`addr:street`, `addr:housenumber`, `addr:postcode`, `addr:city`).
  - basic attributes such as `operator`, `operator:type`, and education-related tags (`isced:level`, `grades`, `min_age`, `max_age` where available).
- For each OSM feature that we classify as a school:
  - create one record in the target schema.
  - set primary_source = OSM_SCHOOLS.
  - keep the original OSM ID in `source_ids` (e.g. `osm:node/…`, `osm:way/…`).

### 3.2 Enrichment sources

Other sources primarily for enrichment, validation, and gap-filling on top of the OSM base:

- SCHULEN_WMS:
  - verify locations.
  - enrich district and locality information.
  - add or confirm ownership information.
  - add official school names where they differ from OSM names.
  - In cases where a school exists in WMS but is missing in OSM, we may create a school record with  
    primary_source = SCHULEN_WMS as a fallback, but OSM remains the default primary source.

- SCHULVERZEICHNIS_WEB:
  - enrich school types and sub-types.
  - add languages, profiles, and all-day programme flags.
  - enrich accessibility information.
  - obtain or confirm official school IDs.

- WIKIDATA_SCHOOLS:
  - optionally add metadata such as founding year, international school flags, and external links (Wikipedia, official website)

### 3.3 Matching & deduplication

- Base principle:  
  - Start with the OSM records as primary.  
  - Enrichment sources are matched onto these records.

- Matching rules (enrichment → OSM) may include:
  - direct ID mappings if available in tags (e.g. official school ID stored in OSM).
  - normalised school name.
  - address components.
  - spatial proximity (distance between geometries).

- If multiple enrichment sources match the same OSM school:
  - create a single merged record.
  - All original source IDs write into source_ids (comma-separated).
  - define precedence rules per attribute, for example:
    - geometry and district information: prefer official WMS if it looks more precise.
    - detailed profile/language information: prefer the school directory.
    - basic existence and geometry: OSM remains the baseline.

- If enrichment sources contain schools with no OSM match:
  - Create new records with primary_source set to the corresponding source.
  - Is clearly and distinctly marked for differentiation.

### 3.4 Linking to districts and neighbourhoods

- Existing district and neighbourhood/LOR tables to derive:
  - `district_id` and `district_name`.
  - `neighborhood_id` and `neighborhood` where feasible.
- Possible strategies:
  - spatial join (geometry of school to district/neighbourhood polygons).
  - or lookup based on address fields if reliable.
- Ensure that:
  - every record has a valid `district_id` where possible.
  - foreign key relationships can be established in the database layer.

### 3.5 Handling missing or inconsistent data

- Define and implement rules for:
  - missing coordinates:  
    - attempt to use geometry from WMS or other sources as a fallback,  
    - if still missing, either drop the record or keep it with `geometry`/`latitude`/`longitude` null and a flag.
  - ambiguous or conflicting names:  
    - prefer official naming from the WMS or the school directory.
  - missing address components:  
    - complete them using enrichment sources.
    - otherwise keep partial addresses but still derive districts via spatial join.
  - closed or inactive schools:  
    - use `is_active` boolean to mark them instead of deleting. 
    - if a source provides status information (open/closed), reflect it in the target table.

---
