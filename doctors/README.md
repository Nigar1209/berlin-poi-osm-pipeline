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

### 3. Transform (Deduplication & Geo-Enrichment)

**Script:** [`doctors_data_transformation.ipynb`](scripts/doctors_data_transformation.ipynb)

* Loads the cleaned `source/doctors.csv`.
* **Geocoding:** Fills any remaining missing `longitude` and `latitude` by geocoding addresses (using `geopy.Nominatim`).
* **Smart Deduplication (Aggregation):**
    * **Groups by** `name`, `street`, and `housenumber` to find true duplicates at a single location (e.g., 'MVZ Berlin Rudow').
    * **Aggregates** these duplicates into a *single row*.
    * **Concatenates** all unique `speciality` strings from the duplicate rows into one comma-separated list (preventing data loss).
* **Amenity Correction:** Cleans the `amenity` column using logic (e.g., if a record now has >1 `speciality`, its `amenity` is set to `clinic`).
* **Final Cleanup:** Drops any remaining "ghost" rows (e.g., `name` is still `NaN` after all steps).
* **Enrichment:** Performs a **spatial join** (`sjoin`) with the `scripts/lor_ortsteile.geojson` file to add `district_id` and `neighborhood_id` to every record.
* Saves the final, clean, enriched, and deduplicated data as `clean/doctors_clean_with_distr.csv`.

### 4. Load

**Script:** [`doctors_upload_to_db.ipynb`](scripts/doctors_upload_to_db.ipynb)

* Loads the final `clean/doctors_clean_with_distr.csv`.
* **Fix Dtypes:** Forces `id`, `postcode`, `district_id`, etc., to be read as strings (`str`) to match the DB schema.
* **Define Schema:** Connects to PostgreSQL and executes the `CREATE TABLE` statement for `berlin_source_data.doctors`.
* **Stage Data:** Re-orders the DataFrame columns (`sql_column_order`) to perfectly match the SQL table schema.
* **Load Data:** Uses the high-performance `copy_expert` (`COPY ... FROM STDIN`) method to bulk-insert all rows.
* **Add Constraints:** Executes `ALTER TABLE` to add the Foreign Key constraint, linking `doctors.district_id` to the `districts` table.

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
