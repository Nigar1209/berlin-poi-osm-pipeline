# db_population_utils/schema_tools.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# type-only import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd

"""
Schema tools — design stub (Step 1).

Purpose:
  Optional helpers for schema planning and documentation.
  Intended to support, not replace, explicit DDL owned by the team.

Planned capabilities (to implement in Step 2):
  - infer_sql_types(df): map pandas dtypes to SQL types (Postgres-first)
  - generate_create_table_sql(...): emit CREATE TABLE with PK and indexes
  - write_schema_markdown(...): save a simple schema doc table for PR review
  - export_dbml(...), export_mermaid(...): optional ERD-friendly text formats
"""


def infer_sql_types(
    df: "pd.DataFrame",
    *,
    overrides: Optional[Dict[str, str]] = None,
    dialect: str = "postgresql"
) -> Dict[str, str]:
    """
    Return a column->SQL type mapping inferred from pandas dtypes.
    'overrides' lets you pin types for specific columns.
    """
    raise NotImplementedError


def generate_create_table_sql(
    table_name: str,
    schema_map: Dict[str, str],
    *,
    primary_key: Optional[List[str]] = None,
    indexes: Optional[List[List[str]]] = None,
    if_not_exists: bool = True,
    schema: Optional[str] = None,
    dialect: str = "postgresql"
) -> str:
    """
    Build a CREATE TABLE statement with optional PK and secondary indexes.
    """
    raise NotImplementedError


def write_schema_markdown(
    table_name: str,
    schema_map: Dict[str, str],
    out_path: str
) -> str:
    """
    Write a simple Markdown table documenting the schema.
    Returns the path written.
    """
    raise NotImplementedError


def export_dbml(
    table_name: str,
    schema_map: Dict[str, str],
    relationships: Optional[List[Tuple[str, str, str]]] = None
) -> str:
    """
    Produce a DBML representation for use with dbdiagram.io or similar tools.
    relationships: optional list of (from_col, to_table.to_col, relation)
    e.g., ("neighborhood_id", "neighborhoods.id", "ref")
    """
    raise NotImplementedError


def export_mermaid(
    table_name: str,
    schema_map: Dict[str, str],
    relationships: Optional[List[Tuple[str, str, str]]] = None
) -> str:
    """
    Produce a Mermaid ER diagram snippet.
    relationships follow the same convention as export_dbml().
    """
    raise NotImplementedError
