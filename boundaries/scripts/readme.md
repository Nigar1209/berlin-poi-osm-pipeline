# 🛠 Step 2: Data Transformation – Milieuschutzgebiete

This step processes the raw preservation zones data (`Milieuschutzgebiete`) and associated address-level matches into a cleaned, structured format for database ingestion.

---

## 🎯 Objective

- Clean and normalize the raw spatial data
- Convert data types and column names to match the final schema
- Join address points to preservation zones spatially (`ST_Intersects`)
- Export clean data for DB insertion (Step 3)
- **No data is inserted into the DB yet**

---

## 🧾 Input Files

Located in `/sources` folder:

| File Name                    | Description                                          |
|-----------------------------|------------------------------------------------------|
| `milieuschutz_areas.geojson`         | Raw preservation zones (GeoJSON, EPSG:25833)       |
| `houses_in_milieuschutz.csv`         | Output from spatial join between houses and zones  |

---

## 🔄 Transformation Steps

1. **Rename columns** from German to English for consistency  
2. **Parse date fields**: convert to ISO format `YYYY-MM-DD`  
3. **Normalize data types** (e.g. house numbers as string, date columns as datetime)  
4. **Remove unnecessary columns** (e.g. `residential_units`, `non_residential_units`, `notes`, etc.)  
5. **Clean missing values**  
6. **Export** final cleaned dataset as `cleaned_houses_in_zones.csv`

---

## 🧱 Output Schema

| Column               | Type     | Description                                        |
|----------------------|----------|----------------------------------------------------|
| `address_id`         | TEXT     | Unique address identifier                          |
| `house_number`       | TEXT     | House number                                       |
| `house_number_extra` | TEXT     | Additional house number info (if available)        |
| `street_name`        | TEXT     | Name of the street                                 |
| `postal_code`        | INT      | Postal code                                        |
| `zone_code`          | TEXT     | Preservation zone code                             |
| `neighborhood`       | TEXT     | Berlin district name                               |
| `zone_name`          | TEXT     | Name of the preservation zone                      |
| `publication_date`   | DATE     | Regulation publication date                        |
| `effective_date`     | DATE     | Regulation effective date                          |
| `area_ha`            | FLOAT    | Area of the preservation zone in hectares          |

---

## 📁 Output File

- `cleaned_houses_in_zones.csv` — ready for database insertion in Step 3

---

## ✅ Status

- ✅ Data downloaded and spatially joined  
- ✅ Columns renamed and cleaned  
- ✅ Types converted and validated  
- ✅ Output exported to CSV  
- 🟢 Ready for **Step 3: Populate Database**
