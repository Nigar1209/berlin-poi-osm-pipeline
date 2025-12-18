# Database Population Utilities (db_population_utils)

## Overview

Comprehensive database infrastructure package for data engineering workflows with advanced connection management, comprehensive reporting, and seamless integration support.

## Architecture

```
DataLoader → DataProcessor → DBConnector ← DBPopulator
```

**Sequential Flow (→):**
- **DataLoader**: Load raw files with quality assessment
- **DataProcessor**: Transform and clean data  
- **DBConnector**: Essential database infrastructure operations

**Infrastructure Usage (←):**
- **DBPopulator**: Uses DBConnector for complex business logic and relationships

## Key Features

✅ **Multi-Environment Support**: Separate `ingestion` and `app` database targets  
✅ **Connection Pooling**: Advanced pooling with health monitoring  
✅ **Comprehensive Reporting**: Detailed reports for all database operations  
✅ **Single-Call Operations**: Execute, report, and handle errors in one call  
✅ **Built-in Error Handling**: Automatic recovery and detailed error reporting  
✅ **Infrastructure Layer**: Designed to be used by other data processing components  
✅ **Production Ready**: Health checks, performance metrics, and monitoring built-in  

## Installation

```bash
pip install sqlalchemy pandas psycopg2-binary
# or
pip install sqlalchemy pandas psycopg
```

## Quick Start

### Environment Setup

Set environment variables:

```bash
# Ingestion Database
export INGESTION_DB_HOST=localhost
export INGESTION_DB_PORT=5432
export INGESTION_DB_USER=ingestion_user
export INGESTION_DB_PASSWORD=secret
export INGESTION_DB_DATABASE=ingestion_db

# App Database  
export APP_DB_URL=postgresql://app_user:secret@localhost:5432/app_db
```

### Basic Usage

```python
from db_population_utils import create_connector_from_env

# Quick setup
connector = create_connector_from_env(echo=True)

# Basic operations
df = connector.fetch_df("SELECT * FROM users")
connector.to_sql(df, "processed_users")
health = connector.test_connection()
```

## Core Methods

### Connection Management
```python
# Get engine for target
engine = connector.get_engine("ingestion")

# Context managers
with connector.connect("ingestion") as conn:
    result = conn.execute(text("SELECT 1"))

with connector.transaction("app") as conn:
    conn.execute(text("INSERT INTO logs VALUES (...)"))
```

### Essential Operations
```python
# Execute SQL
rows_affected = connector.execute(
    "UPDATE users SET status = %(status)s", 
    params={"status": "active"}
)

# Query to DataFrame
df = connector.fetch_df(
    "SELECT * FROM sales WHERE date > %(date)s",
    params={"date": "2024-01-01"}
)

# Insert DataFrame
connector.to_sql(df, "sales_processed", schema="staging")
```

### Health & Schema Management
```python
# Test connection
status = connector.test_connection("ingestion")
# Returns: {"target": "ingestion", "ok": True, "elapsed_sec": 0.012, "version": "..."}

# Check table existence
exists = connector.table_exists("users", schema="public")

# Create schema
created = connector.create_schema("staging")

# Get table info
schema_info = connector.get_table_schema("users", schema="public")
```

## Comprehensive Operations (Single-Call)

### Execute with Full Reporting
```python
rows_affected, report = connector.execute_with_full_report(
    "UPDATE users SET status = %(status)s WHERE active = false",
    params={"status": "inactive"}
)

print(f"Success: {report.success}")
print(f"Rows affected: {report.rows_affected}")
print(f"Execution time: {report.execution_time_seconds:.2f}s")
print(f"Connection healthy: {report.connection_healthy}")
if report.errors:
    print(f"Errors: {report.errors}")
```

### Insert DataFrame with Comprehensive Reporting
```python
success, report = connector.insert_dataframe_with_report(
    df, 
    table="user_data",
    schema="staging", 
    if_exists="append"
)

print(f"Success: {report.success}")
print(f"Rows inserted: {report.rows_inserted}")
print(f"Schema created: {report.schema_created}")
print(f"Table created: {report.table_created}")
print(f"Pre-check results: {report.pre_check_results}")
```

