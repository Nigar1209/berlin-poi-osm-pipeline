# db_population_utils/db_populator/__init__.py

"""
DBPopulator Module - Database Business Logic Layer

This module provides high-level database business logic operations using DBConnector
as the underlying infrastructure layer for all database operations.

Main Components:
- DBPopulator: Core business logic class for complex database operations
- Configuration classes for table schemas, relationships, and business rules
- Report classes for comprehensive operation analysis and tracking
- Custom exceptions for robust business logic error handling

Pipeline Integration:
DataLoader → DataProcessor → DBConnector ← DBPopulator

DBPopulator Philosophy:
DBPopulator focuses on BUSINESS LOGIC - high-level database operations with domain-specific
rules and complex multi-table coordination. Uses DBConnector as infrastructure layer for
all actual database operations. No direct SQL - only business logic and orchestration.

Usage Examples:
    # Basic business logic operations
    from db_population_utils.db_populator import DBPopulator, TableSchema
    from db_population_utils import DBConnector
    
    connector = DBConnector()
    populator = DBPopulator(connector=connector)
    
    # Create table with business rules
    schema = TableSchema(
        table_name="users",
        columns={"id": "INTEGER", "email": "VARCHAR(255)", "created_at": "TIMESTAMP"},
        primary_key=["id"],
        business_rules=[validate_email_format, check_user_permissions]
    )
    report = populator.create_table(schema)
    
    # Comprehensive population with relationships
    df_result, population_report = populator.populate_with_comprehensive_setup(
        df_clean, user_schema, relationships=[user_role_relationship]
    )
    
    # Complex multi-table workflow
    success, workflow_report = populator.execute_complex_population_workflow(
        workflow_config, data_sources, rollback_on_failure=True
    )
"""

# Core business logic components
from .db_populator import (
    # Core class
    DBPopulator,
    
    # Configuration classes
    TableSchema,
    RelationshipConfig,
    UpsertConfig,
    PopulationOptions,
    
    # Report classes
    PopulationReport,
    TableOperationReport,
    UpsertOperationReport,
    
    # Type definitions and enums
    PopulationStrategy,
    ValidationLevel,
    ConstraintType,
    Target,
    UpsertStrategy,
    RelationshipType,
    MigrationDirection,
    
    # Custom exceptions
    DBPopulatorError,
    TableManagementError,
    RelationshipError,
    UpsertError,
    BusinessRuleValidationError,
)

# Module metadata
__version__ = "0.3.0"
__author__ = "Data Engineering Team"
__description__ = "Database business logic operations using DBConnector infrastructure"

# Public API - DBPopulator related components
__all__ = [
    # Core class
    "DBPopulator",
    
    # Configuration classes
    "TableSchema",
    "RelationshipConfig",
    "UpsertConfig", 
    "PopulationOptions",
    
    # Report classes
    "PopulationReport",
    "TableOperationReport",
    "UpsertOperationReport",
    
    # Type definitions
    "PopulationStrategy",
    "ValidationLevel",
    "ConstraintType",
    "Target",
    "UpsertStrategy",
    "RelationshipType", 
    "MigrationDirection",
    
    # Exceptions
    "DBPopulatorError",
    "TableManagementError",
    "RelationshipError",
    "UpsertError",
    "BusinessRuleValidationError",
    
    # Module info
    "__version__",
    
    # Convenience functions
    "create_business_populator",
    "setup_table_with_relationships",
    "execute_upsert_workflow",
    "validate_business_logic",
]

