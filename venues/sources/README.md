# Berlin Venues Layer

This project creates a comprehensive data layer of venues in Berlin, focusing on bars, restaurants, and cafés. The data is extracted using the Overpass API and includes detailed information about each venue, location data, and operational details.

---

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [How It Works](#how-it-works)
4. [Running the Script](#running-the-script)
5. [Output Example](#output-example)
6. [Reverse Geolocation to Create District Column](#reverse-geolocation-to-create-district-column)
7. [Data Transformation and Opening Hours Library](#data-transformation-and-opening-hours-library)

---

## Features

- **Venue Types**: Retrieves data for restaurants, cafés, and bars
- **Comprehensive Data Extraction**:
  - Name
  - Category (amenity type)
  - Cuisine type (if available)
  - Full address
  - Latitude/Longitude coordinates
  - Website
  - Phone number
  - Opening hours
  - Takeaway availability
  - Wheelchair accessibility
- **Data Export**: Saves all data as `berlin_places.csv`

---

## Requirements

- **Python**: 3.8+
- **Required Packages**:

```bash
pip install requests pandas folium geopy
```

---

## How It Works

### 1. Overpass API Query
The script sends a POST request to the Overpass API to select all amenities (restaurant, café, bar) within Berlin's administrative boundaries.

### 2. Data Extraction
For each venue returned, the script extracts:
- Tags like name, amenity, cuisine, etc.
- Address fields (`addr:street`, `addr:housenumber`, `addr:postcode`, `addr:city`)
- Coordinates (from the node or center of a way/relation)

### 3. CSV Export
Extracted data is written to `berlin_places.csv` in UTF-8 encoding.

---

## Running the Script

```bash
python berlin_venues_extractor.py
```

The script will:
- Print "Executing Overpass query…"
- Print the number of elements extracted
- Save the CSV file in the current directory

---

## Output Example

| name | category | cuisine | address | lat | lon | website | phone | opening_hours | takeaway | wheelchair |
|------|----------|---------|---------|-----|-----|---------|-------|---------------|----------|------------|
| Example Café | cafe | coffee | Example St 10, 10115 Berlin | 52.5200 | 13.4050 | example.com | +49 30 … | Mo-Fr 08:00-18:00 | yes | yes |

---

## Reverse Geolocation to Create District Column

### Objective
Convert latitude and longitude coordinates into human-readable administrative districts and add them as a new column to enhance the venue data layer.

### What is Reverse Geolocation?

Reverse geolocation converts geographic coordinates (latitude/longitude) into readable address components such as:
- Street
- City
- District
- Country

**Example**: `Latitude: 52.5200, Longitude: 13.4050` → `District: Mitte`

### Tools in Python
- **geopy**: Provides access to multiple geocoding services (Nominatim, GoogleV3)
- **pandas**: For dataset handling

---

## Data Transformation and Opening Hours Library

### Objective
Transform raw operational data into a structured format and create a reusable Opening Hours library for analysis and filtering.

### Raw Data Overview

**Example input**:
| Store | Monday | Tuesday | … | Sunday |
|-------|--------|---------|---|--------|
| Store A | 9:00-17:00 | 9:00-17:00 | … | Closed |
| Store B | 10:00-18:00 | 10:00-18:00 | … | 10:00-14:00 |

**Challenges**:
- Inconsistent formats (9-5, 09:00-17:00, Closed)
- Missing entries
- Need for standardized, machine-readable format

### Transformation Goals
1. Standardize time format to `HH:MM-HH:MM`
2. Handle special cases (Closed, 24h)
3. Create a reusable dictionary/library for analysis

### Example Workflow

```python
import pandas as pd
import re

# Load venue data
df = pd.read_csv("berlin_places.csv")

# Standardize opening hours function
def parse_opening_hours(hours_str):
    """
    Parse OpenStreetMap opening hours format into structured data
    Example: "Mo-Fr 08:00-18:00; Sa 09:00-17:00" 
    """
    if pd.isna(hours_str) or not hours_str:
        return None
    
    # Initialize days structure
    schedule = {
        'Monday': None, 'Tuesday': None, 'Wednesday': None,
        'Thursday': None, 'Friday': None, 'Saturday': None, 'Sunday': None
    }
    
    # Parse different day formats
    day_mapping = {
        'Mo': 'Monday', 'Tu': 'Tuesday', 'We': 'Wednesday',
        'Th': 'Thursday', 'Fr': 'Friday', 'Sa': 'Saturday', 'Su': 'Sunday'
    }
    
    # Split by semicolon for multiple time ranges
    parts = hours_str.split(';')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Extract day range and time
        if ' ' in part:
            day_part, time_part = part.split(' ', 1)
            
            # Handle day ranges like Mo-Fr
            if '-' in day_part:
                start_day, end_day = day_part.split('-')
                # Implementation for day ranges...
            else:
                # Single day
                if day_part in day_mapping:
                    schedule[day_mapping[day_part]] = time_part
    
    return schedule

# Apply parsing to opening hours
df['parsed_hours'] = df['opening_hours'].apply(parse_opening_hours)

# Create opening hours library
opening_hours_library = {}
for index, row in df.iterrows():
    if row['parsed_hours']:
        opening_hours_library[row['name']] = row['parsed_hours']

# Example output
print(opening_hours_library.get('Example Café'))
```

### Sample Output

```json
{
  "Monday": "08:00-18:00",
  "Tuesday": "08:00-18:00",
  "Wednesday": "08:00-18:00",
  "Thursday": "08:00-18:00",
  "Friday": "08:00-18:00",
  "Saturday": "09:00-17:00",
  "Sunday": null
}
```

---

## Project Structure

```
venues/
├── sources/
│   ├── venues_scraper.ipynb        # Main extraction script (notebook)
│   ├── scraper_test.csv             # Sample test extraction results
│   ├── berlin_venues_raw.csv        # File extracted by scraper
│   ├── berlin_venues_cleaned.csv    # Cleaned & transformed venue data
│   └── README.md                    # Documentation
│
└── scripts/
    └── venues_data_transformation.ipynb                 # Cleans and transforms the raw data
```

## Contributing

Feel free to contribute by:
- Adding support for additional venue types
- Improving data quality checks
- Enhancing the opening hours parser
- Adding data visualization features

## License

This project uses data from OpenStreetMap, which is available under the [Open Database License](https://opendatacommons.org/licenses/odbl/).