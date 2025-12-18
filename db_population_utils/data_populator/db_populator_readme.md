# DBPopulator - Database Business Logic Layer

## Overview

High-level database business logic module that uses DBConnector as infrastructure layer for complex database operations with domain-specific rules and multi-table coordination.

## Pipeline Integration

```
DataLoader → DataProcessor → DBConnector ← DBPopulator
```

**DBPopulator Role:**
- **Uses DBConnector**: As infrastructure layer for all database operations
- **Business Logic**: Applies domain-specific rules and complex coordination
- **High-Level Operations**: Table lifecycle, relationships, and advanced workflows
- **No Direct SQL**: Only business logic orchestration using DBConnector methods

## Key Features

🎯 **Business Logic Capabilities:**
- **Table Lifecycle Management**: Create, modify, and manage tables with business rules
- **Relationship Management**: Establish and maintain foreign key relationships
- **Advanced Upsert Operations**: Intelligent conflict resolution and validation
- **Schema Evolution**: Database migrations with business logic considerations
- **Multi-Table Coordination**: Complex workflows across related tables
- **Business Rule Enforcement**: Domain-specific validation and constraints

✅ **Infrastructure Integration:**
- **Uses DBConnector Methods**: All database operations through DBConnector
- **Comprehensive Operations**: Single-call methods for complex business scenarios
- **Transaction Coordination**: Multi-operation workflows with rollback capability
- **Performance Optimization**: Business-aware indexing and optimization
- **Detailed Reporting**: Business operation tracking and analysis

## Installation

```bash
# Required dependencies
pip install pandas sqlalchemy

# DBPopulator requires DBConnector from the same package
# Ensure db_population_utils package is properly installed
```

## Quick Start

### Basic Setup with DBConnector

```python
from db_population_utils import DBConnector
from db_population_utils.db_populator import DBPopulator, TableSchema

# Step 1: Setup infrastructure layer
connector = DBConnector(ingestion=ingestion_settings, app=app_settings)

# Step 2: Create business logic layer
populator = DBPopulator(connector=connector, verbose=True)

# Step 3: Define table schema with business rules
user_schema = TableSchema(
    table_name="users",
    columns={
        "id": "SERIAL PRIMARY KEY",
        "email": "VARCHAR(255) UNIQUE NOT NULL",
        "name": "VARCHAR(100) NOT NULL",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    },
    business_rules=[validate_email_format, check_name_length]
)

# Step 4: Create table with business logic
table_report = populator.create_table(user_schema)
print(f"✅ Table created: {table_report.success}")
```

### Complete Pipeline Integration

```python
from db_population_utils.data_loader import DataLoader
from db_population_utils.data_processor import DataProcessor
from db_population_utils import DBConnector
from db_population_utils.db_populator import DBPopulator

# Complete data pipeline with business logic
loader = DataLoader()
processor = DataProcessor()
connector = DBConnector()
populator = DBPopulator(connector=connector)

# Step 1: Load raw data
df_raw, load_report = loader.load_with_comprehensive_report("users.csv")

# Step 2: Transform data
if load_report.data_quality.quality_score > 80:
    df_clean, transform_report = processor.clean_data_with_comprehensive_report(df_raw)
    
    # Step 3: Apply business logic and populate database
    if transform_report.validation_passed:
        df_result, population_report = populator.populate_with_comprehensive_setup(
            df_clean, user_schema, relationships=user_relationships
        )
        
        if population_report.overall_success:
            print(f"✅ Pipeline completed: {population_report.total_rows_processed} rows processed")
        else:
            print(f"⚠️  Population issues: {population_report.warnings}")
    else:
        print(f"❌ Data validation failed: {transform_report.validation_errors}")
else:
    print(f"⚠️  Data quality too low: {load_report.data_quality.quality_score}/100")
```

## Core Methods

### Table Management (4 methods)

#### 1. Create Table with Business Rules

```python
# Define comprehensive table schema
user_schema = TableSchema(
    table_name="users",
    columns={
        "id": "SERIAL PRIMARY KEY",
        "email": "VARCHAR(255) UNIQUE NOT NULL",
        "name": "VARCHAR(100) NOT NULL",
        "department_id": "INTEGER REFERENCES departments(id)",
        "salary": "DECIMAL(10,2) CHECK (salary > 0)",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    },
    primary_key=["id"],
    indexes=[
        {"name": "idx_users_email", "columns": ["email"]},
        {"name": "idx_users_department", "columns": ["department_id"]}
    ],
    business_rules=[
        validate_email_format,
        validate_salary_range,
        check_department_exists
    ]
)

# Create table with business logic validation
table_report = populator.create_table(user_schema, if_exists="skip")

print(f"Table created: {table_report.success}")
print(f"Constraints: {table_report.constraints_created}")
print(f"Indexes: {table_report.indexes_created}")
```

