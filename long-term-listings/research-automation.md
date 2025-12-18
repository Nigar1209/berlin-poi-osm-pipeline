# Immowelt Long-Term Listings — Step 1 Review

## Purpose
Collect long-term rental listings from Immowelt and store them in `{schema}.long_term_listings` for analytics.

## How it works (current notebooks)
1) **Scrape** — `sources/scripts/immowelt_scraping_script.ipynb`  
   Selenium renders result pages, BeautifulSoup parses listing cards → CSV `immowelt_pages_{start}_{end}.csv`.
2) **Clean** — `sources/scripts/immowelt_cleaning_script.ipynb`  
   Normalize price/rooms/size, expand `Str.`→`Straße`, standardize floors, drop non-Berlin → `immowelt_cleaned_<date>.csv`.
3) **(Optional) Geocode** — `sources/scripts/immowelt_geocoding_script.ipynb`  
   Nominatim (≥1s delay) + spatial join with LOR (`resources/geo/lor_ortsteile.geojson`) → fill district/ortsteil.
4) **Load** — `sources/scripts/db_script.ipynb`  
   Load cleaned (or geocoded) CSV into Postgres table `{schema}.long_term_listings`.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r long-term-listings/requirements.txt
cp long-term-listings/.env.example long-term-listings/.env   # fill PG_* values
