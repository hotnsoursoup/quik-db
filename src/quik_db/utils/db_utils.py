"""
This module provides utility functions for working with SQL queries and
database configurations.
"""

from __future__ import annotations

import re
from typing import (
    Any,
    Callable,
    Set,
)

import sqlglot
import sqlparse
from sqlglot import exp
from sqlparse.tokens import DML


def is_stored_procedure(query: str) -> bool:
    """
    Determine if a given SQL query string is a stored procedure call.

    This function checks if the provided SQL query matches common
    patterns used to call stored procedures in various SQL dialects.

    Args:
        query (str): The SQL query string to be checked.

    Returns:
        bool: True if the query is identified as a stored procedure
            call, False otherwise.

    Examples:
        >>> is_stored_procedure("EXEC my_stored_procedure")
        True
        >>> is_stored_procedure("SELECT * FROM my_table")
        False

    """
    query = query.strip().lower()

    # Patterns to detect stored procedure calls
    patterns = [
        r"^exec\s",  # SQL Server, Sybase
        r"^execute\s",  # SQL Server, Sybase (alternative)
        r"^call\s",  # MySQL, PostgreSQL, Oracle
        r"^begin\s",  # PL/SQL block in Oracle
        r"^declare\s",  # PL/SQL anonymous block
    ]

    return any(re.match(pattern, query) for pattern in patterns)


def has_sorting(sql: str) -> bool:
    """
    Check if an SQL query contains an "ORDER BY" clause outside
    of subqueries.

    Args:
        sql (str): The SQL query string to be checked.

    Returns:
        bool: True if the SQL query contains an "ORDER BY" clause outside of
        subqueries, False otherwise.

    """
    sql = re.sub(r"\([^()]*\)", "", sql)

    # Check if "ORDER BY" exists outside of subqueries
    order_by_pattern = re.compile(r"\bORDER\s+BY\b", re.IGNORECASE)

    return bool(order_by_pattern.search(sql))


def has_paging(sql: str) -> bool:
    """
    Detect paging with limits and offsets in an SQL query.

    Args:
        sql (str): The SQL query to analyze.

    Returns:
        bool: True if paging is detected, False otherwise.

    """
    # Regular expressions for common paging patterns with diff dialects
    paging_patterns = [
        # MySQL
        r"\bLIMIT\s+(\d+)\s*(?:OFFSET\s+(\d+))?\b",
        # PostgreSQL
        r"\bLIMIT\s+(\d+)\b(?:\s+OFFSET\s+(\d+)\b)?",
        # SQL Server
        r"\bTOP\s+(\d+)\b(?:\s+OFFSET\s+(\d+)\b)?",
        # Oracle
        r"\bROWNUM\s*\b(?:\s*\bBETWEEN\s*\d+\s*AND\s*\d+\b|\s*\b<=?\s*\d+\b)",
        # SQLite
        r"\bLIMIT\s+(\d+)\s*(?:OFFSET\s+(\d+))?\b",
    ]

    for pattern in paging_patterns:
        match = re.search(pattern, sql, re.IGNORECASE)
        if match:
            return True

    return False


def ms_param_string(p: dict[str, Any]) -> str:
    """
    Return a string of SQL parameters for MSSQL.

    Args:
        p (dict[str, Any]): The parameters to format.

    Returns:
        str: The formatted parameter string.

    """
    return ", ".join([f"@{key}=:{key}" for key in p]) if p else ""


def get_default_config(config: dict) -> bool | str:
    """
    Retrieve the default database configuration from a given
    configuration dictionary.

    Args:
        config (dict): A dictionary containing database configurations.
            Each key is a database name, and each value is a dictionary
            with configuration details, including a "default" key.

    Returns:
        bool | str: The configuration dictionary of the default database
        if found, otherwise None.

    """
    for cfg in config.values():
        if cfg.get("default"):
            return cfg
    return None


def get_default_db_count(config: dict) -> int:
    """
    Calculate the number of default databases in the given configuration.

    Args:
        config (dict): The database configuration dictionary that matches the
        MultiDatabaseModel schema.

    Returns:
        int: The count of databases marked as default in the configuration.

    """
    return sum(
        1
        for db in config.values()
        if isinstance(db, dict) and db.get("default")
    )


