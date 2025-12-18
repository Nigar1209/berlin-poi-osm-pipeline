# Milieuschutzgebiete (Preservation Areas) – Berlin

## 🗂 Source Overview

- **Provider:** GDI Berlin (Geospatial Data Infrastructure)
- **Service Type:** WFS (Web Feature Service)
- **Layer Name:** `erhaltungsverordnungsgebiete:erhaltgeb_es`
- **URL:**  
  - WFS Base: https://gdi.berlin.de/services/wfs/erhaltungsverordnungsgebiete  
  - GetCapabilities: https://gdi.berlin.de/services/wfs/erhaltungsverordnungsgebiete?REQUEST=GetCapabilities&SERVICE=wfs
- **License:** [dl-zero-de/2.0](https://www.govdata.de/dl-de/zero-2-0)
- **Published:** 17.06.2024
- **Update Frequency:** Unknown (assumed to be static — one-time import recommended)
- **Data Type:** Static

---

## 🧱 Data Schema

### Selected Fields

| Column                 | Type      | Description                                         |
|------------------------|-----------|-----------------------------------------------------|
| `id`                   | TEXT      | Unique identifier of the preservation zone         |
| `code`                 | TEXT      | Administrative code                                |
| `district`             | TEXT      | Berlin district name                               |
| `zone_name`            | TEXT      | Name of the preservation zone                      |
| `publication_date`     | DATE      | Date published in official gazette (f_gybl_dat)    |
| `effective_date`       | DATE      | Date regulation took effect (f_in_kraft)           |
| `alt_publication_date` | DATE      | Optional alternative publication date (nullable)   |
| `alt_effective_date`   | DATE      | Optional alternative effective date (nullable)     |
| `area_ha`              | NUMERIC   | Area in hectares                                   |
| `geometry`             | GEOMETRY  | Multipolygon geometry in EPSG:25833 (meters)       |

---

## 🌐 Coordinate Reference System (CRS)

- **Current CRS:** `EPSG:25833` — UTM Zone 33N (used in Germany)
- **Note:** This is a projected coordinate system in meters.  
  It differs from the global latitude/longitude standard `EPSG:4326`,  
  so reprojecting may be needed for web maps and PostGIS compatibility.

---

## 🔗 Relationships & Integration

- Will be joined with the `neighborhoods` table using **spatial join** (`ST_Intersects`) based on geometry.
- No explicit foreign keys. Spatial overlap will determine the relationship between preservation zones and neighborhoods.

---

## ⚠️ Known Data Issues

- `alt_publication_date` and `alt_effective_date` are often `null`.
- Some `zone_name` values include line breaks or inconsistent casing.
- Geometry is valid but in a projected CRS (EPSG:25833) and must be handled accordingly.

---

## 🔄 Transformation Plan

1. Rename German columns to English equivalents
2. Parse `*_date` fields into ISO `YYYY-MM-DD` format
3. Clean `zone_name` for whitespace and formatting
4. Validate geometry (repair invalid shapes if needed)
5. Reproject geometries from `EPSG:25833` → `EPSG:4326` for compatibility
6. Export results to:
   - `GeoJSON`: `milieuschutz_areas.geojson`
   - `CSV with WKT geometry`: `milieuschutz_areas_with_geom.csv`
   - (Optional) Excel backup: `milieuschutz_areas.xlsx`

---

## 📁 Files in `/sources`

- `milieuschutz_areas.geojson` – clean GeoJSON with original EPSG:25833
- `milieuschutz_areas_with_geom.csv` – tabular version with WKT geometry
- `milieuschutz_areas.xlsx` – Excel version with same structure
- `README.md` – this file

---

## ✅ Status

- ✅ Step 1.1: Source fully documented  
- ✅ Step 1.2: Schema, relations, and transformation plan defined  
- ✅ Step 1.3: Sources prepared  
- 🟢 Ready to proceed with Step 2: Data Transformation
