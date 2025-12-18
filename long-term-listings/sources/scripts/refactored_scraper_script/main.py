"""
Simple usage example for ImmoweltScraper

This script shows how to use the streamlined scraper.
Geospatial data (district, neighborhood) is added via SQL (see README).
"""

import argparse
from immowelt_scraper import ImmoweltScraper


def main():
    """Run the scraper with optional CLI arguments"""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Immowelt Scraper - Extract listings with geocoding',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use defaults from config.json
  python main.py

  # Scrape Munich instead of default city
  python main.py --url "https://www.immowelt.de/suche/muenchen/wohnungen"

  # Quick test with 3 pages
  python main.py --pages 3

  # Complete custom run
  python main.py --url "https://..." --pages 10 --output munich.csv

Priority:
  URL:   CLI --url > config.json > curl.txt
  Pages: CLI --pages > auto-detect from site
        """
    )
    parser.add_argument(
        '--url',
        type=str,
        help='Target URL (overrides config.json and curl.txt)'
    )
    parser.add_argument(
        '--pages',
        type=int,
        help='Number of pages to scrape (default: auto-detect)'
    )
    parser.add_argument(
        '--start-page',
        type=int,
        default=1,
        help='Starting page number (default: 1)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='immowelt_listings.csv',
        help='Output CSV file (default: immowelt_listings.csv)'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("IMMOWELT SCRAPER")
    print("="*60 + "\n")

    # Initialize scraper
    scraper = ImmoweltScraper()

    # Step 1: Load session
    scraper.load_session()

    # Step 2: Scrape listings (CLI args override defaults)
    scraper.scrape(
        start_page=args.start_page,
        end_page=args.pages,      # None if not provided = auto-detect
        target_url=args.url        # None if not provided = use config/curl
    )

    if not scraper.listings:
        print("❌ No listings found!")
        return

    # Step 3: Geocode addresses
    scraper.geocode()

    # Step 4: Save to CSV with composite IDs
    csv_path = scraper.save_csv(args.output)

    print(f"\n✅ Done! CSV saved to: {csv_path}")
    print(f"\nNext steps:")
    print(f"1. Load CSV to staging table")
    print(f"2. Run SQL script to add geospatial data")
    print(f"   (See SQL_WORKFLOW.md for SQL example)")


if __name__ == '__main__':
    main()