def is_dml_query(statement: str) -> bool:
    """
    Detects if the given query is a DML query (NSERT, UPDATE, DELETE).
    """
    parsed = sqlparse.parse(statement)
    for stmt in parsed:
        for token in stmt.tokens:
            if token.ttype == DML:
                return token.value.upper() in {"INSERT", "UPDATE", "DELETE"}
    return False


def build_sql_proc_params(params: dict[str, str]) -> str:
    """Formats parameters for SQL stored procedure query."""
    return f"({', '.join(f':{key}' for key in params)})" if params else ""


def process_params(
    params: dict[str, str] | tuple[str, str] | tuple[tuple[str, str]],
    handlers: list[Callable],
) -> dict[str, str] | tuple[tuple[str, str]]:
    """
    Preprocess the parameters before passing them to the database query.

    Args:
        params (dict[str, Any] | tuple[tuple[str, Any], ...] | None):
            The parameters to be processed. Can be a dictionary or a tuple
            of key-value pairs.
        processors (list[Callable[[Any], Any]] | None):
            A list of processor functions to apply to each value in the
            parameters. If None,no processing will occur, and the original
            parameters will be returned.

    Returns:
        dict[str, Any] | tuple[tuple[str, Any], ...]:
            The processed parameters as a dictionary or the original type
            if no processing occurs.

    """
    if not params or not handlers:
        return params
    if isinstance(params, dict):
        return {
            key: h(value) for key, value in params.items() for h in handlers
        }
    if isinstance(params, tuple):
        return tuple(
            (key, h(value)) for key, value in params for h in handlers
        )


def return_mapped_dialect(dialect: str) -> str:
    """return mapped dialect for sqlglot"""
    map = {
        "mysql": "mysql",
        "mariadb": "mysql",
        "postgresql": "postgres",
        "sqlite": "sqlite",
        "oracle": "oracle",
        "msql": "sqlserver",
    }

    return map.get(dialect, "")


def is_temp_table(table_name: str, dialect: str) -> bool:
    """
    Determine if the given table name is a temporary table based
    on the provided SQL dialect.

    Args:
        table_name (str): The name of the table to check.
        dialect (str): The SQL dialect in use.

    Returns:
        bool: True if the table is a temporary table, False otherwise.
    """
    if dialect == "tsql":
        return table_name.startswith("#")
    # Add conditions for other dialects if necessary
    return False


def apply_schema_prefix(
    node: exp.Expression, schema_prefix: str, cte_names: Set[str], dialect: str
) -> None:
    """
    Recursively apply a schema prefix to table nodes within an SQL AST.

    Args:
        node (exp.Expression): The current node in the SQL AST.
        schema_prefix (str): The schema prefix to apply.
        cte_names (Set[str]): The set of CTE names to exclude from prefixing.
        dialect (str): The SQL dialect in use.
    """
    match node:
        case exp.Table():
            table_name = node.this.name.lower()
            if table_name not in cte_names and not is_temp_table(
                table_name, dialect
            ):
                # Apply schema prefix
                node.set("db", exp.Identifier(this=schema_prefix))

    for child in node.args.values():
        match child:
            case exp.Expression():
                apply_schema_prefix(child, schema_prefix, cte_names, dialect)
            case list():
                for item in child:
                    if isinstance(item, exp.Expression):
                        apply_schema_prefix(
                            item, schema_prefix, cte_names, dialect
                        )


def apply_schema_to_query(
    query: str, schema_prefix: str, dialect: str = "mysql"
) -> str:
    """
    Modify a SQL query by applying a schema prefix to table references.

    Args:
        query (str): The original SQL query to modify.
        schema_prefix (str): The schema prefix to apply.
        dialect (str, optional): The SQL dialect in use. Defaults
            to 'mysql'.

    Returns:
        str: The modified SQL query with schema prefixes applied.
    """
    dialect = return_mapped_dialect(dialect)
    # Parse the SQL query into an AST with the specified dialect
    ast = sqlglot.parse_one(query, read=dialect)

    # Collect the names of CTEs
    cte_names: Set[str] = {
        cte.alias_or_name.lower() for cte in ast.find_all(exp.CTE)
    }

    # Apply schema prefix to table references
    apply_schema_prefix(ast, schema_prefix, cte_names, dialect)

    return ast.sql(dialect=dialect)