# DBPopulator-specific convenience functions
def create_business_populator(
    connector,  # DBConnector instance
    default_target: Target = "app",
    validation_level: ValidationLevel = ValidationLevel.BUSINESS_RULES,
    verbose: bool = True,
    **kwargs
) -> DBPopulator:
    """
    Create DBPopulator with business-focused configuration.
    
    Uses DBConnector as infrastructure layer for all database operations.
    
    Args:
        connector: DBConnector instance for infrastructure operations
        default_target: Default database target
        validation_level: Default business validation level
        verbose: Enable detailed logging
        **kwargs: Additional DBPopulator arguments
        
    Returns:
        Configured DBPopulator instance optimized for business operations
        
    Example:
        # Standard business populator
        connector = DBConnector()
        populator = create_business_populator(
            connector,
            validation_level=ValidationLevel.COMPREHENSIVE,
            verbose=True
        )
        
        # Conservative populator for critical operations
        populator = create_business_populator(
            connector,
            validation_level=ValidationLevel.COMPREHENSIVE,
            default_target="app"
        )
        
        # High-performance populator for bulk operations
        populator = create_business_populator(
            connector,
            validation_level=ValidationLevel.BASIC,
            default_target="ingestion"
        )
    """
    return DBPopulator(
        connector=connector,
        verbose=verbose,
        default_target=default_target,
        **kwargs
    )


def setup_table_with_relationships(
    connector,  # DBConnector instance
    table_schema: TableSchema,
    relationships: Optional[List[RelationshipConfig]] = None,
    target: Target = "app",
    **setup_options
) -> tuple:
    """
    Complete table setup utility with relationships and business logic.
    
    Args:
        connector: DBConnector instance
        table_schema: Complete table schema with business rules
        relationships: Relationships to establish
        target: Database target
        **setup_options: Additional setup options
        
    Returns:
        Tuple of (setup_success, comprehensive_setup_report)
        
    Example:
        # Define table schema with business rules
        user_schema = TableSchema(
            table_name="users",
            columns={
                "id": "SERIAL PRIMARY KEY",
                "email": "VARCHAR(255) UNIQUE NOT NULL",
                "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            },
            business_rules=[validate_email_format, check_permissions]
        )
        
        # Define relationships
        user_role_relationship = RelationshipConfig(
            source_table="user_roles",
            target_table="users", 
            relationship_type=RelationshipType.MANY_TO_ONE,
            source_columns=["user_id"],
            target_columns=["id"]
        )
        
        # Setup table with relationships
        success, report = setup_table_with_relationships(
            connector, user_schema, [user_role_relationship]
        )
        
        print(f"✅ Table setup: {success}")
        print(f"🔗 Relationships created: {len(report.relationships_created)}")
        print(f"🛡️  Constraints enforced: {len(report.constraints_enforced)}")
    """
    # Create populator
    populator = create_business_populator(connector, default_target=target, verbose=False)
    
    try:
        # Create table with relationships
        table_report = populator.create_table_with_relationships(
            table_schema,
            related_tables=[rel.target_table for rel in relationships] if relationships else [],
            target=target,
            establish_fks=True
        )
        
        # Establish additional relationships if specified
        relationship_reports = []
        if relationships:
            relationship_reports = populator.establish_relationships(
                relationships,
                target=target,
                validate_integrity=True
            )
        
        # Build comprehensive report
        setup_report = {
            "table_created": table_report.success,
            "table_report": table_report,
            "relationships_created": [r.relationships_established for r in relationship_reports],
            "constraints_enforced": table_report.constraints_created,
            "indexes_created": table_report.indexes_created,
            "overall_success": table_report.success and all(r.success for r in relationship_reports),
            "execution_time_seconds": table_report.execution_time_seconds,
            "warnings": table_report.warnings,
            "errors": table_report.errors
        }
        
        return setup_report["overall_success"], setup_report
        
    except Exception as e:
        error_report = {
            "table_created": False,
            "overall_success": False,
            "error": str(e),
            "relationships_created": [],
            "constraints_enforced": [],
            "indexes_created": []
        }
        raise DBPopulatorError(f"Table setup failed: {str(e)}") from e


