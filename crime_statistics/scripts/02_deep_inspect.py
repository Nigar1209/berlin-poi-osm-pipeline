
#!/usr/bin/env python3
"""
Deep Crime Atlas Data Inspection
Examines actual data structure with proper header handling
"""

import pandas as pd
from pathlib import Path

def deep_inspect_sheet(file_path, sheet_name):
    """Deeply inspect a specific sheet with different header rows"""
    print(f"\n🔍 Deep inspection of '{sheet_name}'")
    print("-" * 50)
    
    try:
        # Try reading with different header rows to find the actual data
        for skip_rows in range(0, 8):
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, 
                                 skiprows=skip_rows, nrows=10)
                
                if not df.empty and not all(col.startswith('Unnamed') for col in df.columns):
                    print(f"✅ Found data starting at row {skip_rows + 1}")
                    print(f"   Columns: {list(df.columns)}")
                    print(f"   Shape: {df.shape}")
                    print("   Sample data:")
                    print(df.head(3).to_string(index=False))
                    return skip_rows
                    
            except Exception:
                continue
                
        # If no good headers found, show raw content
        print("⚠️ No clear headers found. Raw content:")
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, nrows=15)
        for i, row in df_raw.iterrows():
            print(f"   Row {i}: {list(row.values)}")
            
    except Exception as e:
        print(f"❌ Error reading sheet: {e}")
    
    return None

def main():
    file_path = Path("sources/crime_atlas/kriminalitaetsatlas_2015-2024.xlsx")
    
    print("🔍 Deep Crime Atlas Data Analysis")
    print("=" * 60)
    
    # Focus on data sheets only
    sheets_to_check = ['Fallzahlen_2023', 'HZ_2023', 'Fallzahlen_2024']
    
    for sheet in sheets_to_check:
        deep_inspect_sheet(file_path, sheet)

if __name__ == "__main__":
    main()
