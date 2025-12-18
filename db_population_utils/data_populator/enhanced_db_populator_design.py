# db_population_utils/db_populator.py

"""
DBPopulator Module - Database Business Logic Layer

This module provides high-level database business logic operations using DBConnector
as the underlying infrastructure layer for all database operations.

Key Design Philosophy:
    - **Business Logic First**: High-level database operations with domain-specific logic
    - **Uses DBConnector**: Leverages DBConnector as infrastructure tool (not direct SQL)
    - **Table Management**: Focus on table lifecycle, relationships, and complex operations
    - **Data Integration**: Combines data from DataProcessor with database business rules
    - **Comprehensive Operations**: Single-call methods for complex database scenarios

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
                                                       ↑
                                                       │ Uses as infrastructure
                                                       │
                                              ┌─────────────────┐
                                              │ DBPopulator     │
                                              │ Business Logic  │
                                              │                 │
                                              │ • Table Mgmt    │
                                              │ • Relationships │
                                              │ • Constraints   │
                                              │ • Upserts       │
                                              │ • Migrations    │
                                              └─────────────────┘

Target Use Cases:
    1. **Table Lifecycle Management**: Create, modify, and manage table structures
    2. **Data Relationships**: Establish and maintain foreign key relationships
    3. **Complex Data Operations**: Upserts, merges, and advanced data integration
    4. **Database Migrations**: Schema changes and data migration operations
    5. **Business Rule Enforcement**: Apply domain-specific constraints and validations
    6. **Multi-Table Operations**: Coordinate operations across multiple related tables

Core Features:
    ✓ High-level database business logic (12 core methods)
    ✓ Comprehensive single-call operations (3 enhanced methods)
    ✓ Uses DBConnector for all infrastructure operations
    ✓ Table relationship management and constraint enforcement
    ✓ Advanced data integration with upsert capabilities
    ✓ Database migration and schema evolution support

Example Usage with DBConnector:
    # DBPopulator uses DBConnector as infrastructure tool
    connector = DBConnector(ingestion=settings)
    populator = DBPopulator(connector=connector)
    
    # High-level business operations
    populator.create_table_with_relationships("users", user_schema, related_tables=["roles", "departments"])
    populator.upsert_with_validation(df_clean, "users", key_columns=["email"], business_rules=user_rules)
    
    # Complex multi-table operations
    populator.populate_with_relationships(df_clean, "users", establish_fks=True, validate_integrity=True)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union, Callable, Literal
from enum import Enum
import logging
import time

# Type-only imports to keep design lightweight
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd
    from .db_connector import DBConnector

# Enhanced type definitions
Target = Literal["ingestion", "app"]
UpsertStrategy = Literal["native", "merge", "replace", "incremental"]
RelationshipType = Literal["one_to_one", "one_to_many", "many_to_many"]
MigrationDirection = Literal["up", "down"]


# -----------------------
# Core Enums
# -----------------------
class PopulationStrategy(Enum):
    """Data population strategies for different scenarios."""
    APPEND_ONLY = "append_only"          # Simple append operations
    UPSERT_SMART = "upsert_smart"        # Intelligent upsert with conflict resolution
    REPLACE_TABLE = "replace_table"       # Full table replacement
    INCREMENTAL = "incremental"          # Incremental updates based on timestamps


class ValidationLevel(Enum):
    """Business rule validation levels."""
    NONE = "none"                        # No business validation
    BASIC = "basic"                      # Basic referential integrity
    BUSINESS_RULES = "business_rules"    # Apply domain-specific rules
    COMPREHENSIVE = "comprehensive"      # Full validation including custom rules


class ConstraintType(Enum):
    """Database constraint types."""
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    UNIQUE = "unique"
    CHECK = "check"
    NOT_NULL = "not_null"


# -----------------------
# Configuration Classes
# -----------------------
@dataclass
class TableSchema:
    """Enhanced table schema definition with business logic."""
    table_name: str
    columns: Dict[str, str]  # column_name: data_type
    primary_key: Optional[List[str]] = None
    foreign_keys: List[Dict[str, Any]] = field(default_factory=list)
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    business_rules: List[Callable] = field(default_factory=list)
    partition_config: Optional[Dict[str, Any]] = None


@dataclass
class RelationshipConfig:
    """Configuration for table relationships."""
    source_table: str
    target_table: str
    relationship_type: RelationshipType
    source_columns: List[str]
    target_columns: List[str]
    on_delete: str = "CASCADE"
    on_update: str = "CASCADE"
    constraint_name: Optional[str] = None


@dataclass
class UpsertConfig:
    """Configuration for upsert operations."""
    key_columns: List[str]
    update_columns: Optional[List[str]] = None
    strategy: UpsertStrategy = UpsertStrategy.NATIVE
    conflict_resolution: str = "update"  # "update", "ignore", "error"
    batch_size: int = 1000
    validate_before_upsert: bool = True


@dataclass
class PopulationOptions:
    """High-level population configuration."""
    # Core settings
    population_strategy: PopulationStrategy = PopulationStrategy.UPSERT_SMART
    validation_level: ValidationLevel = ValidationLevel.BUSINESS_RULES
    target: Target = "app"
    
    # Table management
    create_table_if_missing: bool = True
    create_schema_if_missing: bool = True
    backup_before_operation: bool = False
    
    # Relationship management
    establish_relationships: bool = True
    validate_referential_integrity: bool = True
    create_indexes: bool = True
    
    # Performance settings
    batch_size: int = 5000
    parallel_processing: bool = False
    optimize_for_bulk_operations: bool = True
    
    # Error handling
    continue_on_constraint_violation: bool = False
    rollback_on_error: bool = True
    max_error_count: int = 100


# -----------------------
# Report Classes
# -----------------------
@dataclass
class TableOperationReport:
    """Report from table operation."""
    table_name: str
    operation_type: str
    success: bool
    rows_affected: int = 0
    execution_time_seconds: float = 0.0
    constraints_created: List[str] = field(default_factory=list)
    indexes_created: List[str] = field(default_factory=list)
    relationships_established: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class UpsertOperationReport:
    """Report from upsert operations."""
    table_name: str
    strategy_used: UpsertStrategy
    success: bool
    rows_inserted: int = 0
    rows_updated: int = 0
    rows_skipped: int = 0
    constraint_violations: int = 0
    execution_time_seconds: float = 0.0
    validation_results: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class PopulationReport:
    """Comprehensive population operation report."""
    # Basic info
    operation_type: str
    population_strategy: PopulationStrategy
    validation_level: ValidationLevel
    
    # Table operations
    tables_processed: List[str] = field(default_factory=list)
    table_reports: Dict[str, TableOperationReport] = field(default_factory=dict)
    
    # Data operations
    total_rows_processed: int = 0
    total_rows_inserted: int = 0
    total_rows_updated: int = 0
    total_rows_skipped: int = 0
    
    # Relationship operations
    relationships_created: List[str] = field(default_factory=list)
    constraints_enforced: List[str] = field(default_factory=list)
    indexes_created: List[str] = field(default_factory=list)
    
    # Validation results
    business_rules_validated: int = 0
    validation_failures: List[str] = field(default_factory=list)
    referential_integrity_checked: bool = False
    
    # Performance metrics
    total_execution_time_seconds: float = 0.0
    average_throughput_rows_per_sec: float = 0.0
    
    # Overall results
    overall_success: bool = True
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# -----------------------
# Custom Exceptions
# -----------------------
class DBPopulatorError(Exception):
    """Base exception for DBPopulator operations."""


class TableManagementError(DBPopulatorError):
    """Raised when table management operations fail."""


class RelationshipError(DBPopulatorError):
    """Raised when relationship operations fail."""


class UpsertError(DBPopulatorError):
    """Raised when upsert operations fail."""


class BusinessRuleValidationError(DBPopulatorError):
    """Raised when business rule validation fails."""


# -----------------------
# Enhanced DBPopulator Class
# -----------------------
class DBPopulator:
    """
    DBPopulator — High-level database business logic operations using DBConnector.

    Purpose:
      Provide business logic layer for complex database operations:
        - Table lifecycle management with business rules
        - Relationship establishment and constraint enforcement
        - Advanced data integration with validation
        - Complex upsert operations with conflict resolution
        - Database migration and schema evolution
        - Multi-table operations with transaction coordination

    Integration:
      - Uses DBConnector as infrastructure layer for all database operations
      - Receives clean data from DataProcessor
      - Applies business logic and domain-specific rules
      - Coordinates complex multi-table operations
    """

    def __init__(
        self,
        connector: "DBConnector",
        verbose: bool = True,
        default_target: Target = "app",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize DBPopulator with DBConnector infrastructure.
        
        Args:
            connector: DBConnector instance for infrastructure operations
            verbose: Enable detailed logging during operations
            default_target: Default database target
            logger: Custom logger instance
        """
        raise NotImplementedError

    # -----------------------
    # Table Management Methods (4 methods)
    # -----------------------
    
    def create_table(
        self,
        schema: TableSchema,
        *,
        target: Optional[Target] = None,
        if_exists: str = "skip"  # "skip", "replace", "error"
    ) -> TableOperationReport:
        """
        Create table with comprehensive schema definition including business rules.
        
        Uses DBConnector.execute() for DDL operations.
        
        Args:
            schema: Complete table schema with constraints and business rules
            target: Database target (uses default if None)
            if_exists: Action when table exists
            
        Returns:
            TableOperationReport with creation details
        """
        raise NotImplementedError

    def create_table_with_relationships(
        self,
        schema: TableSchema,
        related_tables: List[str],
        *,
        target: Optional[Target] = None,
        establish_fks: bool = True
    ) -> TableOperationReport:
        """
        Create table and establish relationships with existing tables.
        
        Uses DBConnector.table_exists() and DBConnector.execute() for operations.
        
        Args:
            schema: Table schema definition
            related_tables: List of tables to establish relationships with
            target: Database target
            establish_fks: Create foreign key constraints
            
        Returns:
            TableOperationReport with relationship details
        """
        raise NotImplementedError

    def modify_table_schema(
        self,
        table_name: str,
        modifications: Dict[str, Any],
        *,
        target: Optional[Target] = None,
        backup_first: bool = True
    ) -> TableOperationReport:
        """
        Modify existing table schema with business logic considerations.
        
        Uses DBConnector.get_table_schema() and DBConnector.execute() for operations.
        
        Args:
            table_name: Name of table to modify
            modifications: Schema modifications to apply
            target: Database target
            backup_first: Create backup before modifications
            
        Returns:
            TableOperationReport with modification details
        """
        raise NotImplementedError

    def drop_table_with_dependencies(
        self,
        table_name: str,
        *,
        target: Optional[Target] = None,
        cascade: bool = False,
        backup_first: bool = True
    ) -> TableOperationReport:
        """
        Drop table while handling dependencies and relationships.
        
        Uses DBConnector.get_table_schema() and DBConnector.execute() for operations.
        
        Args:
            table_name: Name of table to drop
            target: Database target
            cascade: Drop dependent objects
            backup_first: Create backup before dropping
            
        Returns:
            TableOperationReport with drop operation details
        """
        raise NotImplementedError

    # -----------------------
    # Data Population Methods (4 methods)
    # -----------------------
    
    def append_with_validation(
        self,
        df: "pd.DataFrame",
        table_name: str,
        *,
        schema: Optional[str] = None,
        target: Optional[Target] = None,
        business_rules: Optional[List[Callable]] = None,
        options: Optional[PopulationOptions] = None
    ) -> UpsertOperationReport:
        """
        Append data with business rule validation and constraint checking.
        
        Uses DBConnector.insert_dataframe_with_report() for data insertion.
        
        Args:
            df: DataFrame to append
            table_name: Target table name
            schema: Database schema
            target: Database target
            business_rules: Business validation rules to apply
            options: Population configuration options
            
        Returns:
            UpsertOperationReport with append operation details
        """
        raise NotImplementedError

    def upsert_with_validation(
        self,
        df: "pd.DataFrame",
        table_name: str,
        config: UpsertConfig,
        *,
        schema: Optional[str] = None,
        target: Optional[Target] = None,
        business_rules: Optional[List[Callable]] = None
    ) -> UpsertOperationReport:
        """
        Perform intelligent upsert operations with business logic validation.
        
        Uses DBConnector.execute() and DBConnector.insert_dataframe_with_report().
        
        Args:
            df: DataFrame to upsert
            table_name: Target table name
            config: Upsert configuration
            schema: Database schema
            target: Database target
            business_rules: Business validation rules
            
        Returns:
            UpsertOperationReport with upsert operation details
        """
        raise NotImplementedError

    def replace_table_data(
        self,
        df: "pd.DataFrame",
        table_name: str,
        *,
        schema: Optional[str] = None,
        target: Optional[Target] = None,
        backup_first: bool = True,
        validate_schema: bool = True
    ) -> UpsertOperationReport:
        """
        Replace entire table data with business logic considerations.
        
        Uses DBConnector.execute() and DBConnector.insert_dataframe_with_report().
        
        Args:
            df: DataFrame with replacement data
            table_name: Target table name
            schema: Database schema
            target: Database target
            backup_first: Create backup before replacement
            validate_schema: Validate schema compatibility
            
        Returns:
            UpsertOperationReport with replacement operation details
        """
        raise NotImplementedError

    def populate_incrementally(
        self,
        df: "pd.DataFrame",
        table_name: str,
        timestamp_column: str,
        *,
        schema: Optional[str] = None,
        target: Optional[Target] = None,
        lookback_hours: int = 24
    ) -> UpsertOperationReport:
        """
        Populate table incrementally based on timestamp columns.
        
        Uses DBConnector.fetch_df() and DBConnector.insert_dataframe_with_report().
        
        Args:
            df: DataFrame with incremental data
            table_name: Target table name
            timestamp_column: Column used for incremental logic
            schema: Database schema
            target: Database target
            lookback_hours: Hours to look back for incremental updates
            
        Returns:
            UpsertOperationReport with incremental operation details
        """
        raise NotImplementedError

    # -----------------------
    # Relationship Management Methods (2 methods)
    # -----------------------
    
    def establish_relationships(
        self,
        relationships: List[RelationshipConfig],
        *,
        target: Optional[Target] = None,
        validate_integrity: bool = True
    ) -> List[TableOperationReport]:
        """
        Establish foreign key relationships between tables.
        
        Uses DBConnector.table_exists() and DBConnector.execute() for operations.
        
        Args:
            relationships: List of relationship configurations
            target: Database target
            validate_integrity: Validate referential integrity
            
        Returns:
            List of TableOperationReports for each relationship
        """
        raise NotImplementedError

    def validate_referential_integrity(
        self,
        table_name: str,
        *,
        schema: Optional[str] = None,
        target: Optional[Target] = None,
        fix_violations: bool = False
    ) -> Dict[str, Any]:
        """
        Validate and optionally fix referential integrity violations.
        
        Uses DBConnector.fetch_df() and DBConnector.execute() for operations.
        
        Args:
            table_name: Table to validate
            schema: Database schema
            target: Database target
            fix_violations: Attempt to fix violations automatically
            
        Returns:
            Validation results with violation details
        """
        raise NotImplementedError

    # -----------------------
    # Advanced Operations Methods (2 methods)
    # -----------------------
    
    def migrate_schema(
        self,
        migration_script: str,
        direction: MigrationDirection = "up",
        *,
        target: Optional[Target] = None,
        dry_run: bool = False
    ) -> TableOperationReport:
        """
        Execute database schema migrations with rollback capability.
        
        Uses DBConnector.execute() and DBConnector.transaction() for operations.
        
        Args:
            migration_script: SQL migration script
            direction: Migration direction (up/down)
            target: Database target
            dry_run: Test migration without executing
            
        Returns:
            TableOperationReport with migration details
        """
        raise NotImplementedError

    def optimize_table_performance(
        self,
        table_name: str,
        *,
        schema: Optional[str] = None,
        target: Optional[Target] = None,
        create_indexes: bool = True,
        update_statistics: bool = True
    ) -> TableOperationReport:
        """
        Optimize table performance through indexing and statistics.
        
        Uses DBConnector.get_table_schema() and DBConnector.execute() for operations.
        
        Args:
            table_name: Table to optimize
            schema: Database schema
            target: Database target
            create_indexes: Create performance indexes
            update_statistics: Update table statistics
            
        Returns:
            TableOperationReport with optimization details
        """
        raise NotImplementedError

    # -----------------------
    # COMPREHENSIVE SINGLE-CALL OPERATIONS (3 methods)
    # -----------------------

    def populate_with_comprehensive_setup(
        self,
        df: "pd.DataFrame",
        table_schema: TableSchema,
        relationships: Optional[List[RelationshipConfig]] = None,
        *,
        options: Optional[PopulationOptions] = None,
        business_rules: Optional[List[Callable]] = None,
    ) -> Tuple["pd.DataFrame", PopulationReport]:
        """
        COMPREHENSIVE: Complete table setup, population, and relationship establishment.
        
        Combines: create_table_with_relationships() + establish_relationships() + 
                  upsert_with_validation() + validate_referential_integrity() + 
                  optimize_table_performance() + comprehensive_reporting()
        
        Uses multiple DBConnector methods as infrastructure layer.
        
        Args:
            df: DataFrame to populate
            table_schema: Complete table schema definition
            relationships: Relationships to establish
            options: Population configuration options
            business_rules: Business validation rules
            
        Returns:
            Tuple of (processed_dataframe, comprehensive_population_report)
            
        Example:
            populator = DBPopulator(connector=connector)
            df_result, report = populator.populate_with_comprehensive_setup(
                df_clean, user_schema, relationships=[user_role_relationship]
            )
            
            print(f"✅ Table setup: {report.overall_success}")
            print(f"📊 Rows processed: {report.total_rows_processed}")
            print(f"🔗 Relationships: {len(report.relationships_created)}")
            print(f"⏱️  Total time: {report.total_execution_time_seconds:.2f}s")
        """
        raise NotImplementedError

    def sync_table_with_source(
        self,
        df: "pd.DataFrame",
        table_name: str,
        sync_config: Dict[str, Any],
        *,
        target: Optional[Target] = None,
        detect_schema_changes: bool = True,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        COMPREHENSIVE: Synchronize table with source data including schema evolution.
        
        Combines: modify_table_schema() + upsert_with_validation() + 
                  validate_referential_integrity() + optimize_table_performance() + 
                  comprehensive_change_tracking()
        
        Uses multiple DBConnector methods for infrastructure operations.
        
        Args:
            df: Source DataFrame
            table_name: Target table name
            sync_config: Synchronization configuration
            target: Database target
            detect_schema_changes: Automatically detect and apply schema changes
            
        Returns:
            Tuple of (sync_success, detailed_sync_report)
            
        Example:
            sync_config = {
                "key_columns": ["id"],
                "update_strategy": "upsert",
                "handle_deletes": True,
                "schema_evolution": "auto"
            }
            
            success, sync_report = populator.sync_table_with_source(
                df_new, "users", sync_config, detect_schema_changes=True
            )
            
            print(f"🔄 Sync status: {'✅ Success' if success else '❌ Failed'}")
            print(f"📈 Changes applied: {sync_report['changes_applied']}")
            print(f"🔧 Schema updates: {sync_report['schema_changes']}")
        """
        raise NotImplementedError

    def execute_complex_population_workflow(
        self,
        workflow_config: Dict[str, Any],
        data_sources: Dict[str, "pd.DataFrame"],
        *,
        target: Optional[Target] = None,
        rollback_on_failure: bool = True,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        COMPREHENSIVE: Execute complex multi-table population workflow with dependencies.
        
        Combines: create_table() + establish_relationships() + populate_incrementally() + 
                  validate_referential_integrity() + optimize_table_performance() + 
                  transaction_coordination() + comprehensive_workflow_reporting()
        
        Uses DBConnector.transaction() for workflow coordination.
        
        Args:
            workflow_config: Complete workflow configuration
            data_sources: Dictionary of table_name -> DataFrame mappings
            target: Database target
            rollback_on_failure: Rollback entire workflow on any failure
            
        Returns:
            Tuple of (workflow_success, comprehensive_workflow_report)
            
        Example:
            workflow_config = {
                "execution_order": ["users", "roles", "user_roles"],
                "table_dependencies": {
                    "user_roles": ["users", "roles"]
                },
                "population_strategies": {
                    "users": "upsert",
                    "roles": "append",
                    "user_roles": "replace"
                }
            }
            
            data_sources = {
                "users": df_users_clean,
                "roles": df_roles_clean, 
                "user_roles": df_user_roles_clean
            }
            
            success, workflow_report = populator.execute_complex_population_workflow(
                workflow_config, data_sources, rollback_on_failure=True
            )
            
            print(f"🏗️  Workflow: {'✅ Completed' if success else '❌ Failed'}")
            print(f"📋 Tables processed: {workflow_report['tables_completed']}")
            print(f"⚠️  Issues: {workflow_report['issues_encountered']}")
        """
        raise NotImplementedError

    # -----------------------
    # Utility and Reporting Methods
    # -----------------------
    
    def build_population_report(self) -> PopulationReport:
        """Build comprehensive population report from current operations."""
        raise NotImplementedError

    def get_table_dependencies(
        self,
        table_name: str,
        *,
        schema: Optional[str] = None,
        target: Optional[Target] = None
    ) -> Dict[str, List[str]]:
        """
        Get table dependencies for proper operation ordering.
        
        Uses DBConnector.get_table_schema() for dependency analysis.
        """
        raise NotImplementedError

    def validate_business_rules(
        self,
        df: "pd.DataFrame",
        rules: List[Callable],
        *,
        stop_on_first_failure: bool = False
    ) -> Dict[str, Any]:
        """Validate DataFrame against business rules."""
        raise NotImplementedError

    # -----------------------
    # Private/Internal Methods
    # -----------------------
    
    def _generate_upsert_sql(
        self,
        table_name: str,
        config: UpsertConfig,
        target: Target
    ) -> str:
        """Generate database-specific upsert SQL."""
        raise NotImplementedError

    def _validate_schema_compatibility(
        self,
        df: "pd.DataFrame",
        table_schema: TableSchema
    ) -> Dict[str, Any]:
        """Validate DataFrame schema against table schema."""
        raise NotImplementedError

    def _execute_with_connector(
        self,
        operation: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation using DBConnector with error handling."""
        raise NotImplementedError

    def _coordinate_transaction(
        self,
        operations: List[Callable],
        target: Target
    ) -> List[Any]:
        """Coordinate multiple operations within a single transaction."""
        raise NotImplementedError

    def _handle_constraint_violations(
        self,
        violations: List[Dict[str, Any]],
        table_name: str,
        action: str = "report"
    ) -> Dict[str, Any]:
        """Handle constraint violations with configurable actions."""
        raise NotImplementedError
