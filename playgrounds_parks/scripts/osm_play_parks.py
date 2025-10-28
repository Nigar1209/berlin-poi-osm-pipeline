import os
import osmnx as ox
import geopandas as gpd
import pandas as pd

# Define the place
place = "Berlin, Germany"

# Define OSM tags for parks and playgrounds
tags = {
    "leisure": ["park", "playground", "garden", "nature_reserve"],
    "landuse": "recreation_ground",
    "boundary": "national_park"
}

print("🔄 Fetching OSM data for parks and playgrounds in Berlin...")
gdf = ox.features_from_place(place, tags)
gdf = gdf[gdf.geometry.notnull()].copy()

# Ensure required columns exist
wanted_cols = [
    "name", "operator", "brand", "accessibility", "opening_hours",
    "addr:street", "addr:housenumber", "addr:postcode", "addr:city", 
    "geometry"
]
for col in wanted_cols:
    if col not in gdf.columns:
        gdf[col] = None

# Extract lat/lon from geometry
gdf["latitude"] = gdf.geometry.centroid.y
gdf["longitude"] = gdf.geometry.centroid.x

# Select and rename columns
df = gdf[[
    "name", "operator", "brand", "accessibility", "opening_hours",
    "addr:street", "addr:housenumber", "addr:postcode", "addr:city",
    "latitude", "longitude"
]].copy()

df.rename(columns={
    "addr:street": "street",
    "addr:housenumber": "house_number",
    "addr:postcode": "postcode",
    "addr:city": "city"
}, inplace=True)

# Save output
output_path = "osm_play_parks_berlin.csv"
df.to_csv(output_path, index=False)
print(f"✅ Done! Saved {len(df)} entries to {output_path}")
>>>>>>> 4b20f66 (Add missing OSM fetch script for playgrounds/parks (#400))
