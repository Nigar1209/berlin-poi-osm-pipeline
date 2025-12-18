
#!/usr/bin/env python3
"""
Crime Atlas Data Extraction with Proper Crime Type Names
Gets the actual German crime type names from the headers
"""

import pandas as pd
from pathlib import Path

def get_crime_type_names(file_path, sheet_name):
    """Extract the actual crime type names from sheet headers"""
    try:
        # Read the header row (row 4, index 3) to get crime names
        df_header = pd.read_excel(file_path, sheet_name=sheet_name, 
                                skiprows=3, nrows=1)
        
        crime_names = {}
        for i, col in enumerate(df_header.columns):
            if i >= 2:  # Skip area_id and area_name columns
                crime_name = str(df_header.iloc[0, i])
                if pd.notna(crime_name) and crime_name.strip():
                    # Clean the crime name
                    clean_name = crime_name.replace('\n', ' ').replace('  ', ' ').strip()
                    crime_names[f'crime_type_{i}'] = clean_name
        
        return crime_names
        
    except Exception as e:
        print(f"   ⚠️ Could not extract crime names: {e}")
        return {}

def extract_with_proper_names(file_path, sheet_name, data_type):
    """Extract data with proper crime type column names"""
    
    year = int(sheet_name.split('_')[1])
    print(f"📊 Processing {sheet_name} ({data_type}, {year})")
    
    try:
        # First get the crime type names
        crime_names = get_crime_type_names(file_path, sheet_name)
        print(f"   🏷️ Found {len(crime_names)} crime types")
        
        # Read the actual data
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=4)  # Skip 4 rows to get past headers
        
        # Set up column names
        new_columns = ['area_id', 'area_name']
        for i in range(2, len(df.columns)):
            col_key = f'crime_type_{i}'
            if col_key in crime_names:
                new_columns.append(crime_names[col_key])
            else:
                new_columns.append(f'unknown_crime_{i}')
        
        df.columns = new_columns[:len(df.columns)]
        
        # Clean data
        df_clean = df.dropna(how='all')
        df_clean = df_clean[df_clean['area_id'].notna()]
        df_clean = df_clean[df_clean['area_id'] != '']
        df_clean['area_id'] = df_clean['area_id'].astype(str).str.strip()
        
        # Remove header remnants
        df_clean = df_clean[~df_clean['area_id'].str.contains('LOR-Schlüssel|Unnamed', na=False)]
        
        # Add metadata
        df_clean = df_clean.copy()
        df_clean['year'] = year
        df_clean['data_type'] = data_type
        
        print(f"   ✅ Extracted {len(df_clean)} rows with proper crime names")
        
        # Show sample crime types
        crime_cols = [col for col in df_clean.columns if col not in ['area_id', 'area_name', 'year', 'data_type']]
        print(f"   🚨 Crime types: {crime_cols[:3]}...")
        
        return df_clean
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    file_path = Path("sources/crime_atlas/kriminalitaetsatlas_2015-2024.xlsx")
    
    print("🔄 Extracting Crime Atlas Data with Proper Names")
    print("=" * 60)
    
    output_dir = Path("transformed_data")
    output_dir.mkdir(exist_ok=True)
    
    # Test with 2024 data
    test_data = []
    
    print(f"\n--- Processing 2024 Data ---")
    
    # Cases data
    cases_df = extract_with_proper_names(file_path, "Fallzahlen_2024", "cases")
    if cases_df is not None:
        test_data.append(cases_df)
    
    # Frequency data  
    freq_df = extract_with_proper_names(file_path, "HZ_2024", "frequency")
    if freq_df is not None:
        test_data.append(freq_df)
    
    if test_data:
        combined_df = pd.concat(test_data, ignore_index=True)
        
        # Save to CSV
        output_file = output_dir / "crime_atlas_with_names.csv"
        combined_df.to_csv(output_file, index=False)
        
        print(f"\n🎉 SUCCESS!")
        print(f"📁 Output: {output_file}")
        print(f"📊 Total rows: {len(combined_df):,}")
        print(f"🏛️ Areas: {combined_df['area_name'].nunique()}")
        
        # Show actual crime type names
        crime_cols = [col for col in combined_df.columns 
                     if col not in ['area_id', 'area_name', 'year', 'data_type']]
        print(f"\n🚨 Actual Crime Types Found:")
        for i, crime in enumerate(crime_cols[:10], 1):
            print(f"   {i:2d}. {crime}")
        
        if len(crime_cols) > 10:
            print(f"   ... and {len(crime_cols) - 10} more")
            
        # Show sample data
        print(f"\n📋 Sample data:")
        sample_cols = ['area_id', 'area_name', crime_cols[0], 'year', 'data_type']
        print(combined_df[sample_cols].head())
        
    else:
        print("❌ No data extracted")

if __name__ == "__main__":
    main()
