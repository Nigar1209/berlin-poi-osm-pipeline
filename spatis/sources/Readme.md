# Script Review

## 1.1 Script & Notebook Review
### 1. Source Check
The current implementation uses the Overpass API to query OpenStreetMap nodes tagged with shop=convenience and shop=kiosk. OpenStreetMap is therefore the primary data source for the Spätis layer.

### 2. Logic Check

The current pipeline uses GeoPandas spatial joins to assign district and neighborhood information to Spätis.
Spätis are first spatially joined with the districts layer to assign district_id and district_name.
After that, Spätis are spatially joined with lor_ortsteile.geojson to assign neighborhood_id and neighborhood_name.
Before the neighborhood join, the coordinate reference system (CRS) is aligned using to_crs(spatis.crs).
This shows that spatial joins for both district and neighborhood assignment are implemented, but the final output should still be checked to confirm that all IDs are filled correctly.

### 3. Requirement Comparison

Requirement comparison is based on the final export used for database insertion (774-row df_export).


| Standard Column   | Current Column      | Standard Type   | Current Type | Status / Gap                |
| ----------------- | ------------------- | --------------- | ------------ | --------------------------- |
| `id`              | `spaeti_id`         | VARCHAR(20)     | int64        | ❌ Name + type mismatch      |
| `district_id`     | `district_id`       | VARCHAR(20)     | int64        | ❌ Type mismatch             |
| `neighborhood_id` | `neighborhood_id`   | VARCHAR(20)     | int64        | ❌ Type mismatch             |
| `name`            | `name`              | VARCHAR(200)    | object       | ⚠️ Type handled at DB level |
| `latitude`        | `latitude`          | DECIMAL(9,6)    | float64      | ⚠️ Type handled at DB level |
| `longitude`       | `longitude`         | DECIMAL(9,6)    | float64      | ⚠️ Type handled at DB level |
| `geometry`        | —                   | VARCHAR (POINT) | missing      | ❌ Missing in final export   |
| `district`        | `district_name`     | VARCHAR(100)    | object       | ⚠️ Naming mismatch          |
| `neighborhood`    | `neighborhood_name` | VARCHAR(100)    | object       | ⚠️ Naming mismatch          |

additional:
- spaeti_id
- address
- phone_number 
- email
- website 
- opening_hours 


## 1.2 Schema & Database Verification
### 1. Constraint Audit

- The required foreign key constraint on `district_id` with `ON DELETE RESTRICT` and `ON UPDATE CASCADE` is correctly defined. 
- The name column is defined as NOT NULL, as required by the standardized schema.
- No foreign key constraint is defined for `neighborhood_id`. This is consistent with the current standardized schema, which does not explicitly require a foreign key for this column.

### 2. Data Type Validation

The standardized schema requires id to be `VARCHAR(20)` and numeric-only. In the current implementation, the primary key is named `spaeti_id` (instead of `id`) with a numeric (`int64`) dtype instead of a string/VARCHAR type, resulting in a naming and type mismatch.
cf. **Requirement Comparison**

### 3. Layer-Specific Columns:

- opening_hours: Requires normalization due to multiple formats (e.g.,Mo-Fr 07:00-22:00 and 24/7).

- name: Present for most records and appears consistent; no clear normalization issues visible from the preview.

- address: Appears consistent (street names only, no house numbers), but contains many missing values, which limits normalization.

- phone_number: Present for a small subset of records; unclear whether multiple formats are used (e.g., with and without country code).

- email / website: Present for very few records; values appear clear, but low coverage limits meaningful normalization.

- beverage_emphasis / has_outdoor_area / alcohol_license / payment_methods: Not present in the final export used for database insertion and therefore cannot be assessed for cleaning.

## 1.3 Transformation Plan & Documentation

### 1 List Gaps

#### Schema Compliance Check
identified Gaps:
- id → complete but present as spaeti_id (name mismatch with standard id) and exportet as `int64` instead of `VARCHAR(20)`
- district_id --> complete but exported as `int64` instead of `VARCHAR(20)`
- name --> complete but exported as `object` instead of `VARCHAR(200)`
- latitude → complete, but exported as `float64` instead of `DECIMAL(9,6)`
- longitude → complete, but exported as `float64` instead of `DECIMAL(9,6)`
- geometry --> **missing**
- neighborhood --> complete but present as neighborhood_name (name mismatch with standard) and exported as `object` instead of `VARCHAR(100)`
- district --> complete but present as district_name (name mismatch with standard) and exported as `object` instead of `VARCHAR(100)`
- neighborhood_id --> complete, but exported as `int64` instead of `VARCHAR(100)`

Planned Actions:

- id → id in the final export and export as `VARCHAR(20)`
- district_id → export as `VARCHAR(20)`
- name → export as `VARCHAR(200)`
- latitude → export as `DECIMAL(9,6)`
- longitude → export as `DECIMAL(9,6)`
- geometry --> include geometry in th final export
- neighborhood --> change neighborhood_name to neighborhood and export `VARCHAR(100)`
- district --> change district_name to district and export as `VARCHAR(100)`
- neighborhood_id --> export as `VARCHAR(100)`

#### Missing Values & Data Validity Check

Identified Gaps:
- High number of missing values in address, phone_number, email, and website.
- opening_hours contains heterogeneous free-text formats (e.g., Mo-Fr 07:00-22:00, 24/7).

Planned Actions:
- Document low coverage for optional fields in the Spätis layer documentation.
- Implement a normalization strategy for opening_hours to reduce format heterogeneity.


#### Geometry Validation

Identified Gaps:
- geometry not included in the final DB export.

Planned Actions:

- Include geometry in the final export used for database insertion.
- Ensure geometry is stored in the expected POINT() string format.

#### District & Neighborhood ID Checks

Identified Gaps:
- Identifier columns are exported as numeric types instead of VARCHAR.

Planned Actions:
- Cast district_id to VARCHAR(20) and neighborhood_id to VARCHAR(100) before export.
