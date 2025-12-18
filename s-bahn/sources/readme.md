S-Bahn Berlin — Sources

Data Source

* I used the GTFS dataset from the Verkehrsverbund Berlin-Brandenburg (VBB), available via the [Berlin Open Data Portal](https://daten.berlin.de/datensaetze/vbb-fahrplandaten-via-gtfs).  
* It is updated twice per week (Wednesday, Friday), licensed under CC-BY, and contains public transport stops, routes, timetables, shapes, and transfers.  

Planned Transformation Steps
* Extract only S-Bahn stops from the GTFS dataset.  
* Join with routes and trips to identify served S-Bahn lines.  
* Remove duplicates and standardise station names.  
* Add placeholders for enrichment (postcode, neighbourhood, district).  
* Save cleaned results to `/sources/sbahn_stations_clean.csv`.  

1.3 Sources Directory

Files in `/sources`:
- `sbahn_stations.csv` → raw extracted S-Bahn stations
- `sbahn_stations_clean.csv` → cleaned and enriched dataset
