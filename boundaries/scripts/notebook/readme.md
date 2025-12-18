# 📓 Data Downloading & Transformation

This directory contains the Jupyter notebook used to download, clean, and transform the data related to **Milieuschutzgebiete (Preservation Areas)** and Berlin address points.

## 📄 Notebook

- `Downloading_and_transformatio_data.ipynb`  
  This notebook performs the following steps:
  
  1. Downloads Milieuschutzgebiete data from GDI Berlin WFS service
  2. Renames and cleans raw columns
  3. Converts geometries to WKT (Well-Known Text)
  4. Downloads address data and performs a spatial join
  5. Cleans and normalizes the joined dataset
  6. Saves transformed files to `/sources`

## 🗂 Output Files (saved to `/sources`)

- `milieuschutz_areas.geojson`
- `milieuschutz_areas_with_geom.csv`
- `cleaned_houses_in_zones.csv`
- `houses_in_milieuschutz.csv`
