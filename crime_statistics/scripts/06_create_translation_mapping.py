
#!/usr/bin/env python3
"""
Create German-English Crime Type Translation Mapping
Maps German crime types to English equivalents for database storage
"""

import pandas as pd
from pathlib import Path

def create_crime_translation_mapping():
    """Create comprehensive German-English crime type mapping"""
    
    # Define the translation mapping based on what we found
    translation_mapping = {
        # German Name -> English Name, Category, Severity Weight
        'Straftaten -insgesamt-': {
            'english': 'Total Crimes', 
            'category': 'Overall', 
            'severity': 1.0,
            'description': 'Total of all reported crimes'
        },
        'Raub': {
            'english': 'Robbery', 
            'category': 'Violent Crime', 
            'severity': 4.0,
            'description': 'Robbery and theft with violence or threat'
        },
        'Straßenraub, Handtaschen-raub': {
            'english': 'Street Robbery', 
            'category': 'Violent Crime', 
            'severity': 4.5,
            'description': 'Street robbery and purse snatching'
        },
        'Körper-verletzungen -insgesamt-': {
            'english': 'Assault Total', 
            'category': 'Violent Crime', 
            'severity': 3.5,
            'description': 'Total assault and bodily harm offenses'
        },
        'Gefährl. und schwere Körper-verletzung': {
            'english': 'Serious Assault', 
            'category': 'Violent Crime', 
            'severity': 4.5,
            'description': 'Dangerous and serious bodily harm'
        },
        'Freiheits-beraubung, Nötigung, Bedrohung, Nachstellung': {
            'english': 'Coercion and Threats', 
            'category': 'Violent Crime', 
            'severity': 3.0,
            'description': 'Deprivation of liberty, coercion, threats, stalking'
        },
        'Diebstahl -insgesamt-': {
            'english': 'Theft Total', 
            'category': 'Property Crime', 
            'severity': 2.0,
            'description': 'Total theft offenses'
        },
        'Diebstahl von Kraftwagen': {
            'english': 'Vehicle Theft', 
            'category': 'Property Crime', 
            'severity': 3.0,
            'description': 'Motor vehicle theft'
        },
        'Diebstahl an/aus Kfz': {
            'english': 'Theft from Vehicles', 
            'category': 'Property Crime', 
            'severity': 2.5,
            'description': 'Theft from or of vehicle parts'
        },
        'Fahrrad- diebstahl': {
            'english': 'Bicycle Theft', 
            'category': 'Property Crime', 
            'severity': 1.5,
            'description': 'Bicycle theft'
        },
        'Wohnraum- einbruch': {
            'english': 'Residential Burglary', 
            'category': 'Property Crime', 
            'severity': 3.5,
            'description': 'Breaking and entering into residential properties'
        },
        'Branddelikte -insgesamt-': {
            'english': 'Arson Total', 
            'category': 'Property Crime', 
            'severity': 4.0,
            'description': 'Total arson and fire-related offenses'
        },
        'Brand- stiftung': {
            'english': 'Arson', 
            'category': 'Property Crime', 
            'severity': 4.5,
            'description': 'Intentional arson'
        },
        'Sach-beschädigung -insgesamt-': {
            'english': 'Property Damage Total', 
            'category': 'Property Crime', 
            'severity': 1.5,
            'description': 'Total property damage offenses'
        },
        'Sach-beschädigung durch Graffiti': {
            'english': 'Graffiti Vandalism', 
            'category': 'Property Crime', 
            'severity': 1.0,
            'description': 'Property damage through graffiti'
        },
        'Rauschgift-delikte': {
            'english': 'Drug Crimes', 
            'category': 'Drug Offense', 
            'severity': 2.5,
            'description': 'Drug-related offenses'
        },
        'Kieztaten': {
            'english': 'Neighborhood Crimes', 
            'category': 'Public Order', 
            'severity': 2.0,
            'description': 'Local neighborhood disturbances and minor crimes'
        }
    }
    
    return translation_mapping

def save_translation_files():
    """Save translation mapping in multiple formats"""
    
    print("🔄 Creating Crime Type Translation Mapping")
    print("=" * 50)
    
    mapping = create_crime_translation_mapping()
    
    # Create DataFrame for easy handling
    translation_data = []
    for german_name, info in mapping.items():
        translation_data.append({
            'german_name': german_name,
            'english_name': info['english'],
            'category': info['category'],
            'severity_weight': info['severity'],
            'description': info['description'],
            'public_safety_relevance': True
        })
    
    translation_df = pd.DataFrame(translation_data)
    
    # Create output directory
    output_dir = Path("transformed_data")
    output_dir.mkdir(exist_ok=True)
    
    # Save as CSV
    csv_file = output_dir / "crime_type_translations.csv"
    translation_df.to_csv(csv_file, index=False)
    
    # Save as JSON for scripts
    import json
    json_file = output_dir / "crime_type_translations.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created translation mapping files:")
    print(f"📊 CSV: {csv_file}")
    print(f"📋 JSON: {json_file}")
    print(f"🚨 Crime types mapped: {len(translation_df)}")
    
    # Show summary by category
    print(f"\n📈 Crime Types by Category:")
    category_counts = translation_df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"   {category}: {count} types")
    
    # Show sample translations
    print(f"\n🔤 Sample Translations:")
    for i, row in translation_df.head(5).iterrows():
        print(f"   {row['german_name']} → {row['english_name']}")
    
    return translation_df

def main():
    save_translation_files()

if __name__ == "__main__":
    main()
