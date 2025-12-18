# Immowelt Scraper

A robust, configuration-driven web scraper for extracting German real estate listings from Immowelt.de with geocoding capabilities.

## Overview

This scraper extracts detailed apartment listings from Immowelt.de, geocodes addresses to coordinates, and exports structured data for downstream spatial analysis in PostgreSQL/PostGIS.

### Key Features

- **Configuration-Driven Architecture**: All HTML selectors and regex patterns externalized to `config.json`
- **Robust Geocoding**: Two-tier geocoding with Nominatim API + postal code fallback (~95-99% success rate)
- **Flexible Address Parsing**: Supports any German city (not hardcoded to Berlin)
- **CLI Arguments**: Override URL and page count at runtime without editing config files
- **Session Management**: Authenticated scraping via curl.txt (preserves cookies/headers)
- **Composite IDs**: Unique identifiers based on type, price, size, and postal code
- **Error Handling**: Graceful degradation with comprehensive error recovery

---

## Technology Stack

- **Python 3.8+**
- **BeautifulSoup 4**: HTML parsing
- **Requests**: HTTP client with session support
- **Pandas**: Data manipulation and CSV export
- **Geopy/Nominatim**: Geocoding API
- **tqdm**: Progress visualization

---

## Architecture & Design Decisions

### Configuration-Driven Approach

The scraper uses `config.json` to separate **what to extract** from **how to extract it**. This makes the code resilient to HTML changes without touching Python code.

#### **Selectors vs Patterns**

**Selectors** (CSS selectors for HTML navigation):
```json
{
  "selectors": {
    "listing_card": "div[data-testid^='classified-card-mfe']",
    "type_source": "div[data-testid='cardmfe-description-box-text-test-id'] a > div",
    "price": "div[data-testid='cardmfe-price-testid']"
  }
}
```

**Patterns** (Regex for text extraction):
```json
{
  "patterns": {
    "type_extraction": "^(\\w+)",
    "rooms": "([\\d,]+)\\s*Zimmer",
    "area": "([\\d,]+)\\s*m²"
  }
}
```

**Why This Matters:**
- When Immowelt changes HTML structure, update `config.json` instead of refactoring code
- Selectors use stable `data-testid` attributes (less likely to break than CSS classes)
- Patterns handle German number formats (comma decimals: `1,5 Zimmer`)

---

## Obstacles Overcome

### 1. **Pagination Parameter Discovery**

**Problem**: Initial implementation used `sp` parameter for pagination, which didn't work.

**Solution**: Discovered correct parameter is `page` through URL analysis.

**Implementation**:
```json
"scraping": {
  "pagination_param": "page"
}
```

---

### 2. **Flexible Address Parsing**

**Problem**: Original code was hardcoded for Berlin addresses only. When scraping other cities (Munich, Hamburg, etc.), all addresses defaulted to "Berlin".

**Solution**: Implemented flexible comma-based parsing that extracts city dynamically.

**Pattern Support**:
```
[street number], [district], CITY (POSTAL)
```

All parts except city and postal code are optional.

**Example Parsing**:
```python
Input:  "Leopoldstraße 15, Schwabing, München (80802)"
Output: street="Leopoldstraße", number="15", city="München", postal="80802"

Input:  "Schwabing, München (80802)"  # No street
Output: city="München", postal="80802"

Input:  "München (80802)"  # Only city/postal
Output: city="München", postal="80802"
```

**Config Override**:
```json
"geocoding": {
  "default_city": "Berlin"  // Fallback if city not found
}
```

---

### 3. **Type Selector Identification**

**Problem**: Listing type (Wohnung, Haus, Maisonette, etc.) was not being extracted correctly.

**Root Cause**: Used wrong selector - extracted from title element instead of description box.

**Solution**: Discovered type is located in a different element:

**Wrong (title element)**:
```json
"title": "div[data-testid='cardmfe-title-testid']"  // Contains "Erstbezug" info, not type
```

**Correct (description box)**:
```json
"type_source": "div[data-testid='cardmfe-description-box-text-test-id'] a > div"
```

**Code Implementation**:
```python
# Type extraction from description box
type_div = card.select_one(self._get_selector('type_source'))
type_text = type_div.get_text(strip=True) if type_div else ""
listing_type = re.match(r'^(\w+)', type_text).group(1)

# First tenant info still from title
title_div = card.select_one(self._get_selector('title'))
first_tenant = 'yes' if 'Erstbezug' in title else 'no'
```

---

### 4. **Geocoding Robustness**

**Problem**: Nominatim API alone only achieved ~70-85% geocoding success. Listings without coordinates are unusable for spatial joins.

