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
## Additional Source Information

**Name:** Berlin Open Data Portal

**Source and origin:**  
- Platform/Organization: Berlin Open Data Portal / Pankow District Office of Berlin  
- Access URL: [https://daten.berlin.de/](https://daten.berlin.de/)
- Name: Loans from Public Libraries in Pankow (2022–2024)
- Access Method: Website download (multiple CSV and DOCX files)  

**Update frequency:**  
- Last updated: July 1, 2025  
- Update schedule: Periodic (annual or biannual updates, based on new loan statistics)  
- Reliability: High — official dataset from a Berlin district government source  

**Data type:**   
- [x] Static (one-time download)  
- [x] Semi-static (periodic manual updates)   

**Access details:**  
- Cost: Free (open data)  
- Authentication required: No  
- API documentation: None (data provided as downloadable files)  
- License: Creative Commons Zero (CC0 — free and unrestricted use)  

---

**Coverage details:**  
- Geographic scope: Pankow District, Berlin  
- Time range: January 1, 2022 – December 31, 2024  
- Temporal granularity: Annual summaries  
- Category: Public administration, budget, and taxes  
- Publishing body: Pankow District Office of Berlin  
- Contact person: Tobias Weiß (tobias.weiss@ba-pankow.berlin.de)  
- Website: [https://www.berlin.de/stadtbibliothek-pankow/](https://www.berlin.de/stadtbibliothek-pankow/)  

**Available formats:**  
- CSV: `AusEx_Pankow_2022.csv`, `AusEx_Pankow_2023.csv`, `AusEx_Pankow_2024.csv`  
- CSV: `Library_Signature_KeyTable.csv`, `SfB_KeyTable.csv`  
- DOCX: `Library_data_documentation.docx`  

---

**Reason for selection:**  
- Provides official library loan and borrower statistics for Pankow over three years (2022–2024)  
- Enables analysis of user demographics, lending patterns, and library activity levels  
- Useful for correlating library usage data with geographic coverage from OSM sources  

**Enrichment potential:**  
- Combine with OSM library coordinates to map library usage intensity per district  
- Use “district” and “library signature” fields for spatial integration and time-series analysis  
- Supports broader research on educational and cultural infrastructure usage in Berlin  
