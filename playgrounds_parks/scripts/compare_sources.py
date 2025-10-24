#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple comparison between OSM and legacy sources.
- Coverage counts
- Attribute (column) differences

Usage:
  python playgrounds_parks/scripts/compare_sources.py \
    --osm playgrounds_parks/data/osm_parks_playgrounds_merged.parquet \
    --legacy_parks path/to/legacy_parks.csv \
    --legacy_playgrounds path/to/legacy_playgrounds.csv
"""
import argparse
import os
import pandas as pd
import geopandas as gpd

def read_any(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    return gpd.read_parquet(path)

def attribute_diff(left_cols, right_cols):
    left_only = sorted(list(set(left_cols) - set(right_cols)))
    right_only = sorted(list(set(right_cols) - set(left_cols)))
    both = sorted(list(set(left_cols).intersection(set(right_cols))))
    return left_only, right_only, both

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--osm", required=True)
    ap.add_argument("--legacy_parks", required=True)
    ap.add_argument("--legacy_playgrounds", required=True)
    args = ap.parse_args()

    osm = gpd.read_parquet(args.osm)
    leg_parks = read_any(args.legacy_parks)
    leg_play = read_any(args.legacy_playgrounds)

    print("=== COVERAGE ===")
    print("OSM total:", len(osm))
    print("OSM parks:", (osm["category"]!="playground").sum())
    print("OSM playgrounds:", (osm["category"]=="playground").sum())
    print("LEG parks:", len(leg_parks), "| LEG playgrounds:", len(leg_play))

    print("\n=== ATTRIBUTE DIFF (Parks) ===")
    lonly, ronly, both = attribute_diff(osm.columns, leg_parks.columns)
    print("Only in OSM:", lonly)
    print("Only in Legacy:", ronly)

    print("\n=== ATTRIBUTE DIFF (Playgrounds) ===")
    lonly, ronly, both = attribute_diff(osm.columns, leg_play.columns)
    print("Only in OSM:", lonly)
    print("Only in Legacy:", ronly)

if __name__ == "__main__":
    main()
