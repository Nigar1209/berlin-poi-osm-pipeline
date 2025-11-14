# Berlin Food & Weekly Markets - Data Pipeline

This project transforms and integrates data about Berlin's food and weekly markets from multiple sources into a clean, database-ready format.

## Project Overview

This data pipeline consists of two main steps:

1. **Step 2: Data Transformation** (this notebook) - Combines, cleans, and enriches market data
2. **Step 3: Database Population** (see below) - Loads the transformed data into PostgreSQL

---

## Step 2: Data Transformation

### What It Does

The transformation notebook (`food_markets_transform.ipynb`) performs the following operations:

1. **Data Loading**: Combines data from 4 sources:
   - `weihnachtsmaerkte.geojson` - Official Christmas markets (berlin.de)
   - `wochen-troedelmaerkte.geojson` - Official weekly markets (berlin.de)
   - `OSM-berlin_markets.json` - OpenStreetMap data for gap filling
   - `wochenmarkt_deutschland.csv` - Additional market data

2. **Data Cleaning**:
   - Filters out flea markets (Trödelmärkte) using keyword matching
   - Filters out past Christmas markets (keeps only current season 2025)
   - Removes duplicates across sources
   - Standardizes column names and data formats

3. **Spatial Join**:
   - Matches market coordinates to Berlin administrative boundaries
   - Adds `neighborhood_id` (4-digit LOR codes: "0101", "0102", etc.)
   - Adds `district_id` (8-digit official Berlin codes: "11001001", etc.)
   - Filters to **Berlin markets only** (163 markets)

4. **Address Enrichment**:
   - Uses Nominatim reverse geocoding to complete missing addresses
   - Extracts postal codes from coordinates
   - Enriches addresses without house numbers

5. **Primary Key Generation**:
   - Generates unique `market_id` for each market (FM001, FM002, etc.)

6. **Export**:
   - Produces `berlin_food_markets_clean.csv` with **zero missing values**
   - All 163 markets are in Berlin (outside markets excluded)

### Prerequisites

- Python 3.8 or higher
- Jupyter Notebook or JupyterLab
- Internet connection (for installing packages and Nominatim geocoding)

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd /path/to/task2+
   ```

2. **Install required packages**:

   The notebook will automatically install required packages on first run, but you can install them manually:

   ```bash
   pip install pandas geopandas geopy
   ```

   Or using conda:

   ```bash
   conda install pandas geopandas
   pip install geopy
   ```

### Directory Structure

```
task2+/
├── food_markets/
│   ├── sources/              # Input data files
│   │   ├── weihnachtsmaerkte.geojson
│   │   ├── wochen-troedelmaerkte.geojson
│   │   ├── OSM-berlin_markets.json
│   │   ├── wochenmarkt_deutschland.csv
│   │   └── visitberlin_markets.txt
│   └── berlin_food_markets_clean.csv  # Output file
├── .ipynb   # Main transformation notebook
└── README.md                           # This file
```

### How to Run

1. **Launch Jupyter**:
   ```bash
   jupyter notebook
   ```

2. **Open the notebook**:
   - Navigate to `food_markets_transform.ipynb`
   - Click to open

3. **Run all cells**:
   - Click `Kernel` → `Restart & Run All`
   - Or press `Ctrl+Enter` on each cell sequentially

4. **Wait for completion**:
   - The notebook takes approximately **2-3 minutes** to complete
   - Nominatim geocoding takes ~1 second per request (~140 addresses)
   - Progress is displayed for each step

### Output

The transformation produces:

**File**: `food_markets/berlin_food_markets_clean.csv`

**Schema** (18 columns):
- `market_id` - Primary key (FM001-FM163)
- `market_name` - Market name
- `market_type` - Type: christmas_market, weekly_market, or food_court
- `address` - Street address
- `postal_code` - Postal code (5-digit PLZ)
- `district` - District name (e.g., "Tempelhof-Schöneberg")
- `neighborhood_id` - LOR neighborhood code (e.g., "0703")
- `district_id` - Official 8-digit district code (e.g., "11007007")
- `opening_days` - Days of operation
- `opening_hours` - Hours of operation
- `operator` - Market operator/organizer
- `contact_email` - Contact email
- `website` - Website URL
- `accessibility` - Accessibility information
- `latitude` - Latitude coordinate
- `longitude` - Longitude coordinate
- `data_source` - Source: berlin.de_official or OSM
- `notes` - Additional notes

**Statistics**:
- Total markets: **163** (all in Berlin)
- Market types: ~43 Christmas markets, ~109 weekly markets, ~11 food courts
- Data quality: **Zero missing values**
- Foreign key ready: `district_id` → `berlin_data.districts(district_id)`

### Data Quality Notes

#### Address Quality
Approximately **50% of addresses lack house numbers**. This is **expected behavior** because:
- Markets are located in public spaces (plazas, squares, parks)
- These locations don't have traditional building addresses
- Examples: "Maybachufer" (embankment), "Helene-Weigel-Platz" (plaza)
- Nominatim returns the best available address for each coordinate

#### District & Postal Code Coverage
- **District names**: All 163 markets have official district names from spatial join
- **Postal codes**: Enriched via Nominatim for geocoded addresses
- **Coordinates**: All markets have valid latitude/longitude

### Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'geopandas'`
- **Solution**: Install geopandas: `pip install geopandas`

**Issue**: Nominatim geocoding is slow
- **Expected**: Respects 1 second delay per request (usage policy)
- **Duration**: ~140 seconds for ~140 addresses

**Issue**: Spatial join fails to find Berlin neighborhoods
- **Solution**: Ensure `mapping/lor_ortsteile.geojson` exists in the correct location

**Issue**: Cell execution order error
- **Solution**: Run `Kernel` → `Restart & Run All` to execute cells in correct order

---

## Step 3: Database Population

_Instructions for loading the transformed data into PostgreSQL will be added here._

### Prerequisites
- PostgreSQL database with `berlin_data` schema
- `berlin_data.districts` table populated with district reference data

### How to Run
_To be documented after implementing the population script._

---

## Author

**Michael Wetzel**
November 2025

## License

This project is part of an internship assignment.