### Query with Data Profiling and Reporting
```python
df, report = connector.query_to_dataframe_with_report(
    "SELECT * FROM staging.user_data WHERE signup_date > %(date)s",
    params={"date": "2024-01-01"}
)

print(f"Success: {report.success}")
print(f"Rows retrieved: {report.rows_retrieved}")
print(f"Memory usage: {report.memory_usage_mb:.1f}MB")
print(f"Data types: {report.data_types}")
print(f"Execution time: {report.execution_time_seconds:.2f}s")
```

## Configuration Options

### DBSettings Configuration
```python
from db_population_utils import DBSettings, DBConnector

# From environment variables
settings = DBSettings.from_env("PROD_DB")

# From dictionary
config = {
    "host": "localhost",
    "port": 5432,
    "user": "dbuser", 
    "password": "secret",
    "database": "mydb",
    "pool_size": 10
}
settings = DBSettings.from_dict(config)

# Direct URL
settings = DBSettings(url="postgresql://user:pass@localhost:5432/db")
```

### Multi-Environment Setup
```python
ingestion_settings = DBSettings.from_env("INGESTION_DB")
app_settings = DBSettings.from_env("APP_DB")

connector = DBConnector(
    ingestion=ingestion_settings,
    app=app_settings,
    echo=True,            # SQL logging
    pool_size=10,         # Connection pool size
    max_overflow=20,      # Max pool overflow
    pool_timeout=30,      # Pool checkout timeout
    pool_recycle=3600     # Connection recycle time
)
```

## Advanced Usage

### Data Pipeline Integration
```python
from db_population_utils import create_connector_from_env

# Setup infrastructure
connector = create_connector_from_env(echo=True)

# Complete pipeline with comprehensive reporting
def process_data_pipeline(source_file: str, target_table: str):
    # Step 1: Load data (DataLoader responsibility)
    # raw_df = loader.load(source_file)
    
    # Step 2: Process data (DataProcessor responsibility)  
    # clean_df = processor.transform(raw_df)
    
    # Step 3: Store with comprehensive reporting
    success, report = connector.insert_dataframe_with_report(
        clean_df, 
        target_table, 
        schema="staging", 
        if_exists="replace"
    )
    
    if success:
        print(f"✅ Pipeline success: {report.rows_inserted} rows inserted")
        
        # Step 4: Business logic (DBPopulator responsibility)
        # populator.establish_relationships(connector, target_table, ["existing_table"])
        
    else:
        print(f"❌ Pipeline failed: {report.errors}")
        
    return success, report
```

### Error Handling and Recovery
```python
from db_population_utils import DBConnectionError, DBOperationError

try:
    rows, report = connector.execute_with_full_report(
        "COMPLEX SQL OPERATION..."
    )
    
    if not report.success:
        print(f"Operation failed but handled gracefully: {report.errors}")
        
except DBConnectionError as e:
    print(f"Connection issue - retry logic here: {e}")
    
except DBOperationError as e:
    print(f"SQL operation failed: {e}")
```

### Performance Monitoring
```python
# Query with performance metrics
df, report = connector.query_to_dataframe_with_report(
    "SELECT * FROM large_table WHERE date > %(date)s",
    params={"date": "2024-01-01"}
)

# Analyze performance
if report.execution_time_seconds > 5.0:
    print(f"⚠️  Slow query detected: {report.execution_time_seconds:.2f}s")
    
if report.memory_usage_mb > 100:
    print(f"⚠️  High memory usage: {report.memory_usage_mb:.1f}MB")
    
print(f"📊 Performance: {report.rows_retrieved} rows in {report.execution_time_seconds:.2f}s")
```

## Report Classes

### ExecutionReport
```python
@dataclass
class ExecutionReport:
    success: bool
    rows_affected: int = 0
    execution_time_seconds: float = 0.0
    connection_healthy: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    query_info: Dict[str, Any] = field(default_factory=dict)
```

