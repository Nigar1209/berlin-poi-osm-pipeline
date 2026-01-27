# 📂 Data Sources for Bouldering Spots

## OpenStreetMap (OSM)

* Source: https://wiki.openstreetmap.org/wiki/OpenStreetMap_API
* Update frequency: Unknown
* Data type: Dynamic (API)
* Relevant OSM Tag: `climbing:boulder=yes`

### Raw Data Sources

#### 📄 `bouldering_spots.geojson`

* Source: https://overpass-turbo.eu/
* Format: GeoJSON
* Description: Raw bouldering spot data extracted from OpenStreetMap using Overpass API.

#### 📄 `bouldering_spots.json`

* Source: https://overpass-turbo.eu/
* Format: JSON
* Description: Raw bouldering spot data extracted from OpenStreetMap using Overpass API, converted to JSON format.

#### 🔗 Overpass API Query

```
[out:json][timeout:25];
// manually define the area by name and admin level (Berlin is level 4)
area["name"="Berlin"]["admin_level"="4"]->.searchArea;

nwr["climbing:boulder"="yes"](area.searchArea);

out geom;
```

#### 🔗 OSM API Query using OSMnx Library

```python
import osmnx as ox

tags = {"climbing:boulder": "yes"}

bouldering_spots_df = ox.features_from_place("Berlin, Germany", tags=tags)
```

## Planned Transformation

1. **Raw Data Extraction**: Fetch raw bouldering spot data from OpenStreetMap using OSMnx.
2. **Data Cleaning**: Remove duplicates, and filter out irrelevant data.
4. **Geocoding**: Convert addresses to latitude and longitude coordinates.
5. **Gemoetry Conversion**: Convert `POLYGON()` geometries to `POINT()` format by using their centroid.
6. **Reverse Geolocation**: Get full address from coordinates.
7. **Convert and Validate Data Types**: Convert data types to ensure consistency and accuracy matching the final schema.
8. **Spatial Join**: Assign district and neighborhood.
9. **Finalize Columns**: Define final columns and their data types.
10. **Quality Checks**: Perform data quality checks to ensure data integrity and consistency.
11. **Export**: Export transformed data into a CSV file.
12. **Upload**: Upload final dataset to a new database table.
