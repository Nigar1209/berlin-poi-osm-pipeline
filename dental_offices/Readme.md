# Dental Offices in Berlin – Data Collection & Analysis

## Overview
This project collects, processes, and analyzes data about dental practices in Berlin.
The focus lies on building a lightweight, reproducible data pipeline using openly
available geospatial data.

The primary goal is to obtain a consistent and up-to-date dataset that can be used
for spatial analysis, visualization, and comparison with other public data sources.

---

## Project Structure

```text
project/
├─ scripts/
│   ├─ dental_data.ipynb
│   └─ kzv_scraper.py
├─ sources/
│   └─ kzv_zahnarztsuche.html   # optional / exploratory
├─ data/
│   └─ kzv_dentists_berlin.csv
└─ README.md
```
## Data Sources
### Evaluated Sources

The following data sources were evaluated:

 - OpenStreetMap (amenity=dentist)

 - Berlin Open Data Portal (health and medical facility datasets)

 - KZV Berlin (Kassenzahnärztliche Vereinigung – official registry)

After evaluation, **OpenStreetMap (OSM)** was selected as the primary data source.

OSM is the only source that provides **continuously updated, dynamic data** that can
be accessed programmatically with minimal technical overhead. Data can be retrieved
via standard APIs or extracts without requiring browser automation or additional
infrastructure such as Selenium or WebDriver.

Other sources, while valuable for validation and legal verification, are either
static, updated infrequently, or require complex scraping setups that are outside
the scope of this project.

### OpenStreetMap (OSM)

| Field            | Description                                                                                                     |
|------------------|-----------------------------------------------------------------------------|
| source           | [OpenStreetMap (OSM) - API](https://overpass-api.de/api/interpreter), global crowdsourced geo DB                |
| update_frequency | Monthly / as published                                                                                          |
| data_type        | Dynamic (crowdsourced data accessed via API)                                                                    |
| relevant_fields  | name, addr:street, addr:housenumber, addr:postcode, addr:city, opening_hours, healthcare:speciality, wheelchair, phone, email, website, geometry   
| license          | ODbL 1.0 (Open Database License); attribution required, share-alike applies |