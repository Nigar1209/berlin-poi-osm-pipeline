# db_population_utils/__init__.py

"""
Database Population Utilities Package

This package provides comprehensive utilities for database connection management,
data processing, and population operations across multiple database environments.

Architecture:
    DataLoader → DataProcessor → DBConnector ← DBPopulator
    
    Sequential Flow (→):
    - DataLoader: Load raw files with quality assessment
    - DataProcessor: Transform and clean data
    - DBConnector: Essential database infrastructure operations
    
    Infrastructure Usage (←):
    - DBPopulator: Uses DBConnector for complex business logic and relationships

Main Components:
- DBConnector: Advanced database connection management with pooling, monitoring, and comprehensive operations
- DBSettings: Configuration management for database connections  
- Comprehensive reporting classes for all database operations
- Custom exceptions for robust error handling

Key Features:
- Multi-environment support (ingestion/app targets)
- Connection pooling and health monitoring
- Comprehensive single-call operations with full reporting
- Built-in error handling and recovery mechanisms
- Infrastructure layer for other data processing components

Usage Examples:

Basic Usage:
    from db_population_utils import DBConnector, DBSettings
    
    # Quick setup from environment
    connector = create_connector_from_env()
    
    # Basic operations
    df = connector.fetch_df("SELECT * FROM users")
    connector.to_sql(df, "processed_users")

Comprehensive Operations:
    # Execute with full reporting
    rows, report = connector.execute_with_full_report(
        "UPDATE users SET status = %(status)s WHERE active = false",
        params={"status": "inactive"}
    )
    
    # Insert DataFrame with pre-checks and reporting
    success, report = connector.insert_dataframe_with_report(
        df, "new_table", schema="staging"
    )
    
    # Query with data profiling and reporting
    df, report = connector.query_to_dataframe_with_report(
        "SELECT * FROM sales WHERE date > %(date)s",
        params={"date": "2024-01-01"}
    )

Advanced Configuration:
    # Multi-environment setup
    ingestion_settings = DBSettings.from_env("PROD_INGESTION")
    app_settings = DBSettings.from_env("PROD_APP")
    
    connector = DBConnector(
        ingestion=ingestion_settings,
        app=app_settings,
        echo=True,
        pool_size=15
    )
    
    # Use different targets
    connector.to_sql(raw_df, "raw_data", target="ingestion")
    processed_df = connector.fetch_df("SELECT * FROM processed_data", target="app")

Integration with Data Pipeline:
    # Complete pipeline example
    from db_population_utils import create_connector_from_env
    
    # Setup infrastructure
    connector = create_connector_from_env(echo=True)
    
    # DataLoader → DataProcessor → DBConnector workflow
    # (DataLoader and DataProcessor would be separate components)
    
    # Step 1: Load data (DataLoader responsibility)
    # raw_df = loader.load("data.csv")
    
    # Step 2: Process data (DataProcessor responsibility)  
    # clean_df = processor.transform(raw_df)
    
    # Step 3: Store with comprehensive reporting
    success, report = connector.insert_dataframe_with_report(
        clean_df, "processed_data", schema="staging", if_exists="replace"
    )
    
    if success:
        print(f"Successfully inserted {report.rows_inserted} rows")
        if report.schema_created:
            print("Created new schema")
        if report.table_created:
            print("Created new table")
    else:
        print(f"Insert failed: {report.errors}")
"""

from .db_connector import (
    # Core classes
    DBConnector,
    DBSettings,
    
    # Report classes
    ExecutionReport,
    InsertionReport,
    QueryReport,
    
    # Type definitions
    Target,
    
    # Custom exceptions
    DBConnectionError,
    DBConfigurationError,
    DBOperationError,
)

# Package metadata
__version__ = "0.2.0"
__author__ = "Data Engineering Team"
__description__ = "Comprehensive database population utilities with advanced reporting"

# Public API - what gets imported with "from db_population_utils import *"
__all__ = [
    # Core classes
    "DBConnector",
    "DBSettings",
    
    # Report classes
    "ExecutionReport",
    "InsertionReport", 
    "QueryReport",
    
    # Type definitions
    "Target",
    
    # Exceptions
    "DBConnectionError",
    "DBConfigurationError", 
    "DBOperationError",
    
    # Convenience functions
    "create_connector_from_env",
    "create_connector_from_config",
    "create_quick_connector",
    
    # Package info
    "__version__",
]

# Convenience imports for common patterns
def create_connector_from_env(
    ingestion_prefix: str = "INGESTION_DB",
    app_prefix: str = "APP_DB",
    **kwargs
) -> DBConnector:
    """
    Convenience function to create DBConnector from environment variables.
    
    Args:
        ingestion_prefix: Environment variable prefix for ingestion DB (default: "INGESTION_DB")
        app_prefix: Environment variable prefix for app DB (default: "APP_DB")
        **kwargs: Additional arguments passed to DBConnector (echo, pool_size, etc.)
        
    Returns:
        Configured DBConnector instance
        
    Example:
        # Uses INGESTION_DB_* and APP_DB_* environment variables
        connector = create_connector_from_env(echo=True, pool_size=10)
        
        # Custom prefixes
        connector = create_connector_from_env(
            ingestion_prefix="PROD_INGESTION",
            app_prefix="PROD_APP",
            echo=True
        )
        
    Environment Variables Expected:
        For ingestion (INGESTION_DB prefix):
        - INGESTION_DB_HOST, INGESTION_DB_PORT, INGESTION_DB_USER
        - INGESTION_DB_PASSWORD, INGESTION_DB_DATABASE
        - INGESTION_DB_URL (alternative to individual components)
        
        For app (APP_DB prefix):
        - APP_DB_HOST, APP_DB_PORT, APP_DB_USER
        - APP_DB_PASSWORD, APP_DB_DATABASE  
        - APP_DB_URL (alternative to individual components)
    """
    try:
        ingestion_settings = DBSettings.from_env(ingestion_prefix)
    except Exception:
        ingestion_settings = None
        
    try:
        app_settings = DBSettings.from_env(app_prefix)
    except Exception:
        app_settings = None
        
    if not ingestion_settings and not app_settings:
        raise DBConfigurationError(
            f"No valid database configuration found in environment. "
            f"Expected variables with prefixes: {ingestion_prefix}_* or {app_prefix}_*"
        )
        
    return DBConnector(
        ingestion=ingestion_settings,
        app=app_settings,
        auto_load_env=False,  # We already loaded manually
        **kwargs
    )

