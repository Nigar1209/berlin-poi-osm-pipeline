# Sources for Bike Lanes Data Modelling

This document lists potential data sources for the bike lanes in Berline, as well as the initial steps for extracting and transforming the data. 

## 1.1 Data Source Discovery 
### Main Source - OpenStreetMap (OSM)

- **Origin**: OSM - Overpass Turbo (https://overpass-turbo.eu/)
- **Update Frequency**: Continuous/Dynamic based on community updates.
- **Data Type**:
   - Dynamic data types through API queries (ie. `cycleway=*`, `highway=cycleway`, `highway=path + bicycle=designated`, etc.).
- **Reason for Selection**:
  - The data is dynamic and continuously maintained by a vast community which helps to ensure the near real-time information on the cycling infrastructure of Berlin.
  - Using the API system allows for more flexible filtering of the data by attributes and locations which makes it easier to tailor the data extraction process for the Berlin dataset.
  - **File location**: In the sources folder of this repository under the name "`osm_bikelanes_raw.geojson`"

### Optional Additional sources from Geoportal Berlin
#### 1. Radverkehrsanlagen (Official Berlin Bike Infrastructure)

- **Origin**: Geoportal Berlin - Radverkehrsanlagen WFS (https://gdi.berlin.de/services/wfs/radverkehrsanlagen) 
- **Update Frequency**: Not planned (static dataset)
- **Data Type**: Static dataset that is downloadable in formats like GeoJSON, CSV and Shapefile.
- **Reason for possible usage**:
     - As this is an official/authoritative dataset collected and compiled by the city, it will help with ensuring the accuracy and alignment with the Berlin transport authorities (ie. Radverkehrsnetz).
     - This data is available in GIS-friendly formats (ie. GeoJSON, WFS, etc.) making it a more reliable source for spatial analysis and integration into the data pipeline.
- **Download URL**: https://gdi.berlin.de/services/wfs/radverkehrsanlagen?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=radverkehrsanlagen:radverkehrsanlagen&OUTPUTFORMAT=shape-zip
  
  *(note: I will use Python to transfor this file into a GeoJSON file)*

#### 2. Fahrradstraßen (Designated Bike Streets)
- **Origin**: Fahrradstraßen WFS (https://gdi.berlin.de/services/wfs/fahrradstrassen)
- **Update Frequency**: Not planned (static dataset)
- **Data Type**: Vector dataset that is downloadable in multiple file formats, representing how streets have been officially designated as bike-priority lanes.
- **Reason for Selection**:
- Adds legal designation information that may not be fully captured in OSM.
- Helps to ensure that specific bike-priority streets are correctly classified in the dataset.
- **Download URL (GeoJSON)**: https://gdi.berlin.de/services/wfs/fahrradstrassen?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=fahrradstrassen:fahrradstrassen&OUTPUTFORMAT=application/json

  *(note: this dataset has already been uploaded as a GeoJSON file in the sources of this repositoryunder the name "`fahrradstrassen.geojson`")*

## 1.2 Initial Steps for Transformation
### 1. Raw Data Collection from Overpass API & Geoportal Berlin
- Export the raw data from Overpass Turbo as a GeoJSON file with the name "`osm_bikelanes_raw.geojson`"
- Download `radverkehrsanlagen.geojson` and `fahrradstrassen.geojson` from the WFS URLs above.
- Place all files in the `/bikelanes/sources/` directory in the repository.

### 2. Data Cleaning and Standardisation using Python
- Load raw files into Jupyter notebook
- Standardise the column names (ie. OSM's `name` → `street_name`, `cycleway` → `lane_type`, etc.)
- Create calculated columns like `length`
- Standardise data types (geometry as LineString, length as float, lane_type and condition as string)

### 4. Spatial Integration
- Connect to the `districts` table via spatial join to assign `district_id` for each bike lane

### 5. Export
- Save cleaned and integrated dataset as `berlin_bikelanes.csv` for database import
