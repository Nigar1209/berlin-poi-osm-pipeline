# Historical Prices and Real Estate Statistics in Berlin

## Identified Data Sources

1. [IBB Wohnungsmarktbericht 2024](https://www.ibb.de/de/ueber-uns/publikationen/wohnungsmarktbericht/2024.html)
    - **Origin**: Public Dataset
    - **Update Frequency**: Annual
    - **Description**: District- and street-level rental prices and case counts in Berlin, with median and mean net cold rent per m2 per month, by year.

2. [FIS-Broker Berlin](https://fbinter.stadt-berlin.de/fb/index.jsp)
    - **Origin**: Public Dataset
    - **Update Frequency**: Annual
    - **Description**: District-level land value indicators, typical land use types and floor space indices, by year.

3. [Immobilienmarktberichte - berlin.de](https://www.berlin.de/gutachterausschuss/marktinformationen/marktanalyse/artikel.175633.php)
    - **Origin**: Public Dataset
    - **Update Frequency**: Annual
    - **Description**: District-level demographic and land use statistics, including population, area, land cover, housing, and living space, by year.
    - **Nutzungsbestimmungen**:
        Für die in GAA Online abgerufenen Fachdaten (z.B. Bodenrichtwerte, Immobilienmarktberichte, Daten der Wertermittlung etc.). gilt seit dem 01.03.2025 die Datenlizenz Deutschland – Zero – Version 2.

        Die Datenlizenz Deutschland Zero kann unter folgendem Link eingesehen werden:
        [Datenlizenz Deutschland Zero 2.0](https://www.govdata.de/dl-de/zero-2-0)

## Modelling & Planning

- **Key Parameters Selected**: From the gathered data, the following columns were selected as most relevant:
    - `district_id`: Unique identifier for the district (01-12)
    - `district`: Name of the district (e.g., Mitte, Spandau, etc.) ((currently known as `district_name`))
    - `street_name`: Name of the street (e.g., Bremer Straße, Neu Westend, etc.)
    - `median_net_rent`: Median net cold rent in euros per square meter per month
    - `number_of_cases`: Number of rental listings (cases) used for calculating statistics
    - `mean_net_rent`: Arithmetic mean net cold rent in euros per square meter per month
    - `year`: Calendar year the data refers to
    - `standart_land_value`: Standard land value (Bodenrichtwert) in euros per square meter
    - `typical_land_use_type`: Typical land use type (e.g., Wohngebiet, Gewerbe, etc.)
    - `typical_floor_space_ratio`: Typical floor space ratio (GFZ), indicating permitted building density
    - `reference_date`: Official assessment date (Stichtag) for the land value and usage data
    - `inhabitants`: Number of inhabitants/residents
    - `total_area_ha`: Total area in hectares
    - `share_forest_water_agriculture`: Percentage share of forest, water, and agriculture area
    - `forest_area_ha`: Forest area in hectares
    - `water_area_ha`: Water area in hectares
    - `agriculture_area_ha`: Agricultural land area in hectares
    - `population_density_per_ha`: Population density (residents per hectare)
    - `number_of_residences`: Number of residential units or dwellings
    - `living_space_per_resident_m2`: Living area per resident in square meters

- **Data Relationships**: All datasets in this project are connected using the `district_id` field as the primary key for joins and integration.

    - `district` (currently known as `district_name`): The standardized name of a Berlin administrative district (e.g., "Friedrichshain-Kreuzberg"). This field is used consistently across all data sources to enable merging and comparison.
    - If available, `district_id` may also be present for reference or indexing

- **Schema**:
    ![Raw Schema](sources_schema.png)


- **Data Issues**: The datasets contain some missing or incomplete data points, which affect certain years and districts unevenly. Additionally, there are occasional inconsistencies in values that may arise from changes in data collection methods or reporting standards over time. Users should be aware of these limitations when analyzing trends across multiple years or comparing districts.

- **Data Transformation Plan**: The dataset will undergo several transformations to ensure consistency, clarity, and readiness for analysis
    - **Column Standardization**: Unify column names (e.g., rename district_name to district), apply consistent formatting (e.g., lowercase, snake_case).
    - **Data Type Consistency**: Ensure all columns have appropriate data types (e.g., dates, numbers, strings).
    - **Missing Data Handling**: Fill missing values using suitable methods (e.g., mean, forward-fill) or remove if necessary.
    - **Value Cleaning**: Normalize formatting (e.g., trim whitespace, unify label casing, map inconsistent entries).
    - **Derived Columns & Calculations**: Create new columns to support analysis.
        - Possible calculations:
            - Annual change in median and median rent, land value, population and housing development trends.
            - Ratios and density metrics in rent per inhabitant, land value per residence, living space per district.
            - Land use insights on share of developed vs. undeveloped land, percentage share of each land type.
            - Urbanization indicators by Floor space ratio vs. population density, residential units per hectare
            - Affordability index, rent vs. land value correlation.
    - **Validation**: Check ranges, formats, and logical consistency post-transformation.