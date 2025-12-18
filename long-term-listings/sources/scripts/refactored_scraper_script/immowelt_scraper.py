"""
Immowelt Scraper - Streamlined Data Extraction
Focus: Extract listing data + geocode to lat/long
Geospatial joins handled via SQL (see SQL script in docs)
"""

import json, random, re, time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class ImmoweltScraper:
    """
    Streamlined scraper for Immowelt listings

    Features: Extract core data, robust geocoding, CSV export with composite IDs
    Note: Geospatial data (district, neighborhood) added via SQL
    """

    def __init__(self, curl_file='curl.txt', config_file='config.json'):
        self.curl_file = curl_file
        self.config_file = config_file
        self.config = self._load_config()
        self.session = None
        self.listings = []
        self.df = None

    def load_session(self):
        """Load authentication from curl.txt (headers + cookies)

        URL extracted as fallback only - target URL determined in scrape() by priority.
        Returns: dict with fallback_url, headers, cookies
        """
        if not Path(self.curl_file).exists():
            raise FileNotFoundError(
                f"❌ {self.curl_file} not found!\n\n"
                "Create it by:\n"
                "1. Browser → F12 → Network tab\n"
                "2. Refresh Immowelt page\n"
                "3. Right-click request → Copy as cURL\n"
                f"4. Paste into {self.curl_file}"
            )

        curl_cmd = Path(self.curl_file).read_text(encoding='utf-8', errors='replace')

        # Extract URL (fallback only)
        url_match = re.search(r"curl\s+['\"]([^'\"]+)['\"]?", curl_cmd)
        fallback_url = url_match.group(1) if url_match else None

        # Extract headers (skip cookie header)
        headers = {
            match.group(1).strip(): match.group(2).strip()
            for match in re.finditer(r"-H\s+['\"]([^:]+):\s*([^'\"]+)['\"]?", curl_cmd, re.I)
            if match.group(1).strip().lower() != 'cookie'
        }

        # Extract cookies
        cookies = {}
        for pattern in [r"(?:-b|--cookie)\s+['\"](.+?)['\"](?:\s|$)", r"-H\s+['\"]cookie:\s*([^'\"]+)['\"]"]:
            match = re.search(pattern, curl_cmd, re.I)
            if match:
                cookies.update({
                    k.strip(): v.strip()
                    for pair in match.group(1).split(';')
                    if '=' in pair
                    for k, v in [pair.split('=', 1)]
                })

        self.session = requests.Session()
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)
        self.fallback_url = fallback_url

        print(f"✓ Session loaded ({len(headers)} headers, {len(cookies)} cookies)")
        return {'fallback_url': fallback_url, 'headers': headers, 'cookies': cookies}

    def scrape(self, start_page=1, end_page=None, target_url=None):
        """Scrape listings from pages

        URL Priority: 1) target_url param, 2) config.json, 3) curl.txt fallback
        Returns: list of dicts with listing data
        """
        if not self.session:
            raise RuntimeError("Session not loaded. Call load_session() first.")

        # Determine target URL by priority
        final_url = (
            target_url or
            self.config['scraping'].get('target_url') or
            getattr(self, 'fallback_url', None)
        )
        if not final_url:
            raise RuntimeError(
                "No target URL available!\n"
                "Provide via: scrape(target_url=...) or config.json or curl.txt"
            )

        # Parse URL to extract base and params
        parsed = urlparse(final_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        base_params = {
            key: value[0] if len(value) == 1 else value
            for key, value in parse_qs(parsed.query).items()
        } if parsed.query else {}

        self.listings = []
        seen_urls = set()
        cfg = self.config['scraping']
        delay_min, delay_max, page_key = cfg['delay_min'], cfg['delay_max'], cfg['pagination_param']

        # Fetch first page
        params = {**base_params, page_key: start_page}
        resp = self.session.get(base_url, params=params)

        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch page {start_page}: Status {resp.status_code}")

        soup = BeautifulSoup(resp.text, 'html.parser')
        end_page = self._detect_total_pages(soup) if end_page is None else end_page

        # Parse first page
        selector = self._get_selector('listing_card')
        cards = soup.select(selector)

        if not cards:
            raise RuntimeError(
                f"No cards found on page {start_page}!\n"
                f"Selector: {selector}\n"
                "Check if curl.txt is fresh (cookies expire quickly)"
            )

        for card in cards:
            data = self._parse_card(card)
            if data and data['url'] and data['url'] not in seen_urls:
                self.listings.append(data)
                seen_urls.add(data['url'])

        # Scrape remaining pages
        print(f"\n🔍 Scraping pages {start_page}-{end_page}...")
        for page_num in tqdm(range(start_page + 1, end_page + 1), desc="Pages", unit="page"):
            time.sleep(random.uniform(delay_min, delay_max))

            try:
                params = {**base_params, page_key: page_num}
                resp = self.session.get(base_url, params=params)

                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for card in soup.select(self._get_selector('listing_card')):
                        data = self._parse_card(card)
                        if data and data['url'] and data['url'] not in seen_urls:
                            self.listings.append(data)
                            seen_urls.add(data['url'])
            except Exception:
                continue

        print(f"✓ Scraped {len(self.listings)} unique listings")
        return self.listings

    def geocode(self, max_retries=3):
        """Add lat/long to listings with robust retry logic + postal fallback

        Critical: Geocoding must succeed for downstream SQL spatial joins
        Returns: DataFrame with coordinates and geocode_source tracking
        """
        if not self.listings:
            raise RuntimeError("No listings to geocode. Call scrape() first.")

        try:
            from geopy.geocoders import Nominatim
            from geopy.extra.rate_limiter import RateLimiter
        except ImportError:
            raise ImportError("geopy not installed!\nInstall with: pip install geopy")

        df = pd.DataFrame(self.listings)
        df['geocode_source'] = None  # Track geocoding source

        cfg = self.config['geocoding']
        geocode_func = RateLimiter(
            Nominatim(user_agent=cfg['user_agent'], timeout=cfg.get('timeout', 10)).geocode,
            min_delay_seconds=cfg['rate_limit']
        )

        # Load postal code fallback database if enabled
        postal_db = None
        postal_cfg = cfg.get('postal_fallback', {})
        if postal_cfg.get('enabled', False):
            db_path = Path(postal_cfg.get('database', 'data/de_postal_codes.csv'))
            if db_path.exists():
                try:
                    postal_db = pd.read_csv(db_path, dtype={'postal_code': str})
                    postal_db = postal_db.set_index('postal_code')
                    print(f"✓ Loaded postal fallback DB: {len(postal_db)} postal codes")
                except Exception as e:
                    print(f"⚠️  Failed to load postal DB: {e}")
                    postal_db = None
            else:
                print(f"⚠️  Postal DB not found: {db_path} (fallback disabled)")

        def build_variants(row):
            """Build 4 address variants for retry (handles edge cases like "16348 Berlin")"""
            street, house_num = row.get('street', ''), row.get('house_number', '')
            postal = row.get('postal_code', '')
            city = row.get('city', cfg.get('default_city', 'Berlin'))

            variants = []
            if street and house_num and postal:
                variants.append(f"{street} {house_num}, {postal} {city}")
            if street and postal:
                variants.append(f"{street}, {postal} {city}")
            if postal:
                variants.extend([f"{postal} {city}", postal])
            return variants

        print(f"\n🌍 Geocoding {len(df)} addresses...")
        stats = {'nominatim': 0, 'postal_fallback': 0, 'failed': 0}

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Geocoding", unit="addr"):
            geocoded = False

            # Try Nominatim first
            for variant in build_variants(row):
                if not variant:
                    continue

                for attempt in range(max_retries):
                    try:
                        location = geocode_func(variant)
                        if location:
                            df.at[idx, 'latitude'] = location.latitude
                            df.at[idx, 'longitude'] = location.longitude
                            df.at[idx, 'geocode_source'] = 'nominatim'
                            stats['nominatim'] += 1
                            geocoded = True
                            break
                    except Exception:
                        if attempt < max_retries - 1:
                            time.sleep(1)

                if geocoded:
                    break

            # Try postal code fallback if Nominatim failed
            if not geocoded and postal_db is not None:
                postal = str(row.get('postal_code', '')).strip()
                if postal and postal in postal_db.index:
                    try:
                        coords = postal_db.loc[postal]
                        df.at[idx, 'latitude'] = coords['latitude']
                        df.at[idx, 'longitude'] = coords['longitude']
                        df.at[idx, 'geocode_source'] = 'postal_fallback'
                        stats['postal_fallback'] += 1
                        geocoded = True
                    except Exception:
                        pass

            # Mark as failed if both methods failed
            if not geocoded:
                df.at[idx, 'geocode_source'] = 'failed'
                stats['failed'] += 1

        # Print statistics
        total = len(df)
        success = stats['nominatim'] + stats['postal_fallback']
        rate = (success / total * 100) if total > 0 else 0

        print(f"\n✓ Geocoding Results: {success}/{total} ({rate:.1f}%)")
        print(f"  Nominatim:       {stats['nominatim']:4d} ({stats['nominatim']/total*100:.1f}%)")
        if postal_db is not None:
            print(f"  Postal Fallback: {stats['postal_fallback']:4d} ({stats['postal_fallback']/total*100:.1f}%)")
        print(f"  Failed:          {stats['failed']:4d} ({stats['failed']/total*100:.1f}%)")

        if stats['failed'] > 0:
            print(f"\n⚠️  WARNING: {stats['failed']} addresses could not be geocoded")
            print("   These records will be SKIPPED in SQL spatial joins")

        self.df = df
        return df

    def save_csv(self, output_file='immowelt_listings.csv'):
        """Save to CSV with composite IDs

        Composite ID format: {TYPE_ABBR}_{RENT}_{SIZE}_{POSTAL}
        Returns: output file path
        """
        if self.df is None:
            if not self.listings:
                raise RuntimeError("No data to save. Call scrape() and geocode() first.")
            self.df = pd.DataFrame(self.listings)

        self.df = self.df.drop_duplicates(subset=['url'], keep='first')
        self.df['id'] = self.df.apply(self._build_composite_id, axis=1)

        # Select core columns
        output_cols = [
            'id', 'url', 'name', 'type', 'first_tenant', 'price_euro',
            'number_of_rooms', 'surface_m2', 'floor',
            'street', 'house_number', 'postal_code', 'city', 'address',
            'latitude', 'longitude', 'geocode_source'
        ]

        df_out = self.df[[col for col in output_cols if col in self.df.columns]]
        df_out.to_csv(output_file, index=False)

        geocoded = df_out['latitude'].notna().sum()
        print(f"\n✓ Saved {len(df_out)} listings to {output_file}")
        print(f"  Geocoded: {geocoded}/{len(df_out)} ({geocoded/len(df_out)*100:.1f}%)")

        return output_file

    # ========================================================================
    # INTERNAL METHODS
    # ========================================================================

    def _build_composite_id(self, row):
        """Build composite key: {TYPE_ABBR}_{RENT}_{SIZE}_{POSTAL}"""
        type_abbr = (row.get('type', 'UNK') or 'UNK')[:3].upper()
        rent = row.get('price_euro', 0) or 0
        size = int(float(row.get('surface_m2', 0) or 0))
        postal = row.get('postal_code', '00000') or '00000'
        postal_str = str(postal) if isinstance(postal, int) else postal

        return f"{type_abbr}_{rent}_{size}_{postal_str}"

    def _load_config(self):
        """Load configuration from config.json (required file)"""
        if not Path(self.config_file).exists():
            raise FileNotFoundError(
                f"❌ {self.config_file} not found!\n"
                "Configuration file is required. See reference structure in docs."
            )

        try:
            config = json.loads(Path(self.config_file).read_text())
            print(f"✓ Loaded config from {self.config_file}")
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load {self.config_file}: {e}")

    def _get_selector(self, key, default=None):
        """Get CSS selector from config"""
        return self.config['selectors'].get(key, default)

    def _build_name(self, listing_type, first_tenant, price, rooms, area, floor,
                    street, house_number, postal_code, city):
        """Build composite name from listing data

        Format: "Type zur Miete [Erstbezug] Price€ Rooms Zimmer Area m² Floor. Geschoss Street Number Postal City"
        """
        parts = []
        if listing_type:
            parts.append(f"{listing_type} zur Miete")
        if first_tenant == 'yes':
            parts.append("Erstbezug")
        if price:
            parts.append(f"{price}€")
        if rooms:
            parts.append(f"{int(rooms)} Zimmer")
        if area:
            parts.append(f"{area}m²")
        if floor:
            parts.append(f"{floor}. Geschoss")
        if street and house_number:
            parts.append(f"{street} {house_number}")
        if postal_code and city:
            parts.append(f"{postal_code} {city}")

        return " ".join(parts) if parts else None

    def _build_address(self, street, house_number, postal_code, city):
        """Build composite address: "Street HouseNumber, Postal City" """
        return (
            f"{street} {house_number}, {postal_code} {city}"
            if all([street, house_number, postal_code, city])
            else None
        )

    def _parse_card(self, card):
        """Extract core data from listing card"""
        try:
            # URL
            link = card.select_one(self._get_selector('card_link'))
            url = link.get('href', '').split('?')[0] if link else None
            if not url:
                return None

            # Price
            price_div = card.select_one(self._get_selector('price'))
            price_text = (price_div.get('aria-label', '') or price_div.get_text(strip=True)) if price_div else None
            price = self._clean_price(price_text) if price_text else None

            # Type extraction from description box
            type_div = card.select_one(self._get_selector('type_source'))
            type_text = type_div.get_text(strip=True) if type_div else ""

            type_pattern = self.config['patterns'].get('type_extraction', r'^(\w+)')
            type_match = re.match(type_pattern, type_text)
            listing_type = type_match.group(1) if type_match else 'Wohnung'

            # First tenant from title element
            title_div = card.select_one(self._get_selector('title'))
            title = title_div.get_text(strip=True) if title_div else ""
            first_tenant = 'yes' if 'Erstbezug' in title else 'no'

            # Key facts (combined text block)
            rooms = area = floor = None
            facts = card.select_one(self._get_selector('keyfacts'))

            if facts:
                text = facts.get_text(" ", strip=True)
                patterns = self.config['patterns']

                rooms_match = re.search(patterns['rooms'], text)
                area_match = re.search(patterns['area'], text)
                floor_match = re.search(patterns['floor'], text)

                rooms = float(rooms_match.group(1).replace(',', '.')) if rooms_match else None
                area = float(area_match.group(1).replace(',', '.')) if area_match else None
                floor = int(floor_match.group(1)) if floor_match else None

            # Address parsing - flexible format
            # Pattern: [street number], [district], CITY (POSTAL)
            # All parts except city and postal are optional
            addr_div = card.select_one(self._get_selector('address'))
            addr_text = addr_div.get_text(strip=True) if addr_div else ""

            street = house_number = city = postal_code = None
            patterns = self.config['patterns']

            # Extract postal code (always in parens)
            zip_match = re.search(patterns['postal_code'], addr_text)
            postal_code = zip_match.group(1) if zip_match else None

            # Remove postal code from text to parse remaining parts
            text_without_postal = re.sub(r'\s*\(\d{5}\)\s*$', '', addr_text).strip()

            # Split by comma - last part is city, earlier parts are street/district
            if text_without_postal:
                parts = [p.strip() for p in text_without_postal.split(',')]

                # City is the last part
                if parts:
                    city = parts[-1]

                # First part (if exists and has more than 1 part) is street + number
                if len(parts) >= 2:
                    street_with_number = parts[0]
                    street_match = re.match(patterns['street_number'], street_with_number)
                    if street_match:
                        street = street_match.group(1).strip()
                        house_number = street_match.group(2).strip()
                    else:
                        street = street_with_number

            # Fallback to config default if city not found
            if not city:
                city = self.config['geocoding'].get('default_city', 'Berlin')

            # Build composite fields
            name = self._build_name(listing_type, first_tenant, price, rooms, area, floor,
                                   street, house_number, postal_code, city)
            address = self._build_address(street, house_number, postal_code, city)

            return {
                'url': url,
                'name': name,
                'type': listing_type,
                'first_tenant': first_tenant,
                'price_euro': price,
                'number_of_rooms': rooms,
                'surface_m2': area,
                'floor': floor,
                'street': street,
                'house_number': house_number,
                'postal_code': postal_code,
                'city': city,
                'address': address,
                'latitude': None,
                'longitude': None
            }

        except Exception:
            return None

    def _clean_price(self, text):
        """Parse '1.250,50 €' → 1250"""
        if not text:
            return None
        clean = text.replace('.', '').replace('€', '').replace(' ', '').strip().replace(',', '.')
        try:
            return int(float(clean))
        except Exception:
            return None

    def _detect_total_pages(self, soup):
        """Auto-detect total pages from pagination"""
        nav = soup.select_one(self._get_selector('pagination'))
        if nav:
            page_numbers = [
                int(match.group(1))
                for btn in nav.select('button')
                if (match := re.search(r'seite\s+(\d+)', btn.get('aria-label', ''), re.I))
            ]
            if page_numbers:
                return max(page_numbers)
        return 5