#### 2. Create Table with Relationships

```python
# Create table and establish relationships with existing tables
related_tables = ["departments", "roles"]

table_report = populator.create_table_with_relationships(
    user_schema,
    related_tables=related_tables,
    establish_fks=True
)

print(f"Table created: {table_report.success}")
print(f"Relationships established: {table_report.relationships_established}")
```

#### 3. Modify Table Schema

```python
# Modify existing table with business considerations
schema_modifications = {
    "add_columns": {
        "phone": "VARCHAR(20)",
        "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    },
    "modify_columns": {
        "name": "VARCHAR(150)"  # Increase length
    },
    "add_indexes": [
        {"name": "idx_users_phone", "columns": ["phone"]}
    ]
}

modification_report = populator.modify_table_schema(
    "users", 
    modifications=schema_modifications,
    backup_first=True
)

print(f"Schema modified: {modification_report.success}")
print(f"Backup created: {'backup' in modification_report.notes}")
```

#### 4. Drop Table with Dependencies

```python
# Safely drop table while handling dependencies
drop_report = populator.drop_table_with_dependencies(
    "users",
    cascade=False,  # Don't cascade by default
    backup_first=True
)

print(f"Table dropped: {drop_report.success}")
if drop_report.warnings:
    print(f"Warnings: {drop_report.warnings}")
```

### Data Population (4 methods)

#### 1. Append with Business Validation

```python
# Define business rules for validation
def validate_user_data(df):
    """Validate user data meets business requirements."""
    # Email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    email_valid = df['email'].str.match(email_pattern).all()
    
    # Salary range validation
    salary_valid = (df['salary'] >= 30000) & (df['salary'] <= 200000)
    
    # Department existence (would check against database)
    dept_valid = df['department_id'].notna().all()
    
    return email_valid and salary_valid.all() and dept_valid

# Append data with business validation
append_report = populator.append_with_validation(
    df_new_users,
    table_name="users",
    business_rules=[validate_user_data],
    options=PopulationOptions(
        validation_level=ValidationLevel.BUSINESS_RULES,
        continue_on_constraint_violation=False
    )
)

print(f"Append success: {append_report.success}")
print(f"Rows inserted: {append_report.rows_inserted}")
print(f"Constraint violations: {append_report.constraint_violations}")
```

#### 2. Intelligent Upsert with Validation

```python
from db_population_utils.db_populator import UpsertConfig, UpsertStrategy

# Configure intelligent upsert
upsert_config = UpsertConfig(
    key_columns=["email"],  # Use email as unique identifier
    update_columns=["name", "salary", "department_id", "updated_at"],
    strategy=UpsertStrategy.NATIVE,  # Use database-native upsert
    conflict_resolution="update",
    validate_before_upsert=True,
    batch_size=1000
)

# Execute upsert with business logic
upsert_report = populator.upsert_with_validation(
    df_updated_users,
    table_name="users",
    config=upsert_config,
    business_rules=[validate_user_data, check_unique_constraints]
)

print(f"Upsert completed: {upsert_report.success}")
print(f"Rows inserted: {upsert_report.rows_inserted}")
print(f"Rows updated: {upsert_report.rows_updated}")
print(f"Rows skipped: {upsert_report.rows_skipped}")
print(f"Strategy used: {upsert_report.strategy_used}")
```

#### 3. Replace Table Data

```python
# Replace entire table data with business safeguards
replace_report = populator.replace_table_data(
    df_complete_users,
    table_name="users",
    backup_first=True,      # Create backup before replacement
    validate_schema=True    # Validate schema compatibility
)

print(f"Table replaced: {replace_report.success}")
print(f"Rows inserted: {replace_report.rows_inserted}")
if replace_report.warnings:
    print(f"Warnings: {replace_report.warnings}")
```

#### 4. Incremental Population

```python
# Populate incrementally based on timestamp
incremental_report = populator.populate_incrementally(
    df_recent_users,
    table_name="users",
    timestamp_column="created_at",
    lookback_hours=24  # Process last 24 hours
)

print(f"Incremental update: {incremental_report.success}")
print(f"New rows: {incremental_report.rows_inserted}")
print(f"Updated rows: {incremental_report.rows_updated}")
```

