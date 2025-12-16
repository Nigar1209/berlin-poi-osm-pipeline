import pandas as pd
import geopandas as gpd
import osmnx as ox
import hashlib
import os

# Configuration
PLACE_NAME = "Berlin, Germany"
OSM_TAGS = {"office": "employment_agency"}
# Ensure this path matches your folder structure
LOR_PATH = "lor_ortsteile.geojson" 
OUTPUT_PATH = "output/jobcenters_berlin.csv"

def generate_hashed_id(row):
    """Generates a unique 20-character ID based on location."""
    unique_str = f"{row.geometry.centroid.y}{row.geometry.centroid.x}"
    return hashlib.sha256(unique_str.encode()).hexdigest()[:20]

def run_pipeline():
    print("Fetching data from OSM...")
    # 1. Extract
    gdf_raw = ox.features_from_place(PLACE_NAME, OSM_TAGS)
    
    # 2. Transform
    gdf_raw = gdf_raw.to_crs(epsg=4326)
    gdf_raw['id'] = gdf_raw.apply(generate_hashed_id, axis=1)
    gdf_raw['latitude'] = gdf_raw.geometry.centroid.y
    gdf_raw['longitude'] = gdf_raw.geometry.centroid.x
    gdf_raw['data_source'] = 'OSM'
    
    # Keep only the columns requested by your schema
    final_cols = ['id', 'name', 'latitude', 'longitude', 'data_source']
    df_final = pd.DataFrame(gdf_raw[final_cols]).reset_index(drop=True)
    
    # 3. Load to CSV
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_final.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Success! Saved {len(df_final)} rows to {OUTPUT_PATH}")

if __name__ == "__main__":
    run_pipeline()