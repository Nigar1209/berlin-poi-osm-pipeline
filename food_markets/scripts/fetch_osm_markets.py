#!/usr/bin/env python3
"""
Fetch market data from OpenStreetMap for Berlin.

This script queries the Overpass API to retrieve marketplace data for Berlin
using the optimized query from the Step 1 README. It fetches:
- Marketplaces (amenity=marketplace)
- Food courts (amenity=food_court)
- Christmas markets (xmas:feature=market)

Output: food_markets/sources/OSM-berlin_markets.json

Usage:
    python3 fetch_osm_markets.py

Requirements:
    - requests library (install via: pip install requests)
    - Internet connection to access Overpass API
"""

import requests
import json
import os
import sys
from pathlib import Path

# Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Optimized Overpass query from Step 1 README
OVERPASS_QUERY = """
[out:json][timeout:60];
/* Get all market types for Berlin */
area["name"="Berlin"]->.searchArea;
(
  /* 1. Marketplaces: Can be nodes, ways, or relations */
  node["amenity"="marketplace"](area.searchArea);
  way["amenity"="marketplace"](area.searchArea);
  relation["amenity"="marketplace"](area.searchArea);

  /* 2. Food Halls: Mapped as nodes or ways */
  node["amenity"="food_court"](area.searchArea);
  way["amenity"="food_court"](area.searchArea);

  /* 3. Christmas Markets: Mapped ONLY as nodes */
  node["xmas:feature"="market"](area.searchArea);
);
/* output geometry for ways/relations */
out center;
"""


def fetch_osm_markets():
    """
    Fetches marketplace data from OpenStreetMap for Berlin.

    Returns:
        dict: JSON response from Overpass API containing market data
    """
    print("📡 Querying Overpass API for Berlin markets...")
    print("   (marketplaces, food courts, and Christmas markets)")
    print("   This may take 10-30 seconds...\n")

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": OVERPASS_QUERY},
            timeout=90
        )
        response.raise_for_status()

        data = response.json()

        # Count elements (excluding geometry nodes)
        elements = [elem for elem in data.get("elements", []) if "tags" in elem]

        # Count by type
        marketplace_count = sum(1 for e in elements if e.get("tags", {}).get("amenity") == "marketplace")
        food_court_count = sum(1 for e in elements if e.get("tags", {}).get("amenity") == "food_court")
        xmas_count = sum(1 for e in elements if e.get("tags", {}).get("xmas:feature") == "market")

        print(f"✅ Successfully fetched {len(elements)} markets from OSM:")
        print(f"   - Marketplaces: {marketplace_count}")
        print(f"   - Food courts: {food_court_count}")
        print(f"   - Christmas markets: {xmas_count}")

        return data

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out. The Overpass API might be busy.")
        print("   Please try again in a few moments.")
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Failed to fetch data from Overpass API")
        print(f"   Details: {e}")
        sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse JSON response")
        print(f"   Details: {e}")
        sys.exit(1)


def save_markets_json(data, output_path):
    """
    Saves market data to JSON file.

    Args:
        data (dict): Market data from OSM
        output_path (Path): Path to output JSON file
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Successfully saved to: {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")

    except IOError as e:
        print(f"❌ Error: Failed to write output file")
        print(f"   Details: {e}")
        sys.exit(1)


def main():
    """Main execution function."""
    print("=" * 60)
    print("🗺️  OSM Berlin Markets Fetcher")
    print("=" * 60)
    print()

    # Determine output path (relative to script location)
    script_dir = Path(__file__).parent
    output_path = script_dir / "../food_markets/sources/OSM-berlin_markets.json"
    output_path = output_path.resolve()

    print(f"📁 Output path: {output_path}")
    print()

    # Check if file already exists
    if output_path.exists():
        print(f"⚠️  Warning: Output file already exists")
        print(f"   It will be overwritten with fresh data from OSM")
        response = input("   Continue? [y/N]: ").strip().lower()
        if response != 'y':
            print("\n🛑 Aborted.")
            sys.exit(0)
        print()

    # Fetch data from OSM
    data = fetch_osm_markets()

    # Save to JSON file
    save_markets_json(data, output_path)

    print()
    print("=" * 60)
    print("✨ Done! Market data successfully fetched from OpenStreetMap.")
    print("   Attribution: © OpenStreetMap contributors (ODbL)")
    print("=" * 60)


if __name__ == "__main__":
    main()