def execute_upsert_workflow(
    connector,  # DBConnector instance
    df,  # pandas.DataFrame
    table_name: str,
    upsert_config: UpsertConfig,
    business_rules: Optional[List[Callable]] = None,
    target: Target = "app",
    **workflow_options
) -> tuple:
    """
    Execute comprehensive upsert workflow with business logic validation.
    
    Args:
        connector: DBConnector instance
        df: DataFrame to upsert
        table_name: Target table name
        upsert_config: Upsert configuration
        business_rules: Business validation rules
        target: Database target
        **workflow_options: Additional workflow options
        
    Returns:
        Tuple of (upsert_success, detailed_upsert_report)
        
    Example:
        # Define upsert configuration
        upsert_config = UpsertConfig(
            key_columns=["email"],
            update_columns=["name", "updated_at"],
            strategy=UpsertStrategy.NATIVE,
            conflict_resolution="update",
            validate_before_upsert=True
        )
        
        # Define business rules
        def validate_email_format(df):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return df['email'].str.match(email_pattern).all()
        
        def check_user_status(df):
            return df['status'].isin(['active', 'inactive', 'pending']).all()
        
        # Execute upsert workflow
        success, upsert_report = execute_upsert_workflow(
            connector, df_users, "users", upsert_config,
            business_rules=[validate_email_format, check_user_status]
        )
        
        print(f"🔄 Upsert: {'✅ Success' if success else '❌ Failed'}")
        print(f"📊 Inserted: {upsert_report.rows_inserted}")
        print(f"🔄 Updated: {upsert_report.rows_updated}")
        print(f"⚠️  Violations: {upsert_report.constraint_violations}")
    """
    # Create populator
    populator = create_business_populator(connector, default_target=target, verbose=False)
    
    try:
        # Execute upsert with validation
        upsert_report = populator.upsert_with_validation(
            df,
            table_name,
            upsert_config,
            target=target,
            business_rules=business_rules
        )
        
        return upsert_report.success, upsert_report
        
    except Exception as e:
        error_report = UpsertOperationReport(
            table_name=table_name,
            strategy_used=upsert_config.strategy,
            success=False,
            errors=[str(e)]
        )
        raise UpsertError(f"Upsert workflow failed: {str(e)}") from e


def validate_business_logic(
    df,  # pandas.DataFrame
    business_rules: List[Callable],
    table_name: Optional[str] = None,
    stop_on_first_failure: bool = False,
    **validation_options
) -> dict:
    """
    Validate DataFrame against business rules without database operations.
    
    Args:
        df: DataFrame to validate
        business_rules: List of business validation functions
        table_name: Table name for context (optional)
        stop_on_first_failure: Stop validation on first rule failure
        **validation_options: Additional validation options
        
    Returns:
        Business logic validation results
        
    Example:
        # Define business rules
        def validate_required_fields(df):
            required_fields = ['id', 'email', 'name']
            missing_fields = [field for field in required_fields if field not in df.columns]
            return len(missing_fields) == 0, f"Missing required fields: {missing_fields}"
        
        def validate_email_uniqueness(df):
            duplicates = df['email'].duplicated().sum()
            return duplicates == 0, f"Found {duplicates} duplicate emails"
        
        def validate_data_types(df):
            # Check if id is numeric
            try:
                pd.to_numeric(df['id'])
                return True, "Data types valid"
            except:
                return False, "Invalid data types detected"
        
        # Validate business logic
        rules = [validate_required_fields, validate_email_uniqueness, validate_data_types]
        validation_results = validate_business_logic(
            df_users, rules, table_name="users", stop_on_first_failure=False
        )
        
        print(f"🔍 Validation: {'✅ Passed' if validation_results['all_passed'] else '❌ Failed'}")
        print(f"📋 Rules checked: {validation_results['total_rules']}")
        print(f"✅ Passed: {validation_results['rules_passed']}")
        print(f"❌ Failed: {validation_results['rules_failed']}")
        
        if validation_results['failures']:
            print("⚠️  Rule failures:")
            for rule_name, failure_reason in validation_results['failures'].items():
                print(f"  • {rule_name}: {failure_reason}")
    """
    validation_results = {
        "table_name": table_name,
        "total_rules": len(business_rules),
        "rules_passed": 0,
        "rules_failed": 0,
        "all_passed": True,
        "failures": {},
        "warnings": [],
        "execution_time_seconds": 0.0
    }
    
    start_time = time.time()
    
    try:
        for rule in business_rules:
            rule_name = rule.__name__ if hasattr(rule, '__name__') else str(rule)
            
            try:
                # Execute business rule
                result = rule(df)
                
                # Handle different return types
                if isinstance(result, bool):
                    rule_passed = result
                    failure_reason = "Rule returned False"
                elif isinstance(result, tuple) and len(result) == 2:
                    rule_passed, failure_reason = result
                else:
                    rule_passed = bool(result)
                    failure_reason = "Rule validation failed"
                
                if rule_passed:
                    validation_results["rules_passed"] += 1
                else:
                    validation_results["rules_failed"] += 1
                    validation_results["all_passed"] = False
                    validation_results["failures"][rule_name] = failure_reason
                    
                    if stop_on_first_failure:
                        break
                        
            except Exception as e:
                validation_results["rules_failed"] += 1
                validation_results["all_passed"] = False
                validation_results["failures"][rule_name] = f"Rule execution error: {str(e)}"
                validation_results["warnings"].append(f"Rule {rule_name} raised exception: {str(e)}")
                
                if stop_on_first_failure:
                    break
        
        validation_results["execution_time_seconds"] = time.time() - start_time
        
        return validation_results
        
    except Exception as e:
        validation_results["execution_time_seconds"] = time.time() - start_time
        validation_results["all_passed"] = False
        validation_results["failures"]["validation_system"] = f"Validation system error: {str(e)}"
        raise BusinessRuleValidationError(f"Business logic validation failed: {str(e)}") from e