### InsertionReport
```python
@dataclass  
class InsertionReport:
    success: bool
    rows_inserted: int = 0
    table_created: bool = False
    schema_created: bool = False
    execution_time_seconds: float = 0.0
    connection_healthy: bool = True
    pre_check_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

### QueryReport
```python
@dataclass
class QueryReport:
    success: bool
    rows_retrieved: int = 0
    execution_time_seconds: float = 0.0
    connection_healthy: bool = True
    data_types: Dict[str, str] = field(default_factory=dict)
    memory_usage_mb: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
```

## Convenience Functions

```python
from db_population_utils import (
    create_connector_from_env,
    create_connector_from_config, 
    create_quick_connector,
    test_connection_quick,
    configure_logging
)

# Quick environment setup
connector = create_connector_from_env(echo=True)

# From config file
connector = create_connector_from_config("config/db.yaml")

# Single URL setup
connector = create_quick_connector(
    "postgresql://user:pass@localhost:5432/db",
    target="ingestion"
)

# Test connection quickly
if test_connection_quick("postgresql://user:pass@localhost:5432/db"):
    print("Connection works!")

# Configure logging
configure_logging("DEBUG")
```

## Integration with Other Components

### With DBPopulator (Business Logic)
```python
# DBConnector provides infrastructure
connector = create_connector_from_env()

# DBPopulator uses DBConnector for complex operations
class DBPopulator:
    def __init__(self, connector: DBConnector):
        self.connector = connector
    
    def establish_relationships(self, new_table: str, existing_tables: List[str]):
        # Use connector for infrastructure operations
        for existing_table in existing_tables:
            if self.connector.table_exists(existing_table):
                # Create foreign key relationships
                sql = f"ALTER TABLE {new_table} ADD CONSTRAINT..."
                rows, report = self.connector.execute_with_full_report(sql)
```

### With DataProcessor (Data Pipeline)
```python
# DataProcessor → DBConnector flow
class DataProcessor:
    def __init__(self, connector: DBConnector):
        self.connector = connector
    
    def save_processed_data(self, df: pd.DataFrame, table: str):
        # Use comprehensive operation
        success, report = self.connector.insert_dataframe_with_report(
            df, table, schema="processed"
        )
        return success, report
```

## Best Practices

### 1. Use Comprehensive Operations
```python
# ✅ Good - Single call with full reporting
success, report = connector.insert_dataframe_with_report(df, "table")

# ❌ Avoid - Multiple separate calls  
connector.test_connection()
connector.create_schema("schema")
connector.to_sql(df, "table")
```

### 2. Handle Reports Properly
```python
success, report = connector.insert_dataframe_with_report(df, "users")

if success:
    # Log success metrics
    logger.info(f"Inserted {report.rows_inserted} rows in {report.execution_time_seconds:.2f}s")
else:
    # Handle errors appropriately
    for error in report.errors:
        logger.error(f"Insert failed: {error}")
```

### 3. Use Appropriate Targets
```python
# Raw data goes to ingestion
connector.to_sql(raw_df, "raw_data", target="ingestion")

# Processed data goes to app
connector.to_sql(processed_df, "clean_data", target="app")
```

### 4. Monitor Performance
```python
df, report = connector.query_to_dataframe_with_report("SELECT ...")

# Set up alerts for slow queries
if report.execution_time_seconds > SLOW_QUERY_THRESHOLD:
    send_alert(f"Slow query detected: {report.execution_time_seconds:.2f}s")
```

## Dependencies

**Required:**
- `sqlalchemy >= 1.4`
- `python >= 3.8`

**Optional:**
- `pandas` - For DataFrame operations
- `psycopg2` or `psycopg` - For PostgreSQL connections

## License

MIT License

## Contributing

1. Follow the architecture: `DataLoader → DataProcessor → DBConnector ← DBPopulator`
2. Use comprehensive operations for all database interactions
3. Include proper error handling and reporting
4. Write tests for all new functionality
5. Update documentation for any API changes

---

**Key Benefits of This Architecture:**

🔧 **Infrastructure First**: DBConnector is pure infrastructure without business logic  
📊 **Comprehensive Reporting**: Every operation returns detailed reports  
⚡ **Single-Call Operations**: Execute, report, and handle errors in one call  
🔄 **Reusable**: Can be used independently or as foundation for other components  
🏗️ **Production Ready**: Built-in health checks, error handling, and monitoring