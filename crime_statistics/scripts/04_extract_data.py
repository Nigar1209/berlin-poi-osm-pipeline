
#!/usr/bin/env python3
"""
Crime Atlas Data Extraction Script
Extracts clean data from all sheets with proper headers
"""

import pandas as pd
from pathlib import Path
import os

def extract_sheet_data(file_path, sheet_name, data_type):
    """Extract data from a specific sheet"""
    
    # Extract year from sheet name (e.g., 'Fallzahlen_2024' -> 2024)
    year = int(sheet_name.split('_')[1])
    
    print(f"📊 Processing {sheet_name} ({data_type}, {year})")
    
    try:
        # Read data starting from row 4 (where headers are)
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=3)
        
        # Clean column names
        cleaned_columns = []
        for col in df.columns:
            if 'LOR-Schlüssel' in str(col):
                cleaned_columns.append('area_id')
            elif 'Bezeichnung' in str(col):
                cleaned_columns.append('area_name')
            else:
                # Keep original German names for crime types
                cleaned_name = str(col).replace('\n', ' ').replace('  ', ' ').strip()
                cleaned_columns.append(cleaned_name)
        
        df.columns = cleaned_columns
        
        # Remove empty rows
        df = df.dropna(subset=['area_id'])
        
        # Add metadata columns
        df['year'] = year
        df['data_type'] = data_type  # 'cases' or 'frequency'
        
        print(f"   ✅ Extracted {len(df)} rows")
        return df
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    file_path = Path("sources/crime_atlas/kriminalitaetsatlas_2015-2024.xlsx")
    
    print("🔄 Extracting Crime Atlas Data")
    print("=" * 50)
    
    # Create output directory
    output_dir = Path("transformed_data")
    output_dir.mkdir(exist_ok=True)
    
    all_data = []
    
    # Process all years (2015-2024)
    years = range(2015, 2025)
    
    for year in years:
        # Extract case numbers (Fallzahlen)
        cases_sheet = f"Fallzahlen_{year}"
        cases_df = extract_sheet_data(file_path, cases_sheet, 'cases')
        if cases_df is not None:
            all_data.append(cases_df)
        
        # Extract frequency numbers (HZ)
        freq_sheet = f"HZ_{year}"
        freq_df = extract_sheet_data(file_path, freq_sheet, 'frequency')
        if freq_df is not None:
            all_data.append(freq_df)
    
    # Combine all data
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Save to CSV
        output_file = output_dir / "crime_atlas_extracted.csv"
        combined_df.to_csv(output_file, index=False)
        
        print(f"\n✅ Successfully extracted data!")
        print(f"📁 Output: {output_file}")
        print(f"📊 Total rows: {len(combined_df):,}")
        print(f"🗓️ Years: {sorted(combined_df['year'].unique())}")
        print(f"📋 Data types: {list(combined_df['data_type'].unique())}")
        print(f"🏛️ Areas: {combined_df['area_name'].nunique()} unique areas")
        
        # Show sample
        print(f"\n📋 Sample data:")
        print(combined_df[['area_id', 'area_name', 'year', 'data_type']].head())
        
    else:
        print("❌ No data extracted")

if __name__ == "__main__":
    main()
