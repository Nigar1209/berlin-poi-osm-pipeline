# Berlin Bus and Tram stops Data Integration

## Sources

The main source of this data is a public API of the BVG, which is the operator of busses and trams in Berlin.
For Reverse Geocoding a google maps API has been used.

## Tranformation & Cleaning

Initial filtering of the API retrieval results included:
* filtering for only bus and tram stops
* filtering for only stop_name, id, bus and tram boolean columns and coordinates (API result contained more info)

Cleaning included
* Checking for missing values
* Removing duplicates

## Reverse Geocoding

To gain the important district and neighborhood columns, reverse geocoding was used to get locational data from the latitude and longitude columns.
* Used coordinates to get exact address for each stop
* extracted zip code form address column
* used zip code to fill district and neighborhood
* used district name to create district id column

## Finalization

* Renamed a few columns to fit required schema
* Reordered columns to fit required schema
* removed a few stops from dataset that couldn't be matched to one of the 12 districts
