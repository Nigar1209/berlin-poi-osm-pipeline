# Berlin Food & Weekly Markets - Data Pipeline

This project transforms and integrates data about Berlin's food and weekly markets from multiple sources into a clean, database-ready format.

## Project Overview

This data pipeline consists of three main steps:

1. **Step 1: Data Collection** - Scrapes non-official market data from web sources
2. **Step 2: Data Transformation** - Combines, cleans, and enriches market data
3. **Step 3: Database Population** - Loads the transformed data into PostgreSQL (documentation coming later)

---

## Step 1: Data Collection

### What It Does

The data collection script (`scripts/scrape_nonofficial.py`) scrapes market data from non-official sources to supplement the official berlin.de datasets:

1. **Visit Berlin** (visitberlin.de)
   - Scrapes 3 pages: covered markets, weekly markets, street food
   - Output: `food_markets/sources/visitberlin_markets.txt`

2. **Wochenmarkt Deutschland** (wochenmarkt-deutschland.de)
   - Scrapes HTML table of Berlin markets
   - Output: `food_markets/sources/wochenmarkt_deutschland.csv`

The scraper is **configuration-driven** - all website-specific settings (URLs, CSS selectors, parser types) are stored in `scripts/scraper_config.json`, making it easy to add new sources or update selectors without touching the code.

### Prerequisites

- Python 3.8 or higher
- Internet connection

### Installation

Install scraping dependencies:

```bash
pip install requests beautifulsoup4 pandas
```
### Configuration

The scraper uses `scripts/scraper_config.json` to configure each source. To add a new source or update selectors:

1. **Inspect the website** using browser DevTools (Chrome/Firefox)
2. **Identify the CSS selector** or table structure
3. **Update the config file**:

```json
{
  "new_source": {
    "description": "Description of the source",
    "urls": ["https://example.com/markets"],
    "parser_type": "selector",  // or "table"
    "selector": "div.market-name",  // CSS selector
    "output_path": "../food_markets/sources/new_source.txt",
    "output_format": "txt"  // or "csv"
  }
}
```

**Parser Types:**
- `"table"` - Scrapes HTML tables (outputs CSV)
- `"selector"` - Scrapes using CSS selectors (outputs TXT)

### How to Run

Navigate to the scripts directory:

```bash
cd scripts
```

**Scrape a specific source:**
```bash
python3 scrape_nonofficial.py visitberlin
python3 scrape_nonofficial.py wochenmarkt
```

**Scrape all sources:**
```bash
python3 scrape_nonofficial.py --all
```

**List available sources:**
```bash
python3 scrape_nonofficial.py --list
```

**Show help:**
```bash
python3 scrape_nonofficial.py --help
```

### Output

The scraper creates files in `food_markets/sources/`:
- `visitberlin_markets.txt` - List of market names (deduplicated and sorted)
- `wochenmarkt_deutschland.csv` - Table with market details

These files are then used as input for Step 2 (Data Transformation).

### Workflow for Adding New Sources

**"Human in the Loop" Workflow:**

1. **Inspect** the website with browser DevTools (F12)
2. **Find** the CSS selector or table structure
3. **Test** the selector in DevTools console:
   ```javascript
   document.querySelectorAll("your.css.selector")
   ```
4. **Update** `scraper_config.json` with the new source
5. **Run** the scraper: `python3 scrape_nonofficial.py new_source`
6. **Verify** the output file was created correctly

### Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'requests'`
- **Solution**: Install dependencies: `pip install requests beautifulsoup4 pandas`

**Issue**: `⚠️ No table found on the page`
- **Solution**: The website structure may have changed. Inspect the page and update the config

**Issue**: `⚠️ No data found with the given selector`
- **Solution**: The CSS selector is incorrect. Use DevTools to find the correct selector

**Issue**: `❌ Unknown source: xyz`
- **Solution**: Check available sources with `--list` or add the source to `scraper_config.json`

### Fetching OpenStreetMap Data

The OSM data serves as the **base layer** for the data transformation pipeline, providing rich, structured
market data including standardized opening hours, operator information, and accessibility details.

**Script**: `scripts/fetch_osm_markets.py`

This script queries the Overpass API using the optimized query from the Step 1 README to fetch:
   - Marketplaces (`amenity=marketplace`)
   - Food courts (`amenity=food_court`)
   - Christmas markets (`xmas:feature=market`)

**How to run:**

Navigate to the scripts directory:
```bash
cd scripts
```

Run the fetch script:
```bash
python3 fetch_osm_markets.py
```

**Output:**
`food_markets/sources/OSM-berlin_markets.json` - Market data from OpenStreetMap

**Note**: The script will prompt for confirmation if the output file already exists. The data is fetched in
real-time from OSM, so results may vary slightly from run to run as the OSM database is continuously updated by
contributors.

**Attribution**: Data © OpenStreetMap contributors, available under the Open Database License (ODbL).

---

## Step 2: Data Transformation

### What It Does

The transformation notebook (`scripts/food_markets_transform.ipynb`) performs the following operations:

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
   cd /path/to/food_markets
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
├── food_markets/
│   └── sources/              # Input data files
│       ├── weihnachtsmaerkte.geojson
│       ├── wochen-troedelmaerkte.geojson
│       ├── OSM-berlin_markets.json
│       ├── wochenmarkt_deutschland.csv
│       ├── visitberlin_markets.txt
│       └── lor_ortsteile.geojson     # Berlin neighborhood boundaries
└── scripts/
    ├── scrape_nonofficial.py         # Data collection script
    ├── scraper_config.json           # Scraper configuration
    ├── food_markets_transform.ipynb  # Main transformation notebook
    ├── berlin_food_markets_clean.csv # Output file (for now)
    └── README.md                     # This file
```

### How to Run

1. **Navigate to the scripts directory**:
   ```bash
   cd scripts
   ```

2. **Launch Jupyter**:
   ```bash
   jupyter notebook
   ```

3. **Open the notebook**:
   - Navigate to `food_markets_transform.ipynb`
   - Click to open

4. **Run all cells**:
   - Click `Kernel` → `Restart & Run All`
   - Or press `Ctrl+Enter` on each cell sequentially

5. **Wait for completion**:
   - The notebook takes approximately **2-3 minutes** to complete
   - Nominatim geocoding takes ~1 second per request (~140 addresses)
   - Progress is displayed for each step

### Output

The transformation produces:

**File**: `scripts/berlin_food_markets_clean.csv`

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
- **Solution**: Ensure `food_markets/sources/lor_ortsteile.geojson` exists in the correct location

**Issue**: Cell execution order error
- **Solution**: Run `Kernel` → `Restart & Run All` to execute cells in correct order

---

## Step 3: Database Population

*Documentation for database population will be added here later.*

---

## Author

**Michael Wetzel**
November 2025

## License

This project is part of an internship assignment.
