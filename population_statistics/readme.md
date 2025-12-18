# Population Statistics in Berlin
🔍 Data Source Used


* File: SB_A01-05-00_2024h02_BE.xlsx


* Source: Statistik Berlin-Brandenburg [statistik-berlin-brandenburg.de](https://www.statistik-berlin-brandenburg.de/bevoelkerung)


*  Description: Population by age group and gender, broken down by Berlin districts and postal codes


*  Type: Static (semi-annual release)


*  Update Frequency: Twice a year (H1 and H2)


*  License: Open public data


✅ Modelling & Planning


📌 Key Parameters / Columns from Raw Data


File: SB_A01-05-00_2024h02_BE.xlsx (Population by age groups, neighbourhood and gender)


 Relevant Columns:

 
* District
* Maritalstatus
* Gender (M, F)
* Age_Groups (0–5, 6–10, ..., 80+)
* nationality
* Population_Count
* last_updated_date


🧩 How This Data Connects to Existing Tables


*  Primary Join Field: Neighborhood(matching neighborhood or district name in listings dataset) and postcode.


🗂️ Planned Schema for Population_stats


| Column                 | Type      | Description                                         |
|------------------------|-----------|-----------------------------------------------------|
| `district`                   | STRING      | District name (Bezirk)         |
| `male`             | INTEGER     | Number of male residents                               |
| `female`            | INTEGER      | Number of female residents                      |
| `germans`     | INTEGER      | Number of german residents    |
| `foreigners`       | INTEGER      | Number of foreign residents           |
| `single` | INTEGER      | Number of residents who are single   |
| `married` | INTEGER      | Number of residents who are married   |
| `widowed` | INTEGER      | Number of residents who are widowed   |
| `divorced` | INTEGER      | Number of residents who are divorced   |
| `civil_partnership` | INTEGER      | Number of residents in a civil partnership   |
| `evangelische_kirchen` | INTEGER      | Number of residents affiliated with the Evangelical Church   |
| `römisch_katholische_kirche` | INTEGER      | Number of residents affiliated with the Roman Catholic Church   |
| `religion_other_or_none` | INTEGER      | Number of residents with other or no religious affiliation   |
| `0-6` | INTEGER      | Number of residents aged 0–6   |
| `6-15` | INTEGER      | Number of residents aged 6–15   |
| `15-18` | INTEGER      | Number of residents aged 15–18   |
| `18-27` | INTEGER     | Number of residents aged 18–27   |
| `27-45` | INTEGER      | Number of residents aged 27–45   |
| `45-55` | INTEGER      | Number of residents aged 45–55   |
| `55-65` | INTEGER      | Number of residents aged 55–65   |
| `65+` | INTEGER      | Number of residents aged 65 and above   |
| `district_id` | STRING      | District Id's (01 to 12)   |



⚠️ Known Data Issues or Inconsistencies


* Inconsistent naming for districts.


* Age groups may be non-uniform across files


* Some totals are duplicated across gender/nationality aggregations (double counting possible)



🔄 Transformation Plan


1. Load & Normalize:


    *  Import CSV files into dataframes.


    *  Normalize all column headers.


2. Unpivot Age/Nationality Columns:


    *  Reshape wide age/nationality columns into long format (age_group, nationality)


3. Join Mapping Tables:


    *  Primary Join Field: Neighbourhood(matching neighborhood or district name in listings dataset) and postcode.


4. Standardize Columns:


    *  Rename columns consistently.


    *  Convert types (e.g., integers, strings).


5. Deduplicate:


    *  Remove total rows or repeated counts.


6. Save Cleaned File:


    *  Output as CSV  under a transformed/ directory for loading.
