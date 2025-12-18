
# Crime Statistics Transformation Scripts

This directory contains all data processing scripts for the Berlin Crime Statistics layer.

## 📜 Script Inventory

### **Data Inspection Scripts**
- `01_inspect_data.py` - Initial Excel file structure analysis
- `02_deep_inspect.py` - Deep sheet-level inspection  
- `03_full_inspect.py` - Complete data discovery
- `09_inspect_current_data.py` - Current data pattern analysis

### **Data Extraction & Transformation**
- `04_extract_data.py` - Initial data extraction attempt
- `04_extract_data_fixed.py` - Fixed extraction with error handling
- `05_extract_with_crime_names.py` - Extraction with proper German crime names
- `07_transform_all_data.py` - Complete transformation pipeline
- `07_transform_all_data_fixed.py` - Fixed version with 'neighborhood' column

### **Translation & Mapping**
- `06_create_translation_mapping.py` - German-English crime type mapping

### **Schema Implementation**  
- `10_transform_complete_schema.py` - Complete schema with mentor feedback
- `11_consolidate_data_structure_simple.py` - Final data consolidation

### **Reporting & Analysis**
- `08_transformation_report.py` - Generates transformation summary
- `12_inspect_final_data.py` - Final data structure analysis

### **Interactive Analysis**
- `Berlin_Crime_Statistics_Transformation.ipynb` - Complete workflow notebook

## 🎯 Final Output

**Main Dataset**: `../transformed_data/berlin_crime_statistics_final.csv`
- 26,503 records (one per locality-year-crime combination)
- 11 columns with complete schema
- Ready for database insertion

## 📊 Usage

All scripts are designed to run from the `crime_statistics/` directory:

```bash
# Activate environment
source crime_env/bin/activate

# Run any script
python scripts/[script_name].py
For interactive analysis, use the Jupyter notebook in VS Code.