# Optional: Add logging configuration
import logging
import sys
import warnings
from typing import List, Optional, Any, Callable
import time

# Set up module logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Check for required dependencies
_ESSENTIAL_DEPENDENCIES = {
    'pandas': "pip install pandas>=1.3.0", 
    'sqlalchemy': "pip install sqlalchemy>=1.4.0"
}

_BUSINESS_LOGIC_DEPENDENCIES = {
    'db_connector': "DBConnector must be available in db_population_utils",
    'data_processor': "DataProcessor integration for clean data input"
}

# Check essential dependencies
for dep, install_cmd in _ESSENTIAL_DEPENDENCIES.items():
    try:
        __import__(dep)
    except ImportError:
        warnings.warn(
            f"CRITICAL: Required dependency '{dep}' not found. Install with: {install_cmd}",
            ImportWarning,
            stacklevel=2
        )

def check_population_capabilities() -> dict:
    """
    Check which database population capabilities are available.
    
    Returns:
        Dictionary with capability status and integration health
        
    Example:
        capabilities = check_population_capabilities()
        print(f"DBConnector integration: {capabilities['db_connector_available']}")
        print(f"Business logic validation: {capabilities['business_validation']}")
        print(f"Advanced upsert support: {capabilities['advanced_upsert']}")
        print(f"Migration capabilities: {capabilities['schema_migration']}")
    """
    capabilities = {
        'basic_population': True,  # Always available with pandas
        'db_connector_available': False,
        'business_validation': True,  # Available with core Python
        'advanced_upsert': False,
        'schema_migration': False,
        'relationship_management': False,
        'missing_components': []
    }
    
    # Check DBConnector availability
    try:
        from ..db_connector import DBConnector
        capabilities['db_connector_available'] = True
        capabilities['advanced_upsert'] = True
        capabilities['schema_migration'] = True
        capabilities['relationship_management'] = True
    except ImportError:
        capabilities['missing_components'].append({
            'component': 'DBConnector',
            'impact': 'DBPopulator cannot function without DBConnector infrastructure',
            'required': True
        })
    
    # Check DataProcessor integration
    try:
        from ..data_processor import DataProcessor
        capabilities['data_processor_integration'] = True
    except ImportError:
        capabilities['missing_components'].append({
            'component': 'DataProcessor',
            'impact': 'Reduced integration capabilities for clean data processing',
            'required': False
        })
    
    # Check SQLAlchemy features
    try:
        import sqlalchemy
        version = tuple(map(int, sqlalchemy.__version__.split('.')[:2]))
        if version >= (1, 4):
            capabilities['modern_sqlalchemy'] = True
        else:
            capabilities['missing_components'].append({
                'component': 'SQLAlchemy >= 1.4',
                'impact': 'Some advanced database features may not be available',
                'required': False
            })
    except ImportError:
        capabilities['missing_components'].append({
            'component': 'SQLAlchemy',
            'impact': 'Database operations not available',
            'required': True
        })
    
    return capabilities

