"""
OSM Fetch Script for Playgrounds (Berlin)
-----------------------------------------
This script retrieves playground locations from OpenStreetMap (OSM)
using the osmnx library and saves the results in GeoJSON format.

Author: mahdiamin1980
Date: October 2025
Task: [Data Integration] Refactoring Playgrounds and Parks Layers (#400)
"""

import os
import geopandas as gpd
import osmnx as ox

# -----------------------------------------------------------
# Configuration
# -----------------------------------------------------------
CITY_NAME = "Berlin, Germany"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "berlin_playgrounds_osm.geojson")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------------
# Fetch OSM Data
# -----------------------------------------------------------
print(f"Fetching playground data from OSM for {CITY_NAME} ...")

tags = {"leisure": "playground"}

# Fetch playground polygons and points
gdf_playgrounds = ox.geometries_from_place(CITY_NAME, tags)

# -----------------------------------------------------------
# Clean and Standardize Columns
# -----------------------------------------------------------
keep_cols = ["geometry", "name", "access", "addr:street", "operator", "opening_hours", "source"]

for col in keep_cols:
    if col not in gdf_playgrounds.columns:
        gdf_playgrounds[col] = None

gdf_playgrounds = gdf_playgrounds[keep_cols]

# Add metadata
gdf_playgrounds["source"] = "OpenStreetMap"

# -----------------------------------------------------------
# Export
# -----------------------------------------------------------
gdf_playgrounds.to_file(OUTPUT_PATH, driver="GeoJSON")
print(f"✅ Exported {len(gdf_playgrounds)} playgrounds to {OUTPUT_PATH}")
