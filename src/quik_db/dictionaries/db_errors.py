"Database error messages."

from quik_db.utils.formatters import flatten_dict


db_errors = {
    "duplicate_value": """
        Duplicate value provided for {}.
    """,
    "handler_not_callable": """
        Handler must be callable.
    """,
    "invalid_connector": """
        Invalid connector specified. Only sqlalchemy, odbc, and dsn are
        allowed.
    """,
    "invalid_fetch": """
        Fetch value must be an integer. Use 0 for all rows.
    """,
    "invalid_fetch_size": """
        Fetch value must be an integer. Use 0 for all rows.
    """,
    "invalid_fetch_type": """
        Fetch value must be an integer. Use 0 for all rows.
    """,
    "invalid_session_type": """
        session_type must be in ('direct', 'scoped', 'session').
    """,
    "invalid_fetch_settings": """
        Fetch value is provided, but fetch is disabled.
    """,
    "key_error": """
        Please check your configuration file for a valid database entry.
    """,
    "missing_connector_with_url": """
        A valid connector is required when using a connection string.
    """,
    "missing_db_config": """
        Please check your configuration file for a valid database entry.
    """,
    "missing_dialect": """
        Please check your configuration file. A valid dialect or
        connection string is required.
    """,
    "missing_params": """
        Please check your configuration file. Missing connection
        information.
    """,
    "missing_type": """
        A connection string requires a type: ODBC, DSN, SQLAlchemy.
    """,
    "named_db_not_found": """
        The named database configuration was not found in the
        configuration file.
    """,
    "no_connection": """
        No connection was established.
    """,
    "no_connect_method": """
        You may see this error if you are attempting to use the
        DatabaseConnection class directly without subclassing. The
        DatabaseConnection class does not natively create connections
        itself, rather, it esbalishes a base configuration along with
        methods that can be used with a database.
    """,
    "no_database": """
        No database listed in the configuration file. Stored procedure
        may not work properly.
    """,
    "no_fetch_method": """
        The connection does not have a fetch method. You may see this
        errorif you have created a subclass and the connection method
        used does not have the method fetch. You must create a custom
        fetch method.
    """,
    "no_session": """
        A session was never created. Use connect() first.
    """,
    "no_result": """
        You have attempted to access the result object or a command that
        requires a result object, but the result object does not exist.
        Ensure you have executed a query statement before you fetch.
    """,
    "prefix_error": """
        Prefix requires a query, stored procedure, or function name.
    """,
    "not_implemented": """
        Method not implemented.
    """,
    "sqlite_no_sp": """
        SQLite does not support stored procedures or functions.
    """,
    "unsupported_dialect": """
        The database dialect is not supported. Please refer to the
        documentation for supported dialects.
    """,
    "unsupported_dialect_paging": """
        Unsupported database dialect for paging.
    """,
}

db_errors = flatten_dict(db_errors)