### Relationship Management (2 methods)

#### 1. Establish Relationships

```python
from db_population_utils.db_populator import RelationshipConfig, RelationshipType

# Define table relationships
relationships = [
    RelationshipConfig(
        source_table="users",
        target_table="departments", 
        relationship_type=RelationshipType.MANY_TO_ONE,
        source_columns=["department_id"],
        target_columns=["id"],
        on_delete="RESTRICT",
        on_update="CASCADE"
    ),
    RelationshipConfig(
        source_table="user_roles",
        target_table="users",
        relationship_type=RelationshipType.MANY_TO_ONE,
        source_columns=["user_id"],
        target_columns=["id"],
        on_delete="CASCADE"
    )
]

# Establish relationships with validation
relationship_reports = populator.establish_relationships(
    relationships,
    validate_integrity=True
)

for report in relationship_reports:
    print(f"Relationship {report.table_name}: {report.success}")
    print(f"Constraints created: {report.constraints_created}")
```

#### 2. Validate Referential Integrity

```python
# Validate and optionally fix referential integrity
integrity_report = populator.validate_referential_integrity(
    table_name="users",
    fix_violations=False  # Just report, don't fix automatically
)

print(f"Integrity check: {integrity_report['passed']}")
if integrity_report['violations']:
    print(f"Violations found: {len(integrity_report['violations'])}")
    for violation in integrity_report['violations']:
        print(f"  • {violation['description']}")
```

### Advanced Operations (2 methods)

#### 1. Schema Migration

```python
# Execute database schema migration
migration_script = """
    ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
    CREATE INDEX idx_users_last_login ON users(last_login);
    UPDATE users SET last_login = created_at WHERE last_login IS NULL;
"""

migration_report = populator.migrate_schema(
    migration_script,
    direction="up",
    dry_run=False  # Set to True to test without executing
)

print(f"Migration completed: {migration_report.success}")
print(f"Execution time: {migration_report.execution_time_seconds:.2f}s")
```

#### 2. Optimize Table Performance

```python
# Optimize table for better performance
optimization_report = populator.optimize_table_performance(
    table_name="users",
    create_indexes=True,     # Create performance indexes
    update_statistics=True   # Update table statistics
)

print(f"Optimization completed: {optimization_report.success}")
print(f"Indexes created: {optimization_report.indexes_created}")
```

## Comprehensive Operations

### 1. Complete Table Setup and Population

```python
# Single-call comprehensive setup with relationships and population
df_result, population_report = populator.populate_with_comprehensive_setup(
    df_clean_users,
    table_schema=user_schema,
    relationships=user_relationships,
    options=PopulationOptions(
        population_strategy=PopulationStrategy.UPSERT_SMART,
        validation_level=ValidationLevel.COMPREHENSIVE,
        establish_relationships=True,
        create_indexes=True
    ),
    business_rules=[validate_user_data, check_business_constraints]
)

print(f"✅ Setup completed: {population_report.overall_success}")
print(f"📊 Rows processed: {population_report.total_rows_processed}")
print(f"📝 Rows inserted: {population_report.total_rows_inserted}")
print(f"🔄 Rows updated: {population_report.total_rows_updated}")
print(f"🔗 Relationships: {len(population_report.relationships_created)}")
print(f"🛡️  Constraints: {len(population_report.constraints_enforced)}")
print(f"📈 Indexes: {len(population_report.indexes_created)}")
print(f"⏱️  Total time: {population_report.total_execution_time_seconds:.2f}s")

# Access detailed reports
for table_name, table_report in population_report.table_reports.items():
    print(f"Table {table_name}: {table_report.success}")
    if table_report.warnings:
        print(f"  Warnings: {table_report.warnings}")
```

### 2. Table Synchronization with Source

```python
# Synchronize table with source data including schema evolution
sync_config = {
    "key_columns": ["email"],
    "update_strategy": "upsert",
    "handle_deletes": True,
    "schema_evolution": "auto",
    "conflict_resolution": "source_wins"
}

success, sync_report = populator.sync_table_with_source(
    df_updated_users,
    table_name="users",
    sync_config=sync_config,
    detect_schema_changes=True
)

print(f"🔄 Sync status: {'✅ Success' if success else '❌ Failed'}")
print(f"📈 Changes applied: {sync_report['changes_applied']}")
print(f"🔧 Schema updates: {sync_report['schema_changes']}")
print(f"➕ Records added: {sync_report['records_added']}")
print(f"🔄 Records updated: {sync_report['records_updated']}")
print(f"➖ Records deleted: {sync_report['records_deleted']}")

if sync_report['conflicts']:
    print(f"⚠️  Conflicts resolved: {len(sync_report['conflicts'])}")
```

