"""
Collection of dictionaries used to store messages related to database models,
configuration, and errors.
"""

from quik_db.utils.formatters import flatten_dict


connection_params_fields = {
    "drivername": {
        "title": "Database Driver",
        "description": (
            "Specifies the driver for the database connection, which may vary "
            "across database dialects or when ODBC support is enabled."
        ),
        "example": "mysql+pymysql",
    },
    "host": {
        "title": "Database Host",
        "description": "The hostname or IP address of the database server.",
        "example": "127.0.0.1",
    },
    "port": {
        "title": "Database Port",
        "description": "The port number that the database server is listening on.",
        "example": 5432,
    },
    "username": {
        "title": "Database Username",
        "description": "The username for authenticating the database connection.",
        "example": "user123",
    },
    "password": {
        "title": "Database Password",
        "description": "The password associated with the database username.",
        "example": "pass123",
    },
    "database": {
        "title": "Database Name",
        "description": "The name of the specific database to connect to.",
        "example": "mydatabase",
    },
    "query": {
        "title": "URL Query Parameters",
        "description": (
            "Optional query parameters to include in the connection URL, "
            "formatted as key-value pairs (e.g., ?param1=value1&param2=value2)."
        ),
        "example": {"param1": "value1", "param2": "value2"},
    },
}

connection_params_fields = flatten_dict(connection_params_fields)

query_settings_fields = {
    "enable_fetch": {
        "title": "Enable Fetch",
        "description": (
            "Enabled by default. Fetches results from the Result object. "
            "Set to False to disable fetching and return the Result object."
        ),
    },
    "prefix_schema": {
        "title": "Schema Prefix",
        "description": (
            "The prefix format to add to query names, stored procedures, "
            "or functions if they do not already have a schema prefix."
        ),
    },
    "prefix_queries": {
        "title": "Prefix Queries",
        "description": "If set to True, applies the schema prefix to queries.",
    },
    "prefix_procedures": {
        "title": "Prefix Procedures",
        "description": (
            "If set to True, applies the schema prefix to stored procedures "
            "or function names."
        ),
    },
    "limit": {
        "title": "Query Limit",
        "description": (
            "Limits the number of rows returned in raw queries, implementing "
            "paging. Setting this to 0 disables paging."
        ),
        "example": 100,
    },
}

query_settings_fields = flatten_dict(query_settings_fields)

db_model_fields = {
    "connection_params": {
        "title": "Connection Parameters",
        "description": (
            "Parameters for connecting to a database. Used in replacement"
            " of the `url` field"
        ),
    },
    "default_config": {
        "title": "Default Config",
        "description": (
            "Specifies the default configuration to use when a database name "
            "is not provided during DatabaseConnection initialization."
        ),
        "example": "default_db_config",
    },
    "default_config_name": {
        "title": "Default Config Name",
        "description": (
            "The key name of the default database configuration, used to "
            "reference this configuration when multiple databases are "
            "configured in a MultiDatabase model"
        ),
        "example": "mydatabase",
    },
    "dialect": {
        "title": "Database Dialect",
        "description": (
            "The type of database being connected to. Supported values include "
            "mysql, mariadb, mssql, postgresql, oracle, and sqlite."
        ),
        "example": "postgresql",
    },
    "description": {
        "title": "Description",
        "description": "A description field for self documentation.",
    },
    "default": {
        "title": "Is Default",
        "description": "If set to True, marks this database configuration as "
        "the default database in a multi-database configuration.",
    },
    "options": {
        "title": "Connection Options",
        "description": (
            "Additional connection options, such as echo settings, pool size, "
            "or connection arguments."
        ),
        "example": {"echo": True, "pool_size": 5},
    },
    "query_settings": {
        "title": "Query Settings",
        "description": "Settings for query execution and result handling.",
    },
    "result_as_mappings": {
        "title": "Return as Mappings",
        "description": "If set to True, returns query results as a list of dictionaries.",
    },
    "schema_name": {
        "title": "Schema Name",
        "description": "The schema_name used. May not be applicable for some dialects",
        "example": "public",
    },
    "url": {
        "title": "Database URL",
        "description": (
            "A connection string or DSN name. For ODBC, this refers to the DSN "
            "name."
        ),
        "example": "postgresql://user:password@localhost/dbname",
    },
}
db_model_fields = flatten_dict(db_model_fields)
