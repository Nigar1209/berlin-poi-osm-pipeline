## Berlin Pools Data Integration

### Objective:
The goal of this project is to create a clean, geocoded, and analysis-ready dataset of public pools in Berlin, 
which can be used for mapping, visualization, accessibility studies, and other geospatial analyses.

### Data Sources:

Official Berlin Pool Dataset (baederleben_berlin.xlsx): Provides detailed information about public swimming pools, 
including names, types, addresses, opening hours, and accessibility.

EU Bathing Water Data: Indicates whether a facility is a designated EU bathing site, supporting water quality analyses.

### Transformation & Cleaning Steps:
Loading & Initial Filtering:
The raw dataset is loaded from an Excel file into a pandas DataFrame.
Only the columns relevant for mapping and analysis are retained. These include:

Identifiers: Bad-ID (unique pool ID), Name

Location: Straße, Postleitzahl, Ort, Bezirk, Breitengrad, Längengrad

Pool characteristics: Badtyp, eu_badegewaesser, Barrierefreiheit, Wasserqualitaet, Baujahr, Ganzjährig geöffnet

Discounts: Ermäßigung Kind, Ermäßigung Familie, Ermäßigung Behinderte

Operational info: Öffnungsstunden pro Jahr, Name des Eigentümers

### Column Renaming (German → English):

Column names are translated into English for consistency and clarity:

Example: Bad-ID → pool_id, Breitengrad → latitude, Längengrad → longitude.

Boolean Conversion:
Columns like open_all_year are standardized as Boolean (True/False) for easier analysis, converting from German/English 
yes/no values.

### Column Selection for Mapping:

Only the most important columns for geospatial and analytical purposes are retained:

['pool_id', 'name', 'pool_type', 'street', 'postal_code', 
 'city', 'latitude', 'longitude', 'open_all_year']

These columns ensure the dataset is suitable for interactive mapping, location clustering, accessibility studies, and integration with 
other spatial datasets.

### Outcome:
The resulting dataset is a clean, geospatially accurate, and standardized table of Berlin public pools. It can be used to:

Plot facilities on a city map.

Analyze pool types, availability, and accessibility.

Combine with district-level or environmental datasets for deeper insights.

Serve as a foundation for interactive dashboards or location-based applications.
