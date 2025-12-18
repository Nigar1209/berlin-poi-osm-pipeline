# 0 General OSM
🌍 OpenStreetMap (OSM) is a free, collaborative map of the world that anyone can edit.
- It contains geospatial data: roads, railways, buildings, parks, rivers, amenities (cafés, hospitals, schools, etc.).
- Data is stored as:
  - Nodes (points, e.g. bus stops, cafés).
  - Ways (lines/polygons, e.g. roads, parks, building outlines).
  - Relations (groupings, e.g. bus routes, administrative boundaries).
- Everything is tagged with simple key=value pairs (e.g. amenity=cafe, highway=residential).

Most OSM objects will at least have:
- Identity (name, operator, brand)
- Location (addr:*)
- Availability (opening_hours, access)
- Contact (phone, website)
- Accessibility (wheelchair)

Data can be retrieved by using the following Python code:
```
import osmnx as ox
import geopandas as gpd
import pandas as pd

# populating a dataframe
tags = {"amenity": "university"}
university_gdf = ox.features_from_place("Berlin, Germany", tags)
university_gdf.info()
```
Example output:
```
<class 'geopandas.geodataframe.GeoDataFrame'>
MultiIndex: 117 entries, ('node', np.int64(278540049)) to ('way', np.int64(1211946568))
Data columns (total 87 columns):
 #   Column                     Non-Null Count  Dtype   
---  ------                     --------------  -----   
 0   geometry                   117 non-null    geometry
 1   addr:city                  62 non-null     object  
 2   addr:country               42 non-null     object  
 3   addr:housenumber           61 non-null     object  
 4   addr:postcode              61 non-null     object  
 5   addr:street                62 non-null     object  
 6   addr:suburb                44 non-null     object  
 7   amenity                    117 non-null    object  
 8   contact:phone              8 non-null      object  
 9   name                       109 non-null    object  
 10  operator                   59 non-null     object  
 ...
```
geometry contains information about longitude and latitude of an object and is provided in the format: POINT (13.35074 52.42464)

# 1 Columns of OSM to be used in all layers

| Columns name | Description | OSM object name |  mapping instruction | example |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| name | stores the primary, commonly used name of an object | name | 1:1 | Volkspark Friedrichshain, Café Einstein | 
| operator | organization that runs it | operator | 1:1 | S-Bahn Berlin GmbH | 
| brand | chain brand | brand | 1:1 | Starbucks | 
| longitude | east–west position on Earth | geometry | retrieve from first number in brackets | 13.34455 | 
| latitude | specifies how far north or south a point is from the Equator (0°) | geometry | retrieve from second number in brackets | 52.4988 | 
| country | country where object is located | addr:country | rename | DE | 
| city | city where object is located | addr:city | rename | Berlin | 
| street | street where object is located | addr:street | rename | Friedrichstraße | 
| housenumber | housenumber of street where object is located | addr:housenumber | rename | 180 | 
| postcode | postcode of city and street where object is located | addr:postcode | rename | 10117 | 
| neighborhood | neighborhood of object | addr:suburb | rename | Mitte | 
| phone | contact: phone number | contact:phone or phone | rename or 1:1 | +493045040 | 
| email | contact: email | contact:email or email | rename or 1:1 | |
| website | contact: website | contact:website or website| rename or 1:1 | | 
| wheelchair |accessibility for wheelchair | wheelchair | 1:1 | yes/no/limited |
| wheelchair_toilets |toilets accessible for wheelchairs | toilets:wheelchair | 1:1 | yes/no |
| opening_hours |opening hours of object in a standard machine-readable syntax| opening_hours | 1:1 | Mo-Su 08:00-20:00 |

## 1.1: in addition **district and district_id** shouild be added to all layers

# 2 Layer-by-Layer Review of Existing Data Sources
All columns shown in the table above should be added to all layers, independently if they are available in the legacy database or not.
In addition to these OSM or non-OSM columns have to be added according to legacy database.