### 3. Complex Multi-Table Workflow

```python
# Execute complex workflow across multiple related tables
workflow_config = {
    "execution_order": ["departments", "roles", "users", "user_roles"],
    "table_dependencies": {
        "users": ["departments"],
        "user_roles": ["users", "roles"]
    },
    "population_strategies": {
        "departments": PopulationStrategy.APPEND_ONLY,
        "roles": PopulationStrategy.REPLACE_TABLE,
        "users": PopulationStrategy.UPSERT_SMART,
        "user_roles": PopulationStrategy.INCREMENTAL
    },
    "business_rules": {
        "users": [validate_user_data, check_department_exists],
        "user_roles": [validate_role_assignments, check_permissions]
    },
    "transaction_scope": "entire_workflow"  # Single transaction for all operations
}

# Data sources for each table
data_sources = {
    "departments": df_departments_clean,
    "roles": df_roles_clean,
    "users": df_users_clean,
    "user_roles": df_user_roles_clean
}

# Execute complex workflow
success, workflow_report = populator.execute_complex_population_workflow(
    workflow_config=workflow_config,
    data_sources=data_sources,
    rollback_on_failure=True
)

print(f"🏗️  Workflow: {'✅ Completed' if success else '❌ Failed'}")
print(f"📋 Tables processed: {workflow_report['tables_completed']}")
print(f"🔗 Dependencies resolved: {workflow_report['dependencies_satisfied']}")
print(f"⏱️  Total execution time: {workflow_report['total_time']:.2f}s")

if not success:
    print(f"❌ Failed at table: {workflow_report['failed_table']}")
    print(f"⚠️  Issues: {workflow_report['issues_encountered']}")
    if workflow_report['rollback_performed']:
        print("🔄 Rollback completed - database state restored")
```

## Configuration and Business Rules

### Population Options

```python
from db_population_utils.db_populator import (
    PopulationOptions, PopulationStrategy, ValidationLevel
)

# Configure comprehensive population behavior
options = PopulationOptions(
    # Core strategy
    population_strategy=PopulationStrategy.UPSERT_SMART,
    validation_level=ValidationLevel.COMPREHENSIVE,
    target="app",
    
    # Table management
    create_table_if_missing=True,
    create_schema_if_missing=True,
    backup_before_operation=True,
    
    # Relationship management  
    establish_relationships=True,
    validate_referential_integrity=True,
    create_indexes=True,
    
    # Performance settings
    batch_size=5000,
    parallel_processing=False,
    optimize_for_bulk_operations=True,
    
    # Error handling
    continue_on_constraint_violation=False,
    rollback_on_error=True,
    max_error_count=100
)

# Use options in population
df_result, report = populator.populate_with_comprehensive_setup(
    df_clean, schema, options=options
)
```

### Business Rules Definition

```python
# Define comprehensive business rules
def validate_email_format(df):
    """Validate email addresses follow business standards."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    valid_emails = df['email'].str.match(email_pattern)
    
    if not valid_emails.all():
        invalid_count = (~valid_emails).sum()
        return False, f"Found {invalid_count} invalid email addresses"
    
    return True, "All email addresses valid"

def validate_salary_range(df):
    """Validate salary ranges meet business requirements."""
    min_salary = 30000
    max_salary = 500000
    
    # Check for valid salary range
    valid_salaries = (df['salary'] >= min_salary) & (df['salary'] <= max_salary)
    
    if not valid_salaries.all():
        invalid_count = (~valid_salaries).sum()
        return False, f"Found {invalid_count} salaries outside valid range (${min_salary:,} - ${max_salary:,})"
    
    return True, "All salaries within valid range"

def check_department_exists(df):
    """Validate all departments exist in departments table."""
    # This would use DBConnector to check against database
    # For example purposes, showing the pattern
    valid_departments = ['IT', 'HR', 'Finance', 'Sales', 'Marketing']
    
    if 'department_code' in df.columns:
        invalid_depts = ~df['department_code'].isin(valid_departments)
        if invalid_depts.any():
            invalid_count = invalid_depts.sum()
            return False, f"Found {invalid_count} invalid department codes"
    
    return True, "All departments valid"

def validate_unique_constraints(df):
    """Validate business-level uniqueness constraints."""
    # Check email uniqueness
    email_duplicates = df['email'].duplicated().sum()
    if email_duplicates > 0:
        return False, f"Found {email_duplicates} duplicate email addresses"
    
    # Check employee ID uniqueness if present
    if 'employee_id' in df.columns:
        id_duplicates = df['employee_id'].duplicated().sum()
        if id_duplicates > 0:
            return False, f"Found {id_duplicates} duplicate employee IDs"
    
    return True, "All uniqueness constraints satisfied"

# Apply business rules in operations
business_rules = [
    validate_email_format,
    validate_salary_range,
    check_department_exists,
    validate_unique_constraints
]

# Use in upsert operation
upsert_report = populator.upsert_with_validation(
    df_users, "users", upsert_config, business_rules=business_rules
)
```