**Solution**: Multi-tier geocoding strategy:

#### **Tier 1: Nominatim with 4 Address Variants**

For each listing, try 4 different address formats (handles edge cases like "16348 Berlin" where postal code doesn't match city boundaries):

```python
variants = [
    "Leopoldstraße 15, 80802 München",  # Full address
    "Leopoldstraße, 80802 München",     # Street without number
    "80802 München",                     # Postal + city
    "80802"                              # Postal only
]
```

Each variant is retried 3 times with 1-second delays.

**Timeout Protection**:
```json
"geocoding": {
  "timeout": 10  // Prevent hanging on slow responses
}
```

#### **Tier 2: Postal Code Fallback Database**

If Nominatim fails, lookup postal code centroid coordinates from GeoNames.org database (~8,000 German postal codes).

**Expected Coverage**:
- Nominatim: ~70-85%
- Postal Fallback: +10-20%
- **Total: ~95-99% success rate**

**Tracking**:
Every record gets a `geocode_source` field:
- `nominatim` - Successfully geocoded via API
- `postal_fallback` - Used postal code database
- `failed` - Both methods failed (no coordinates)

---

## CLI Arguments: Value & Flexibility

### Why CLI Arguments Matter

The scraper supports **three-tier URL priority** for maximum flexibility:

```
1. Runtime CLI argument  (--url)
2. config.json override  ("scraping.target_url")
3. curl.txt fallback     (extracted from curl command)
```

This allows you to:
- **Test different cities** without editing config files
- **Quick ad-hoc runs** for specific searches
- **Maintain default configuration** while experimen ting

### Usage Examples

#### **Default Behavior** (uses config.json or curl.txt)
```bash
python main.py
```

#### **Scrape Different City**
```bash
python main.py --url "https://www.immowelt.de/suche/muenchen/wohnungen"
```

#### **Quick Test Run**
```bash
python main.py --pages 3
```

#### **Complete Custom Run**
```bash
python main.py \
  --url "https://www.immowelt.de/suche/hamburg/wohnungen" \
  --pages 10 \
  --start-page 1 \
  --output hamburg_listings.csv
```

#### **Priority Examples**

**Scenario 1: CLI overrides everything**
```bash
# config.json has Berlin URL
# curl.txt has Munich URL
python main.py --url "https://...hamburg..."
# Result: Scrapes Hamburg (CLI wins)
```

**Scenario 2: Config overrides curl.txt**
```bash
# config.json: "target_url": "https://...munich..."
# curl.txt has Berlin URL
python main.py
# Result: Scrapes Munich (config wins)
```

**Scenario 3: Fallback to curl.txt**
```bash
# config.json: "target_url": ""
# curl.txt has Berlin URL
python main.py
# Result: Scrapes Berlin (curl.txt fallback)
```

### Available Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--url` | Target search URL | Config/curl.txt |
| `--pages` | Number of pages to scrape | Auto-detect |
| `--start-page` | Starting page number | 1 |
| `--output` | Output CSV filename | immowelt_listings.csv |

---

## Setup & Installation

### 1. Clone Repository

```bash
cd long-term-listings
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements**:
- requests>=2.31.0
- beautifulsoup4>=4.12.0
- pandas>=2.0.0
- geopy>=2.4.0
- tqdm>=4.66.0

### 3. Create curl.txt (Authentication)

The scraper needs valid cookies/headers from your browser session:

1. Open Immowelt.de in browser
2. Press `F12` (Developer Tools)
3. Go to **Network** tab
4. Refresh page
5. Right-click any request → **Copy as cURL**
6. Paste into `curl.txt`

**Note**: Cookies expire quickly - regenerate curl.txt if scraping fails.

### 4. Configure config.json (Optional)

**Minimal config** (use defaults):
```json
{
  "scraping": {
    "target_url": ""  // Leave empty to use curl.txt URL
  }
}
```

**Custom config** (override for specific city):
```json
{
  "scraping": {
    "target_url": "https://www.immowelt.de/suche/muenchen/wohnungen",
    "delay_min": 2,
    "delay_max": 5
  },
  "geocoding": {
    "default_city": "München"
  }
}
```

### 5. Optional: Setup Postal Code Fallback

For best geocoding results, download German postal code database:

```bash
mkdir -p data
wget http://download.geonames.org/export/zip/DE.zip -O data/DE.zip
unzip data/DE.zip -d data/
```

Process to required format (see [POSTAL_FALLBACK_SETUP.md](POSTAL_FALLBACK_SETUP.md)):

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/DE.txt', sep='\t', header=None,
                 names=['country', 'postal_code', 'place_name', 'admin_name1', 'admin_code1',
                        'admin_name2', 'admin_code2', 'admin_name3', 'admin_code3',
                        'latitude', 'longitude', 'accuracy'])
postal_db = df[['postal_code', 'latitude', 'longitude']].groupby('postal_code').agg({'latitude': 'mean', 'longitude': 'mean'}).reset_index()
postal_db['postal_code'] = postal_db['postal_code'].astype(str).str.zfill(5)
postal_db.to_csv('data/de_postal_codes.csv', index=False)
print(f'✓ Processed {len(postal_db)} postal codes')
"
```

---

## Usage

### Basic Usage

```bash
python main.py
```

**What happens:**
1. Loads authentication from curl.txt
2. Scrapes all pages (auto-detects total from pagination)
3. Geocodes all addresses (Nominatim + postal fallback)
4. Exports to `immowelt_listings.csv`

### Advanced Usage

```python
from immowelt_scraper import ImmoweltScraper

# Initialize scraper
scraper = ImmoweltScraper()

# Load session
scraper.load_session()

# Scrape with custom parameters
scraper.scrape(
    start_page=1,
    end_page=10,
    target_url="https://www.immowelt.de/suche/muenchen/wohnungen"
)

# Geocode
scraper.geocode(max_retries=3)

# Save
scraper.save_csv('output.csv')
```

---

## Output Structure

### CSV Columns

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Composite key | `WOH_1250_65_10115` |
| `url` | Listing URL | `https://...` |
| `name` | Generated description | `Wohnung zur Miete 1250€ 2 Zimmer 65m²...` |
| `type` | Listing type | `Wohnung`, `Haus`, `Maisonette` |
| `first_tenant` | First occupancy | `yes`, `no` |
| `price_euro` | Monthly rent (€) | `1250` |
| `number_of_rooms` | Room count | `2.0` |
| `surface_m2` | Area (m²) | `65.5` |
| `floor` | Floor number | `3` |
| `street` | Street name | `Leopoldstraße` |
| `house_number` | House number | `15` |
| `postal_code` | Postal code | `80802` |
| `city` | City name | `München` |
| `address` | Full address | `Leopoldstraße 15, 80802 München` |
| `latitude` | Latitude | `48.1549` |
| `longitude` | Longitude | `11.5829` |
| `geocode_source` | Geocoding method | `nominatim`, `postal_fallback`, `failed` |

### Composite ID Format

```
{TYPE_ABBR}_{RENT}_{SIZE}_{POSTAL}
```

**Example**:
```
WOH_1250_65_80802
│   │    │   └─ Postal code
│   │    └───── Surface m² (integer)
│   └────────── Monthly rent (€)
└────────────── Type abbreviation (first 3 chars)
```

**Purpose**: Unique identifier for deduplication and tracking across scraping runs.

---

## Geocoding Statistics

After geocoding, you'll see detailed statistics:

```
🌍 Geocoding 487 addresses...
[████████████████████] 487/487

✓ Geocoding Results: 475/487 (97.5%)
  Nominatim:       402 (82.5%)
  Postal Fallback:  73 (15.0%)
  Failed:           12 (2.5%)

✓ Saved 487 listings to immowelt_listings.csv
  Geocoded: 475/487 (97.5%)
```

---

## SQL Integration

This scraper is designed for PostgreSQL/PostGIS spatial analysis. See [SQL_WORKFLOW.md](SQL_WORKFLOW.md) for:

- Loading CSV to staging tables
- Spatial joins with district/neighborhood geometries
- Enriching data with geospatial attributes

**Example SQL workflow**:
```sql
-- Load CSV
\COPY staging.long_term_listings_staging FROM 'immowelt_listings.csv' WITH CSV HEADER;

-- Create geometries and join districts
INSERT INTO staging.long_term_listings_postgis
SELECT
    src.*,
    ST_SetSRID(ST_MakePoint(src.longitude, src.latitude), 4326) AS geometry,
    d.district_id,
    d.district,
    n.neighborhood_id,
    n.neighborhood
FROM staging.long_term_listings_staging AS src
LEFT JOIN berlin_source_data.districts AS d
    ON ST_Contains(d.geometry, ST_SetSRID(ST_MakePoint(src.longitude, src.latitude), 4326))
LEFT JOIN berlin_source_data.neighborhoods AS n
    ON ST_Contains(n.geometry, ST_SetSRID(ST_MakePoint(src.longitude, src.latitude), 4326))
WHERE src.geocode_source != 'failed';
```

---

## Configuration Reference

### Complete config.json

```json
{
  "selectors": {
    "listing_card": "div[data-testid^='classified-card-mfe']",
    "card_link": "a[data-testid='card-mfe-covering-link-testid']",
    "keyfacts": "div[data-testid='cardmfe-keyfacts-testid']",
    "price": "div[data-testid='cardmfe-price-testid']",
    "title": "div[data-testid='cardmfe-title-testid']",
    "address": "div[data-testid='cardmfe-description-box-address']",
    "type_source": "div[data-testid='cardmfe-description-box-text-test-id'] a > div",
    "pagination": "nav[aria-label='pagination navigation']"
  },

  "patterns": {
    "type_extraction": "^(\\w+)",
    "rooms": "([\\d,]+)\\s*Zimmer",
    "area": "([\\d,]+)\\s*m²",
    "floor": "(\\d+)\\.\\s*Geschoss",
    "postal_code": "\\((\\d{5})\\)",
    "street_number": "^(.+?)\\s+(\\d+[a-zA-Z]?)$"
  },

  "scraping": {
    "target_url": "",
    "delay_min": 2,
    "delay_max": 5,
    "pagination_param": "page"
  },

  "geocoding": {
    "rate_limit": 1.0,
    "user_agent": "immowelt_berlin_scraper_v1",
    "timeout": 10,
    "default_city": "Berlin",
    "postal_fallback": {
      "enabled": true,
      "database": "data/de_postal_codes.csv"
    }
  }
}
```

### Updating Selectors

If Immowelt changes their HTML:

1. **Inspect element** in browser (F12)
2. **Find data-testid** attribute (most stable)
3. **Update selector** in config.json
4. **Test scraper** on small page count

**Example**:
```json
// Old (broken)
"price": "div.price-class-xyz"

// New (fixed)
"price": "div[data-testid='cardmfe-price-testid']"
```

No Python code changes needed!

---

## Troubleshooting

### No Listings Found

**Error**: `No cards found on page 1!`

**Cause**: Cookies expired or wrong selector

**Fix**:
1. Regenerate curl.txt (cookies expire quickly)
2. Check if `listing_card` selector still works

---

### Geocoding Failures

**Warning**: `⚠️ WARNING: 50 addresses failed geocoding`

**Causes**:
- Invalid addresses
- Nominatim rate limiting
- Network issues

**Fixes**:
1. Enable postal fallback (see setup)
2. Increase timeout: `"timeout": 20`
3. Check address data quality

---

### Type Always Shows "Wohnung"

**Cause**: `type_source` selector not finding element

**Debug**:
```python
# Add to _parse_card method
type_div = card.select_one(self._get_selector('type_source'))
print(f"DEBUG: type_div={type_div}")
print(f"DEBUG: type_text='{type_text}'")
```

**Fix**: Update `type_source` selector in config.json

---

## Project Structure

```
long-term-listings/
├── immowelt_scraper.py          # Main scraper class
├── main.py                       # CLI entry point
├── config.json                   # Configuration (selectors/patterns)
├── curl.txt                      # Session auth (headers/cookies)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── SQL_WORKFLOW.md               # PostgreSQL integration guide
├── POSTAL_FALLBACK_SETUP.md      # Postal DB setup instructions
└── data/
    └── de_postal_codes.csv       # German postal code database (optional)
```

---

## Contributing

When updating the scraper:

1. **Always test changes** on small page counts first (`--pages 3`)
2. **Update config.json** instead of hardcoding values
3. **Maintain backwards compatibility** where possible
4. **Document selector changes** in git commit messages
5. **Verify geocoding coverage** stays above 95%

---

## License

This scraper is for personal research and analysis only. Respect Immowelt's terms of service and rate limits.

**Data Attribution**:
- Postal code data from [GeoNames.org](http://www.geonames.org/) (CC BY 4.0)

---

## Changelog

### v3.0 - Current Release
- ✅ Fixed type extraction (correct selector: `type_source`)
- ✅ Added postal code fallback geocoding (~95-99% coverage)
- ✅ Added CLI arguments (--url, --pages, --start-page, --output)
- ✅ Added geocode_source tracking
- ✅ Flexible address parsing for any German city
- ✅ Pagination parameter fix (sp → page)

### v2.0
- ✅ Configuration-driven architecture
- ✅ OOP design with ImmoweltScraper class
- ✅ Robust geocoding with 4 address variants
- ✅ Composite ID generation
- ✅ Session management via curl.txt

### v1.0
- Initial Jupyter notebook implementation

---

## Support

For issues or questions:
1. Check [SQL_WORKFLOW.md](SQL_WORKFLOW.md) for SQL integration
2. Check [POSTAL_FALLBACK_SETUP.md](POSTAL_FALLBACK_SETUP.md) for geocoding setup
3. Review configuration reference above
4. Check git commit history for recent changes
