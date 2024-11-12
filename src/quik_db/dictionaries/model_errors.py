"Database model error related dictionaries"

from quik_db.utils.formatters import flatten_dict


db_model_errors = {
    "invalid_dialect": """
        Invalid dialect. Only the following dialects are supported:
        mysql, mariadb, mssql, postgresql, oracle, sqlite.
    """,
    "invalid_model_name": """
        Model name provided does not match.
    """,
    "invalid_nesting": """
        Values in a 'MultiDatabaseModel' must be a dictionary. Each
        dictionary represents a database configuration and is validated
        to ensure it matches the schema 'DatabaseModel'.
    """,
    "invalid_params": """
        Connection parameters are missing or incomplete.
    """,
    "invalid_prefix_settings": """
        Schema_prefix is provided, but both prefix_queries and
        prefix_procedures are disabled.
    """,
    "invalid_sqlite_params": """
        Sqlite configuration does not support connection parameters.
        Remove the connection parameters and use_params option if set.
    """,
    "invalid_root": """
        Configuration must be a mapping.
    """,
    "invalid_statevars": """
        State variables are not settable.
    """,
    "invalid_value_type": """
        Configuration must be a mapping.
    """,
    "missing_dialect": """
        Dialect is required for the database configuration.
    """,
    "missing_host": """
        Host is required for the database connection parameters
    """,
    "missing_odbc_driver": """
        Driver is required when using ODBC connections.
    """,
    "missing_params": """
        Connection parameters are required if use_params is set to True.
    """,
    "missing_password": """
        Password is required for the database connection when username
        is provided.
    """,
    "missing_schema": """
        Schema name is required when using the `add_schema_prefix`
        option.
    """,
    "missing_sqlite_url": """
        Sqlite requires a url (path) to the database file. Please
        provide a valid url to the sqlite database file and ensure it
        is in the correct fmt. e.g. (url: '/path/to/sqlite.db')
    """,
    "multiple_default_db": """
        Only one default database can be defined.
    """,
    "invalid_url_and_params": """
        Url and connection_params cannot be provided together.
    """,
    "missing_url_or_params": """
        Either `url` or `connection_params` must be provided for
        non-sqlite dialects.
    """,
}

db_model_errors = flatten_dict(db_model_errors)

db_validation_errors = {
    "invalid_dialect": {
        "loc": ("dialect",),
        "type": "value_error",
        "ctx": {
            "error": db_model_errors["invalid_dialect"],
        },
    },
    "invalid_nesting": {
        "loc": ("__root__",),
        "type": "value_error",
        "ctx": {
            "error": db_model_errors["invalid_nesting"],
        },
    },
    "invalid_value_type": {
        "loc": ("__root__",),
        "type": "value_error",
        "ctx": {
            "error": db_model_errors["invalid_value_type"],
        },
    },
    "invalid_params": {
        "loc": ("connection_params",),
        "type": "missing",
        "ctx": {
            "error": db_model_errors["invalid_params"],
            "example": {
                "connection_params": {
                    "host": "localhost",
                    "username": "user",
                    "password": "pass1",
                    "port": 3306,
                    "database": "mydb",
                },
            },
        },
    },
    "invalid_prefix_settings": {
        "loc": ("query_settings",),
        "type": "value_error",
        "ctx": {
            "error": db_model_errors["invalid_prefix_settings"],
        },
    },
    "invalid_url_and_params": {
        "loc": ("url", "connection_params"),
        "type": "value_error",
        "ctx": {
            "error": db_model_errors["invalid_url_and_params"],
        },
    },
    "missing_dialect": {
        "loc": ("dialect",),
        "type": "missing",
        "ctx": {
            "error": db_model_errors["missing_dialect"],
            "valid_values": [
                "mysql",
                "mariadb",
                "mssql",
                "postgresql",
                "oracle",
                "sqlite",
            ],
        },
    },
    "missing_host": {
        "loc": ("connection_params.host",),
        "type": "missing",
        "ctx": {
            "error": db_model_errors["missing_host"],
        },
    },
    "missing_params": {
        "loc": ("connection_params",),
        "type": "missing",
        "ctx": {"error": db_model_errors["missing_params"]},
    },
    "missing_password": {
        "loc": ("connection_params.password",),
        "type": "missing",
        "ctx": {
            "error": db_model_errors["missing_password"],
        },
    },
    "missing_odbc_driver": {
        "loc": ("driver",),
        "type": "missing",
        "ctx": {
            "error": db_model_errors["missing_odbc_driver"],
        },
    },
    "missing_schema": {
        "loc": ("query_settings.schema_name",),
        "type": "missing",
        "ctx": {
            "error": db_model_errors["missing_schema"],
        },
    },
    "missing_sqlite_url": {
        "loc": ("path",),
        "type": "missing",
        "ctx": {
            "error": db_model_errors["missing_sqlite_url"],
            "example": {"path": "/path/to/sqlite.db"},
        },
    },
    "multiple_default_db": {
        "loc": ("default",),
        "type": "value_error",
        "ctx": {
            "error": db_model_errors["multiple_default_db"],
        },
    },
    "missing_url_or_params": {
        "loc": ("url", "connection_params"),
        "type": "missing",
        "ctx": {
            "error": db_model_errors["missing_url_or_params"],
            "example": {
                "url": "sqlite:///path/to/sqlite.db",
                "connection_params": {
                    "host": "localhost",
                    "username": "user",
                    "password": "pass1",
                    "port": 3306,
                    "database": "mydb",
                },
            },
        },
    },
}
db_validation_errors = flatten_dict(db_validation_errors)
