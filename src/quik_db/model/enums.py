"""This module contains enums for database operations."""

from enum import Enum, auto


class QueryType(str, Enum):
    """
    Enum for database operation types.

    This enum specifies the types of database operations that can be
    performed.
    """

    PROCEDURE = "procedure"  # Represents a stored procedure operation.
    FUNCTION = "function"  # Represents a function call operation.
    QUERY = "query"  # Represents a standard SQL query operation.


class Dialect(str, Enum):
    """
    Enum for supported database dialects.

    This enum defines the types of database dialects supported by the
    application.
    """

    MYSQL = "mysql"
    MARIADB = "mariadb"
    MSSQL = "mssql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    SQLITE = "sqlite"


class ExecutionState(str, Enum):
    """
    Enum for database execution states.

    Represents the current state of database execution operations.
    """

    IDLE = "idle"  # Execution is idle.
    ACTIVE = "active"  # Execution is active.
    ERROR = "error"  # Execution encountered an error.


class ConnectionState(Enum):
    """
    Enum representing the state of a database connection.

    Used to track the status of the database connection.
    """

    CONNECTED = auto()  # Connection is active.
    DISCONNECTED = auto()  # Connection is not active.
    ERROR = auto()  # Connection encountered an error.
