### 1.1 Data Source Discovery  
**Topic:** Libraries in Berlin  

---

#### Main Source

**Name:** OpenStreetMap (OSM) via Overpass API  

**Source and Origin:**  
Public, crowdsourced geospatial database  
Accessed via Overpass Turbo ([https://overpass-turbo.eu/](https://overpass-turbo.eu/))  
and Overpass API ([https://overpass-api.de/api/interpreter](https://overpass-api.de/api/interpreter))  

---

**Update Frequency:**  
Continuous, real-time updates (dynamic)  
Community-maintained by contributors worldwide  
Changes occur whenever users add or edit library data  

---

**Data Type:**  
Dynamic (API query using `amenity=library`)  
Can be queried programmatically for automated updates  
No manual downloads required for production use  

---

**Coverage:**  
Approximately **107–149 library locations** identified within Berlin:  
- 107 nodes (point markers)  
- 36 ways (building outlines)  
- 6 relations (complex or grouped features)  

---

**Relevant Data Fields:**  

**Core fields (≈100% coverage):**  
- Library name  
- Coordinates (latitude/longitude)  
- Amenity type (library)  

**Address fields (≈90% coverage):**  
- Street name and house number  
- Postal code  
- City  
- District/suburb name  

**Contact information (≈70–80% coverage):**  
- Phone number  
- Website URL  
- Email address (≈30% coverage)  

**Operational details (≈40–60% coverage):**  
- Opening hours (in OSM format)  
- Operator name and type  
- Building information (type, levels, materials)  

**Accessibility & services (≈30–50% coverage):**  
- Wheelchair accessibility  
- Internet access (Wi-Fi)  
- Accessible toilets  
- Baby feeding facilities  

**Reference codes (≈40% coverage):**  
- ISIL codes (International Standard Identifier for Libraries)  
- Wikidata IDs  
- Wikipedia references  

---

**Reason for Selection:**  
✅ Best source for geographic coordinates (all entries include lat/lon)  
✅ Broad coverage – includes public, university, and specialized libraries  
✅ Free and open access (ODbL license)  
✅ API access allows programmatic integration and automation  
✅ Generally accurate – spot checks confirm reliability  
✅ Self-updating – community continuously improves data  

---

**Limitations Identified:**  
⚠️ Inconsistent completeness (some entries contain minimal information)  
⚠️ Missing detailed service information (e.g., study rooms, collections)  
⚠️ Some opening hours may be outdated (last edited in 2022 for a few entries)  
⚠️ Field naming inconsistencies require normalization during data import  