### Population Strategies

```python
# Different strategies for different scenarios

# 1. Append Only - for log-like data
PopulationStrategy.APPEND_ONLY
# - Never updates existing records
# - Fast for time-series or audit data
# - Good for event logging

# 2. Smart Upsert - for master data (default)
PopulationStrategy.UPSERT_SMART
# - Intelligent conflict resolution
# - Updates existing, inserts new
# - Preserves data integrity
# - Good for user data, products

# 3. Replace Table - for reference data
PopulationStrategy.REPLACE_TABLE
# - Completely replaces table contents
# - Good for lookup tables, configurations
# - Ensures data freshness

# 4. Incremental - for time-based updates
PopulationStrategy.INCREMENTAL
# - Updates based on timestamp columns
# - Efficient for large datasets
# - Good for transaction data

# Example usage
options = PopulationOptions(
    population_strategy=PopulationStrategy.UPSERT_SMART
)
```

## Error Handling

### Exception Hierarchy

```python
from db_population_utils.db_populator import (
    DBPopulatorError,              # Base exception
    TableManagementError,          # Table operations
    RelationshipError,             # Relationship issues
    UpsertError,                   # Data population issues
    BusinessRuleValidationError    # Business logic violations
)

try:
    # Execute complex population workflow
    success, report = populator.execute_complex_population_workflow(
        workflow_config, data_sources
    )
    
except TableManagementError as e:
    print(f"🏗️  Table management failed: {e}")
    # Handle table creation/modification issues
    # Maybe retry with simpler schema
    
except RelationshipError as e:
    print(f"🔗 Relationship setup failed: {e}")
    # Handle foreign key constraint issues
    # Maybe establish relationships later
    
except UpsertError as e:
    print(f"📊 Data population failed: {e}")
    # Handle data insertion/update issues
    # Maybe use fallback population strategy
    
except BusinessRuleValidationError as e:
    print(f"🛡️  Business rule validation failed: {e}")
    # Handle business logic violations
    # Maybe relax validation or fix data
    
except DBPopulatorError as e:
    print(f"⚙️  General business operation failed: {e}")
    # Handle other business logic errors
```

### Graceful Error Recovery

```python
def robust_population_workflow(df_clean, schema, relationships):
    """Robust population with multiple fallback strategies."""
    
    # Strategy 1: Try comprehensive setup
    try:
        df_result, report = populator.populate_with_comprehensive_setup(
            df_clean, schema, relationships,
            options=PopulationOptions(
                population_strategy=PopulationStrategy.UPSERT_SMART,
                validation_level=ValidationLevel.COMPREHENSIVE
            )
        )
        
        if report.overall_success:
            return df_result, report, "comprehensive"
            
    except (UpsertError, BusinessRuleValidationError):
        print("⚠️  Comprehensive setup failed, trying standard...")
    
    # Strategy 2: Try standard population without relationships
    try:
        table_report = populator.create_table(schema, if_exists="skip")
        upsert_report = populator.upsert_with_validation(
            df_clean, schema.table_name,
            UpsertConfig(key_columns=["email"]),
            business_rules=[validate_email_format]  # Reduced rules
        )
        
        if upsert_report.success:
            return df_clean, upsert_report, "standard"
            
    except UpsertError:
        print("⚠️  Standard population failed, trying basic...")
    
    # Strategy 3: Basic append with minimal validation
    try:
        append_report = populator.append_with_validation(
            df_clean, schema.table_name,
            options=PopulationOptions(
                validation_level=ValidationLevel.BASIC,
                continue_on_constraint_violation=True
            )
        )
        
        return df_clean, append_report, "basic"
        
    except DBPopulatorError as e:
        print(f"❌ All population strategies failed: {e}")
        raise

# Usage
try:
    df_result, report, strategy = robust_population_workflow(
        df_clean, user_schema, user_relationships
    )
    print(f"✅ Population completed using {strategy} strategy")
    
except DBPopulatorError:
    print("❌ Population completely failed")
```

