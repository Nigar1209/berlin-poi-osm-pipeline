# 🏛️ Museums & Galleries in Berlin  
## 📌 Step 1: Research & Data Modelling

---

## 🔍 Data Source Discovery

- **Primary Source:** [OpenStreetMap (OSM)](https://www.openstreetmap.org) via the `osmnx` Python library  
  - **Why OSM?** Open, free, and continuously updated. Includes location, address, and metadata for museums, galleries, public artworks, and exhibition centers in Berlin.  
  - **Query Filters Used:**  
    - `tourism`: `["museum", "gallery", "artwork"]`  
    - `amenity`: `"exhibition_center"`  
  - **Data Type:** Dynamic (queried via API)  
  - **Update Frequency:** Continuous  

- **Additional Sources (not yet integrated):**  
  - [Berlin Open Data Portal](https://daten.berlin.de) – for optional enrichment  
  - [Deutsche Digitale Bibliothek REST API](https://www.deutsche-digitale-bibliothek.de/content/api) – requires API key  
  - [Kulturgutdigital – Berliner OpenGLAM-Daten](https://openglam.berlin.de) – cultural metadata

---

## 🗂️ Raw File Creation

- Generated separate raw files for each of the four tags (`museum`, `gallery`, `artwork`, `exhibition_center`)  
- Currently evaluating whether to merge into a single table or maintain separate datasets for artworks and exhibition centers  
- Identifying common columns for potential joins

---

## ✅ To Do

### 🔧 Column Selection
- Plan to remove columns with **≥ 75% missing data**

### 🧭 Schema Planning
- Add `latitude` and `longitude` to the cleaned dataset

### 🔄 Transformation Strategy
- Rename columns for consistency across layers  
- Align naming conventions with the ERD (Entity Relationship Diagram)

---

## 🛠️ Tools & Technologies

- **Languages & Libraries:**  
  - Python  
  - `osmnx`, `geopandas`, `pandas`  
- **Environment:**  
  - Jupyter Notebook (for analysis and exploration)

---

## 📌 Step 2: Data Transformation & Preprocessing

After a thorough examination of the raw data, I decided to maintain four distinct tables — one for each cultural layer — to preserve schema clarity and support tailored enrichment workflows. This modular approach allows for future merging if needed, while respecting the unique tagging schemes of each category.

The following layers are processed independently:

- 🖼️ **Galleries**
- 🏛️ **Museums**
- 🎨 **Public Artworks**
- 🏢 **Exhibition Centers**

Each layer will be transformed in its own notebook and pushed to the database as a separate table.

---

## 🖼️ Galleries — Data Transformation & Preprocessing

📓 Notebook: `galleries_data_transformation.ipynb`

### ✅ Initial Setup
- Imported all required libraries
- Loaded raw gallery data

### 🧹 Column Cleanup
- Dropped unnecessary columns:
  - `Berlin` and `DE` — redundant since the dataset is Berlin-specific
  - `tourism` — all entries are galleries
  - `suburb` — duplicate of `neighbourhood`, which is enriched later
- Standardized column names:
  - Removed whitespace and special characters
  - Replaced spaces with underscores
  - Converted all names to lowercase
  - Removed `addr:` prefixes

### 🔍 Data Enrichment
- Fetched `district_name` and `neighbourhood_id` from `or_ortsteile.geojson`
- Added `district_id` for foreign key reference
- Used reverse geocoding to retrieve:
  - `street` and `postal_code`
  - Filled missing values in original columns where applicable

### 🧼 Data Cleaning
- Replaced all missing values with `NaN`
- Dropped rows missing both `gallery_name` and `street`
- Replaced missing `gallery_name` with `"Unknown Gallery Name"`
- Filled missing values in `wheelchair`, `website`, and `opening_hours` with `"unknown"`
- Converted all text fields to lowercase to prevent duplication due to case differences
- Dropped temporary columns: `geometry`, `districts`, `postal_code_from_geo`, `street_from_geo`
- Verified and corrected data types
- Removed duplicate rows
- Reordered columns to match the ERD schema

---

### 🧾 Planned Schema: `gallery_listings`

| Column Name        | Data Type | Description             | Example             |
|--------------------|-----------|-------------------------|---------------------|
| gallery_id         | int       | Unique gallery ID       | 301107444           |
| gallery_name       | text      | Name of the gallery     | atelier achim kühn  |
| house_number       | text      | House number            | 12A                 |
| street             | text      | Street name             | invalidenstraße     |
| neighbourhood_id   | int       | FK to neighbourhood     | 0908                |
| district_id        | int       | FK to district          | 11009009            |
| postal_code        | text      | Postal code             | 10115               |
| website            | text      | Gallery website         | www.example.com     |
| opening_hours      | text      | Opening times           | Mo-Su 10:00-18:00   |
| fee                | text      | Entry fee info          | True/False          |
| latitude           | float     | Latitude coordinate     | 52.5200             |
| longitude          | float     | Longitude coordinate    | 13.4050             |
