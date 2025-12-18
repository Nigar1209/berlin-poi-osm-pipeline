
#!/usr/bin/env python3
"""
Full Crime Atlas Data Inspection
Examines the complete structure and finds where data actually starts
"""

import pandas as pd
from pathlib import Path

def find_actual_data(file_path, sheet_name):
    """Find where the actual data starts in a sheet"""
    print(f"\n🔍 Finding actual data in '{sheet_name}'")
    print("-" * 50)
    
    try:
        # Read more rows to find data
        df_full = pd.read_excel(file_path, sheet_name=sheet_name, nrows=50)
        
        print(f"📊 Total readable rows: {len(df_full)}")
        
        # Look for rows with meaningful data (not all NaN/empty)
        for i, row in df_full.iterrows():
            row_values = [str(val) for val in row.values if pd.notna(val) and str(val).strip() != '']
            
            if len(row_values) > 5:  # Row with substantial data
                print(f"✅ Data found at row {i + 1}")
                print(f"   Content: {row_values[:10]}...")  # Show first 10 values
                
                # Try to read from this row as header
                if i > 0:
                    try:
                        df_from_here = pd.read_excel(file_path, sheet_name=sheet_name, 
                                                   skiprows=i, nrows=10)
                        if not df_from_here.empty:
                            print(f"   Columns from row {i + 1}: {list(df_from_here.columns)[:5]}...")
                            print(f"   Sample data:")
                            print(df_from_here.head(3).to_string(index=False))
                    except:
                        pass
                        
                break
        else:
            print("❌ No substantial data found in first 50 rows")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_sheet_dimensions(file_path, sheet_name):
    """Check the full dimensions of a sheet"""
    try:
        # Read without nrows limit to see full sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"📐 Sheet '{sheet_name}' full dimensions: {df.shape}")
        
        # Count non-empty rows
        non_empty_rows = df.dropna(how='all').shape[0]
        print(f"📊 Non-empty rows: {non_empty_rows}")
        
        return df.shape
        
    except Exception as e:
        print(f"❌ Error reading full sheet: {e}")
        return None

def main():
    file_path = Path("sources/crime_atlas/kriminalitaetsatlas_2015-2024.xlsx")
    
    print("🔍 Full Crime Atlas Data Analysis")
    print("=" * 60)
    
    # Check a few key sheets
    test_sheets = ['Fallzahlen_2024', 'HZ_2024', 'Fallzahlen_2023']
    
    for sheet in test_sheets:
        print(f"\n" + "="*60)
        check_sheet_dimensions(file_path, sheet)
        find_actual_data(file_path, sheet)

if __name__ == "__main__":
    main()
