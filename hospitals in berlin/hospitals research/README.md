# 1. Source considerations
## 1.1 Current sources should be replaced
## 1.2 OSM data should be used   
- content of old data columns should be replaced by OSM data if possible, investigations whether old columns can be reused and joined
- content should be easily retrieved
- required updates should be easily implemented in future releases
- it should be challenged whether "old" content is really required in the light of future updates and extension to other cities

# 2. OSM data
## 2.1 Available tags in OSM:
  - amenity: hospital
  - amenity: clinic
  - healthcare: hospital, clinic
### 2.1.1 amenity: hospital
- 58 entries, 89 columns
- contains not only hopsitals, but also clinics, e.g. Gemeinschaftspraxis Michael Balschin, Vadim Rubinstein, Irina Rabinovich
### 2.1.2 amenity: clinic
- 180 entries, 88 columns (no bed column)
- contains also hopsitals, e.g. Charité Comprehensive Cancer Center 
## 2.2: which data should go in this layer and who decided what is needed?

## 2.3 row deletion
- my proposal: delete Ärtze, Ärztehaus, Versorgungszentrum, etc.
  --> but for future use also in other cities this might not be a clean option
- after deletion 22 entries in clincis and 58 in hospitals
- total 80 entries

  ## 2.4 relevant columns:
"name", "geometry", "operator", "brand", "addr:city", "addr:street", "addr:housenumber", "addr:postcode", "addr:suburb", 
"phone","email", "website", "wheelchair", "toilets:wheelchair", "beds", "emergency", "healthcare:speciality","opening_hours","source"  

## 2.5 data derivation
- longitude, latitude using geometry
- district, district_id, neighborhood using reverse geolocation


## 2.6 proposed dataset: 80 columns, 24 rows
## 2.7 outstanding discussion about columns with many missings, e.g. opening_hours, source, brand
- source could be hard-coded with OSM


# 3 Old data
- 75 rows, 12 columns
- contains also information grouped as clinic data, e.g. Tagesklinik
- 3 additional columns: bed, distance (to a reference point), cases
- is there any option to get updated data if required?
- what does distance mean? to Berlin Mitte?

# 4 Join old and new data
## 4.1 joined by name: cumbersome a typos and different spelling of same hospital name
- rename of old hospital name to match OSM data
- 105 rows:
  - both    50
  - new     30
  - old     25

# Do we really want to jump through hoops to get the data, just for bed, distance and cases?
# proposal: use OSM data and don't try to add and clean data to get similar result as in old dataset
- data not static
- easy update
- extension to other cities others than Berlin

# 5 Decision
- OSM data is used without any modification/deletion of rows
- OSM data is used with tag information (amenity, healthcare, hospital or clinic)
- old data, especially beds, distance and cases will not be added to OSM dataset
- OSM dataset will be name hospital_osm

