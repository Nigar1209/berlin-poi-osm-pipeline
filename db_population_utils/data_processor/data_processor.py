from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable, Mapping, Tuple, Union
import logging
from dataclasses import dataclass

# Optional: keep pandas as a type-only import to avoid heavy deps at design time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd
    import numpy as np

logger = logging.getLogger(__name__)

@dataclass  # NEW
class ValidationResult:
    """Structured validation output"""
    passed: bool
    issues: List[str]
    stats: Dict[str, Any]  # NEW: Added basic statistics
    sample_failures: Dict[str, List[Any]]  # NEW: Example bad records

class DataProcessor:
    """
    Reusable, schema-agnostic preprocessing utilities.
    
    Key Design Updates:  # NEW SECTION
    - Now handles coordination with DataLoader's output
    - Added structured validation reporting
    - Supports both strict (exception) and soft (logging) modes
    """

    def __init__(self, strict_mode: bool = False):  # NEW
        """
        Args:
            strict_mode: If True, raises exceptions on validation failures
        """
        self.strict_mode = strict_mode
        self._validation_results = {}

    def standardize_columns(
        self,
        df: "pd.DataFrame",
        *,
        to_case: str = "lower",
        strip: bool = True,
        snake_case: bool = True,
        dedupe: bool = True,
        rename_map: Optional[Dict[str, str]] = None  # NEW
    ) -> "pd.DataFrame":
        """
        Return a copy with standardized column names.
        
        Changes:  # NEW
        - Added rename_map for explicit column renaming
        - Improved duplicate handling for production
        """
        raise NotImplementedError

    def coerce_types(
        self,
        df: "pd.DataFrame",
        type_map: Mapping[str, str],
        *,
        errors: str = "coerce",
        override_loader_types: bool = False  # NEW
    ) -> "pd.DataFrame":
        """
        Cast columns to specified dtypes.
        
        Changes:  # NEW
        - override_loader_types: If False, respects DataLoader's type parsing
        - Added timezone awareness for datetime columns
        """
        raise NotImplementedError

    def handle_nulls(
        self,
        df: "pd.DataFrame",
        strategy: Mapping[str, Any],
        *,
        drop_rows_if_any_null_in: Optional[List[str]] = None,
        interpolate_time_series: Optional[str] = None  # NEW
    ) -> "pd.DataFrame":
        """
        Handle nulls per-column using a strategy dict.
        
        Changes:  # NEW
        - Added time-series interpolation support
        - Improved statistical filling (median/mean) for sparse data
        """
        raise NotImplementedError

    def preprocess_loaded_data(  # NEW METHOD
        self,
        df: "pd.DataFrame",
        datetime_columns: Optional[List[str]] = None,
        type_hints: Optional[Dict[str, str]] = None
    ) -> "pd.DataFrame":
        """
        Standard pipeline for DataLoader output:
        1. Column standardization
        2. Type coercion
        3. Null handling
        
        Args:
            datetime_columns: Columns to parse as datetimes if not already parsed
            type_hints: Override DataLoader's type inference
        """
        raise NotImplementedError

    def validate(
        self,
        df: "pd.DataFrame",
        checks: Dict[str, Any],
        *,
        schema: Optional[Dict[str, str]] = None  # NEW
    ) -> ValidationResult:  # CHANGED return type
        """
        Run validation with enhanced reporting.
        
        Changes:  # NEW
        - Added schema validation against expected dtypes
        - Returns ValidationResult dataclass instead of dict
        - Samples failing records for debugging
        """
        raise NotImplementedError

    def run_pipeline(
        self,
        df: "pd.DataFrame",
        steps: List[Callable[["pd.DataFrame"], "pd.DataFrame"]],
        *,
        stop_on_error: bool = True  # NEW
    ) -> "pd.DataFrame":
        """
        Execute transformation pipeline.
        
        Changes:  # NEW
        - Added stop_on_error flag
        - Improved error context in logging
        """
        raise NotImplementedError

    def get_data_summary(self, df: "pd.DataFrame") -> Dict[str, Any]:  # NEW METHOD
        """
        Generate comprehensive data profile.
        Includes:
        - Memory usage
        - Null distribution
        - Basic statistics
        - Schema snapshot
        """
        raise NotImplementedError