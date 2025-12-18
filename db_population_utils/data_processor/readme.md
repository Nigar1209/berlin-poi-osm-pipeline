# Data Population Utilities

## DataProcessor Module

### Purpose

Transforms and validates raw DataFrames from DataLoader into analysis-ready formats.

### Key Workflow

```python
from db_population_utils import DataLoader, DataProcessor

# Load
loader = DataLoader()
df = loader.load("data.csv")

# Process 
processor = DataProcessor(strict_mode=True)
df = processor.preprocess_loaded_data(
    df,
    datetime_columns=["order_date"],
    type_hints={"price": "float32"}
)

# Validate
report = processor.validate(df, checks={
    "required_columns": ["id", "order_date"],
    "non_null": ["id"]
})

if report["passed"]:
    # Ready for database insertion
    pass
```
