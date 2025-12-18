
#!/usr/bin/env python3
"""
Inspect current transformed data to understand area_id patterns
"""

import pandas as pd
from pathlib import Path

def inspect_current_data():
    """Look at current data to understand area_id patterns"""
    
    print("🔍 Inspecting Current Transformed Data")
    print("=" * 50)
    
    # Load current data
    file_path = Path("transformed_data/berlin_crime_statistics_transformed_fixed.csv")
    df = pd.read_csv(file_path)
    
    # Get unique area_id and neighborhood combinations
    unique_areas = df[['area_id', 'neighborhood']].drop_duplicates().sort_values('area_id')
    
    print(f"📊 Total unique areas: {len(unique_areas)}")
    print(f"📋 Sample area_id and current neighborhood mapping:")
    print()
    
    # Show all unique combinations
    for _, row in unique_areas.head(20).iterrows():
        print(f"   {row['area_id']:>6} → {row['neighborhood']}")
    
    print(f"\n... showing first 20 of {len(unique_areas)} total areas")
    
    # Group by first 2 digits to see district patterns
    print(f"\n🏛️ Area ID patterns by district:")
    unique_areas['district_code'] = unique_areas['area_id'].astype(str).str[:2]
    district_groups = unique_areas.groupby('district_code')['neighborhood'].first()
    
    for district_code, neighborhood in district_groups.items():
        count = len(unique_areas[unique_areas['district_code'] == district_code])
        print(f"   {district_code}xxxx → {neighborhood} ({count} areas)")

if __name__ == "__main__":
    inspect_current_data()
