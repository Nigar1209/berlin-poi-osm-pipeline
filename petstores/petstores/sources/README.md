Pet Stores Data Sources
==
This layer will use data sourced primarily from OpenStreetMap (OSM).

- Source: https://wiki.openstreetmap.org/wiki/OpenStreetMap_API
- Data type: Dynamic (available via API requests)
- Update frequency: Unknown (for now use "unknown")
- Relevant OSM Tag: `shop=pet`

At this stage, only the data source has been identified.
No data has been downloaded or transformed yet.

### Raw Data Source Links

- **OpenStreetMap Overpass API Query Tool:**  
  https://overpass-turbo.eu/

- **OSM Feature Tag Used:**  
  `shop=pet`

### Initial Data Extraction Status

Data was pulled using Python OSMnx library:

```python
import osmnx as ox
tags = {"shop": "pet"}
petstores_gdf = ox.features_from_place("Berlin, Germany", tags)

