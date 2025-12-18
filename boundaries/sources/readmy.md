# 🛡️ Milieuschutzgebiete (Preservation Areas) – Berlin

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
- **Data Type:** Static (not dynamically updated via API)

---

## 🧱 Data Schema (Joined with Adressen Berlin)

### Selected Fields

| Column                 | Type     | Description                                             |
|------------------------|----------|---------------------------------------------------------|
| `address_id`           | TEXT     | Unique address identifier                               |
| `house_number`         | TEXT     | House number                                            |
| `house_number_extra`   | TEXT     | Additional house number info (e.g. A, B) (nullable)     |
| `street_name`          | TEXT     | Street name                                             |
| `postal_code`          | INTEGER  | Postal code                                             |
| `zone_code`            | TEXT     | Code of the preservation zone                           |
| `neighborhood`         | TEXT     | Berlin district name                                    |
| `zone_name`            | TEXT     | Name of the preservation zone                           |
| `publication_date`     | DATE     | Official gazette publication date                       |
| `effective_date`       | DATE     | Date the regulation came into force                     |
| `area_ha`              | FLOAT    | Area size in hectares                                   |

---

## 🌐 Coordinate Reference System (CRS)

- **Original CRS:** `EPSG:25833` – UTM Zone 33N (meters, projected)
- **Target CRS (optional):** `EPSG:4326` – WGS84 (lat/lon in degrees)
- ⚠️ CRS must be declared when importing into PostGIS or transformed for web mapping.

---

## 🔗 Relationships & Integration

- Will be joined with `neighborhoods` using **spatial join** via `ST_Intersects`.
- This allows analysis of which buildings fall within which preservation areas.
- No foreign key – geometry-based relationships only.

---

## ⚠️ Known Data Issues

- `house_number_extra` is often `null`
- Geometry not stored in final CSV export – used only during spatial join
- Data assumed to be static; no dynamic updates planned
- Geometry uses projected CRS (EPSG:25833), not compatible with web maps unless reprojected

---

## 🔄 Transformation Plan

1. Download preservation zones from WFS as GeoJSON
2. Download address dataset (`adressen_berlin`) from WFS
3. Reproject geometries to match (EPSG:25833)
4. Spatial join: match addresses to preservation zones via `intersects`
5. Rename German column names to English
6. Normalize data types (dates, IDs, etc.)
7. Export cleaned results to:
   - `cleaned_houses_in_zones.csv`

---
  
## 📁 Files in `/sources`

- `milieuschutzgebiete.geojson` – raw GeoJSON with original geometry
- `milieuschutz_areas_with_geom.csv` – CSV version including WKT geometry
- `cleaned_houses_in_zones.csv` – final cleaned CSV (without geometry)
- houses_in_milieuschutz.csv - Raw result of spatial join: addresses matched to preservation zones
- `README.md` – this file

---
---

## ✅ Status

- ✅ Step 1.1: Data source identified and documented
- ✅ Step 1.2: Schema, structure, and transformation plan defined
- ✅ Step 1.3: Raw and cleaned data saved to `/sources`
- ✅ Step 1.4: Ready for Step 2 (Data Transformation)