def _check_dependency(dep_name: str) -> bool:
    """Check if dependency is available."""
    try:
        __import__(dep_name)
        return True
    except ImportError:
        return False

# Export dependency checker
__all__.append("check_population_capabilities")

# Pipeline integration examples and best practices
"""
DBPopulator - Pipeline Integration Examples

Complete Pipeline Architecture:
    DataLoader → DataProcessor → DBConnector ← DBPopulator
    
    # Step 1: Load raw data (DataLoader)
    loader = DataLoader()
    df_raw, load_report = loader.load_with_comprehensive_report("data.csv")
    
    # Step 2: Transform data (DataProcessor)
    processor = DataProcessor()
    df_clean, transform_report = processor.clean_data_with_comprehensive_report(df_raw)
    
    # Step 3: Database infrastructure (DBConnector)
    connector = DBConnector()
    
    # Step 4: Business logic operations (DBPopulator)
    populator = DBPopulator(connector=connector)
    df_result, population_report = populator.populate_with_comprehensive_setup(
        df_clean, table_schema, relationships=relationships
    )

Business Logic Focused Operations:
    # DBPopulator handles business logic, uses DBConnector for infrastructure
    populator = DBPopulator(connector=connector)
    
    # High-level business operations
    table_report = populator.create_table_with_relationships(schema, related_tables)
    upsert_report = populator.upsert_with_validation(df, table, config, business_rules)
    migration_report = populator.migrate_schema(migration_script, direction="up")
    
    # Complex workflows
    success, workflow_report = populator.execute_complex_population_workflow(
        workflow_config, data_sources, rollback_on_failure=True
    )

Table Schema with Business Rules:
    # Define comprehensive table schema
    user_schema = TableSchema(
        table_name="users",
        columns={
            "id": "SERIAL PRIMARY KEY",
            "email": "VARCHAR(255) UNIQUE NOT NULL", 
            "name": "VARCHAR(100) NOT NULL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "status": "VARCHAR(20) DEFAULT 'active'"
        },
        primary_key=["id"],
        indexes=[
            {"name": "idx_users_email", "columns": ["email"]},
            {"name": "idx_users_status", "columns": ["status"]}
        ],
        business_rules=[
            validate_email_format,
            check_name_length,
            validate_status_values
        ]
    )

Relationship Management:
    # Define table relationships
    relationships = [
        RelationshipConfig(
            source_table="user_roles",
            target_table="users",
            relationship_type=RelationshipType.MANY_TO_ONE,
            source_columns=["user_id"], 
            target_columns=["id"],
            on_delete="CASCADE"
        ),
        RelationshipConfig(
            source_table="user_roles", 
            target_table="roles",
            relationship_type=RelationshipType.MANY_TO_ONE,
            source_columns=["role_id"],
            target_columns=["id"]
        )
    ]
    
    # Establish relationships with validation
    relationship_reports = populator.establish_relationships(
        relationships, validate_integrity=True
    )

Upsert Operations with Business Logic:
    # Configure intelligent upsert
    upsert_config = UpsertConfig(
        key_columns=["email"],
        update_columns=["name", "status", "updated_at"],
        strategy=UpsertStrategy.NATIVE,
        conflict_resolution="update",
        validate_before_upsert=True
    )
    
    # Business validation rules
    def validate_user_data(df):
        # Email format validation
        email_valid = df['email'].str.match(r'^[^@]+@[^@]+\.[^@]+$').all()
        # Status validation
        status_valid = df['status'].isin(['active', 'inactive', 'pending']).all()
        return email_valid and status_valid
    
    # Execute upsert with business logic
    upsert_report = populator.upsert_with_validation(
        df_users, "users", upsert_config, business_rules=[validate_user_data]
    )

Complex Multi-Table Workflows:
    # Define workflow configuration
    workflow_config = {
        "execution_order": ["departments", "users", "roles", "user_roles"],
        "table_dependencies": {
            "users": ["departments"],
            "user_roles": ["users", "roles"]
        },
        "population_strategies": {
            "departments": PopulationStrategy.APPEND_ONLY,
            "users": PopulationStrategy.UPSERT_SMART,
            "roles": PopulationStrategy.REPLACE_TABLE,
            "user_roles": PopulationStrategy.INCREMENTAL
        },
        "business_rules": {
            "users": [validate_email, check_department_exists],
            "user_roles": [validate_role_permissions]
        }
    }
    
    # Data sources for each table
    data_sources = {
        "departments": df_departments_clean,
        "users": df_users_clean,
        "roles": df_roles_clean,
        "user_roles": df_user_roles_clean
    }
    
    # Execute complex workflow
    success, workflow_report = populator.execute_complex_population_workflow(
        workflow_config, data_sources, rollback_on_failure=True
    )

Error Handling and Recovery:
    try:
        # Attempt comprehensive population
        df_result, report = populator.populate_with_comprehensive_setup(
            df_clean, schema, relationships
        )
        
        if not report.overall_success:
            # Handle partial failures
            print(f"⚠️  Partial success: {report.warnings}")
            
    except TableManagementError as e:
        # Handle table creation/modification issues
        print(f"🏗️  Table management failed: {e}")
        
    except RelationshipError as e:
        # Handle relationship establishment issues  
        print(f"🔗 Relationship setup failed: {e}")
        
    except UpsertError as e:
        # Handle data population issues
        print(f"📊 Data population failed: {e}")
        
    except BusinessRuleValidationError as e:
        # Handle business logic violations
        print(f"🛡️  Business rule validation failed: {e}")
        
    except DBPopulatorError as e:
        # Handle general business logic errors
        print(f"⚙️  Business operation failed: {e}")

Performance Optimization:
    # Configure for high-performance bulk operations
    options = PopulationOptions(
        population_strategy=PopulationStrategy.UPSERT_SMART,
        batch_size=10000,
        parallel_processing=True,
        optimize_for_bulk_operations=True,
        create_indexes=False  # Create indexes after bulk load
    )
    
    # Execute with performance options
    df_result, report = populator.populate_with_comprehensive_setup(
        df_large, schema, options=options
    )
    
    # Create indexes after bulk load for better performance
    optimization_report = populator.optimize_table_performance(
        table_name, create_indexes=True, update_statistics=True
    )

Business Rule Validation:
    # Define comprehensive business rules
    def validate_user_business_rules(df):
        rules_passed = []
        
        # Email uniqueness
        email_unique = df['email'].nunique() == len(df)
        rules_passed.append(("email_uniqueness", email_unique))
        
        # Valid department codes
        valid_departments = df['department_code'].isin(['IT', 'HR', 'FINANCE', 'SALES']).all()
        rules_passed.append(("valid_departments", valid_departments))
        
        # Salary ranges
        salary_valid = (df['salary'] >= 30000) & (df['salary'] <= 200000)
        rules_passed.append(("salary_range", salary_valid.all()))
        
        return all(passed for _, passed in rules_passed), rules_passed
    
    # Apply business rules in population
    upsert_report = populator.upsert_with_validation(
        df_users, "users", upsert_config, 
        business_rules=[validate_user_business_rules]
    )
"""