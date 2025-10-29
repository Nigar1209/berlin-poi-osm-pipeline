# Berlin Open Data ETL Pipeline: Nightclubs

This project is an ETL (Extract, Transform, Load) pipeline built with Python and SQL. Its purpose is to fetch raw data on nightclubs in Berlin from OpenStreetMap (OSM), clean it, enrich it with district/neighborhood data, and finally load it into a PostgreSQL database for analysis.

## Project Workflow

The pipeline is broken down into four main stages, executed by separate Jupyter notebooks:

### 1. Extract (Download)

**Script:** [`night_clubs_download.ipynb`](scripts/night_clubs_download.ipynb)

* Connects to the Overpass API (using an efficient query with Berlin's Relation ID).
* Fetches all `amenity=nightclub` objects within the Berlin boundary.
* Saves the raw JSON response as `source/night_clubs_raw.geojson`.

### 2. Clean

**Script:** [`night_clubs_data_cleaning.ipynb`](scripts/night_clubs_data_cleaning.ipynb)

* Loads the raw `night_clubs_raw.geojson` file.
* Flattens the JSON structure into a DataFrame.
* Performs initial cleaning: drops irrelevant columns, merges duplicate columns (e.g., `phone`, `website`), and handles missing values.
* Saves the first-pass cleaned data to `source/night_clubs.csv`.

### 3. Transform (Enrich)

**Script:** [`night_clubs_data_transformation.ipynb`](scripts/night_clubs_data_transformation.ipynb) 

* Loads the cleaned `night_clubs.csv`.
* **Geocoding:** Fills missing `longitude` and `latitude` by geocoding addresses (using `geopy`).
* **Reverse Geocoding:** Fills missing address columns (`street`, `postcode`) by reverse-geocoding coordinates.
* **Enrichment:** Performs a **spatial join** (`sjoin`) with the `scripts/lor_ortsteile.geojson` file to add `district_id` and `neighborhood_id`.
* **Validation:** Confirms that all coordinates fall within the Berlin boundary.
* Saves the final, enriched data as `clean/night_clubs_clean_with_distr.csv`.

### 4. Load

**Script:** [`night_clubs_upload_to_database.ipynb`](scripts/night_clubs_upload_to_database.ipynb)

* Loads the final `clean/night_clubs_clean_with_distr.csv`.
* **Define Schema:** Connects to PostgreSQL and executes the `CREATE TABLE` statement for `berlin_source_data.night_clubs`.
* **Stage Data:** Re-orders the DataFrame columns to perfectly match the SQL table schema.
* **Load Data:** Uses the high-performance `copy_expert` (`COPY ... FROM STDIN`) method to bulk-insert all rows.
* **Add Constraints:** Executes `ALTER TABLE` to add the Foreign Key constraint, linking `night_clubs.district_id` to the `districts` table.

---

## Project Structure

## Project Structure
```
night_clubs/
├── scripts/
│   ├── night_clubs_download.ipynb
│   ├── night_clubs_data_cleaning.ipynb
│   ├── night_clubs_data_transformation.ipynb
│   ├── night_clubs_upload_to_database.ipynb
│   └── lor_ortsteile.geojson
│
├── clean/
│   ├── night_clubs_clean.csv
│   └── night_clubs_clean_with_distr.csv
│
├── source/
│   ├── districts.csv
│   ├── neighborhoods.csv
│   ├── night_clubs_raw.geojson
│   └── night_clubs.csv
│
└── README.md
