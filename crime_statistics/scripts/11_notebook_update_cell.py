
#!/usr/bin/env python3
"""
Generate updated notebook cell showing the mentor feedback implementation
"""

notebook_cell_code = '''
# 🔄 MENTOR FEEDBACK IMPLEMENTATION
# Addressing mentor's requirements: separate locality from neighborhood (district)

print("🔄 Implementing Mentor Feedback")
print("=" * 50)

# Load current data and transform
import pandas as pd
from pathlib import Path

# Load existing transformed data
df = pd.read_csv("../transformed_data/berlin_crime_statistics_transformed_fixed.csv")
print(f"📊 Loaded {len(df):,} records")

# Step 1: Rename 'neighborhood' to 'locality'
df = df.rename(columns={'neighborhood': 'locality'})

# Step 2: Create district mapping function
def get_district_from_area_id(area_id):
    """Map area_id to parent district"""
    area_str = str(int(float(area_id)))
    
    if area_str.startswith('1'): return 'Mitte'
    elif area_str.startswith('2'): return 'Friedrichshain-Kreuzberg'
    elif area_str.startswith('3'): return 'Pankow'
    elif area_str.startswith('4'): return 'Charlottenburg-Wilmersdorf'
    elif area_str.startswith('5'): return 'Spandau'
    elif area_str.startswith('6'): return 'Steglitz-Zehlendorf'
    elif area_str.startswith('7'): return 'Tempelhof-Schöneberg'
    elif area_str.startswith('8'): return 'Neukölln'
    elif area_str.startswith('9'): return 'Treptow-Köpenick'
    else: return 'Unknown'

# Step 3: Create new neighborhood column with districts
df['neighborhood'] = df['area_id'].apply(get_district_from_area_id)

# Step 4: Add missing schema columns
df['absolute_cases'] = df.apply(lambda row: row['value'] if row['data_type'] == 'cases' else None, axis=1)
df['frequency_100k'] = df.apply(lambda row: row['value'] if row['data_type'] == 'frequency' else None, axis=1)
df['population_base'] = None

# Step 5: Reorder columns
column_order = [
    'area_id', 'locality', 'neighborhood', 'year', 'data_type',
    'crime_type_german', 'crime_type_english', 'category',
    'absolute_cases', 'frequency_100k', 'population_base',
    'value', 'severity_weight'
]
df_final = df[column_order]

# Save updated data
df_final.to_csv("../transformed_data/berlin_crime_statistics_final.csv", index=False)

print(f"✅ MENTOR FEEDBACK IMPLEMENTED!")
print(f"📊 Records: {len(df_final):,}")
print(f"🏘️ Localities: {df_final['locality'].nunique()}")
print(f"🏛️ Districts: {df_final['neighborhood'].nunique()}")

# Show sample of final structure
print(f"\\n📋 Final Data Structure:")
sample_cols = ['area_id', 'locality', 'neighborhood', 'year', 'absolute_cases', 'frequency_100k']
display(df_final[sample_cols].head(10))

# Show district mapping
print(f"\\n🏛️ District Distribution:")
district_counts = df_final.groupby('neighborhood')['locality'].nunique().sort_values(ascending=False)
for district, count in district_counts.items():
    print(f"   {district}: {count} localities")
'''

print("📝 Add this cell to your Jupyter notebook:")
print("=" * 60)
print(notebook_cell_code)
print("=" * 60)

if __name__ == "__main__":
    pass
