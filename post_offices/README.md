# Berlin Post Offices Data Processing Pipeline

This project outlines the end-to-end pipeline for processing, cleaning, enriching, and loading data on post offices in Berlin into a PostgreSQL database. The pipeline is implemented in a series of Jupyter Notebooks using Python libraries such as `pandas`, `geopandas`, and `sqlalchemy`.

## Data Sources
- **Raw Data:** `raw_post.json` (The initial, unprocessed JSON data source).
- **Geospatial Data:** `lor_ortsteile.geojson` (Contains Berlin's neighborhood polygons, used for spatial joins).
- **Lookup Tables:** `districts.csv` and `neighborhoods.csv` (Reference tables, exported from the database, containing names and unique IDs for Berlin's districts and neighborhoods).

## Project Structure

> ```text
> └── post_offices/
>     ├── clean/
>     │   ├── deutschepost_clean.csv
>     │   └── deutschepost_clean_with_distr.csv
>     ├── scripts/
>     │   ├── convert_and_clean.ipynb
>     │   ├── post_offices_data_transformation.ipynb
>     │   ├── upload_to_database.ipynb
>     │   └── lor_ortsteile.geojson
>     └── sources/
>         ├── deutschepost_final_data_raw.csv
>         ├── deutschepost_raw.csv
>         ├── raw_post.json
>         ├── districts.csv
>         └── neighborhoods.csv
> ```

**Folder Descriptions:**
- `post_offices/scripts/`: Contains the Jupyter Notebooks that form the core of the ETL pipeline, along with the required geospatial data.
- `post_offices/sources/`: Contains the raw and intermediate data files used in the initial processing steps.
- `post_offices/clean/`: Contains the cleaned and enriched data files that are ready for loading into the database or for further analysis.

---
## Pipeline Workflow

The process is divided into three main stages, each handled by a dedicated script.

### Stage 1: Initial Cleaning and Standardization
**Script:** `post_offices/scripts/convert_and_clean.ipynb`

This script handles the initial processing of the raw JSON data to transform it into a usable, standardized CSV format.
* **Initial Conversion:** The raw `raw_post.json` file is parsed, and the primary list of locations is extracted into a base CSV file (`deutschepost_raw.csv`).
* **Feature Extraction & Cleaning:** A series of operations are then performed to clean the raw CSV:
    * **Feature Extraction:** Key information is extracted from complex string-based columns (e.g., parsing `pfTimeinfos` to create an `opening_hours` string and `geoPosition` to create `latitude` and `longitude` columns).
    * **Filtering by Location Type:** Irrelevant location types (e.g., `Poststation`) are removed.
    * **Column Cleanup & Renaming:** Unnecessary columns are dropped, and existing columns are renamed to a standard `snake_case` format.
    * **Adjusting Data Types:** The data types for the `zip_code` and `id` columns were explicitly converted to `object` (string). This ensures that these fields are treated as textual labels rather than numerical values, preventing potential errors from unintended mathematical operations.
* **Final Output:** The resulting clean DataFrame is saved to `clean/deutschepost_clean.csv`, ready for the enrichment stage.

### Stage 2: Data Enrichment
**Script:** `post_offices/scripts/post_offices_data_transformation.ipynb`

This stage augments the location data with geographical context by adding unique IDs for districts and neighborhoods.
* **Geospatial Join:** The **GeoPandas** library is used to perform a spatial join between the post office locations and the `lor_ortsteile.geojson` polygons. This temporarily adds the human-readable `district` and `neighborhood` names to the dataset.
* **ID Merging:** The dataset is then merged with the `districts.csv` and `neighborhoods.csv` lookup tables on the name columns to add the final `district_id` and `neighborhood_id`.
* **Column Cleanup:** After the IDs are merged, the temporary name columns (`district`, `neighborhood`) are dropped.
* **Final Result:** The enriched DataFrame is saved as `deutschepost_clean_with_distr.csv`.

### Stage 3: Test loading data into the Neon DB
**Script:** `post_offices/scripts/upload_to_database.ipynb`

[Description here](layered-populate-data-pool-da/post_offices/scripts/README.md)

---
## Final Database Schema

The final table in the database is defined by the following SQL schema:
| Column Name | Key | Data Type | Description | Data Example |
|---|---|---|---|---|
| `id` | Primary Key | `VARCHAR(20)` | Unique identifier for the post office. | `4340626`, `6730` |
| `district_id` | Foreign Key | `VARCHAR(20)` | Identifier for the Berlin district, references the `districts` table. | `11001001` |
| `neighborhood_id` | | `VARCHAR(20)` | Identifier for the Berlin neighborhood. | `101` |
| `zip_code` | | `VARCHAR(10)` | The 5-digit postal code of the location. | `10178` |
| `city` | | `VARCHAR(20)` | City name, expected to be 'Berlin'. | `Berlin` |
| `street` | | `VARCHAR(200)` | The name of the street where the office is located. | `Rathausstr.` |
| `house_no` | | `VARCHAR(20)` | The house number on the street. | `5` |
| `location_type` | | `VARCHAR(200)`| The category or type of the postal location. | `POSTBANK_FINANCE_CENTER` |
| `location_name` | | `VARCHAR(200)`| The specific name or title of the post office branch. | `Postbank Filiale` |
| `closure_periods` | | `VARCHAR(400)`| Information on planned or temporary closures (e.g., holidays). | `[]` |
| `opening_hours` | | `VARCHAR(400)`| A formatted string detailing the weekly opening hours. | `Monday: 09:00-18:00; ...` |
| `latitude` | | `DECIMAL(9,6)` | The geographic latitude of the location (WGS 84). | `52.517041` |
| `longitude` | | `DECIMAL(9,6)` | The geographic longitude of the location (WGS 84). | `13.388860` |

