"""
Non-Official Market Data Scraper

Scrapes market data from non-official sources (visitberlin, wochenmarkt-deutschland).
Configuration is loaded from scraper_config.json.

Usage:
    python3 scrape_nonofficial.py visitberlin
    python3 scrape_nonofficial.py wochenmarkt
    python3 scrape_nonofficial.py --all
    python3 scrape_nonofficial.py --list
    python3 scrape_nonofficial.py --help

Author: Michael Wetzel
Date: November 2025
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import sys
import os
from pathlib import Path

def load_config(config_file='scraper_config.json'):
    """Load scraper configuration from JSON file."""
    config_path = Path(__file__).parent / config_file

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("Please ensure scraper_config.json exists in the scripts directory.")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        sys.exit(1)

def parse_table(soup, output_path):
    """
    Parses a table from the soup and saves it to a CSV file.
    """
    table = soup.find("table")
    if not table:
        print("⚠️  No table found on the page.")
        return False

    headers = [header.text.strip() for header in table.find_all("th")]
    rows = []
    for row in table.find_all("tr"):
        cols = [col.text.strip() for col in row.find_all("td")]
        if cols:
            rows.append(cols)

    if not rows:
        print("⚠️  No data rows found in table.")
        return False

    df = pd.DataFrame(rows, columns=headers)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"✓ Scraped {len(rows)} rows and saved to {output_path}")
    return True

def parse_with_selector(soup, selector):
    """
    Parses data using a CSS selector and returns list of text elements.
    """
    elements = soup.select(selector)
    data = [element.text.strip() for element in elements]
    return data

def scrape_source(source_name, config):
    """
    Scrape data from a single source based on configuration.
    """
    print(f"\n{'=' * 70}")
    print(f"Scraping: {source_name}")
    print(f"Description: {config['description']}")
    print(f"{'=' * 70}")

    parser_type = config['parser_type']
    urls = config['urls']
    output_path = Path(__file__).parent / config['output_path']

    if parser_type == 'table':
        # Table parser - single URL only
        if len(urls) > 1:
            print("⚠️  Table parser only supports a single URL. Using first URL.")

        url = urls[0]
        print(f"Fetching: {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching URL: {e}")
            return False

        soup = BeautifulSoup(response.content, "html.parser")
        return parse_table(soup, output_path)

    elif parser_type == 'selector':
        # Selector parser - supports multiple URLs
        selector = config['selector']
        all_data = []

        for i, url in enumerate(urls, 1):
            print(f"Fetching ({i}/{len(urls)}): {url}")

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Error fetching URL: {e}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            elements = parse_with_selector(soup, selector)
            all_data.extend(elements)
            print(f"  → Found {len(elements)} items")

        if not all_data:
            print("⚠️  No data found with the given selector.")
            return False

        # Remove duplicates and sort
        all_data = sorted(list(set(all_data)))

        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(output_path, "w", encoding='utf-8') as f:
            for item in all_data:
                f.write(f"{item}\n")

        print(f"✓ Scraped {len(all_data)} unique items and saved to {output_path}")
        return True

    else:
        print(f"❌ Unknown parser type: {parser_type}")
        return False

def list_sources(config):
    """Display all available sources."""
    print("\n📋 Available sources:")
    print("-" * 70)
    for source_name, source_config in config.items():
        print(f"\n  {source_name}")
        print(f"    Description: {source_config['description']}")
        print(f"    URLs: {len(source_config['urls'])}")
        print(f"    Parser: {source_config['parser_type']}")
        print(f"    Output: {source_config['output_path']}")
    print()

def show_help():
    """Display help message."""
    print(__doc__)

def main():
    """Main function."""
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("❌ No source specified.")
        print("\nUsage:")
        print("  python3 scrape_nonofficial.py <source>")
        print("  python3 scrape_nonofficial.py --all")
        print("  python3 scrape_nonofficial.py --list")
        print("  python3 scrape_nonofficial.py --help")
        print("\nRun with --list to see available sources.")
        sys.exit(1)

    arg = sys.argv[1]

    # Load configuration
    config = load_config()

    # Handle special arguments
    if arg == '--help' or arg == '-h':
        show_help()
        list_sources(config)
        sys.exit(0)

    if arg == '--list' or arg == '-l':
        list_sources(config)
        sys.exit(0)

    if arg == '--all' or arg == '-a':
        # Scrape all sources
        print("\n" + "=" * 70)
        print("SCRAPING ALL SOURCES")
        print("=" * 70)

        success_count = 0
        for source_name in config.keys():
            if scrape_source(source_name, config[source_name]):
                success_count += 1

        print("\n" + "=" * 70)
        print(f"✨ SCRAPING COMPLETE: {success_count}/{len(config)} sources successful")
        print("=" * 70)
        sys.exit(0)

    # Scrape specific source
    source_name = arg

    if source_name not in config:
        print(f"❌ Unknown source: {source_name}")
        print("\nAvailable sources:")
        for name in config.keys():
            print(f"  - {name}")
        print("\nRun with --list for more details.")
        sys.exit(1)

    # Scrape the requested source
    success = scrape_source(source_name, config[source_name])

    if success:
        print("\n" + "=" * 70)
        print("✨ SCRAPING COMPLETE")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ SCRAPING FAILED")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
