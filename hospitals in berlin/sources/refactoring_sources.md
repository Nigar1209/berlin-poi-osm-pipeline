# 1. Sources 
OSM data is used 

## 1.1 amenity=* is the older tagging scheme
Traditionally, amenity=hospital and amenity=clinic were used.
Many OSM objects are still tagged this way because it was the original convention.

## 1.2. healthcare=* is the newer tagging scheme
The OSM healthcare tagging scheme was introduced later to be more flexible and precise.
healthcare=hospital or healthcare=clinic is now the recommended way.
But adoption is still ongoing, so not everything has been updated.

## 1.3. Overlap in practice

Often there are both tags used on the same feature (e.g., a hospital may have amenity=hospital and healthcare=hospital).
But some places may only have one of the two, depending on the mapper’s preference or when it was mapped.

## 1.4 both tags with both, hospital and clinic are used to retrieve OSM data
- there are 35 mismatches in the tags, but I decided to keep the information as is

# 2. Data manipulation
## 2.1 drivations
- longitude and latitude from column geometry
- addr:country set to DE if NULL and addr:city is Berlin
- district, district_id and neighborhood by using reverse geolocation
- replaced NULL values with "unknown"

## 2.2 columns and type reformatting
- columns beds and brand dropped
- source hardcoded to OSM if NULL
- stardized column names
- converted certain colums to correct type
- normalized yes/no column "wheelchair" to Boolean

## 2.3 address
- I decided to store the address parts as available in OSM. They are seperated and not concatenated

# 3. Dataset description

| column | Description | dtype | example
| ----------- | ----------- | ----------- | ----------- |
| name | name of hospital or clinic | object | Helios Arthropädicum Kaulsdorf |
| operator | operator of hospital or clinic | object | Helios Kliniken |
| country | country of hospital or clinic | object | DE |
| city | city of hospital or clinic | object | Berlin |
| street | street of hospital or clinic | object |  Heinrich-Grüber-Straße |
| housenumber | housenumber of hospital or clinic | object | 9 |
| postcode | postcode of street and housenumber of hospital or clinic | object | 12621 |
| heighborhood | neighborhood of hospital or clinic | object | Kaulsdorf |
| phone | phone number of hospital or clinic | object | +49 30 54707477 |
| email | email of hospital or clinic | object |  unknown|
| website | website of hospital or clinic | object | https://www.helios-gesundheit.de/ambulant/berlin-kaulsdorf-arthropaedicum-fachaerzte/ |
| wheelchair | accessibilit by wheelchair of hospital or clinic | object | False|
| toilets_wheelchair | accessibilit of toilets by wheelchair of hospital or clinic | object | yes |
| emergency | emergency unit available of hospital or clinic | object | yes |
| speciality | speciality area of hospital or clinic | object | xurgery;general |
| opening_hours | opening hours of hospital or clinic | object | Mo,Tu,Th 08:00-18:00; We,Fr 08:00-12:00 |
| latitude | latitude of location | float64 | 52.439692 |
| longitude | longitude of location | float 64  13.500167|
| geometry | geometry of hospital or clinic | geometry| POINT (13.50017 52.43969) |
| source | source of data | object | OSM |
| amenity_tag | content of amenity tag | object | clinic |
| healthcare_tag | content of healtcare tag | object | clinic |
| district | district of hospital or clinic | object | Steglitz-Zehlendorf |
| district_id | district_id of hospital or clinic | object | 11006006 |

   
  
