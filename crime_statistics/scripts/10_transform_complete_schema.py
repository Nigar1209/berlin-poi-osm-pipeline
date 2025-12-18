
#!/usr/bin/env python3
"""
Transform data addressing mentor's feedback:
1. Split 'neighborhood' into 'locality' and 'neighborhood' (district)
2. Add missing schema columns: absolute_cases, frequency_100k, population_base
"""

import pandas as pd
import json
from pathlib import Path

def create_district_mapping():
    """Map area_ids to their parent districts based on patterns"""
    
    # Berlin district mapping based on area_id patterns
    district_mapping = {
        # Mitte (1x codes)
        'default_1': 'Mitte',
        
        # Friedrichshain-Kreuzberg (2x codes)
        'default_2': 'Friedrichshain-Kreuzberg',
        
        # Pankow (3x codes)
        'default_3': 'Pankow',
        
        # Charlottenburg-Wilmersdorf (4x codes)
        'default_4': 'Charlottenburg-Wilmersdorf',
        
        # Spandau (5x codes)
        'default_5': 'Spandau',
        
        # Steglitz-Zehlendorf (6x codes)
        'default_6': 'Steglitz-Zehlendorf',
        
        # Tempelhof-Schöneberg (7x codes)
        'default_7': 'Tempelhof-Schöneberg',
        
        # Neukölln (8x codes)
        'default_8': 'Neukölln',
        
        # Treptow-Köpenick (9x codes)
        'default_9': 'Treptow-Köpenick',
        
        # Marzahn-Hellersdorf (10x codes) - if they exist
        'default_10': 'Marzahn-Hellersdorf',
        
        # Lichtenberg (11x codes) - if they exist  
        'default_11': 'Lichtenberg',
        
        # Reinickendorf (12x codes) - if they exist
        'default_12': 'Reinickendorf'
    }
    
    return district_mapping

def get_district_from_area_id(area_id):
    """Get district name from area_id pattern"""
    
    area_str = str(int(float(area_id)))  # Convert to clean string
    
    # Extract first digit(s) to determine district
    if area_str.startswith('1'):
        return 'Mitte'
    elif area_str.startswith('2'):
        return 'Friedrichshain-Kreuzberg'
    elif area_str.startswith('3'):
        return 'Pankow'
    elif area_str.startswith('4'):
        return 'Charlottenburg-Wilmersdorf'
    elif area_str.startswith('5'):
        return 'Spandau'
    elif area_str.startswith('6'):
        return 'Steglitz-Zehlendorf'
    elif area_str.startswith('7'):
        return 'Tempelhof-Schöneberg'
    elif area_str.startswith('8'):
        return 'Neukölln'
    elif area_str.startswith('9'):
        return 'Treptow-Köpenick'
    elif area_str.startswith('10'):
        return 'Marzahn-Hellersdorf'
    elif area_str.startswith('11'):
        return 'Lichtenberg'
    elif area_str.startswith('12'):
        return 'Reinickendorf'
    else:
        return 'Unknown'

def transform_with_mentor_feedback():
    """Transform existing data to address mentor's feedback"""
    
    print("🔄 Transforming Data with Mentor Feedback")
    print("=" * 50)
    
    # Load current transformed data
    input_file = Path("transformed_data/berlin_crime_statistics_transformed_fixed.csv")
    df = pd.read_csv(input_file)
    
    print(f"📊 Loaded {len(df):,} records from current data")
    
    # Step 1: Rename current 'neighborhood' to 'locality'
    df = df.rename(columns={'neighborhood': 'locality'})
    
    # Step 2: Create new 'neighborhood' column with district names
    df['neighborhood'] = df['area_id'].apply(get_district_from_area_id)
    
    # Step 3: Add missing schema columns based on data_type
    df['absolute_cases'] = df.apply(
        lambda row: row['value'] if row['data_type'] == 'cases' else None, axis=1
    )
    df['frequency_100k'] = df.apply(
        lambda row: row['value'] if row['data_type'] == 'frequency' else None, axis=1
    )
    df['population_base'] = None  # Will be calculated later if needed
    
    # Step 4: Reorder columns to match mentor's requested schema
    column_order = [
        'area_id', 'locality', 'neighborhood', 'year', 'data_type',
        'crime_type_german', 'crime_type_english', 'category',
        'absolute_cases', 'frequency_100k', 'population_base',
        'value', 'severity_weight'
    ]
    
    df_final = df[column_order]
    
    return df_final

def main():
    transformed_data = transform_with_mentor_feedback()
    
    if transformed_data is not None:
        # Save updated dataset
        output_dir = Path("transformed_data")
        output_file = output_dir / "berlin_crime_statistics_mentor_feedback.csv"
        transformed_data.to_csv(output_file, index=False)
        
        print(f"\n🎉 TRANSFORMATION COMPLETE!")
        print(f"📁 Output: {output_file}")
        print(f"📊 Total records: {len(transformed_data):,}")
        print(f"🏘️ Localities: {transformed_data['locality'].nunique()}")
        print(f"🏛️ Neighborhoods (Districts): {transformed_data['neighborhood'].nunique()}")
        
        # Show sample of updated data
        print(f"\n📋 Sample of Updated Data Structure:")
        sample_cols = ['area_id', 'locality', 'neighborhood', 'year', 'data_type', 'absolute_cases', 'frequency_100k']
        print(transformed_data[sample_cols].head(10).to_string(index=False))
        
        # Show district breakdown
        print(f"\n🏛️ Neighborhoods (Districts) Mapping:")
        district_summary = transformed_data.groupby('neighborhood')['locality'].nunique().sort_values(ascending=False)
        for district, locality_count in district_summary.items():
            print(f"   {district}: {locality_count} localities")
        
        # Show schema validation
        print(f"\n📋 Schema Columns Created:")
        for col in ['area_id', 'locality', 'neighborhood', 'absolute_cases', 'frequency_100k', 'population_base']:
            non_null = transformed_data[col].notna().sum()
            print(f"   {col}: {non_null:,} non-null values")
            
    else:
        print("❌ Transformation failed")

if __name__ == "__main__":
    main()
