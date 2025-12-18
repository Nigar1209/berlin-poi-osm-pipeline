
#!/usr/bin/env python3
"""
Crime Atlas Data Extraction Script - Fixed Version
Extracts clean data from all sheets with proper error handling
"""

import pandas as pd
from pathlib import Path
import numpy as np

def extract_sheet_data(file_path, sheet_name, data_type):
    """Extract data from a specific sheet with better error handling"""
    
    # Extract year from sheet name
    year = int(sheet_name.split('_')[1])
    
    print(f"📊 Processing {sheet_name} ({data_type}, {year})")
    
    try:
        # Read data starting from row 4 (where headers are)
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=3)
        
        print(f"   📐 Original shape: {df.shape}")
        print(f"   📋 Original columns: {list(df.columns)[:3]}...")
        
        # Clean column names - be more careful
        new_columns = []
        for i, col in enumerate(df.columns):
            col_str = str(col)
            if i == 0:  # First column is area_id
                new_columns.append('area_id')
            elif i == 1:  # Second column is area_name
                new_columns.append('area_name')
            else:
                # Clean crime type names
                clean_name = col_str.replace('\n', ' ').replace('  ', ' ').strip()
                if clean_name.startswith('Unnamed'):
                    clean_name = f'crime_type_{i}'
                new_columns.append(clean_name)
        
        df.columns = new_columns
        
        # Remove completely empty rows
        df_clean = df.dropna(how='all')
        
        # Remove rows where area_id is NaN or empty
        df_clean = df_clean[df_clean['area_id'].notna()]
        df_clean = df_clean[df_clean['area_id'] != '']
        
        # Convert area_id to string and clean
        df_clean['area_id'] = df_clean['area_id'].astype(str).str.strip()
        
        # Remove rows with invalid area_ids (like header remnants)
        df_clean = df_clean[~df_clean['area_id'].str.contains('LOR-Schlüssel|Unnamed', na=False)]
        
        # Add metadata
        df_clean = df_clean.copy()
        df_clean['year'] = year
        df_clean['data_type'] = data_type
        
        print(f"   ✅ Cleaned to {len(df_clean)} valid rows")
        
        if len(df_clean) > 0:
            print(f"   📋 Sample area_ids: {list(df_clean['area_id'].head(3))}")
            return df_clean
        else:
            print(f"   ⚠️ No valid data rows found")
            return None
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    file_path = Path("sources/crime_atlas/kriminalitaetsatlas_2015-2024.xlsx")
    
    print("🔄 Extracting Crime Atlas Data (Fixed)")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("transformed_data")
    output_dir.mkdir(exist_ok=True)
    
    all_data = []
    
    # Test with just 2024 first
    test_years = [2024, 2023]
    
    for year in test_years:
        print(f"\n--- Processing Year {year} ---")
        
        # Extract case numbers
        cases_sheet = f"Fallzahlen_{year}"
        cases_df = extract_sheet_data(file_path, cases_sheet, 'cases')
        if cases_df is not None:
            all_data.append(cases_df)
        
        # Extract frequency numbers  
        freq_sheet = f"HZ_{year}"
        freq_df = extract_sheet_data(file_path, freq_sheet, 'frequency')
        if freq_df is not None:
            all_data.append(freq_df)
    
    # Process results
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Save to CSV
        output_file = output_dir / "crime_atlas_sample.csv"
        combined_df.to_csv(output_file, index=False)
        
        print(f"\n🎉 SUCCESS!")
        print(f"📁 Output: {output_file}")
        print(f"📊 Total rows: {len(combined_df):,}")
        print(f"🗓️ Years: {sorted(combined_df['year'].unique())}")
        print(f"📋 Data types: {list(combined_df['data_type'].unique())}")
        print(f"🏛️ Unique areas: {combined_df['area_name'].nunique()}")
        
        # Show sample data structure
        print(f"\n📋 Sample data:")
        sample_cols = ['area_id', 'area_name', 'year', 'data_type']
        print(combined_df[sample_cols].head(10))
        
        print(f"\n📊 Column names:")
        print(list(combined_df.columns))
        
    else:
        print("\n❌ No data extracted - check errors above")

if __name__ == "__main__":
    main()