def create_connector_from_config(
    config_path: str,
    **kwargs
) -> DBConnector:
    """
    Convenience function to create DBConnector from configuration file.
    
    Args:
        config_path: Path to configuration file (YAML/JSON)
        **kwargs: Additional arguments passed to DBConnector
        
    Returns:
        Configured DBConnector instance
        
    Example:
        connector = create_connector_from_config(
            "config/database.yaml",
            echo=True,
            pool_size=15
        )
        
    Config File Format (YAML):
        ingestion:
          host: localhost
          port: 5432
          user: ingestion_user
          password: secret
          database: ingestion_db
          
        app:
          url: postgresql://app_user:secret@localhost:5432/app_db
          pool_size: 10
    """
    return DBConnector(config_file=config_path, **kwargs)

def create_quick_connector(
    url: str,
    target: Target = "ingestion",
    **kwargs
) -> DBConnector:
    """
    Convenience function to quickly create DBConnector from a single URL.
    
    Args:
        url: Database connection URL
        target: Which target to configure ("ingestion" or "app")
        **kwargs: Additional arguments passed to DBConnector
        
    Returns:
        Configured DBConnector instance
        
    Example:
        # Quick setup for single database
        connector = create_quick_connector(
            "postgresql://user:pass@localhost:5432/mydb",
            target="ingestion",
            echo=True
        )
        
        # Use the connector
        df = connector.fetch_df("SELECT * FROM users")
    """
    settings = DBSettings(url=url)
    
    if target == "ingestion":
        return DBConnector(ingestion=settings, **kwargs)
    else:
        return DBConnector(app=settings, **kwargs)

# Package-level logging configuration
import logging
import sys
import warnings

# Set up package logger with null handler by default
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def configure_logging(level: str = "INFO", format_string: str = None):
    """
    Configure package logging.
    
    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
        format_string: Custom format string for log messages
        
    Example:
        from db_population_utils import configure_logging
        configure_logging("DEBUG")
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# Version and compatibility checks
if sys.version_info < (3, 8):
    warnings.warn(
        "db_population_utils requires Python 3.8 or higher. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}.",
        UserWarning,
        stacklevel=2
    )

# Check for required dependencies
def _check_dependencies():
    """Check for required and optional dependencies."""
    missing_required = []
    missing_optional = []
    
    # Required dependencies
    try:
        import sqlalchemy
        if tuple(map(int, sqlalchemy.__version__.split('.')[:2])) < (1, 4):
            warnings.warn(
                f"SQLAlchemy version {sqlalchemy.__version__} detected. "
                "db_population_utils works best with SQLAlchemy 1.4 or higher.",
                UserWarning,
                stacklevel=3
            )
    except ImportError:
        missing_required.append("sqlalchemy")
    
    # Optional dependencies
    try:
        import pandas
    except ImportError:
        missing_optional.append("pandas")
        
    try:
        import psycopg2
    except ImportError:
        try:
            import psycopg
        except ImportError:
            missing_optional.append("psycopg2 or psycopg")
    
    # Warn about missing dependencies
    if missing_required:
        warnings.warn(
            f"Required dependencies missing: {', '.join(missing_required)}. "
            f"Install with: pip install {' '.join(missing_required)}",
            ImportWarning,
            stacklevel=3
        )
        
    if missing_optional:
        warnings.warn(
            f"Optional dependencies missing: {', '.join(missing_optional)}. "
            "Some functionality may not be available. "
            f"Install with: pip install {' '.join(missing_optional)}",
            ImportWarning,
            stacklevel=3
        )

# Run dependency check on import
_check_dependencies()

# Utility function for testing
def test_connection_quick(url: str) -> bool:
    """
    Quick utility to test if a database connection URL works.
    
    Args:
        url: Database connection URL to test
        
    Returns:
        True if connection successful, False otherwise
        
    Example:
        if test_connection_quick("postgresql://user:pass@localhost/db"):
            print("Connection works!")
    """
    try:
        connector = create_quick_connector(url)
        result = connector.test_connection()
        return result["ok"]
    except Exception:
        return False

# Add utility functions to __all__
__all__.extend([
    "configure_logging",
    "test_connection_quick"
])

# Package initialization message (optional, can be removed for production)
def _show_init_info():
    """Show package initialization info in debug mode."""
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"db_population_utils v{__version__} initialized")
        logger.debug("Available targets: ingestion, app")
        logger.debug("Use create_connector_from_env() for quick setup")

# Only show info if debug logging is enabled
try:
    _show_init_info()
except:
    pass  # Ignore any errors in initialization info