## Performance Optimization

### Large Dataset Handling

```python
# Configure for high-performance bulk operations
bulk_options = PopulationOptions(
    population_strategy=PopulationStrategy.UPSERT_SMART,
    batch_size=10000,                    # Large batches
    parallel_processing=True,            # Enable parallelization
    optimize_for_bulk_operations=True,   # Bulk-specific optimizations
    create_indexes=False,                # Create indexes after bulk load
    validate_referential_integrity=False # Skip during bulk load
)

# Execute bulk population
df_result, report = populator.populate_with_comprehensive_setup(
    df_large_dataset, schema, options=bulk_options
)

# Create indexes after bulk load for better performance
if report.overall_success:
    optimization_report = populator.optimize_table_performance(
        schema.table_name,
        create_indexes=True,
        update_statistics=True
    )
    print(f"📈 Post-load optimization: {optimization_report.success}")
```

### Performance Monitoring

```python
# Monitor business operation performance
df_result, report = populator.populate_with_comprehensive_setup(
    df_data, schema, relationships
)

# Analyze performance metrics
print(f"📊 Performance Analysis:")
print(f"  Total execution time: {report.total_execution_time_seconds:.2f}s")
print(f"  Average throughput: {report.average_throughput_rows_per_sec:.0f} rows/sec")
print(f"  Total rows processed: {report.total_rows_processed:,}")

# Table-level performance
for table_name, table_report in report.table_reports.items():
    print(f"  {table_name}: {table_report.execution_time_seconds:.2f}s")
    
# Identify bottlenecks
if report.total_execution_time_seconds > 60:
    print("⚠️  Long execution time detected")
    report.recommendations.append("Consider batch processing or performance optimization")

# Business operation recommendations
if report.recommendations:
    print(f"\n💡 Performance Recommendations:")
    for rec in report.recommendations:
        print(f"  • {rec}")
```

## Convenience Functions

```python
from db_population_utils.db_populator import (
    create_business_populator,
    setup_table_with_relationships,
    execute_upsert_workflow,
    validate_business_logic,
    check_population_capabilities
)

# Quick business populator setup
populator = create_business_populator(
    connector,
    validation_level=ValidationLevel.COMPREHENSIVE,
    default_target="app"
)

# Quick table setup with relationships
success, setup_report = setup_table_with_relationships(
    connector, user_schema, user_relationships
)

# Quick upsert workflow
success, upsert_report = execute_upsert_workflow(
    connector, df_users, "users", upsert_config, business_rules
)

# Standalone business logic validation
validation_results = validate_business_logic(
    df_users, [validate_email_format, validate_salary_range]
)

# Check available capabilities
capabilities = check_population_capabilities()
print(f"DBConnector integration: {capabilities['db_connector_available']}")
print(f"Advanced upsert support: {capabilities['advanced_upsert']}")
```

## Advanced Use Cases

### Custom Business Rule Development

```python
# Develop sophisticated business rules
class UserBusinessRules:
    def __init__(self, connector):
        self.connector = connector
    
    def validate_department_capacity(self, df):
        """Check if departments can accommodate new users."""
        # Use connector to check current department sizes
        current_counts = self.connector.fetch_df("""
            SELECT department_id, COUNT(*) as current_count 
            FROM users 
            GROUP BY department_id
        """)
        
        # Check department limits (business rule)
        dept_limits = {'IT': 50, 'HR': 20, 'Finance': 30}
        
        for dept_id in df['department_id'].unique():
            current = current_counts[current_counts['department_id'] == dept_id]['current_count'].iloc[0] if not current_counts.empty else 0
            new_additions = (df['department_id'] == dept_id).sum()
            limit = dept_limits.get(dept_id, float('inf'))
            
            if current + new_additions > limit:
                return False, f"Department {dept_id} would exceed capacity limit of {limit}"
        
        return True, "All departments within capacity"
    
    def validate_salary_equity(self, df):
        """Ensure salary equity within roles."""
        # Business rule: salary variance within same role should be reasonable
        for role in df['role'].unique():
            role_salaries = df[df['role'] == role]['salary']
            if len(role_salaries) > 1:
                salary_range = role_salaries.max() - role_salaries.