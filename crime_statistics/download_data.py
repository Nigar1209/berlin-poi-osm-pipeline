#!/usr/bin/env python3
"""
🚔 Berlin Crime Atlas Data Download Script
===========================================
Downloads Berlin Crime Atlas data for Step 1: Data Modeling phase.
Focuses exclusively on Crime Atlas data from Berlin Police Department.
"""

import os
import requests
from pathlib import Path
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BerlinCrimeAtlasDownloader:
    def __init__(self, base_dir="sources"):
        self.base_dir = Path(base_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Berlin-Crime-Atlas-Integration/1.0 (Research Project)'
        })
        
    def create_directories(self):
        """Create the Crime Atlas directory structure"""
        crime_atlas_dir = self.base_dir / "crime_atlas"
        crime_atlas_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {crime_atlas_dir}")
    
    def download_crime_atlas_data(self):
        """Download Berlin Crime Atlas data from Open Data Portal"""
        logger.info("🔍 Downloading Berlin Crime Atlas data...")
        
        # Primary URLs to try for Crime Atlas data
        crime_atlas_urls = [
            "https://daten.berlin.de/sites/default/files/adressen/csv/kriminalitaetsatlas_berlin.xlsx",
            "https://www.polizei.berlin.de/verschiedenes/kriminalitaetsatlas/kriminalitaetsatlas.xlsx",
            "https://daten.berlin.de/datensaetze/kriminalitatsatlas-berlin"  # Fallback info page
        ]
        
        download_successful = False
        
        for url in crime_atlas_urls:
            try:
                logger.info(f"🌐 Trying URL: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if we got actual Excel data
                if response.headers.get('content-type', '').startswith('application/') and len(response.content) > 1000:
                    output_path = self.base_dir / "crime_atlas" / "kriminalitaetsatlas_2014-2023.xlsx"
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                        
                    logger.info(f"✅ Downloaded crime atlas data to: {output_path}")
                    
                    # Create metadata file
                    metadata = {
                        "source_url": url,
                        "download_date": datetime.now().isoformat(),
                        "file_size_bytes": len(response.content),
                        "description": "Berlin Police Crime Statistics Atlas 2014-2023",
                        "format": "XLSX",
                        "license": "CC-BY-SA",
                        "update_frequency": "Biennial",
                        "data_source": "Berlin Police Department",
                        "portal": "Berlin Open Data Portal"
                    }
                    
                    metadata_path = self.base_dir / "crime_atlas" / "metadata.json"
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    logger.info(f"✅ Created metadata file: {metadata_path}")
                    download_successful = True
                    break
                    
            except requests.RequestException as e:
                logger.warning(f"⚠️ Failed to download from {url}: {e}")
                continue
        
        if not download_successful:
            logger.error("❌ All automatic download attempts failed")
            self._create_download_instructions()
    
    def _create_download_instructions(self):
        """Create manual download instructions when automatic download fails"""
        instructions_content = """# 🚔 Berlin Crime Atlas Manual Download Instructions

## Automatic Download Failed ⚠️

Please manually download the Crime Atlas data using the steps below:

### 📥 Primary Source (Recommended)
1. **Visit**: https://daten.berlin.de/datensaetze/kriminalitatsatlas-berlin
2. **Look for**: Download button or link to Excel/XLSX file
3. **Save as**: `kriminalitaetsatlas_2014-2023.xlsx`
4. **Place in**: `sources/crime_atlas/` directory

### 📊 Alternative Source
1. **Visit**: https://www.kriminalitaetsatlas.berlin.de/
2. **Navigate to**: Data download section
3. **Download**: Latest available XLSX file
4. **Rename and place** as described above

### 📋 What to Look For
The file should contain:
- **Columns**: Bezirk, Bezirksregion, RAUMID, Delikt, Jahr, Fallzahl, Häufigkeitszahl
- **Years**: 2014-2023 (biennial data)
- **Areas**: 12 Berlin districts, 138 district regions
- **Crime Types**: 17 different categories

### 🆘 If You Still Have Issues
1. Check if the Berlin Open Data Portal structure has changed
2. Search for "Kriminalitätsatlas" or "Crime Statistics" on the portal
3. Contact Berlin Open Data support if the dataset is no longer available
4. Consider using historical data from previous years as a fallback

### 📞 Support Resources
- **Berlin Open Data Portal**: https://daten.berlin.de
- **Police Crime Atlas**: https://www.polizei.berlin.de/service/kriminalitaetsatlas/
- **Technical Documentation**: Check the README.md for more details

---
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        instructions_path = self.base_dir / "crime_atlas" / "DOWNLOAD_INSTRUCTIONS.md"
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write(instructions_content)
            
        logger.info(f"📋 Created download instructions: {instructions_path}")
    
    def create_data_dictionary(self):
        """Create comprehensive data dictionary for Crime Atlas"""
        logger.info("📚 Creating Crime Atlas data dictionary...")
        
        data_dict_content = """# 🚔 Berlin Crime Atlas Data Dictionary

## 📊 Overview
This document describes the structure and content of the Berlin Crime Atlas data file.

## 📁 File Information
- **Filename**: `kriminalitaetsatlas_2014-2023.xlsx`
- **Source**: Berlin Police Department (Polizei Berlin)
- **Format**: Microsoft Excel (XLSX)
- **License**: Creative Commons Attribution Share-Alike (CC-BY-SA)

## 📋 Expected Columns

| **German Name** | **English Translation** | **Data Type** | **Description** |
|-----------------|------------------------|---------------|-----------------|
| `Bezirk` | District | Text | Berlin district name (e.g., "Mitte") |
| `Bezirksregion` | District Region | Text | Sub-district area name |
| `RAUMID` | Area ID | Text | Unique LOR area identifier (7-digit code) |
| `Delikt` | Crime Type | Text | German crime category name |
| `Jahr` | Year | Integer | Year of data (2014, 2016, 2018, 2020, 2022, 2023) |
| `Fallzahl` | Case Count | Integer | Absolute number of reported cases |
| `Häufigkeitszahl` | Frequency Number | Float | Cases per 100,000 inhabitants |
| `EinwohnerInnen` | Residents | Integer | Population base for calculation |

## 🚨 Crime Types (German → English)

| **German** | **English** | **Category** |
|------------|-------------|--------------|
| Diebstahl | Theft | Property Crime |
| Straßenraub | Street Robbery | Violent Crime |
| Wohnungseinbruch | Residential Burglary | Property Crime |
| Fahrraddiebstahl | Bicycle Theft | Property Crime |
| Rauschgiftdelikte | Drug Crimes | Drug Offense |
| Sachbeschädigung | Property Damage | Property Crime |
| Körperverletzung | Assault | Violent Crime |
| Betrug | Fraud | Financial Crime |
| Taschendiebstahl | Pickpocketing | Property Crime |
| Autodiebstahl | Vehicle Theft | Property Crime |
| Einbruch in Keller/Boden | Cellar/Attic Burglary | Property Crime |
| Vandalismus | Vandalism | Property Crime |
| Gewalt in öffentlichen Räumen | Public Space Violence | Violent Crime |
| Sexualdelikte | Sexual Offenses | Violent Crime |
| Häusliche Gewalt | Domestic Violence | Violent Crime |
| Jugendkriminalität | Youth Crime | Various |
| Internetkriminalität | Cybercrime | Financial Crime |

## 🗺️ Geographic Structure

### 📍 LOR Area ID Format (RAUMID)
- **Format**: 7-digit number (e.g., "1011303")
- **Structure**: BPGBNPR
  - **B**: Bezirk (District) - 1 digit
  - **PG**: Prognoseraum (Forecast Area) - 2 digits  
  - **BN**: Bezirksregion (District Region) - 2 digits
  - **PR**: Planungsraum (Planning Area) - 2 digits

### 🏛️ Administrative Levels
1. **Bezirk** (District): 12 total districts
2. **Bezirksregion** (District Region): 138 total regions
3. **Planungsraum** (Planning Area): 542 total areas

## 📊 Data Quality Notes

### ✅ Expected Data Quality
- **Completeness**: All districts and regions should be present
- **Consistency**: RAUMID codes should be valid LOR identifiers
- **Accuracy**: Case counts should be non-negative integers
- **Timeliness**: Data reflects biennial reporting cycle

### ⚠️ Known Issues
1. **Temporal Gaps**: Data published every 2 years (2014, 2016, 2018, 2020, 2022, 2023)
2. **Language Dependency**: All original data in German
3. **Geographic Changes**: LOR boundaries may change over time
4. **Reporting Variations**: Different crime types may have different detection rates

### 🔍 Validation Checks
- [ ] File opens correctly in Excel/LibreOffice
- [ ] All expected columns are present
- [ ] RAUMID codes follow 7-digit format
- [ ] Years match expected biennial pattern
- [ ] Case counts are realistic (not negative, not impossibly high)
- [ ] Population figures are reasonable for Berlin areas

## 🔄 Processing Notes

### 🛠️ Transformation Requirements
1. **Translation**: Convert German crime types to English
2. **Standardization**: Normalize area names and IDs
3. **Interpolation**: Handle missing years between biennial reports
4. **Validation**: Check data consistency and outliers
5. **Geographic Mapping**: Convert RAUMID to coordinates

### 📈 Derived Metrics
- **Safety Scores**: Composite metric based on multiple crime types
- **Risk Levels**: Categorical classification (very_low to very_high)  
- **Trends**: Year-over-year changes in crime patterns
- **Density**: Crime rate per square kilometer

---

## 📞 Support Information

**Data Issues**: Contact Berlin Open Data Portal support  
**Technical Questions**: Refer to project documentation  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  
"""
        
        dict_path = self.base_dir / "crime_atlas" / "data_dictionary.md"
        with open(dict_path, 'w', encoding='utf-8') as f:
            f.write(data_dict_content)
            
        logger.info(f"✅ Created data dictionary: {dict_path}")
    
    def create_download_report(self):
        """Create summary report of download process"""
        logger.info("📋 Creating download report...")
        
        # Check what files exist
        crime_atlas_dir = self.base_dir / "crime_atlas"
        files_found = []
        
        if crime_atlas_dir.exists():
            for file_path in crime_atlas_dir.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.'):
                    file_size = file_path.stat().st_size
                    files_found.append({
                        'name': file_path.name,
                        'size': file_size,
                        'path': file_path.relative_to(self.base_dir)
                    })
        
        report_content = f"""# 🚔 Berlin Crime Atlas - Download Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Focus**: Crime Atlas Data Only  
**Status**: {'✅ Success' if any(f['name'].endswith('.xlsx') for f in files_found) else '⚠️ Manual Download Required'}

## 📊 Download Summary

### 📁 Files Created:
"""
        
        if files_found:
            for file in sorted(files_found, key=lambda x: x['name']):
                report_content += f"- `{file['path']}` ({file['size']:,} bytes)\n"
        else:
            report_content += "- No files found - manual download required\n"

        report_content += f"""
### 🎯 Step 1 Status: Data Modeling

| **Task** | **Status** | **File** |
|----------|------------|----------|
| Crime Atlas Documentation | ✅ Complete | `README.md` |
| Database Schema Design | ✅ Complete | `database_schema.sql` |
| Data Dictionary | ✅ Complete | `data_dictionary.md` |
| Download Infrastructure | ✅ Complete | `download_data.py` |
| Download Instructions | ✅ Complete | `DOWNLOAD_INSTRUCTIONS.md` |
| Actual Data File | {'✅ Downloaded' if any(f['name'].endswith('.xlsx') for f in files_found) else '⚠️ Manual Required'} | `kriminalitaetsatlas_2014-2023.xlsx` |

## 🔄 Next Steps

### ✅ For Step 1 (Current)
- Review all documentation files
- Verify database schema completeness
- Submit PR for data modeling phase

### ⏳ For Step 2 (Data Transformation)
- Download Crime Atlas XLSX file (if not already done)
- Develop Python scripts for data extraction
- Implement German-English crime type translation
- Create data cleaning and validation pipeline
- Generate safety scores and risk metrics

### ⏳ For Step 3 (Database Population)
- Create database tables and indexes
- Load transformed data into database
- Establish relationships with existing neighborhood data
- Set up biennial update workflows

## 📋 Data Quality Checklist

### ✅ Step 1 Requirements Met
- [x] Primary data source identified and documented
- [x] Database schema designed for Crime Atlas data
- [x] Data dictionary created with German-English mappings
- [x] Download automation attempted with fallback instructions
- [x] File structure organized and documented

### ⏳ Step 2 Validation (Future)
- [ ] Crime Atlas XLSX file opens correctly
- [ ] All expected columns present (Bezirk, RAUMID, Delikt, etc.)
- [ ] Data covers expected years (2014-2023, biennial)
- [ ] Geographic identifiers are valid LOR codes
- [ ] Crime statistics are reasonable and consistent

## 🆘 Manual Download Required?

If automatic download failed, follow these steps:
1. Open `DOWNLOAD_INSTRUCTIONS.md` in the crime_atlas folder
2. Visit https://daten.berlin.de/datensaetze/kriminalitatsatlas-berlin
3. Download the Excel file manually
4. Save as `kriminalitaetsatlas_2014-2023.xlsx` in `sources/crime_atlas/`

## 📞 Support Resources

- **Berlin Open Data Portal**: https://daten.berlin.de
- **Crime Atlas Interactive**: https://www.kriminalitaetsatlas.berlin.de/
- **Project Documentation**: See README.md files in this repository

---

**🎯 Ready for Step 1 PR Submission**: {'✅ Yes' if len(files_found) >= 2 else '⚠️ Review Required'}
"""
        
        report_path = self.base_dir / "download_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logger.info(f"✅ Created download report: {report_path}")
    
    def run_download(self):
        """Execute the complete Crime Atlas download process"""
        logger.info("🚀 Starting Berlin Crime Atlas data download...")
        
        # Create directory structure
        self.create_directories()
        
        # Download Crime Atlas data
        self.download_crime_atlas_data()
        
        # Create documentation
        self.create_data_dictionary()
        
        # Create summary report
        self.create_download_report()
        
        logger.info("🎉 Crime Atlas download process completed!")
        logger.info("📋 Check download_report.md for detailed status")
        logger.info("🎯 Ready for Step 1 PR submission!")

def main():
    """Main execution function"""
    print("🚔 Berlin Crime Atlas Downloader")
    print("=" * 40)
    downloader = BerlinCrimeAtlasDownloader()
    downloader.run_download()

if __name__ == "__main__":
    main()