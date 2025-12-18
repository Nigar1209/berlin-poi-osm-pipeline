# Step 1: Research 

**PR Branch Name:**  vets-data-modelling

This folder documents the research for Step 1 of the "Vet Clinics in Berlin" layer project:

 -   **1.1 Data Source Research and Discovery**
 - 
 - In short, while there is no single open dataset covering all vet clinics in Berlin, a combination of **official lists**, **private directories**, and **OpenStreetMap** provides a solid foundation. Any data collection effort should account for update schedules, technical scraping challenges and legal restrictions.
 
I found following resources to have a look at:
 -   **Official sources:** 
 - **Tierärztekammer Berlin** publishes an emergency‑service page listing clinics that offer 24‑hour coverage, after‑hours services and specialist hospitals for horses and livestock. It is a dynamic, manually maintained list and the most authoritative source for emergency vet information in Berlin. 
   - **Bundesverband Praktizierender Tierärzte (bpt)** runs a **Tierarztsuche** tool that lets users search for veterinary practices by animal species, last name, postal code and distance. It draws on the association’s membership database but does not offer a public download.

    
 **Private directories:** Several websites provide free‑to‑view directories. 
 - **Tierarzt‑Onlineverzeichnis** offers a list of Berlin vets and clinics within 150 km, including names, addresses and phone numbers.
 - **Tierarztliste online** presents a similar list with star‑ratings and contact details. These sites are dynamic – entries change when practices update their information – and can be scraped technically, though terms of use should be respected. 
 - **All About Berlin** publishes a guide to English‑speaking veterinarians, updated in July 2025, which is useful for non‑German speakers. 
 - **AG ARK Tierarztliste** lists veterinarians who participate in the organisation’s reptile and amphibian conferences; it warns that it is not an official recommendation and discourages republishing without permission. 
 - **AniCura** provides a corporate directory of its clinics in Germany with filters for opening hours and services, but it does not offer an API. 
 - **PerPETual** hosts an English summary of the Berlin emergency‑vet list.
   
 -   **Documentation and data characteristics:** For each source, we documented the origin (official body, private directory or corporate site), observed that most have no publicly documented API, and noted whether the data are static (one‑off articles) or dynamic (continuously updated lists). We also assessed the update frequency and concluded that official lists are updated as schedules change, while private directories update irregularly.
    
 -   **Scraping feasibility:** 
 - The Notdienst page, Tierarzt‑Onlineverzeichnis, Tierarztliste online, All About Berlin guide and PerPETual post are simple HTML pages that can be scraped with standard tools. 
 - The bpt search tool and AniCura directory are more complex – they rely on forms and client‑side scripts – and would require form automation or a headless browser to extract data. For legal compliance, scraping should respect each site’s terms of service; 
 - AG ARK explicitly discourages copying its list.
    
 -   **Additional sources:** There are no open, downloadable government datasets of Berlin veterinary clinics. A good alternative is **OpenStreetMap**, which uses the tag `amenity=veterinary` to mark veterinary practices. OSM data can be queried via the free Overpass API or downloaded as geospatial extracts. Combining OSM data with the official emergency list and private directories may yield a comprehensive dataset. 
    
 -   **Commercial POI APIs** – Proprietary services that offer veterinary points of interest. Examples include Google Places (https://developers.google.com/maps/documentation/places), Foursquare Places API (https://location.foursquare.com/developer/docs/places-api/) and TomTom Search API (https://developer.tomtom.com/search-api/search-api-documentation). These services are dynamic and regularly updated, but they require API keys and impose usage limits and restrictions on data reuse.    

 -   **Municipal open data (Berlin Open Data portal)** – The official portal for Berlin’s government datasets. At present there is no dataset for veterinary clinics, but you can browse other datasets at [https://daten.berlin.de/](https://daten.berlin.de/). If a veterinary dataset is published in the future, its update frequency will depend on the city’s release schedule.


**Main sources to use**
There are a few avenues with free or open data on veterinary clinics and first to start with

**Source/origin**
 - **OpenStreetMap (OSM)** – Community‑curated open geodata project. The tag `amenity=veterinary` indicates veterinary practices[wiki.openstreetmap.org](https://wiki.openstreetmap.org/wiki/Tag:amenity=veterinary#:~:text=Description%20A%20place%20that%20deals,2%3A%20Show%2Fedit%20corresponding%20data%20item)
 - **Update frequency** :updated continuously by contributors
 - **Data type (static/dynamic)** Dynamic
 - Additonal: Documentation for the tag is available at [https://wiki.openstreetmap.org/wiki/Tag:amenity=veterinary](https://wiki.openstreetmap.org/wiki/Tag:amenity=veterinary), and you can explore or download extracts via Geofabrik (e.g. https://download.geofabrik.de/europe.html).
    
 **Source/origin**
 - **Overpass API  queries** – Interfaces for querying OSM data. Overpass lets you craft custom queries such as `amenity=veterinary` within Berlin;  https://overpass-turbo.eu/. 
 - **Update frequency** : live OSM database
 - **Data type (static/dynamic)** Dynamic
 
 
  **Source/origin**
 -   **Nominatim reverse‑geocoding service**  Nominatim provides search and reverse‑geocoding based on OSM data; see the public instance at https://nominatim.openstreetmap.org/. 
  - **Update frequency** : live OSM database
 - **Data type (static/dynamic)** Dynamic
  - Additional:
	Documentation and usage limits can be found at https://nominatim.org/release-docs/latest/api/Overview/
    
  
For each of the OSM‑derived sources , the underlying data model is based on the tags and geometry stored in OpenStreetMap. The key data fields we can expect from these sources are:

-   **OpenStreetMap (amenity = veterinary):**
    
    -   `name` – the clinic’s name (if provided by contributors).
    -   Coordinates – latitude and longitude of the node or centroid of the polygon representing the clinic.    
    -   Address tags (when available):
        -   `addr:street` – street name;         
        -   `addr:housenumber` – house number;            
        -   `addr:postcode` – postal code;            
        -   `addr:city` – city/locality.
            
    -   Contact details:       
        -   `phone` or `contact:phone`;          
        -   `website` or `contact:website`;           
        -   `email` or `contact:email`.
            
    -   `opening_hours` – structured opening hours encoded using the OSM opening hours specification, if contributors have added this tag.        
    -   `operator` or `brand` – organisation running the clinic, when specified.
            
    -   Other descriptive tags that sometimes appear (but are optional) include `veterinary:speciality` (e.g. equine), `wheelchair` accessibility, or `emergency` (indicating 24‑hour service).
        
-   **Overpass API / Overpass Turbo queries:**
    
    -   Returns the same set of OSM tags and geometry as described above, because Overpass simply filters OSM data. Results can be output in GeoJSON, XML or CSV formats, containing:        
        -   Node/way/relation ID;            
        -   Latitude and longitude (for nodes) or polygon coordinates (for ways/relations);            
        -   All tags associated with each object (`name`, `addr:*`, `phone`, `opening_hours`, etc.).            
    -   You can also request bounding‑box coordinates or metadata such as version and timestamp if you need to track edits.
        
-   **Nominatim search and reverse‑geocoding:**
    
    -   For search queries, Nominatim returns a list of matching places with:        
        -   `display_name` – human‑readable description of the place;            
        -   `lat` and `lon` – coordinates;            
        -   `osm_type` and `osm_id` – references back to the underlying OSM element;            
        -   `type` and `category` – general classification (e.g. “veterinary”);            
        -   `address` – an object containing keys like `road`, `house_number`, `postcode`, `city`, `state`, `country`, etc.            
    -   Reverse‑geocoding responses include similar fields, mapping coordinates to the nearest OSM object and returning its address structure.        
    -   Nominatim does not expose all tags by default (e.g. it may omit `phone` or `opening_hours`), so for full attribute detail you would still query the object via the Overpass API using the `osm_type` and `osm_id` it returns.
      