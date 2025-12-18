"""
Data Loader Module - Simple & Smart Data Loading

 Philosophy: "Simple things should be simple!"

This module provides SmartAutoDataLoader - an intelligent data loader that:
- Automatically detects file format, encoding, delimiters
- Finds and parses datetime columns automatically  
- Provides comprehensive reporting and error handling
- Works with just one line of code: loader.load("file.csv")

Example:
    >>> from db_population_utils.data_loader import SmartAutoDataLoader
    >>> loader = SmartAutoDataLoader(verbose=True)
    >>> df = loader.load("data.csv")  # Everything automatic!
"""

__version__ = "1.0.0"
__author__ = "Data Pool Team"

# Core imports
try:
    from .smart_auto_data_loader import SmartAutoDataLoader, LoadReport
    
    # Backward compatibility with old complex API
    DataLoader = SmartAutoDataLoader  # For legacy code
    
    # Export the main classes
    __all__ = [
        "SmartAutoDataLoader",  # Primary class
        "LoadReport",           # Result reporting
        "DataLoader",           # Legacy compatibility
    ]
    
except ImportError as e:
    # Graceful fallback if dependencies missing
    print(f"Warning: Could not import SmartAutoDataLoader: {e}")
    __all__ = []

# Module metadata
__doc__ = """
Simple Smart Data Loading

The SmartAutoDataLoader automatically handles:
✅ Format detection (CSV, Excel, JSON)
✅ Encoding detection (UTF-8, Latin-1, etc.)  
✅ Delimiter detection (comma, semicolon, tab)
✅ DateTime parsing and conversion
✅ Comprehensive error handling and reporting

Key Features:
- One-line loading: loader.load("file.csv")
- Full automation: no manual configuration needed
- Intelligent detection: finds dates, encodings, formats
- Detailed reporting: knows what it did and why
- Error recovery: handles problematic files gracefully

Usage:
    from db_population_utils.data_loader import SmartAutoDataLoader
    
    loader = SmartAutoDataLoader(verbose=True)
    df = loader.load("your_data.csv")
    
That's it! Everything else happens automatically.
"""