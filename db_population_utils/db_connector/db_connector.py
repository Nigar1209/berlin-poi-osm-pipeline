# db_population_utils/db_connector.py

"""
DBConnector Module - Database Infrastructure Layer

This module provides essential database infrastructure for data engineering workflows.
DBConnector serves as the low-level database operations layer that other components use.

Key Design Philosophy:
    - **Infrastructure First**: Low-level database operations without business logic
    - **Tool for Other Classes**: Designed to be used by DBPopulator and other components
    - **Multi-Environment**: Support for separate 'ingestion' and 'app' database targets
    - **Reliability**: Built-in health checks and comprehensive error reporting
    - **Comprehensive Operations**: Single-call methods that combine connection, execution, and reporting

Architecture Overview (4-Class System):
    ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ DataLoader  │───→│ DataProcessor   │───→│ DBConnector     │←───│ DBPopulator     │
    │             │    │                 │    │                 │    │                 │
    │ • Load Raw  │    │ • Transform     │    │ • Infrastructure│    │ • Business      │
    │   Files     │    │ • Clean Data    │    │ • Connections   │    │   Logic         │
    │ • Quality   │    │ • Normalize     │    │ • Execute SQL   │    │ • Relationships │
    │   Reports   │    │ • Validation    │    │ • Comprehensive │    │ • Constraints   │
    │             │    │                 │    │   Operations    │    │ • Complex Ops   │
    └─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘

Target Use Cases:
    1. **Database Infrastructure**: Provide reliable database operations for other classes
    2. **Development Support**: Connection management across dev/staging/prod environments
    3. **Data Pipeline Foundation**: Low-level operations used by DBPopulator and DataProcessor
    4. **Quick Operations**: Single-call methods for common database patterns

Core Features:
    ✓ Essential database operations (12 core methods)
    ✓ Comprehensive single-call operations (3 enhanced methods)
    ✓ Multi-environment support (ingestion/app targets)
    ✓ Connection pooling and health monitoring
    ✓ Built-in error handling and recovery
    ✓ Infrastructure tool for DBPopulator business logic

Example Usage as Infrastructure Tool:
    # Direct usage for simple operations
    connector = DBConnector(ingestion=settings)
    df = connector.fetch_df("SELECT * FROM table")
    connector.to_sql(df, "new_table")
    
    # Comprehensive single-call operations
    rows, report = connector.execute_with_full_report("CREATE INDEX...")
    df, report = connector.query_to_dataframe_with_report("SELECT...")
    success, report = connector.insert_dataframe_with_report(df, "table")
    
    # Used by DBPopulator for complex business logic
    populator = DBPopulator(connector=connector)
    populator.establish_relationships("new_table", ["listings", "neighborhoods"])
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Iterator, Literal, List, Union, Tuple
from contextlib import contextmanager
from pathlib import Path
import logging
import time
import os
from urllib.parse import quote_plus

try:
    import sqlalchemy
    from sqlalchemy import create_engine, text, inspect
    from sqlalchemy.engine import Engine, Connection
    from sqlalchemy.exc import SQLAlchemyError, DatabaseError, OperationalError
    from sqlalchemy.pool import StaticPool, QueuePool
except ImportError:
    raise ImportError(
        "SQLAlchemy is required for DBConnector. Install with: pip install sqlalchemy"
    )

try:
    import pandas as pd
except ImportError:
    pd = None
    import warnings
    warnings.warn(
        "Pandas not found. DataFrame operations will not be available. "
        "Install with: pip install pandas",
        ImportWarning
    )

Target = Literal["ingestion", "app"]


@dataclass
class DBSettings:
    """
    Database connection settings for one target environment.

    Purpose:
      - Hold connection parameters for one target (e.g., 'ingestion' or 'app')
      - Provide helpers to load from environment and compose SQLAlchemy URL
      - Support connection pooling configuration
    """
    url: Optional[str] = None
    driver: str = "postgresql+psycopg2"
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    query: Dict[str, Any] = field(default_factory=dict)

    # Connection pooling configuration
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    connect_args: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls, prefix: str) -> "DBSettings":
        """Load settings from environment variables with the given prefix."""
        def get_env(key: str, default=None, cast_type=str):
            value = os.getenv(f"{prefix}_{key}", default)
            if value is None:
                return default
            if cast_type == int:
                return int(value)
            elif cast_type == bool:
                return value.lower() in ('true', '1', 'yes', 'on')
            return value

        # Try to get complete URL first
        url = get_env("URL")
        if url:
            return cls(
                url=url,
                pool_size=get_env("POOL_SIZE", 5, int),
                max_overflow=get_env("MAX_OVERFLOW", 10, int),
                pool_timeout=get_env("POOL_TIMEOUT", 30, int),
                pool_recycle=get_env("POOL_RECYCLE", 3600, int),
                pool_pre_ping=get_env("POOL_PRE_PING", True, bool),
            )

        # Build from components
        return cls(
            driver=get_env("DRIVER", "postgresql+psycopg2"),
            host=get_env("HOST"),
            port=get_env("PORT", 5432, int),
            user=get_env("USER"),
            password=get_env("PASSWORD"),
            database=get_env("DATABASE"),
            pool_size=get_env("POOL_SIZE", 5, int),
            max_overflow=get_env("MAX_OVERFLOW", 10, int),
            pool_timeout=get_env("POOL_TIMEOUT", 30, int),
            pool_recycle=get_env("POOL_RECYCLE", 3600, int),
            pool_pre_ping=get_env("POOL_PRE_PING", True, bool),
        )

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "DBSettings":
        """Load settings from configuration dictionary."""
        return cls(**config)

    def sqlalchemy_url(self) -> str:
        """Compose and return a SQLAlchemy URL string."""
        if self.url:
            return self.url

        if not all([self.host, self.user, self.password, self.database]):
            raise ValueError("Missing required connection parameters")

        password = quote_plus(str(self.password))
        url = f"{self.driver}://{self.user}:{password}@{self.host}:{self.port}/{self.database}"
        
        if self.query:
            query_string = "&".join(f"{k}={v}" for k, v in self.query.items())
            url += f"?{query_string}"
        
        return url

    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.url:
            return bool(self.url.strip())
        
        required = [self.host, self.user, self.password, self.database]
        return all(param is not None for param in required)

    def get_safe_info(self) -> Dict[str, Any]:
        """Return connection info without sensitive data (passwords)."""
        return {
            "driver": self.driver,
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "database": self.database,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "has_password": bool(self.password),
            "has_url": bool(self.url),
        }


@dataclass
class ExecutionReport:
    """Report from SQL execution operations."""
    success: bool
    rows_affected: int = 0
    execution_time_seconds: float = 0.0
    connection_healthy: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    query_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InsertionReport:
    """Report from DataFrame insertion operations."""
    success: bool
    rows_inserted: int = 0
    table_created: bool = False
    schema_created: bool = False
    execution_time_seconds: float = 0.0
    connection_healthy: bool = True
    pre_check_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class QueryReport:
    """Report from DataFrame query operations."""
    success: bool
    rows_retrieved: int = 0
    execution_time_seconds: float = 0.0
    connection_healthy: bool = True
    data_types: Dict[str, str] = field(default_factory=dict)
    memory_usage_mb: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DBConnectionError(Exception):
    """Raised on unrecoverable DB errors."""


class DBConfigurationError(Exception):
    """Raised on configuration validation errors."""


class DBOperationError(Exception):
    """Raised on database operation failures."""


class DBConnector:
    """
    Focused DBConnector — essential database operations with comprehensive reporting.

    Purpose:
      - Manage pooled engines for multiple targets (ingestion/app)
      - Provide context-managed connections and transactions
      - Execute database operations with comprehensive reporting
      - Support essential schema management operations
      - Provide comprehensive single-call operations for common patterns
    """

    def __init__(
        self,
        ingestion: Optional[DBSettings] = None,
        app: Optional[DBSettings] = None,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        config_file: Optional[Union[str, Path]] = None,
        auto_load_env: bool = True,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize DBConnector with essential configuration options.
        
        Args:
            ingestion: Database settings for ingestion target
            app: Database settings for app target
            echo: Enable SQL query logging
            pool_size: Default connection pool size
            max_overflow: Default maximum pool overflow
            pool_timeout: Default pool checkout timeout
            pool_recycle: Default connection recycle time
            config_file: Path to configuration file (YAML/JSON)
            auto_load_env: Automatically load settings from environment
            logger: Custom logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        
        # Engine cache
        self._engines: Dict[Target, Engine] = {}
        
        # Load settings
        self._settings: Dict[Target, Optional[DBSettings]] = {}
        
        if config_file:
            self._load_from_config_file(config_file)
        elif auto_load_env:
            self._load_from_environment()
        
        # Override with explicit settings
        if ingestion:
            self._settings["ingestion"] = ingestion
        if app:
            self._settings["app"] = app
            
        # Validate at least one target is configured
        if not any(self._settings.values()):
            raise DBConfigurationError("At least one database target must be configured")

    def _load_from_environment(self):
        """Load settings from environment variables."""
        try:
            self._settings["ingestion"] = DBSettings.from_env("INGESTION_DB")
        except Exception as e:
            self.logger.debug(f"Could not load ingestion settings from env: {e}")
            self._settings["ingestion"] = None
            
        try:
            self._settings["app"] = DBSettings.from_env("APP_DB")
        except Exception as e:
            self.logger.debug(f"Could not load app settings from env: {e}")
            self._settings["app"] = None

    def _load_from_config_file(self, config_file: Union[str, Path]):
        """Load settings from configuration file."""
        # Implementation would depend on file format (YAML/JSON)
        # For now, raise NotImplementedError
        raise NotImplementedError("Config file loading not yet implemented")

    # --- Core Connection Management (4 methods) ---
    
    def get_engine(self, target: Target = "ingestion") -> Engine:
        """Return (or lazily create) a SQLAlchemy Engine for the target."""
        self._validate_target(target)
        
        if target not in self._engines:
            settings = self._get_settings(target)
            self._engines[target] = self._create_engine(settings)
            
        return self._engines[target]

    @contextmanager
    def connect(self, target: Target = "ingestion") -> Iterator[Connection]:
        """
        Yield a live DB-API/SQLAlchemy Connection (no explicit transaction).
        
        Usage:
            with connector.connect("ingestion") as conn:
                result = conn.execute(text("SELECT 1"))
        """
        engine = self.get_engine(target)
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self, target: Target = "ingestion") -> Iterator[Connection]:
        """
        Yield a Connection inside a transaction (commit on success, rollback on error).
        
        Usage:
            with connector.transaction("app") as conn:
                conn.execute(text("INSERT INTO ..."))
        """
        with self.connect(target) as conn:
            trans = conn.begin()
            try:
                yield conn
                trans.commit()
            except Exception:
                trans.rollback()
                raise

    def dispose_all(self) -> None:
        """Dispose and remove all cached engines and connection pools."""
        for engine in self._engines.values():
            engine.dispose()
        self._engines.clear()

    # --- Essential Data Operations (3 methods) ---
    
    def to_sql(
        self,
        df,  # pandas.DataFrame expected
        table: str,
        schema: Optional[str] = None,
        if_exists: str = "append",
        chunksize: int = 5000,
        target: Target = "ingestion",
        method: Optional[str] = None,
    ) -> None:
        """Write a pandas DataFrame to a database table."""
        if pd is None:
            raise ImportError("pandas is required for DataFrame operations")
            
        engine = self.get_engine(target)
        df.to_sql(
            name=table,
            con=engine,
            schema=schema,
            if_exists=if_exists,
            index=False,
            chunksize=chunksize,
            method=method
        )

    def execute(
        self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None, 
        target: Target = "ingestion"
    ) -> int:
        """Execute a DDL/DML statement within a transaction and return rowcount."""
        with self.transaction(target) as conn:
            result = conn.execute(text(sql), params or {})
            return result.rowcount

    def fetch_df(
        self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None, 
        target: Target = "ingestion"
    ):
        """Execute a SELECT and return a pandas DataFrame."""
        if pd is None:
            raise ImportError("pandas is required for DataFrame operations")
            
        engine = self.get_engine(target)
        return pd.read_sql(sql, engine, params=params)

    # --- Essential Health & Schema Checks (4 methods) ---
    
    def test_connection(self, target: Target = "ingestion") -> Dict[str, Any]:
        """
        Run a lightweight probe (e.g., SELECT 1) and return a status dict.
        
        Returns:
            {"target": "ingestion", "ok": True, "elapsed_sec": 0.012, "version": "..."}
        """
        start_time = time.time()
        result = {
            "target": target,
            "ok": False,
            "elapsed_sec": 0.0,
            "version": None,
            "error": None
        }
        
        try:
            with self.connect(target) as conn:
                # Test basic connectivity
                conn.execute(text("SELECT 1"))
                
                # Try to get database version
                try:
                    version_result = conn.execute(text("SELECT version()"))
                    result["version"] = version_result.fetchone()[0]
                except Exception:
                    result["version"] = "Unknown"
                    
                result["ok"] = True
                
        except Exception as e:
            result["error"] = str(e)
            
        result["elapsed_sec"] = time.time() - start_time
        return result

    def table_exists(
        self, 
        table: str, 
        schema: Optional[str] = None, 
        target: Target = "ingestion"
    ) -> bool:
        """Check if table exists in database."""
        try:
            engine = self.get_engine(target)
            inspector = inspect(engine)
            
            if schema:
                return inspector.has_table(table, schema=schema)
            else:
                return inspector.has_table(table)
                
        except Exception:
            return False

    def create_schema(self, schema: str, target: Target = "ingestion") -> bool:
        """Create database schema if it doesn't exist."""
        try:
            sql = f"CREATE SCHEMA IF NOT EXISTS {schema}"
            self.execute(sql, target=target)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create schema {schema}: {e}")
            return False

    def get_table_schema(
        self, 
        table: str, 
        schema: Optional[str] = None, 
        target: Target = "ingestion"
    ) -> Dict[str, Any]:
        """Retrieve comprehensive table schema information."""
        try:
            engine = self.get_engine(target)
            inspector = inspect(engine)
            
            # Get columns
            columns = inspector.get_columns(table, schema=schema)
            
            # Get primary keys
            pk_constraint = inspector.get_pk_constraint(table, schema=schema)
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table, schema=schema)
            
            # Get indexes
            indexes = inspector.get_indexes(table, schema=schema)
            
            return {
                "table": table,
                "schema": schema,
                "columns": columns,
                "primary_key": pk_constraint,
                "foreign_keys": foreign_keys,
                "indexes": indexes,
                "exists": True
            }
            
        except Exception as e:
            return {
                "table": table,
                "schema": schema,
                "exists": False,
                "error": str(e)
            }

    # --- Comprehensive Operation Methods (3 methods) ---
    
    def execute_with_full_report(
        self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None, 
        target: Target = "ingestion"
    ) -> Tuple[int, ExecutionReport]:
        """
        Execute SQL with comprehensive reporting and error handling.
        
        Combines: test_connection() + execute() + error handling + performance metrics
        
        Args:
            sql: SQL statement to execute
            params: Parameters for parameterized query
            target: Database target
            
        Returns:
            Tuple of (rows_affected, comprehensive_report)
        """
        start_time = time.time()
        report = ExecutionReport(success=False)
        rows_affected = 0
        
        try:
            # Pre-flight connection health check
            health_check = self.test_connection(target)
            report.connection_healthy = health_check["ok"]
            
            if not report.connection_healthy:
                report.errors.append(f"Connection health check failed: {health_check.get('error', 'Unknown error')}")
                return rows_affected, report
            
            # Execute the SQL statement
            rows_affected = self.execute(sql, params, target)
            
            # Success
            report.success = True
            report.rows_affected = rows_affected
            report.query_info = {
                "sql_type": self._get_sql_type(sql),
                "has_params": bool(params),
                "param_count": len(params) if params else 0
            }
            
        except Exception as e:
            report.errors.append(f"Execution failed: {str(e)}")
            self.logger.error(f"SQL execution failed: {e}")
            
        finally:
            report.execution_time_seconds = time.time() - start_time
            
        return rows_affected, report

    def insert_dataframe_with_report(
        self,
        df,  # pandas.DataFrame expected
        table: str,
        schema: Optional[str] = None,
        if_exists: str = "append",
        target: Target = "ingestion",
        **kwargs
    ) -> Tuple[bool, InsertionReport]:
        """
        Insert DataFrame with pre-checks, execution, and comprehensive reporting.
        
        Combines: test_connection() + table_exists() + create_schema() + to_sql() + reporting
        
        Args:
            df: DataFrame to insert
            table: Target table name
            schema: Target schema name
            if_exists: What to do if table exists
            target: Database target
            
        Returns:
            Tuple of (success, comprehensive_report)
        """
        if pd is None:
            raise ImportError("pandas is required for DataFrame operations")
            
        start_time = time.time()
        report = InsertionReport(success=False)
        
        try:
            # Pre-flight connection health check
            health_check = self.test_connection(target)
            report.connection_healthy = health_check["ok"]
            report.pre_check_results["health_check"] = health_check
            
            if not report.connection_healthy:
                report.errors.append(f"Connection health check failed: {health_check.get('error', 'Unknown error')}")
                return False, report
            
            # Check if schema needs to be created
            if schema:
                if not self._schema_exists(schema, target):
                    schema_created = self.create_schema(schema, target)
                    report.schema_created = schema_created
                    report.pre_check_results["schema_created"] = schema_created
                    
                    if not schema_created:
                        report.errors.append(f"Failed to create schema: {schema}")
                        return False, report
            
            # Check if table exists
            table_existed = self.table_exists(table, schema, target)
            report.pre_check_results["table_existed_before"] = table_existed
            
            # Validate DataFrame
            if df.empty:
                report.warnings.append("DataFrame is empty - no rows to insert")
                report.success = True
                return True, report
            
            # Execute insertion
            self.to_sql(df, table, schema, if_exists, target=target, **kwargs)
            
            # Check if table was created (for new tables)
            if not table_existed:
                report.table_created = self.table_exists(table, schema, target)
            
            # Success
            report.success = True
            report.rows_inserted = len(df)
            
        except Exception as e:
            report.errors.append(f"DataFrame insertion failed: {str(e)}")
            self.logger.error(f"DataFrame insertion failed: {e}")
            
        finally:
            report.execution_time_seconds = time.time() - start_time
            
        return report.success, report

    def query_to_dataframe_with_report(
        self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None, 
        target: Target = "ingestion"
    ) -> Tuple["pd.DataFrame", QueryReport]:
        """
        Query database and return DataFrame with execution report.
        
        Combines: test_connection() + fetch_df() + data profiling + performance metrics
        
        Args:
            sql: SQL query to execute
            params: Parameters for parameterized query
            target: Database target
            
        Returns:
            Tuple of (dataframe, comprehensive_report)
        """
        if pd is None:
            raise ImportError("pandas is required for DataFrame operations")
            
        start_time = time.time()
        report = QueryReport(success=False)
        df = pd.DataFrame()  # Empty fallback
        
        try:
            # Pre-flight connection health check
            health_check = self.test_connection(target)
            report.connection_healthy = health_check["ok"]
            
            if not report.connection_healthy:
                report.errors.append(f"Connection health check failed: {health_check.get('error', 'Unknown error')}")
                return df, report
            
            # Execute query
            df = self.fetch_df(sql, params, target)
            
            # Success - gather metrics
            report.success = True
            report.rows_retrieved = len(df)
            
            # Data profiling
            if not df.empty:
                report.data_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
                report.memory_usage_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            else:
                report.warnings.append("Query returned no rows")
                
        except Exception as e:
            report.errors.append(f"Query execution failed: {str(e)}")
            self.logger.error(f"Query execution failed: {e}")
            
        finally:
            report.execution_time_seconds = time.time() - start_time
            
        return df, report

    # --- Private/Internal Methods ---
    
    def _create_engine(self, settings: DBSettings) -> Engine:
        """Internal method to create SQLAlchemy engine."""
        if not settings.validate():
            raise DBConfigurationError("Invalid database settings")
            
        url = settings.sqlalchemy_url()
        
        # Engine configuration
        engine_kwargs = {
            "echo": self.echo,
            "pool_size": settings.pool_size,
            "max_overflow": settings.max_overflow,
            "pool_timeout": settings.pool_timeout,
            "pool_recycle": settings.pool_recycle,
            "pool_pre_ping": settings.pool_pre_ping,
        }
        
        if settings.connect_args:
            engine_kwargs["connect_args"] = settings.connect_args
            
        return create_engine(url, **engine_kwargs)

    def _validate_target(self, target: Target) -> None:
        """Internal method to validate target parameter."""
        if target not in ["ingestion", "app"]:
            raise ValueError(f"Invalid target: {target}. Must be 'ingestion' or 'app'")
            
        if self._settings.get(target) is None:
            raise DBConfigurationError(f"No configuration found for target: {target}")

    def _get_settings(self, target: Target) -> DBSettings:
        """Internal method to get settings for target."""
        self._validate_target(target)
        return self._settings[target]

    def _check_connection_health(self, target: Target) -> Dict[str, Any]:
        """Internal method for connection health checking."""
        return self.test_connection(target)

    def _handle_db_error(self, error: Exception, operation: str, target: Target):
        """Internal method for standardized error handling."""
        error_msg = f"Database error during {operation} on {target}: {str(error)}"
        self.logger.error(error_msg)
        
        if isinstance(error, OperationalError):
            raise DBConnectionError(error_msg) from error
        elif isinstance(error, DatabaseError):
            raise DBOperationError(error_msg) from error
        else:
            raise DBOperationError(error_msg) from error

    def _get_sql_type(self, sql: str) -> str:
        """Determine the type of SQL statement."""
        sql_upper = sql.strip().upper()
        
        if sql_upper.startswith("SELECT"):
            return "SELECT"
        elif sql_upper.startswith("INSERT"):
            return "INSERT"
        elif sql_upper.startswith("UPDATE"):
            return "UPDATE"
        elif sql_upper.startswith("DELETE"):
            return "DELETE"
        elif sql_upper.startswith("CREATE"):
            return "CREATE"
        elif sql_upper.startswith("DROP"):
            return "DROP"
        elif sql_upper.startswith("ALTER"):
            return "ALTER"
        else:
            return "OTHER"

    def _schema_exists(self, schema: str, target: Target) -> bool:
        """Check if schema exists."""
        try:
            engine = self.get_engine(target)
            inspector = inspect(engine)
            return schema in inspector.get_schema_names()
        except Exception:
            return False