| Layer Name  | Current Data Source | Can OSM Replace? | Tag in OSM  | Replacement Scope (Full/Partial) | Columns in OSM in addition to those under 1 | proposed additional Columns in OSM | Columns Missing from OSM | Notes/Matching Stragegy |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |  ----------- |  ----------- |  ----------- |
| banks | OSM  |  |  |   |  |   |  |
| boundary / mileuschutz | gdi.berlin.de/ ../erhaltungs verordnungsgebiete | no well-established OSM tag/schema |  |  |  | |   |  |
| colleges | edurank.org | yes | amenity, university | partial |  | | university_id |  |
| | | | | |  | | rank_in_berlin_brandenburg |  |
| | | | | |  | | rank_in_germany |  |
| | | | | |  | | enrollment |  |
| | | | | |  | | founded |  |
| crime_statistics | Publisher: Berlin Police Department | no |  |   |   |  |  |
| dental_offices | OSM |  |  |   |   |  |  |
|  | Berlin Open Data Portal |  |  |   |   |  |  |
| gym | OSM |  |  |   |   |  |  |  |
| hospitals | deutsches-krankenhaus-verzeichnis.de | yes | amenity, hospital | partial | beds (many missings in OSM) | emergency (whether emergeny care is available): yes, no, designated | cases |it may be possible to add parking information from amenity=parking |
|  |  |  |  |   |  |  healthcare:speciality: e.g. cardiolog, oncolog, psychiatry |  | amubulance information from emergency=ambulance_station or emergeny=access_point |
|  |  |  |  |   |  |  health_specialty:ophthalmology |  |  |
|  |  |  |  |   |  |  health_specialty:optometry  |  |  |
|  |  |  |  |   |  |  health_specialty:geriatrics |  |  |
|  |  |  |  |   |  |  health_specialty:occupational_therapy |  |  |
|  |  |  |  |   |  |  health_specialty:phoniatrics |  |  |
|  |  |  |  |   |  |  health_specialty:physiotherapy |  |  |
| pools | baederleben.de | yes | leisure, swimming_pool | full | pool_type (e.g.indoor, outdoor)  | access (public, private, members) | pool_id |  | 
|  |  |  | leisure, bathing_place (n=1) |   |   | depth | open_all_year |  |
|  |  |  | leisure, swimming_area |   |   | length |  |  |
|  |  |  | sport, swimming |   |   | heated |  |  |
|  |  |  | |   |   | fee |  |  |
| population_statistics | statistik-berlin-brandenburg.de | no | |   |   | |  |  |
| post_offices | Deutsche Post | yes | amenity, post_office | partial |   | | additionalInfo | consider to use operating_hours instead Monday, Tuesday, ... Sunday |
| | | | |  |   | | format1 | consider to map pfServicetype from map from service:copy, service: print,  post_office:letter_from, post_office:parcel_from, post_office:parcel_pickup |
| | | | |  |   | | format2 | |
| | | | |  |   | | keyWord | |
| | | | |  |   | | locationTyp | |
| | | | |  |   | | locationName | |
| | | | |  |   | | primaryKeyDeliverySystem| |
| | | | |  |   | | primaryKeyZipRegion | |
| | | | |  |   | | systemID | |
| | | | |  |   | | primaryKeyPF | |
| | | | |  |   | | pfAccessibilitytypes | |
| | | | |  |   | | pfClosureperiods | |
| public_transport | vbb.de, gtfs.de, bvg.de, openstreetmap.org, daten.berlin.de| | |  |   | | | seems, that OSM is used already|
| real_estate_statistics | IBB Wohnungsmarktbericht 2024, FIS-Broker Berlin, Immobilienmarktberichte - berlin.de| no | |  |   | | ID| check, if locality = neighborhood|
| recreational_zone | Berlin Open Data - Parks Layer (?) | yes | parks:| full | green_area_type --> surface=* and grass=* | access (public, private, etc.) | area_sqm | |
| | Berlin Open Data - Playgrounds Layer (?) | | leisure=park → general green/park areas |  |   | playground = climbingframe| planning_area_name | |
| | | | leisure=garden → smaller gardens or landscaped areas |  |   | age (recommended age) | source | |
| | | | landuse=recreation_ground → larger recreation areas |  |   | playground = swing | created_at | |
| | | | leisure=nature_reserve → protected natural areas |  |   | playground = slide | updated_at | |
| | | | boundary=national_park (not common inside Berlin) |  |   | surface=* → ground type (sand, rubber, grass) | | |
| | | | Playgrounds: |  |   |access=* → public vs private (e.g. playgrounds in housing complexes) | | |
| | | | leisure=playground → main tag for children’s play areas) |  |   | | | |
| | | | boundary=national_park (not common inside Berlin) |  |   | | | |
| s-bahn | berlin open data portal | |  |  |   | | | I think e.g. railway stations,stops,etc. can be mapped from OSM --> further investigation required to find out how|
| schools| ? | yes | amenity=school | part |   | isced:level=* → education level (1=primary, 2=lower secondary, 3=upper secondary, etc.) | school_type_de | quarter is neighborhood in OSM |
| | | | amenity=college |  |   | school:gender=* → male, female, or mixed | ownership_en | |
| | | | |  |   | | school_category_de | |
| | | | |  |   | | school_category_en | |
| | | | |  |   | | school_year | |
| | | | |  |   | | students_total | |
| | | | |  |   | | students_f | |
| | | | |  |   | | students_m | |
| | | | |  |   | | teachers_total | |
| | | | |  |   | | teachers_f | |
| | | | |  |   | | teachers_m | |
| | | | |  |   | | startchancen_flag | |
| tram_bus | public API of the BVG | yes | railway=tram_stop | full |   |   | stop_id |   |
| | |  | highway=bus_stop |  |   |   |   |   |
| venues | Overpass API | yes | amenity=cafe |  |   | cuisine=* (e.g. cuisine=coffee_shop, cuisine=italian) |   | |
| | | | amenity=restaurant |  |   | outdoor_seating=yes/no |   | |
| | | | amenity=bar |  |   | smoking=yes/no/separated |   | |
| | | | amenity=pub |  |   | wifi=yes/no/free |   | |
| | | | amenity=beer_garden |  |   | diet:vegetarian=yes |   | |
| | | |   |  |   | diet:vegan=yes |   | |
| | | |  |  |   | diet:halal=yes |   | |
| | | |  |  |   | diet:gluten_free=yes |   | |
| | | |   |  |   | delivery=yes/no (sometimes included) |   | |
| | | |   |  |   | drink:cocktail=yes |   | |
| | | |   |  |   | drink:beer=yes |   | |
| | | |   |  |   | drink:wine=yes |   | |
| vet_clinics | OSM | |   |  |   |   |   | |
| short_term_listing | inside Airbnb | yes | tourism=apartment | partial | beds=* → number of beds |  | ID | not sure if it makes sense to switch to OSM |
| | | | tourism=guest_house |  |    |  | host_ID | |
| | | | tourism=hotel |  |   |  | property_type | |
| | | | tourism=hostel |  |   |  | room_type | |
| | | | tourism=chalet |  |   |  | accomodates | |
| | | | tourism=camp_site |  |   |  | bedrooms | |
| | | | caravan_site |  |   |  | is_shared | |
| | | | tourism=motel |  |   |  | amenities  | |
| | | |   |  |   |  | price | |
| | | |  |  |   |  | minimum_nights | |
| | | |  |  |   |  | maximimum_nights | |
| | | |  |  |   |  | number_of_reviews | |
| | | |  |  |   |  | review_scores_rating | |
| | | |  |  |   |  | review_scores_accuracy | |
| | | |  |  |   |  | review_scores_cleanliness | |
| | | |  |  |   |  | review_scores_checkin | |
| | | |  |  |   |  | review_scores_communication | |
| | | |  |  |   |  | review_scores_location | |
| | | |  |  |   |  | review_scores_value | |
| | | |  |  |   |  | review_scores_communication | |
| | | |  |  |   |  | reviews_per_month | |
|ubahn | Wikidata via SPARQL | yes | railway=station | full | line --> ref=*(The line reference, e.g. "U1", "U2") | platform --> railway=platform + public_transport=platform |   |mapping might not that easy as many tags have to be used |
| | | | station=subway |  | station --> railway=subway_entrance  | Layer--> railway=platform + public_transport=platform |   | |
| | | | type=route + route=subway |  |   | level --> railway=platform + public_transport=platform |   | |
| | | |  |  |   |  |  | |
