# Smart Data Loader

 **Philosophy: "Simple things should be simple!"**

SmartAutoDataLoader - intelligent data loading that works automatically without complex configuration.

## Quick Start

```python
from db_population_utils.data_loader import SmartAutoDataLoader

# Create loader
loader = SmartAutoDataLoader(verbose=True)

# Load any file - everything automatic!
df = loader.load("data.csv")
```

That's it! No configuration needed. The loader automatically:
- ✅ Detects file format (CSV, Excel, JSON)
- ✅ Finds the right encoding (UTF-8, Latin-1, etc.)
- ✅ Discovers delimiters (comma, semicolon, tab)
- ✅ Identifies and parses datetime columns
- ✅ Provides comprehensive reporting
- ✅ Handles errors gracefully


```

### ✅ The Simple Way (2 lines, works automatically)
```python
loader = SmartAutoDataLoader(verbose=True)
df = loader.load("data.csv")  # Handles everything automatically!
```

## Features

SmartAutoDataLoader implements all 10 essential methods:

### Loading Functions
1. **`load(file_path)`** - Universal loading with auto-detection
2. **`load_csv(file_path)`** - Optimized CSV loading
3. **`load_excel(file_path)`** - Excel file support
4. **`load_json(file_path)`** - JSON/JSONL support
5. **`parse_datetimes(df)`** - Intelligent datetime parsing

### Detection Functions  
6. **`detect_format(file_path)`** - Automatic format detection
7. **`detect_encoding(file_path)`** - Smart encoding detection
8. **`sniff_csv_params(file_path)`** - CSV parameter discovery

### Analysis & Reporting
9. **`estimate_memory_usage(file_path)`** - Memory requirements prediction
10. **`build_report()`** - Comprehensive loading reports
11. **`detect_time_columns(df)`** - Automatic datetime column detection

## Real Examples

### CSV with Automatic Detection
```python
loader = SmartAutoDataLoader(verbose=True)
df = loader.load("sales_data.csv")

# Output:
# 🎯 SmartAutoDataLoader ready!
# 🎯 Loading file: sales_data.csv
# 🔍 Format detected: csv
# 📊 Loading CSV file...
# 🔤 Encoding detected: utf-8
# 🗓️ Searching for date columns...
#    📅 Found date columns: ['order_date', 'ship_date']
# ✅ CSV loaded: 10000 rows, 8 columns
```

## API Reference

### SmartAutoDataLoader Class

```python
class SmartAutoDataLoader:
    def __init__(self, verbose: bool = False):
        """Initialize smart data loader.
        
        Args:
            verbose: Enable detailed logging
        """
    
    def load(self, file_path: str) -> pd.DataFrame:
        """Universal file loading with auto-detection.
        
        Automatically detects format, encoding, delimiters, and dates.
        """
    
    def build_report(self) -> LoadReport:
        """Get comprehensive loading report."""
```

## Why SmartAutoDataLoader?

###  **Automatic Everything**
- No manual encoding/delimiter specification
- No complex configuration objects
- No trial-and-error loading

###  **Intelligent Detection**
- Learns from file content, not just extensions
- Handles edge cases and problematic files
- Provides detailed feedback on what was detected

###  **Robust Error Handling**  
- Graceful fallbacks for encoding issues
- Recovery strategies for malformed data
- Comprehensive error reporting

---

**Built with ❤️ for data scientists who want to focus on analysis, not file loading hassles.**