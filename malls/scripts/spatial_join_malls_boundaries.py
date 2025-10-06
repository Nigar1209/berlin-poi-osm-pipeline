import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path

# Paths
malls_path = Path(__file__).parent.parent / "sources" / "osm_malls_berlin_20250928.csv"
districts_path = Path(__file__).parent.parent / "sources" / "wfs_downloads" / "alkis_bezirke_bezirksgrenzen.geojson"
neighborhoods_path = Path(__file__).parent.parent / "sources" / "wfs_downloads" / "alkis_ortsteile_ortsteile.geojson"

# Output
out_path = Path(__file__).parent.parent / "sources" / "osm_malls_with_boundaries.csv"

# Load malls CSV and create geometry from lat/lon
malls_df = pd.read_csv(malls_path)
geometry = [Point(xy) for xy in zip(malls_df["lon"], malls_df["lat"])]
malls = gpd.GeoDataFrame(malls_df, geometry=geometry, crs="EPSG:4326")

# Load districts (as polygons)
districts = gpd.read_file(districts_path)
# Reproject malls to match districts CRS if needed
if malls.crs != districts.crs:
    malls = malls.to_crs(districts.crs)

# Spatial join: assign district to each mall
malls_with_district = gpd.sjoin(malls, districts, how="left", predicate="within", rsuffix="_district")

# Load neighborhoods (as polygons)
neighborhoods = gpd.read_file(neighborhoods_path)
if malls_with_district.crs != neighborhoods.crs:
    malls_with_district = malls_with_district.to_crs(neighborhoods.crs)

# Spatial join: assign neighborhood to each mall
malls_with_both = gpd.sjoin(malls_with_district, neighborhoods, how="left", predicate="within", rsuffix="_neigh")

# Save result
malls_with_both.to_csv(out_path, index=False)
print(f"Spatial join complete. Output: {out_path}")