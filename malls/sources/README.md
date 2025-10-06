
# Malls – Data Sources & Workflow

## 1. OpenStreetMap (Overpass API)
- **Source and origin:** [Overpass API](https://overpass-api.de/api/interpreter) (OpenStreetMap public API)
- **Update frequency:** Near real-time (data is updated by the OSM community continuously; API responses reflect the latest state)
- **Data type:** Dynamic (API, can be queried as often as needed)
- **Relevant data fields:**
	- `name` (mall name)
	- `shop=mall` (tag indicating a mall)
	- `opening_hours`
	- `website`
	- `addr:*` (address fields: street, housenumber, postcode, city)
	- `lat`, `lon` (coordinates)
	- `wheelchair`
	- `operator`, `brand`, `start_date`, `level`
	- Geometry (point or polygon)
	- **Script:** `../scripts/fetch_malls_osm.py`


## 2. Berlin Administrative Boundaries (FIS-Broker WFS)
- **Source and origin:** [Berlin Open Data / FIS-Broker WFS](https://www.fis-broker.de/)  
	Downloaded via WFS endpoints (see scripts)
- **Update frequency:** Occasional (updated by Berlin authorities; check “Stand”/date on the portal for latest version)
- **Data type:** Static (downloaded as files, update manually as needed)
- **Relevant data fields:**
	- `name` (district or neighborhood name)
	- `gem`, `namgem`, `namlan`, `lan` (various administrative codes/names)
	- Geometry (polygon boundaries)
	- **Files:**
		- `wfs_downloads/alkis_bezirke_bezirksgrenzen.geojson` (districts)
		- `wfs_downloads/alkis_ortsteile_ortsteile.geojson` (neighborhoods)
	- **Scripts:** `../scripts/download_wfs_layers.py`, `../scripts/gml_to_geojson_bezirke.py`, `../scripts/gml_to_geojson_ortsteile.py`
	- **Usage:** These GeoJSONs can be loaded directly as map layers in web/mobile apps or used for spatial joins.


## Scripts & Automation
- `../scripts/download_wfs_layers.py`: Download latest Berlin boundaries from WFS endpoints
- `../scripts/gml_to_geojson_bezirke.py` and `../scripts/gml_to_geojson_ortsteile.py`: Convert GML to GeoJSON
- `../scripts/fetch_malls_osm.py`: Download malls POIs from OSM
- `../scripts/spatial_join_malls_boundaries.py`: Spatially join OSM malls with district and neighborhood boundaries, outputting `osm_malls_with_boundaries.csv`


## How to Combine & Enrich Sources
- Load both GeoJSONs as separate layers in your app for districts and neighborhoods.
- To spatially join OSM malls with boundaries, use the script above. The output CSV will contain each mall with its district and neighborhood attributes.
- To merge boundaries into one file for visualization, see the example Python snippet below:

```python
import json
bezirke = json.load(open("wfs_downloads/alkis_bezirke_bezirksgrenzen.geojson"))
ortsteile = json.load(open("wfs_downloads/alkis_ortsteile_ortsteile.geojson"))
combined = {"type": "FeatureCollection", "features": bezirke["features"] + ortsteile["features"]}
json.dump(combined, open("wfs_downloads/berlin_boundaries_combined.geojson", "w"), ensure_ascii=False, indent=2)
```

## Planned Transformations
- Deduplicate by geometry/name (Jaro-Winkler on names within 150m)
- Normalize addresses
- Enrich with district/Ortsteil via spatial join
- Standardize `opening_hours`
- Output tidy CSV/GeoJSON for downstream use
