
#!/usr/bin/env python3
"""
Consolidate Data Structure - Simple Merge Approach
Use straightforward filtering and merging instead of pivot
"""

import pandas as pd
from pathlib import Path

def consolidate_data_structure():
    """Consolidate cases and frequency data using simple merge approach"""
    
    print("🔄 Consolidating Data Structure (Simple Approach)")
    print("=" * 50)
    
    # Load current data
    input_file = Path("transformed_data/berlin_crime_statistics_complete_schema.csv")
    df = pd.read_csv(input_file)
    
    print(f"📊 Input records: {len(df):,}")
    print(f"📋 Data types: {df['data_type'].value_counts().to_dict()}")
    
    # Step 1: Get cases data
    cases_df = df[df['data_type'] == 'cases'].copy()
    print(f"📊 Cases records: {len(cases_df):,}")
    
    # Step 2: Get frequency data  
    frequency_df = df[df['data_type'] == 'frequency'].copy()
    print(f"📊 Frequency records: {len(frequency_df):,}")
    
    # Step 3: Prepare cases data (keep absolute_cases, drop frequency_100k)
    cases_clean = cases_df[[
        'area_id', 'locality', 'neighborhood', 'year',
        'crime_type_german', 'crime_type_english', 'category',
        'absolute_cases', 'population_base', 'severity_weight'
    ]].copy()
    
    # Rename absolute_cases to total_number_cases
    cases_clean = cases_clean.rename(columns={'absolute_cases': 'total_number_cases'})
    
    # Step 4: Prepare frequency data (keep only frequency_100k)
    frequency_clean = frequency_df[[
        'area_id', 'locality', 'neighborhood', 'year',
        'crime_type_german', 'crime_type_english', 'frequency_100k'
    ]].copy()
    
    # Step 5: Merge cases and frequency data
    merge_keys = ['area_id', 'locality', 'neighborhood', 'year', 
                  'crime_type_german', 'crime_type_english']
    
    df_merged = pd.merge(
        cases_clean,
        frequency_clean,
        on=merge_keys,
        how='inner'  # Inner join to ensure we have both cases and frequency
    )
    
    print(f"📊 Merged records: {len(df_merged):,}")
    
    # Step 6: Final column order
    final_columns = [
        'area_id', 'locality', 'neighborhood', 'year',
        'crime_type_german', 'crime_type_english', 'category',
        'total_number_cases', 'frequency_100k', 'population_base', 'severity_weight'
    ]
    
    df_final = df_merged[final_columns]
    df_final = df_final.sort_values(['year', 'area_id', 'crime_type_english'])
    
    return df_final

def main():
    consolidated_data = consolidate_data_structure()
    
    if consolidated_data is not None and len(consolidated_data) > 0:
        # Save final dataset
        output_file = Path("transformed_data/berlin_crime_statistics_final.csv")
        consolidated_data.to_csv(output_file, index=False)
        
        print(f"\n🎉 DATA STRUCTURE CONSOLIDATED!")
        print(f"📁 Output: {output_file}")
        print(f"📊 Final records: {len(consolidated_data):,}")
        print(f"📉 Reduction: {((55233 - len(consolidated_data)) / 55233 * 100):.1f}% (combined cases+frequency)")
        
        # Show final structure
        print(f"\n📋 FINAL SCHEMA ({len(consolidated_data.columns)} columns):")
        for i, col in enumerate(consolidated_data.columns, 1):
            non_null = consolidated_data[col].notna().sum()
            print(f"   {i:2d}. {col:<25} | {non_null:>7,} non-null")
        
        # Sample data
        print(f"\n📊 Sample Data:")
        sample_cols = ['area_id', 'locality', 'year', 'total_number_cases', 'frequency_100k']
        sample = consolidated_data[sample_cols].head(5)
        print(sample.to_string(index=False))
        
        # Validation checks
        print(f"\n✅ Validation:")
        unique_combinations = consolidated_data[['area_id', 'year', 'crime_type_english']].drop_duplicates()
        print(f"   Unique area-year-crime combinations: {len(unique_combinations):,}")
        print(f"   Expected: ~{consolidated_data['area_id'].nunique() * consolidated_data['year'].nunique() * consolidated_data['crime_type_english'].nunique():,}")
        
    else:
        print("❌ Consolidation failed - no data produced")

if __name__ == "__main__":
    main()
