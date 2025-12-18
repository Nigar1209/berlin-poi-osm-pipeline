# === 🏋️‍♂️ Berlin Gyms Spatial Join Workflow – DB-Ready Schema ===
# Script: Exportiert gyms_with_district_and_neighborhood.csv EXAKT passend zum DB-Schema!

import os
import glob
import pandas as pd
import numpy as np
from datetime import datetime
import geopandas as gpd
from shapely.geometry import Point

# ===========================================================
# Step 1: Load and Clean OSM Gym Data
# ===========================================================

pattern = os.path.join('gyms/sources', 'gyms_osm_berlin_*.csv')
osm_files = glob.glob(pattern)
if not osm_files:
    raise FileNotFoundError("No OSM gym export file found in /gyms/sources/")

def extract_date(fname):
    basename = os.path.basename(fname)
    date_str = basename.replace('gyms_osm_berlin_', '').replace('.csv', '')
    return datetime.strptime(date_str, "%Y-%m-%d")

osm_files_sorted = sorted(osm_files, key=extract_date)
raw_file = osm_files_sorted[-1]
print(f"Loading OSM export: {raw_file}")
df = pd.read_csv(raw_file)
print("Rows loaded:", len(df))

# --- Cleaning, Typing, Renaming for DB ---
df['name'] = df['name'].fillna('Unknown Gym')
df['street'] = df['street'].fillna('')
df['housenumber'] = df['housenumber'].fillna('')
df['address'] = (df['street'] + ' ' + df['housenumber']).str.strip()
df['postal_code'] = df['postcode'].astype(str).fillna('')
df['phone_number'] = df['phone'].fillna('').astype(str)
df['email'] = df['email'].fillna('')
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['gym_id'] = df['osm_id'].astype(str)  # gym_id = osm_id (immer String!)
df['coordinates'] = df.apply(
    lambda row: f"POINT ({row['longitude']} {row['latitude']})" if pd.notnull(row['longitude']) and pd.notnull(row['latitude']) else None,
    axis=1
)
df['district_id'] = None  # Wird nach Spatial Join gefüllt
df['district'] = None     # Wird nach Spatial Join gefüllt
df['neighborhood'] = None # Wird nach Spatial Join gefüllt

# Nur für die Felder, die du wirklich brauchst
cols = [
    'gym_id', 'district_id', 'name', 'address', 'postal_code',
    'phone_number', 'email', 'coordinates', 'latitude', 'longitude',
    'neighborhood', 'district'
]
for col in cols:
    if col not in df.columns:
        df[col] = None
df = df[cols]

# ===========================================================
# Step 2: Spatial Join zu Bezirken & Ortsteilen
# ===========================================================
districts_gdf = gpd.read_file('gyms/sources/berlin_districts.geojson')
neigh_gdf = gpd.read_file('gyms/sources/berlin_neighborhood.geojson')

gyms_gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df['longitude'], df['latitude'])],
    crs="EPSG:4326"
)

# Join zu Districts
gyms_with_district = gpd.sjoin(
    gyms_gdf, districts_gdf, how="left", predicate='within'
)
gyms_with_district['district_id'] = gyms_with_district['Schluessel_gesamt']
gyms_with_district['district'] = gyms_with_district['Gemeinde_name']

# Join zu Neighborhoods
gyms_with_neigh = gpd.sjoin(
    gyms_with_district, neigh_gdf, how="left", predicate='within',
    lsuffix='_gym', rsuffix='_neigh'
)
gyms_with_neigh['neighborhood'] = gyms_with_neigh['spatial_name']

# Finales DB-konformes DataFrame (alle Spalten als String/Nullable bis auf latitude/longitude)
final_cols = [
    'gym_id', 'district_id', 'name', 'address', 'postal_code',
    'phone_number', 'email', 'coordinates', 'latitude', 'longitude',
    'neighborhood', 'district'
]
final_df = gyms_with_neigh[final_cols].copy()

# Datentyp-Anpassung: district_id und postcode als VARCHAR, alles andere siehe SQL
final_df['district_id'] = final_df['district_id'].astype(str)
final_df['postal_code'] = final_df['postal_code'].astype(str)
final_df['gym_id'] = final_df['gym_id'].astype(str)

# Exportiere die finale Tabelle
out_csv = 'gyms/sources/gyms_with_district_and_neighborhood.csv'
final_df.to_csv(out_csv, index=False)
print(f"Exported {len(final_df)} gyms to {out_csv} (ready for DB insert!)")
