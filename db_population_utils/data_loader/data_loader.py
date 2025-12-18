# db_population_utils/data_loader.py

"""
DataLoader Module - Essential Data Loading with Quality Assessment

This module provides essential data loading capabilities with intelligent format
detection and quality assessment for core file formats based on requirements.

Key Design Philosophy:
    - **Intelligence First**: Automatic detection of formats, encodings, and structures
    - **Quality Focused**: Built-in data validation, profiling, and quality assessment (no transformation)
    - **Requirements**: Exactly 10 methods focusing on critical functionality
    - **Core Formats**: Only 3 essential file formats (CSV 95%, Excel 80%, JSON 70%)
    - **Integration Ready**: Seamless integration with DataProcessor and DBConnector
    - **Comprehensive Operations**: Single-call methods combining detection, loading, and reporting

Architecture Overview:
    ┌──────────────────┐    ┌─────────────────────┐    ┌──────────────────────┐
    │   Data Sources   │───→│    DataLoader       │───→│   Raw DataFrames     │
    │                  │    │                     │    │                      │
    │ • CSV Files      │    │ • Format Detection  │    │ • Data as-is         │
    │ • Excel Files    │    │ • Parameter Sniffing│    │ • Quality Reports    │
    │ • JSON Files     │    │ • Encoding Detection│    │ • Ready for          │
    │ • Local Paths    │    │ • Memory Estimation │    │   DataProcessor      │
    │                  │    │ • Comprehensive Ops │    │   or Analysis        │
    └──────────────────┘    └─────────────────────┘    └──────────────────────┘
                                       │
                            ┌─────────────────────┐
                            │   Intelligence      │
                            │                     │
                            │ • Encoding Detection│
                            │ • CSV Sniffing      │
                            │ • DateTime Parsing  │
                            │ • Quality Analysis  │
                            │ • Error Recovery    │
                            └─────────────────────┘

Requirements Implementation:
    ✓ Loading Functions (5): load(), load_csv(), load_excel(), load_json(), parse_datetimes()
    ✓ Detection Functions (3): detect_format(), detect_encoding(), sniff_csv_params()
    ✓ Performance (1): estimate_memory_usage()
    ✓ Reporting & Error Handling (2): build_report(), detect_time_columns()
    ✓ Total: 10 core methods + 3 comprehensive operations

Core Features:
    ✓ Essential loading operations (10 core methods)
    ✓ Comprehensive single-call operations (3 enhanced methods)
    ✓ Format detection and parameter sniffing
    ✓ Built-in error handling and recovery
    ✓ Memory estimation and optimization
    ✓ Quality assessment and reporting

Target Use Cases:
    1. **Data Ingestion**: Load raw data from various sources for processing
    2. **ETL Pipelines**: Extract data from files as first step in transformation workflows
    3. **Data Analysis**: Load files for exploratory analysis with quality checks
    4. **Data Validation**: Verify file data quality before database insertion

    Integration with DataProcessor & DBConnector:
    ```python
    # Complete data pipeline
    loader = DataLoader()
    processor = DataProcessor()  # Separate class for transformations
    connector = DBConnector()
    
    # Comprehensive loading with full reporting
    df_raw, report = loader.load_with_comprehensive_report("raw_data.csv")
    
    if report.data_quality.quality_score > 80:
        df_clean = processor.clean_data(df_raw)  # Processing in separate class
        success, db_report = connector.insert_dataframe_with_report(df_clean, "clean_data")
    ```

Format Support (Manager Priority Only):
    Format     │ Detection │ Memory Est │ Datetime │ Usage Priority │ Status
    ───────────┼───────────┼────────────┼──────────┼────────────────┼──────────
    CSV/TSV    │    ✓      │     ✓      │    ✓     │ 95% (CRITICAL) │ REQUIRED
    Excel      │    ✓      │     ✓      │    ✓     │ 80% (HIGH)     │ REQUIRED  
    JSON       │    ✓      │     ✓      │    ✓     │ 70% (MEDIUM)   │ REQUIRED


"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, Literal, Callable
from pathlib import Path
from enum import Enum
import logging
import time
import os

# Type-only imports to keep design stub lightweight
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd
    from io import IOBase

# Type definitions (Manager Requirements Only)
PathLike = Union[str, Path]
SourceLike = Union[PathLike, "IOBase"]  # Local files only per manager requirements
Kind = Literal["auto", "csv", "tsv", "excel", "json"]  # Only 3 core formats per manager
CompressionType = Literal["infer", "gzip", "bz2", "zip", None]  # Basic compression only


# -----------------------
# Core Enums
# -----------------------
class LoadStrategy(Enum):
    """Loading strategies for different scenarios."""
    MEMORY_EFFICIENT = "memory_efficient"
    PERFORMANCE = "performance" 
    ROBUST = "robust"


# -----------------------
# Core Support dataclasses
# -----------------------
@dataclass
class CsvParams:
    """Parameters for CSV/TSV loading with detection results."""
    delimiter: str = ","
    decimal: str = "."
    header: Optional[int] = 0
    encoding: Optional[str] = None
    quote_char: str = '"'
    escape_char: Optional[str] = None
    null_values: List[str] = field(default_factory=lambda: ['', 'NULL', 'null', 'NA', 'na'])
    skip_rows: int = 0
    # Detection confidence scores
    delimiter_confidence: float = 0.0
    encoding_confidence: float = 0.0


@dataclass
class ExcelParams:
    """Parameters for Excel file loading."""
    sheet: Union[str, int, Literal["auto"], None] = "auto"
    engine: Optional[str] = None
    header: Optional[Union[int, List[int]]] = 0
    # Detection results
    available_sheets: List[str] = field(default_factory=list)
    recommended_sheet: Optional[str] = None
    sheet_shapes: Dict[str, Tuple[int, int]] = field(default_factory=dict)


@dataclass
class JsonParams:
    """Parameters for JSON file loading."""
    record_path: Optional[Union[str, List[str]]] = None
    orient: Optional[str] = None
    # Detection results
    structure_type: str = "unknown"  # "flat", "nested", "array_of_objects"
    estimated_records: Optional[int] = None


@dataclass
class LoadOptions:
    """High-level overrides to control loading behavior across formats."""
    # Format detection
    kind: Kind = "auto"
    encoding: Optional[str] = None
    compression: CompressionType = "infer"
    
    # Performance options
    chunksize: Optional[int] = None
    nrows: Optional[int] = None
    low_memory: bool = True
    dtype_overrides: Optional[Dict[str, Any]] = None
    
    # CSV/TSV specific
    delimiter: Optional[str] = None
    decimal: Optional[str] = None
    header: Optional[Union[int, List[int]]] = None
    
    # Excel specific
    sheet: Union[str, int, Literal["auto"], None] = "auto"
    
    # JSON specific
    flatten_json: bool = True
    record_path: Optional[Union[str, List[str]]] = None
    
    # Datetime handling (Manager priority: parse_datetimes)
    date_columns: Optional[List[str]] = None
    detect_time_columns: bool = True
    infer_datetime_format: bool = True
    
    # Error handling
    on_bad_lines: str = "error"  # "error", "warn", "skip"
    error_tolerance: float = 0.0  # percentage of errors to tolerate
    
    # Memory and performance
    load_strategy: LoadStrategy = LoadStrategy.PERFORMANCE


@dataclass
class MemoryEstimate:
    """Memory usage estimation (Manager requirement)."""
    estimated_memory_mb: float
    recommended_chunksize: Optional[int] = None
    can_load_in_memory: bool = True
    memory_per_row_bytes: float = 0.0


@dataclass
class DataQualityReport:
    """Data quality assessment."""
    missing_data_ratio: float = 0.0
    duplicate_rows: int = 0
    unique_values_per_column: Dict[str, int] = field(default_factory=dict)
    data_types_detected: Dict[str, str] = field(default_factory=dict)
    quality_score: float = 0.0  # 0-100
    recommendations: List[str] = field(default_factory=list)


@dataclass
class LoadReport:
    """Comprehensive summary of loading operation (Manager requirement)."""
    # Basic info
    source: str
    kind: Kind
    load_strategy: LoadStrategy
    
    # Detection results
    encoding: Optional[str] = None
    compression_detected: Optional[str] = None
    csv_params: Optional[CsvParams] = None
    excel_params: Optional[ExcelParams] = None
    json_params: Optional[JsonParams] = None
    
    # Data characteristics  
    shape: Optional[Tuple[int, int]] = None
    columns_detected: List[str] = field(default_factory=list)
    data_types: Dict[str, str] = field(default_factory=dict)
    
    # Datetime processing (Manager priority)
    detected_time_cols: List[str] = field(default_factory=list)
    datetime_parsing_success_rate: Dict[str, float] = field(default_factory=dict)
    
    # Quality assessment
    data_quality: Optional[DataQualityReport] = None
    
    # Performance metrics
    load_time_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    rows_processed: int = 0
    processing_speed_rows_per_sec: float = 0.0
    
    # Issues and notes
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    
    # Source metadata
    file_size_bytes: Optional[int] = None
    source_accessible: bool = True


# -----------------------
# Custom Exceptions
# -----------------------
class DataLoaderError(Exception):
    """Base exception for DataLoader operations."""


class DetectionError(DataLoaderError):
    """Raised when automatic detection fails."""


class UnsupportedFormatError(DataLoaderError):
    """Raised when file format is not supported."""


class LoadingMemoryError(DataLoaderError):
    """Raised when estimated memory usage exceeds limits."""


# -----------------------
# DataLoader (EXACT Manager Requirements - 10 Methods)
# -----------------------
class DataLoader:
    """
    DataLoader — Essential data loading with intelligent detection and quality assessment.

    Purpose:
      Load tabular data from 3 core file formats (CSV, Excel, JSON) with:
        - Advanced format detection and parameter sniffing
        - Critical encoding detection for CSV files
        - Datetime parsing and detection
        - Data quality analysis and assessment (no transformation)
        - Memory-efficient processing
        - Comprehensive error handling and reporting

    Requirements Implementation (10 Core Methods):
      ✓ Loading Functions (5): load(), load_csv(), load_excel(), load_json(), parse_datetimes()
      ✓ Detection Functions (3): detect_format(), detect_encoding(), sniff_csv_params()
      ✓ Performance (1): estimate_memory_usage()
      ✓ Reporting & Error Handling (2): build_report(), detect_time_columns()

    Supported Formats:
      - CSV/TSV: 95% usage (CRITICAL) - Full parameter detection
      - Excel: 80% usage (HIGH) - Sheet detection and selection  
      - JSON: 70% usage (MEDIUM) - Structure flattening
    """

    def __init__(
        self,
        verbose: bool = True,
        max_memory_usage_gb: float = 4.0,
        default_encoding: str = 'utf-8',
        logger: Optional[logging.Logger] = None,
        load_strategy: LoadStrategy = LoadStrategy.PERFORMANCE,
    ):
        """
        Initialize essential DataLoader.
        
        Args:
            verbose: Enable detailed logging during operations
            max_memory_usage_gb: Maximum memory usage limit
            default_encoding: Default text encoding
            logger: Custom logger instance
            load_strategy: Default loading strategy
        """
        self.verbose = verbose
        self.max_memory_usage_gb = max_memory_usage_gb
        self.default_encoding = default_encoding
        self.logger = logger or logging.getLogger(__name__)
        self.load_strategy = load_strategy
        
        # Internal state for reporting
        self._current_report = None
        self._start_time = None
        
        if self.verbose:
            self.logger.info("DataLoader initialized with settings: ")

    # -----------------------
    # LOADING FUNCTIONS (5 methods - Manager Requirements)
    # -----------------------
    
    def load(
        self,
        source: SourceLike,
        *,
        kind: Kind = "auto",
        options: Optional[LoadOptions] = None,
    ) -> "pd.DataFrame":
        """
        Main loading method with automatic format detection.
        
        Manager Priority: Core loading functionality for all 3 supported formats.
        
        Args:
            source: Local file path or file-like object
            kind: Format type ('auto', 'csv', 'excel', 'json')
            options: Loading configuration options
            
        Returns:
            Raw DataFrame loaded as-is (no transformations applied)
            
        Raises:
            DataLoaderError: On loading failures
            UnsupportedFormatError: For unsupported formats
        """
        raise NotImplementedError

    def load_csv(
        self,
        source: SourceLike,
        *,
        params: Optional[CsvParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
        date_columns: Optional[List[str]] = None,
        chunksize: Optional[int] = None,
        encoding: Optional[str] = None,
        compression: CompressionType = "infer",
    ) -> Union["pd.DataFrame", Iterator["pd.DataFrame"]]:
        """
        CSV/TSV loader with advanced parameter detection.
        

        
        Args:
            source: CSV file path or file-like object
            params: CSV parameters (auto-detected if None)
            dtype_overrides: Custom data types for columns
            date_columns: Columns to parse as dates
            chunksize: Process in chunks (returns iterator)
            encoding: Text encoding (auto-detected if None)
            compression: Compression format
            
        Returns:
            DataFrame or iterator of DataFrames (if chunked)
        """
        raise NotImplementedError

    def load_excel(
        self,
        source: SourceLike,
        *,
        params: Optional[ExcelParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        """
        Excel loader with intelligent sheet selection.
        
        
        Args:
            source: Excel file path (.xlsx, .xls)
            params: Excel parameters (auto-detected if None)
            dtype_overrides: Custom data types for columns
            
        Returns:
            DataFrame from selected/detected sheet
        """
        raise NotImplementedError

    def load_json(
        self,
        source: SourceLike,
        *,
        params: Optional[JsonParams] = None,
        dtype_overrides: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        """
        JSON loader with advanced flattening.
        
        
        Args:
            source: JSON file path or file-like object
            params: JSON parameters (auto-detected if None)
            dtype_overrides: Custom data types for columns
            
        Returns:
            DataFrame with flattened JSON structure
        """
        raise NotImplementedError

    def parse_datetimes(
        self,
        df: "pd.DataFrame",
        cols: Optional[List[str]] = None,
        *,
        infer: bool = True,
        dayfirst: bool = False,
        errors: str = 'coerce',
        format: Optional[str] = None,
    ) -> "pd.DataFrame":
        """
        Parse datetime columns with intelligent detection and error handling.
        
        Priority: CRITICAL - "can cause lots of troubles and can be pretty common"
        
        Args:
            df: DataFrame with columns to parse
            cols: Specific columns to parse (if None, auto-detect)
            infer: Automatically infer datetime format
            dayfirst: Interpret first value as day
            errors: How to handle parsing errors ('raise', 'coerce', 'ignore')
            format: Explicit datetime format string
            
        Returns:
            DataFrame with parsed datetime columns
            
        Example:
            # Auto-detect and parse datetime columns
            df_parsed = loader.parse_datetimes(df)
            
            # Parse specific columns
            df_parsed = loader.parse_datetimes(df, cols=['created_at', 'updated_at'])
            
            # Custom format with error handling
            df_parsed = loader.parse_datetimes(df, cols=['date'], format='%Y-%m-%d', errors='coerce')
        """
        raise NotImplementedError

    # -----------------------
    # DETECTION FUNCTIONS (3 methods - Manager Requirements)
    # -----------------------
    
    def detect_format(self, source: SourceLike) -> Tuple[Kind, float]:
        """
        Auto-detect file format with confidence score.
        
        
        Args:
            source: File path or file-like object
            
        Returns:
            Tuple of (detected_format, confidence_score)
            
        Supported Detection:
            - CSV/TSV: By extension (.csv, .tsv) and content analysis
            - Excel: By extension (.xlsx, .xls) and file headers
            - JSON: By extension (.json) and structure validation
        """
        raise NotImplementedError

    def detect_encoding(
        self, 
        source: SourceLike, 
        *, 
        sample_size: int = 20000,
        confidence_threshold: float = 0.8
    ) -> Tuple[str, float]:
        """
        Critical encoding detection with confidence score.
        
        Priority: CRITICAL - "encoding might cause nasty problems, based on our experience, 
        so we definitely should have it, great job."
        
        Args:
            source: File path or file-like object
            sample_size: Number of bytes to sample for detection
            confidence_threshold: Minimum confidence for successful detection
            
        Returns:
            Tuple of (detected_encoding, confidence_score)
            
        Common Encodings Detected:
            - UTF-8, UTF-16, UTF-32
            - Latin1, CP1252, ISO-8859-1
            - Windows-1251, Windows-1252
        """
        raise NotImplementedError

    def sniff_csv_params(
        self, 
        source: SourceLike, 
        *, 
        sample_size: int = 20000
    ) -> CsvParams:
        """
        Auto-detect CSV parameters with advanced sniffing.
        
    
        
        Args:
            source: CSV file path or file-like object
            sample_size: Number of bytes to sample for detection
            
        Returns:
            CsvParams with detected parameters and confidence scores
            
        Detected Parameters:
            - Delimiter (comma, semicolon, tab, pipe)
            - Quote character
            - Header row position
            - Null value representations
        """
        raise NotImplementedError

    # -----------------------
    # PERFORMANCE (1 method - Manager Requirements)
    # -----------------------
    
    def estimate_memory_usage(
        self, 
        source: SourceLike, 
        *, 
        sample_ratio: float = 0.01
    ) -> MemoryEstimate:
        """
        Estimate memory requirements for loading large files.
        
        Priority: Essential for large file handling.
        
        Args:
            source: File path or file-like object
            sample_ratio: Ratio of file to sample for estimation
            
        Returns:
            MemoryEstimate with usage prediction and recommendations
            
        Provides:
            - Estimated memory usage in MB
            - Recommended chunk size for large files
            - Can-load-in-memory assessment
        """
        raise NotImplementedError

    # -----------------------
    # REPORTING & ERROR HANDLING (2 methods - Manager Requirements)
    # -----------------------
    
    def build_report(self) -> LoadReport:
        """
        Generate comprehensive load reports.
        
        Priority: Essential for monitoring and debugging.
        
        Returns:
            LoadReport with comprehensive loading metrics and analysis
            
        Report Contents:
            - Loading performance metrics
            - Data quality assessment
            - Detection results and confidence scores
            - Errors, warnings, and recommendations
        """
        raise NotImplementedError

    def detect_time_columns(
        self,
        df: "pd.DataFrame",
        *,
        hints: Optional[List[str]] = None,
        min_parse_rate: float = 0.8,
        sample_size: Optional[int] = None,
    ) -> List[str]:
        """
        Datetime detection - identify potential datetime columns.
        
       Priority: Essential for parse_datetimes() functionality.
        
        Args:
            df: DataFrame to analyze
            hints: Column name hints for datetime detection
            min_parse_rate: Minimum successful parse rate for detection
            sample_size: Number of rows to sample (None for all)
            
        Returns:
            List of column names likely to contain datetime data
            
        Detection Methods:
            - Column name patterns (date, time, created, updated, etc.)
            - Content pattern analysis
            - Successful parsing rate testing
        """
        raise NotImplementedError

    # -----------------------
    # COMPREHENSIVE SINGLE-CALL OPERATIONS (3 methods)
    # These combine multiple core methods for common workflows
    # -----------------------

    def load_with_comprehensive_report(
        self,
        source: SourceLike,
        *,
        kind: Kind = "auto",
        options: Optional[LoadOptions] = None,
        include_quality_analysis: bool = True,
        include_datetime_detection: bool = True,
    ) -> Tuple["pd.DataFrame", LoadReport]:
        """
        COMPREHENSIVE: Load data with full detection, quality analysis, and reporting.
        
        Combines: detect_format() + detect_encoding() + load() + detect_time_columns() + 
                  parse_datetimes() + analyze_data_quality() + build_report() + error handling
        
        Args:
            source: File path or file-like object
            kind: Format type or 'auto' for detection
            options: Loading configuration options
            include_quality_analysis: Perform data quality assessment
            include_datetime_detection: Detect and parse datetime columns
            
        Returns:
            Tuple of (loaded_dataframe, comprehensive_report)
            
        Manager Workflow:
            loader = DataLoader()
            df, report = loader.load_with_comprehensive_report("data.csv")
            
            print(f"✅ Loaded {report.shape[0]} rows, {report.shape[1]} columns")
            print(f"📊 Quality Score: {report.data_quality.quality_score}/100")
            print(f"⏱️  Load Time: {report.load_time_seconds:.2f}s")
            print(f"🕒 Datetime Columns: {report.detected_time_cols}")
        """
        raise NotImplementedError

    def load_csv_with_smart_detection(
        self,
        source: SourceLike,
        *,
        auto_fix_common_issues: bool = True,
        return_detection_details: bool = True,
    ) -> Tuple["pd.DataFrame", Dict[str, Any]]:
        """
        COMPREHENSIVE: CSV loading with smart detection and issue fixing.
        
        Combines: detect_encoding() + sniff_csv_params() + load_csv() + 
                  error recovery + issue detection + reporting
        
        Manager Priority: CRITICAL for 95% usage CSV format.
        
        Args:
            source: CSV file path or file-like object
            auto_fix_common_issues: Automatically fix common CSV issues
            return_detection_details: Return detailed detection information
            
        Returns:
            Tuple of (loaded_dataframe, detection_and_issues_report)
            
        Manager Workflow:
            df, details = loader.load_csv_with_smart_detection("messy_data.csv")
            
            print(f"📄 Detected delimiter: '{details['csv_params']['delimiter']}'")
            print(f"📝 Detected encoding: {details['encoding']['detected']}")
            print(f"🔧 Issues fixed: {details['issues_fixed']}")
        """
        raise NotImplementedError

    def load_with_fallback_strategies(
        self,
        source: SourceLike,
        *,
        max_attempts: int = 3,
        enable_error_recovery: bool = True,
    ) -> Tuple["pd.DataFrame", Dict[str, Any]]:
        """
        COMPREHENSIVE: Load data with multiple fallback strategies on failure.
        
        Combines: detect_format() + load() + error recovery + fallback strategies + 
                  partial loading + comprehensive error reporting
        
        Args:
            source: File path or file-like object
            max_attempts: Maximum number of fallback attempts
            enable_error_recovery: Enable partial data recovery on errors
            
        Returns:
            Tuple of (loaded_dataframe, recovery_report)
            
        Manager Workflow:
            df, recovery = loader.load_with_fallback_strategies("problematic_file.csv")
            
            print(f"📊 Final result: {recovery['final_status']}")
            print(f"🔄 Attempts made: {recovery['attempts_made']}")
            print(f"💾 Data recovered: {recovery['recovery_percentage']:.1f}%")
        """
        raise NotImplementedError

    # -----------------------
    # Private/Internal Methods
    # -----------------------
    
    def _analyze_data_quality(self, df: "pd.DataFrame") -> DataQualityReport:
        """Internal method for data quality analysis."""
        raise NotImplementedError

    def _detect_file_format(self, source: SourceLike) -> Kind:
        """Internal format detection logic for 3 supported formats."""
        raise NotImplementedError

    def _validate_source(self, source: SourceLike) -> bool:
        """Internal source validation."""
        raise NotImplementedError

    def _update_report(self, **kwargs) -> None:
        """Internal method to update loading report."""
        raise NotImplementedError

    def _handle_loading_error(
        self, 
        error: Exception, 
        source: SourceLike, 
        context: str
    ) -> None:
        """Internal error handling and logging."""
        raise NotImplementedError