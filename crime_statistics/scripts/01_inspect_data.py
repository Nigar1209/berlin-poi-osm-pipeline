
#!/usr/bin/env python3
"""
Crime Atlas Data Inspection Script
Examines the structure of the downloaded XLSX file
"""

import pandas as pd
import sys
from pathlib import Path

def inspect_crime_atlas_data():
    """Inspect the Crime Atlas XLSX file structure"""
    
    # Updated file path with actual years
    data_file = Path("sources/crime_atlas/kriminalitaetsatlas_2015-2024.xlsx")
    
    if not data_file.exists():
        print("❌ Crime Atlas file not found!")
        print(f"Expected: {data_file}")
        print("Please move the downloaded file to this location")
        return False
    
    print("🔍 Inspecting Crime Atlas Data Structure")
    print("=" * 50)
    
    try:
        print(f"📁 File: {data_file}")
        print(f"📊 File size: {data_file.stat().st_size:,} bytes")
        
        # Get sheet names
        excel_file = pd.ExcelFile(data_file)
        print(f"📋 Number of sheets: {len(excel_file.sheet_names)}")
        print(f"📝 Sheet names: {excel_file.sheet_names}")
        
        # Examine each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\n🔍 Examining sheet: '{sheet_name}'")
            try:
                df = pd.read_excel(data_file, sheet_name=sheet_name, nrows=10)
                print(f"   Columns ({len(df.columns)}): {list(df.columns)}")
                print(f"   Shape: {df.shape[0]} rows x {df.shape[1]} columns")
                
                if not df.empty:
                    print(f"   Sample data (first 3 rows):")
                    print(df.head(3).to_string(index=False))
                else:
                    print(f"   ⚠️ Sheet appears to be empty")
                    
            except Exception as sheet_error:
                print(f"   ❌ Error reading sheet: {sheet_error}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    inspect_crime_atlas_data()
