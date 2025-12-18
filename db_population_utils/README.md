
# DB Population Utilities (Design – Step 1)

Reusable building blocks for consistent data ingestion across layers (banks, hospitals, schools, etc.).  
**This PR ships design stubs + a minimal working connector; full features land in Step 2.**

---

## Repository layout

```
.
├── db_population_utils/
│   ├── __init__.py
│   ├── db_connector/
│   │   ├── __init__.py
│   │   ├── db_connector.py
│   │   └── README.md
│   ├── data_loader/
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   └── README.md
│   ├── data_processor/
│   │   ├── __init__.py
│   │   ├── data_processor.py
│   │   └── README.md
│   ├── db_populater/
│   │   ├── __init__.py
│   │   ├── db_populater.py
│   │   └── README.md
│   └── schema_tools/
│       ├── __init__.py
│       ├── schema_tools.py
│       └── README.md
├── examples/
│   ├── example_usage.py
│   └── example_data_loader.py
├── tests/
│   ├── test_db_connector_design.py
│   └── test_data_loader_design.py
└── README.md


````

---

## Components (planned)

- **DBConnector** *(MVP implemented)*: pooled connections for `ingestion` & `app`, health check, SQL exec, DataFrame I/O.
- **DataLoader** *(design stub)*: robust loading for CSV/TSV, Excel, JSON (encoding/delimiter sniffing, JSON flattening, datetime+TZ handling).
- **DataProcessor** *(design stub)*: common preprocessing (standardize columns, type coercion, nulls, dedupe, validation).
- **DBPopulater** *(design stub)*: table creation and append (upsert in Step 2) using DBConnector.
- **Schema tools** *(design stub)*: optional helpers to infer SQL types, generate DDL, and export schema docs/ERD.

---

## Configuration

Prefer **environment variables** (CI-friendly):

**Ingestion DB**
- `INGESTION_DB_URL` **or**
- `INGESTION_DB_DRIVER`, `_HOST`, `_PORT`, `_USER`, `_PASSWORD`, `_DATABASE`
- optional: `INGESTION_DB_SSLMODE`, pooling vars: `_POOL_SIZE`, `_MAX_OVERFLOW`, `_POOL_TIMEOUT`

**Application DB**
- `APP_DB_URL` **or**
- `APP_DB_DRIVER`, `_HOST`, `_PORT`, `_USER`, `_PASSWORD`, `_DATABASE`
- optional: `APP_DB_SSLMODE`, pooling vars

SQLite quick start:
```bash
export INGESTION_DB_URL="sqlite:///:memory:"
````

---

## Quick start

**DBConnector (works now)**

```python
from db_population_utils import DBConnector
import pandas as pd

dbc = DBConnector()
print(dbc.test_connection("ingestion"))  # {'ok': True, ...}

dbc.execute("CREATE TABLE demo (id INTEGER PRIMARY KEY, name TEXT)", target="ingestion")
dbc.to_sql(pd.DataFrame([{"id": 1, "name": "Alice"}]), "demo", target="ingestion")
print(dbc.fetch_df("SELECT * FROM demo", target="ingestion"))
```

**DataLoader (design stub; implement in Step 2)**

```python
# from db_population_utils import DataLoader, LoadOptions
# dl = DataLoader(verbose=True)
# df = dl.load("path/to/file.csv", options=LoadOptions(kind="csv"))
# print(dl.build_report())
```

---

## Testing

Uses in-memory SQLite for design smoke tests:

```bash
pytest -q
```

---

## Roadmap

* **Step 2: Implementation**

  * Fill `DataLoader`, `DataProcessor`, and `DBPopulater.append/create_table` (plus Postgres/MySQL upsert).
  * Add schema tools: `infer_sql_types`, `generate_create_table_sql`, and simple ERD exports.
  * Unit tests for each public method.

* **Step 3: Finalization**

  * Integration example (e2e sample layer).
  * Expanded README and optional CI workflow.

##  **WORKFlow**

**`DataLoader → DataProcessor → DBConnector ← DBPopulator`** is the optimal logic. Here's why:

## 🎯 **Optimal Flow Explanation:**

### **Sequential Data Processing (→):**
```
DataLoader → DataProcessor → DBConnector
```

**Why this direction?**
- **Data flows forward**: Raw files → Clean DataFrames → Database
- **Each class has single responsibility**: Loading → Processing → Database Operations
- **Clear dependencies**: Each step depends on the previous one's output

### **Infrastructure Usage (←):**
```
DBConnector ← DBPopulator
```

**Why this direction?**
- **DBPopulator uses DBConnector as infrastructure tool**
- **DBConnector provides low-level operations** (execute, to_sql, create_schema)
- **DBPopulator provides high-level business logic** (relationships, constraints, complex integrations)

## 🔧 **Why This Architecture is Optimal:**

### **1. Separation of Concerns:**
- **DataLoader**: Pure file loading + quality assessment
- **DataProcessor**: Pure data transformation 
- **DBConnector**: Pure database infrastructure
- **DBPopulator**: Pure business logic for database population

### **2. Single Responsibility Principle:**
Each class does **one thing well**:
- DataLoader ≠ data processing
- DataProcessor ≠ database operations  
- DBConnector ≠ business logic
- DBPopulator ≠ low-level SQL operations

### **3. Reusability:**
```python
# DBConnector can be used independently
connector.execute("SELECT * FROM table")
connector.to_sql(df, "table")

# DBPopulator uses DBConnector internally
populator.establish_relationships(connector=connector)
populator.create_indexes(connector=connector)
```

### **4. Testability:**
- Each class can be **unit tested independently**
- **Mock dependencies easily**: Mock DBConnector in DBPopulator tests
- **Clear interfaces**: Each class has well-defined inputs/outputs

### **5. Flexibility:**
- **Use DBConnector without DBPopulator** for simple operations
- **Use DBPopulator with different DBConnector configurations**
- **Replace any component** without affecting others

## 📊 **Real-World Workflow:**

```python
# Step 2: Sequential Processing
loader = DataLoader()
processor = DataProcessor()

df_raw = loader.load("boundaries.geojson")      # Raw data
df_clean = processor.transform(df_raw)          # Clean data

# Step 3: Parallel Infrastructure Usage  
connector = DBConnector()
populator = DBPopulator()

# Basic operations through DBConnector
connector.to_sql(df_clean, "boundaries")

# Complex operations through DBPopulator (using DBConnector)
populator.create_relationships(
    connector=connector,
    new_table="boundaries", 
    existing_tables=["listings", "neighborhoods"]
)
```

This architecture **scales well**, **maintains clean code**, and **follows software engineering best practices**.