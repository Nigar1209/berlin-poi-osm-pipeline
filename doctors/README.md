# Berlin Open Data ETL Pipeline: Doctors

This project is an ETL (Extract, Transform, Load) pipeline built with Python and SQL. Its purpose is to fetch raw data on healthcare facilities (doctors' offices, clinics, and medical centers) in Berlin from OpenStreetMap (OSM), execute a complex data cleaning and enrichment process, and finally load the validated data into a PostgreSQL database for analysis.

## Project Workflow

The pipeline is broken down into four main stages, executed by separate Jupyter notebooks:

### 1. Extract (Download)

**Script:** [`doctors_download.ipynb`](scripts/doctors_download.ipynb)

* Connects to the Overpass API (using an efficient query with Berlin's Relation ID).
* Fetches all `amenity=doctors` and `amenity=clinic` objects within the Berlin boundary.
* **Note:** The query returns raw **Overpass JSON** (not GeoJSON).
* Saves the raw JSON response as `source/doctors_and_clinics_raw.geojson`.

### 2. Clean (Primary Cleaning & Enrichment)

**Script:** [`doctors_data_cleaning.ipynb`](scripts/doctors_data_cleaning.ipynb)

This is the most complex stage, involving parsing, cleaning, and manual enrichment.

* Loads the raw `source/doctors_and_clinics_raw.geojson` file.
* **Parses JSON:** Iterates through the `elements` list (not `features`), flattens the `tags` key, and extracts coordinates (from `lat/lon` or `center.lat/lon`).
* **Column Reduction:** Drops over 180+ irrelevant/sparse columns, reducing the DataFrame from ~210 to ~20 key columns.
* **Manual Enrichment (Data Salvaging):**
    * Inspects rows with missing `name` but an available `website`.
    * Manually updates these rows with the correct `name`, `speciality`.
* **Ghost Row Deletion:** Drops rows that have no `name`, `website`, *or* `address` information, as they are unrecoverable.
* Saves the intermediate, cleaned data to `source/doctors.csv`.

## 3. Transform (Deduplication, Geo-Enrichment & Feature Engineering)

**Script:** [`doctors_data_transformation.ipynb`](scripts/doctors_data_transformation.ipynb)

* Loads the cleaned `source/doctors.csv`.
* **Geocoding:** Fills any remaining missing `longitude` and `latitude` by geocoding addresses (using `geopy.Nominatim`).
* **Smart Deduplication & Aggregation:**
    * **Groups by** `name`, `street`, and `housenumber` to find true duplicates at a single location.
    * **Aggregates** duplicates into a *single row*.
    * **Concatenates** all unique `speciality` strings from the duplicate rows into one comma-separated list.
    * **Amenity Correction:** If the aggregated row now has **multiple unique specialities**, the `amenity` is automatically set to `clinic`.
* **Amenity/Infrastructure Re-categorization (3-Tier Logic):**
    * Creates a new, clean `amenity` column by classifying facilities into three tiers using advanced keyword matching (`str.contains`) on the `name` column: `clinic` (Tier 3), `group_practice` (Tier 2), and `practice` (Tier 1).
* **Speciality Enrichment:** Fills remaining missing `speciality` values by matching German keywords in the `name` column against a predefined `speciality_map`.
* **Final Cleanup:** Drops any remaining "ghost" rows where `name` is still `NaN`.
* **Geo-Enrichment:** Performs a **spatial join** (`sjoin`) with the `scripts/lor_ortsteile.geojson` file to add `district_id` and `neighborhood_id` to every record.
* **Feature Engineering (Creating Healthcare Density Scores):**
    * **Capacity Scoring:** Assigns a `capacity_score` (weight) to each record based on its final `amenity` category (`practice: 1.0`, `group_practice: 2.7`, `clinic: 6.3`), derived from official statistics.
    * **Service Categorization:** Categorizes each facility's services into three types: `primary_adult`, `pediatric`, and `specialist`.
    * **Complex Aggregation & Scoring:** Calculates the total healthcare capacity for each district (`district_id`):
        * **Practices/Groups:** Aggregates the weighted `capacity_score` for each service type (`primary_adult_score`, `pediatric_score`, `specialist_score`).
        * **Clinics (Explosion Logic):** Splits the comma-separated `speciality` list of clinics into individual service rows (`explode`) to accurately count service units (e.g., `primary_care_adult_services`), which are then added to the scores.
        * **Final Scores:** Calculates the final, combined feature scores for each district (e.g., `total_primary_adult_score`, `total_pediatric_score`, `specialist_score_total`).
* Saves the final, clean, enriched, and deduplicated data as `clean/doctors_clean_with_distr.csv` **and** the aggregated feature table as `clean/healthcare_features.csv`.

### 4. Load & Feature Integration

**Script:** [`doctors_upload_to_db.ipynb`](scripts/doctors_upload_to_db.ipynb)

* This final stage performs two primary functions: loading the base data and integrating the calculated features.

#### Part 1: Loading Cleaned Doctor Records
* Loads the final `clean/doctors_clean_with_distr.csv`.
* **Fix Dtypes:** Forces `id`, `postcode`, `district_id`, etc., to be read as strings (`str`) to match the DB schema.
* **Define Schema:** Connects to PostgreSQL and executes the `CREATE TABLE` statement for `berlin_source_data.doctors`.
* **Stage Data:** Re-orders the DataFrame columns (`sql_column_order`) to perfectly match the SQL table schema.
* **Load Data:** Uses the high-performance `copy_expert` (`COPY ... FROM STDIN`) method to bulk-insert all rows.
* **Add Constraints:** Executes `ALTER TABLE` to add the Foreign Key constraint, linking `doctors.district_id` to the `districts` table.

#### Part 2: Feature Integration and Validation
* Loads the aggregated `clean/healthcare_features.csv` into a temporary staging table (`temp_healthcare_scores`).
* **Schema Update (ALTER):** Connects as `data_team` (using `SET ROLE`) to execute `ALTER TABLE` and dynamically add the new score columns (`total_primary_adult_score`, etc.) to the target table: `berlin_labels.district_features`.
* **Feature Load (UPDATE):** Executes a high-performance `UPDATE... FROM` query to transfer the calculated score values from the temporary staging table into the permanent `berlin_labels.district_features` table, matching on `district_id`.
* **Role Management & Cleanup:** Resets the role (`RESET ROLE`) before dropping the temporary staging table to manage object ownership permissions.
* **Post-Load Verification:** Executes final SQL checks to confirm:
    * The number of updated rows matches the expected count from the staging data.
    * Data integrity is maintained (no unexpected `NULL` values or inconsistencies) in the newly populated score columns.

---

## Project Structure

``` doctors/
├── scripts/
│   ├── doctors_download.ipynb
│   ├── doctors_data_cleaning.ipynb
│   ├── doctors_data_transformation.ipynb
│   ├── doctors_upload_to_db.ipynb
│   └── lor_ortsteile.geojson
│
├── clean/
│   ├── doctors_clean.csv
│   └── doctors_clean_with_distr.csv
│
├── source/
│   ├── districts.csv
│   ├── neighborhoods.csv
│   ├── doctors.csv
│   └── doctors_and_clinics_raw.geojson
│
└── README.md 
