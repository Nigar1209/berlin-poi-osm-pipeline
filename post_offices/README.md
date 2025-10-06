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
>     │   ├── upload_to_test_database.ipynb
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
**Script:** `post_offices/scripts/upload_to_test_database.ipynb`

[Description here](layered-populate-data-pool-da/post_offices/scripts/README.md)

### Stage 4: Populating and Validating the Production Table
**Script:** `post_offices/scripts/upload_to_database.ipynb`

This final stage of the pipeline connects to the development database, deploys the final table schema, loads the prepared data, and runs a series of comprehensive validation checks to ensure data integrity and correctness.

* **Database Connection:** A connection to the local development PostgreSQL database (`layereddb`) was established using SQLAlchemy, with `pool_pre_ping=True` to ensure a stable and reliable connection.

* **Schema Deployment:** The `berlin_source_data.post_offices` table was created by executing a `CREATE TABLE` statement. The script first uses `DROP TABLE IF EXISTS` to ensure the process is idempotent (re-runnable without errors).

* **Data Preparation:** The final enriched dataset (`deutschepost_clean_with_distr.csv`) was loaded into a pandas DataFrame, and its columns were reordered to exactly match the SQL table schema, creating a final `df_for_upload` DataFrame.

* **Data Loading:** The data was efficiently loaded into the new table using PostgreSQL's high-performance `COPY` command. This was executed via a low-level `psycopg2` connection obtained from the SQLAlchemy engine. The `SET search_path` command was used to guarantee the correct schema context for the transaction.

* **Adding Foreign Key Constraint:** After the data was successfully loaded, an `ALTER TABLE` command was executed to add the `FOREIGN KEY` constraint to the `district_id` column, establishing referential integrity with the `districts` table.

* **Post-Load Validation Queries:** A comprehensive suite of SQL validation queries was executed directly from the notebook to verify the integrity and quality of the loaded data. These checks included:
    * Verifying the total row count against the source DataFrame.
    * Checking for coordinate outliers outside of Berlin's approximate bounding box.
    * Comparing distinct `district_id`s between the `post_offices` table and the `districts` reference table.
    * Confirming primary key uniqueness.
    * Explicitly checking for any rows with foreign key violations.

* **Applying NOT NULL Constraints:** As a final schema modification, a series of `ALTER TABLE ... SET NOT NULL` commands were executed to enforce that key columns could not contain null values.

* **Final Schema Verification:** The script concluded by querying the `information_schema` to programmatically display and confirm the final table structure, including all column names, data types, and nullability constraints.

---

## Next Steps & Potential Automation

The `closure_periods` column, which currently exists as a raw text field, offers opportunities for future automation to enhance the dataset's usability and provide real-time status updates.

* **Automated Removal of Permanently Closed Locations:** A future script could be developed to parse the `closure_periods` string. This script would identify entries indicating a permanent closure (e.g., by looking for keywords in 'info'). By comparing the closure `from` date with the current date, the pipeline could automatically filter out and archive locations that are no longer in service.

* **Dynamic Status for Temporary Closures:** The data in this column can be used by a frontend application to provide a better user experience. The application could parse the closure details and, if the current date falls within a `from` and `to` period (e.g., for a holiday or vacation), it could display a dynamic status like "Temporarily closed for holidays" rather than simply showing the location as closed. This would accurately inform users that the location is still active but temporarily unavailable.

* **Scheduled ETL Pipeline for Regular Updates:** The entire data pipeline (Extract, Transform, Load) could be automated to run on a schedule (e.g., weekly or monthly). Since the source website is regularly updated with information on new branches, holiday schedules, and permanent closures, a scheduled script could automatically fetch the latest raw data, execute all the transformation notebooks, and update the database. This would ensure the data remains current over time, even though the exact update frequency of the source is not specified.

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

