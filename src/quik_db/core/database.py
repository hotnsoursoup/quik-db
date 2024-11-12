"""
Database connection classes used to instantiate database connections using
mappings.

"""

# ruff: noqa: D102
# flake8: noqa: E501
# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
from __future__ import annotations

from abc import ABC, abstractmethod
from pprint import pformat
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    override,
)
from warnings import warn

from sqlalchemy import (
    URL,
    create_engine,
    text,
)
from sqlalchemy.orm import (
    Session,
    scoped_session,
    sessionmaker,
)

from quik_db.core.handlers import handler
from quik_db.dictionaries.db_errors import db_errors as errors
from quik_db.model.enums import (
    ConnectionState,
    Dialect,
    ExecutionState,
    QueryType,
)
from quik_db.model.models import (
    DatabaseModel,
    MultiDatabaseModel,
    StateVars,
)
from quik_db.model.validator import model_validator
from quik_db.utils.db_utils import (
    apply_schema_to_query,
    build_sql_proc_params,
    get_default_config,
    has_paging,
    process_params,
)


if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.engine import (
        Connection,
        Engine,
        Result,
    )


class Configuration:
    """
    Configuration class for database handlers and attribute instantiation.
    """

    def __init__(
        self,
        config: dict,
        name: str = "",
        handlers: dict[str, Callable | list[Callable]] | None = None,
    ):
        """
        Initializes the database configuration.

        The config is passed to a pydantic model to be validated. This
        is to ensure it has the correct values to create a connection
        or if a feature is enabled that the feature has the values it
        needs to function.

        Args:
            config (dict): The configuration dictionary for the database.
            name (str, optional): The name of the database being called
                in a multidb configiration. Only applies for multidb
                configurations.
            handlers (dict[str, Callable | list[Callable]] | None):
                A dictionary of handlers you can assign to the instance
                class.

        Returns:
            Configuration: An instance of the Configuration
                class.

        Attributes:
            model (BaseDatabaseModel | MultiDatabaseModel): The validated
                pydantic model (BaseModel) with the configuration values.
            execution_handler (Callable): Handler to override the default
                query execution.
            result_handlers (Callable | list[Callable]): Handlers to process
                results from the database.
            error_handlers (Callable | list[Callable]): Handlers to process
                errors from the database or other handlers.
            param_handlers (Callable | list[Callable]): handlers to process
                parameters before executing queries. (e.g. sanitizing)

        """

        self.name = name
        self.result = None
        self.execution_handler = None
        self.result_handlers = []
        self.error_handlers = []
        self.param_handlers = []
        self._exc = ExecutionState.IDLE
        self.vars = StateVars()
        # Validate the configuration against the database models.
        # The returned model is used to set the connection parameters.
        model = model_validator(config)
        _config = model.model_dump()

        # Set the configuration in a multi-database model.
        if model.__class__ == MultiDatabaseModel:
            if name:
                _config = _config["name"]
            elif get_default_config(_config):
                _config = get_default_config(_config)
            elif self.default_config:
                _config = self.default_config
            elif self.default_config_name:
                _config = _config[self.default_config_name]
            else:
                _config = next(iter(_config.items()))

            model = DatabaseModel(**_config)  # pyright: ignore[reportCallIssue]

        self.config = model
        self.qs = self.config.query_settings

        self.conn_build_type = "url" if self.config.url else "params"
        # Set the handlers
        if handlers:
            self.set_handlers(handlers)

    def __repr__(self) -> str:
        """
        Return a string representation of the combined configuration
        and statevars, including only set attributes for config.
        """

        if self.connection:
            self.vars.state = ConnectionState.CONNECTED

        config_data = self.config.model_dump()
        statevars_data = self.vars.model_dump()

        config_data.update(statevars_data)

        return pformat(config_data)

    @property
    def url_string(self) -> str | URL:
        """Return the URL if it is assigned, otherwise return the param URL."""

        return (
            self.config.url
            if self.conn_build_type == "url"
            else self.param_url
        )

    @property
    def param_url(self) -> URL:
        """Return the connection URL built from connection parameters."""
        return URL.create(**self.config.connection_params.model_dump())

    @property
    def url_base(self) -> str:
        """The base string for the connection uri."""
        return "{drivername}://{username}:{password}@{host}:{port}/{database}"

    @property
    def prefix_schema(self):
        """
        Get the schema name from the configuration.

        Returns:
            str: Name of the schema
        """
        schema = self.qs.prefix_schema
        return schema if schema else ""

    @property
    def handler_list(self):
        """Return the list of handlers."""
        return [
            "param_handlers",
            "result_handlers",
            "success_handler",
            "execution_handler",
            "error_handlers",
        ]

    def set_handlers(
        self, handlers: dict[str, Callable | list[Callable]]
    ) -> None:
        """
        Sets the handlers for the database operations.

        This method takes a dictionary of handlers and assigns them to
        the corresponding attributes of the instance. Each handler can
        be a single callable or a list of callables.

        Args:
            handlers (dict[str, Callable | list[Callable]]):
        Returns:
            None
        """

        for handler_name, _handler in handlers.items():
            if handler_name not in self.handler_list:
                raise ValueError(f"Invalid handler name: {handler_name}")
            setattr(self, handler_name, _handler)


class DatabaseConnection(Configuration, ABC):
    """
    Base class for database connections.

    This class provides a standardized configuration framework for
    connectingto various database systems. It supports multi-database
    configurations,allowing you to set a default database if none is
    specified in the configuration file.

    Features:

    - Raw SQL support:
        Helps create raw SQL queries, handle stored procedures, add
        pagination, and provide custom execution and result processing
        handlers.

        >> Example:
        params = {"id": 1}
        query: "SELECT * FROM my_table WHERE id = :id"
        self.execute(query, params)

    - Stored procedure execution:
        Generates a sql to call the procedure based on the database
        dialect. You can provide them with or without the schema or
        database prefix. If you want the prefix to be added
        automatically, you can enable it in query_settings.

        >> Example without prefix (will execute the procedure as is):

        name = "my_procedure"
        self.execute_sp(name, params)

        >> Enable prefixing:
        # YAML
        query_settings:
            schema_prefix: "dbo"

        name = "my_procedure"
        self.execute_sp(name, params)
        # "my_procedure" -> "dbo.my_procedure"

    - Pagination:
        Automatic paging of queries can be set. Set query limit in the
        configuration file for all instances. Paging can also be
        handled at the query level using `limit` and `offset` parameters
        in `execute`. This does not work with stored procedures - only
        raw SQL queries.

        # yaml - affects all instances using this configuration
        dialect: mysql
        url:"mysql+pymysql://user:pass@localhost:3306/mysql"
        query_settings:
            limit: 30

        >> Example (query level):
        self.execute(query, params, offset=offset, limit=limit)

    """

    def __init__(
        self,
        config: dict,
        name: str = "",
        handlers: dict[str, Callable | list[Callable]] | None = None,
    ):
        """
        Initialize the database connection object with the configuration.

        The configuration is validated against the database models to
        ensure that the configuration has the necessary parameters to
        create a connection. The configuration itself supports two
        distinct models: a single database model and a multi-database
        model. Refer to  the documentation on the database models for
        more information.

        Simple example with a single database model:

        - Single Database Model:

            >> with uri
            # yaml
            dialect: mysql
            url:"mysql+pymysql://user:pass@localhost:3306/mysql"
            query_settings:
                limit: 30

            >> with connection params
            dialect: mysql
            query_settings:
                limit: 30
            connection_params:
              host: localhost
              port: 3306
              username: user
              password: pass

        Args:
            handlers (dict[str, Callable | list[Callable]] | None):
                You can assign handlers to the instance class during
                instantiation by passing in a dictionary with the
                handler name as the key and the handler or list of
                handlers as the value.

                e.g.

                myhandlers = {
                    "execution_handler": custom_execution_handler,
                    "result_handlers": [handler1, handler2],
                }
        """
        super().__init__(config, name=name, handlers=handlers)

        self.connection = None
        self._columns = []
        self.exit = None

    def __enter__(self) -> DatabaseConnection:
        """Enter a connection state with the connection object."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Use the connection's exit method if it exists."""
        if self.connection and hasattr(self.connection, "__exit__"):
            self.connection.__exit__(exc_type, exc_val, exc_tb)
        else:
            self.close()

    def execute_sp(
        self,
        procedure_name: str,
        params: dict[str, Any] | None = None,
        fetch: int | None = None,
    ) -> dict | list:
        """
        Execute a stored procedure with the given parameters.

        Args:
            procedure_name (str): The name of the stored procedure to
                call.
            params (dict[str, Any] | None, optional): A dictionary of
                parameter names and values. Defaults to None.

        Raises:
            ValueError: If the database dialect is not supported.
        """
        self._set_activte_state()
        self.vars.query.append(("execute_sp", procedure_name))
        if not self.connection:
            self.connect()

        dialect = self.config.dialect

        if dialect == "sqlite":
            raise ValueError(errors["sqlite_no_sp"])

        # Apply a schema prefix if enabled
        if not self.vars.schema_applied and self.qs.prefix_procedures:
            procedure_name = self.add_schema_prefix(procedure_name)
            self.vars.schema_applied = True

        if dialect == Dialect.MSSQL and params:
            params_str = ", ".join(f"@{key} = :{key}" for key in params)
        else:
            params_str = build_sql_proc_params(params) if params else ""

        # SQL templates based on dialect
        sql_templates = {
            "postgresql": f"CALL {procedure_name}{params_str}",
            "mysql": f"CALL {procedure_name}{params_str}",
            "mariadb": f"CALL {procedure_name}{params_str}",
            "mssql": f"EXEC {procedure_name} {params_str}",
            "oracle": f"BEGIN {procedure_name}{params_str}; END;",
        }

        _query = sql_templates[dialect]

        return self.execute(query=_query, params=params, fetch=fetch)

    def execute(
        self,
        query: str,
        params: dict[str, str] | tuple[tuple[str, str]] | tuple[str, str] = (),
        fetch: int | None = None,
        offset: int = 0,
        limit: int = 0,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """
        Execute a SQL query with optional parameters and pagination.

        Parameters:
            query (str): SQL query to execute.
            params (dict[str, str] | tuple[str, str]): Query parameters.
            fetch (int): Number of rows to fetch.
            offset (int): Row offset for pagination.
            limit (int): Limit of rows to fetch.

        Returns:
            list[dict[str, Any]] | dict[str, Any]: Query result as a
            list of dictionaries or a dictionary.
        """
        self._set_activte_state()
        result = None
        # Check for connection
        if not self.connection:
            self.connect()

        sv = self.vars
        # Add query for tracking
        sv.query.append(("execute_input", query))
        # Track the input
        sv.params.append(("input", params))
        # Prepare query with schema and pagination
        if not self.vars.schema_applied and self.qs.prefix_queries:
            query = self.add_schema_prefix(query, "query")

        if offset or limit:
            query = self.add_paging(query, offset, limit)
            sv.query.append(("paging", query))
        # Process parameters and update query params state
        if self.param_handlers and params:
            params = process_params(params, self.param_handlers)
            sv.params.append(("processed", params))
        try:
            if callable(self.execution_handler):
                self.result = self.execution_handler(query, params, fetch)  # pylint: disable=not-callable
                # Execute the query
            else:
                result = self.result = self.connection.execute(
                    text(query), params
                )

                # Check for results
                if not result.returns_rows:
                    return result

                sv.columns = result.keys()

                # Get the fetch value based on fetch settings
                fetch_size = self._get_fetch_value(fetch)

                if fetch_size is not None:
                    result = self.fetch_results(fetch_size)

            return self.process_results(result)

        except* Exception as e:  # pylint: disable=broad-except
            self.vars.state = ConnectionState.ERROR
            if self.error_handlers:
                exception = handler(self.error_handlers, e)
                if isinstance(exception, Exception):
                    raise exception from e
            raise e

        finally:
            self._exc = ExecutionState.IDLE
            if self.vars.state != ConnectionState.ERROR:
                self.commit()

    def add_paging(
        self,
        query: str,
        offset: int = 0,
        limit: int = 0,
    ) -> str:
        """
        Adds paging (limit and offset) to an SQL query based on the
        dialect.

        Args:
            query (str): The SQL query to modify.
            offset (int): Number of records to skip.
            limit (int): Maximum number of records to return.

        Returns:
            str: The SQL query with paging added, or the original if
            paging is present.
        """

        limit = self.get_limit(limit)

        if has_paging(query):
            return query

        # Retrieve the statevariables
        var = self.vars

        offset = var.offset or offset

        # Limit can be set in the config as well
        limit = var.limit or limit or self.config.params.get("limit", 0)

        paging = ""

        if self.config.dialect in {"mysql", "mariadb", "postgres", "sqlite"}:
            # If only offset is provided, allow 'LIMIT ALL'
            if limit > 0:
                paging = f"LIMIT {limit} OFFSET {offset}"
            elif offset > 0:
                paging = f"LIMIT ALL OFFSET {offset}"

        elif self.config.dialect in {"sql server", "oracle"}:
            # SQL Server and Oracle require 'FETCH NEXT' with OFFSET
            if limit > 0:
                paging = f"OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
            elif offset > 0:
                paging = f"OFFSET {offset} ROWS FETCH NEXT ALL ROWS ONLY"

        return f"{query} {paging}" if paging else query

    def process_results(
        self, result: dict | Result, query_type: QueryType = QueryType.QUERY
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """
        Process the results from a database query or return a success
        message for DML (Data Manipulation Language) queries.

        Args:
            result: The result object or dictionary from the database query.
            query_type: The type of query being processed; defaults to `QUERY`.

        Returns:
            A list of dictionaries representing query results or a success
            message with the affected row count for DML queries.
        """
        d = self.config.dialect

        if query_type == QueryType.PROCEDURE and d in (
            Dialect.ORACLE,
            Dialect.POSTGRESQL,
        ):
            rows: int = result.rowcount
            return {
                "message": f"Success. Rows affected {rows}",
                "rows_affected": rows,
            }

        if self.result_handlers:
            return handler(self.result_handlers, result)
        return result

    def fetch_results(self, fetch_size: int) -> dict[str, Any] | list:
        """Fetch results from the result object as mappings."""

        result = self.result
        if not result:
            raise ValueError(errors["no_result"])

        if self.config.result_as_mappings:
            if fetch_size == 0:
                return result.mappings().all()
            return result.mappings().fetchmany(fetch_size)

        if fetch_size == 0:
            return result.all()

        return result.fetchmany(fetch_size)

    def add_schema_prefix(
        self, query: str, query_type: Literal["procedure", "query"] = "query"
    ) -> str:
        """Add the schema to stored procedure/function names."""

        if query_type == "procedure":
            if "." in query:
                warn(errors["prefix_error"], stacklevel=2)
            return f"{self.prefix_schema}.{query}"

        return apply_schema_to_query(
            query, self.prefix_schema, self.config.dialect
        )

    def limit(self, limit: int):
        self._set_activte_state()
        "Assigns a limit to the query."
        self.vars.limit = limit
        return self

    def offset(self, offset: int):
        self._set_activte_state()
        """Assign an offset to the query."""
        self.vars.offset = offset
        return self

    def fetch(self, fetch_size: int):
        self._set_activte_state()
        """Fetch results from the result object."""
        self.vars.fetch_size = fetch_size

        return self

    def rollback(self) -> None:
        """Rollback the transaction."""
        if self.connection:
            self.connection.rollback()
        else:
            raise ConnectionError(errors["no_connection"])

    def commit(self) -> None:
        """Commit the transaction."""
        if self.connection:
            self.connection.commit()
        else:
            raise ConnectionError(errors["no_connection"])

    def close(self) -> None:
        """
        Close the connection to the database.

        Subclass and override if conn.close() is not supported by the
        database.
        """
        self.vars.state = ConnectionState.DISCONNECTED

        if self.connection and self.vars.state not in [
            ConnectionState.DISCONNECTED,
            ConnectionState.ERROR,
        ]:
            self.connection.close()
            self.connection = None

    def _set_activte_state(self) -> None:
        """Check and set the execution state"""

        if self._exc == ExecutionState.IDLE:
            self._exc = ExecutionState.ACTIVE
            # Reset the statevars
            self.vars = StateVars()

    def _get_fetch_value(self, fetch_size: int | None):
        """
        Return the fetch value for the query.
        """
        fetch_size = fetch_size or self.vars.fetch_size

        if fetch_size is None and self.qs.enable_fetch:
            fetch_size = 0
        return fetch_size

    @abstractmethod
    def connect(self) -> Connection | Session | scoped_session:
        """
        Open, set, and return the connection.
        """
        raise NotImplementedError(errors["no_connect_method"])


class SqlAlchemyConnection(DatabaseConnection):
    """Create a SqlAlchemyDatabase object from a configuration file."""

    def __init__(
        self,
        config: dict,
        name: str = "",
        connection_type: Literal["scoped", "session", "direct"] = "direct",
        session: Session | scoped_session | None = None,
    ) -> None:
        """
        Initialize the database connection.

        Args:
            config (dict): Configuration dictionary for the database.
            name (str): Name of the database. Defaults to empty string.
            connect (bool): If True, connect on instantiation. Defaults
                to False.
            connection_type (Literal['scoped', 'session', 'direct']):
                Type of connection ('scoped', 'session', 'direct').
                Defaults to 'direct'.
            session (sessionmaker | scoped_session | None): Existing
                session factory.
        """

        if not session and not config:
            raise ValueError(errors["no_config"])

        super().__init__(config, name=name)

        self._session_factory = session if session else None
        self.connection_type = connection_type

        if session:
            self.connect()

    @property
    def engine(self) -> Engine:
        """Create a SQLAlchemy engine."""
        engine_options = self.config.options if self.config.options else {}
        return create_engine(self.url_string, **engine_options)

    def session(self) -> SqlAlchemyConnection:
        """
        Return a new session from the sessionmaker while maintaining
        the SqlAlchemyConnection instance configuration
        """

        if not self._session_factory:
            raise ValueError(errors["no_session"])

        return SqlAlchemyConnection(
            config=self.config,
            name=self.name,
            connection_type=self.connection_type,
            session=self._session_factory(),  # pyright: ignore[reportCallIssue]
        )

    @override
    def connect(self) -> Connection | Session | scoped_session:
        """Open, set, and return the connection."""

        if self.connection:
            return self.connection

        # create a connection based off existing session
        if self._session_factory:
            self.connection = self._session_factory()

        conn_type = self.connection_type

        if conn_type == "direct":
            self.connection = self.engine.connect()
        else:
            # Create a session and store it
            self._session_factory = self._create_session_factory()
            # Create a connection off the session
            self.connection = self._session_factory()

        if not self.connection:
            raise ConnectionError(errors["no_connection"])

        self.vars.state = ConnectionState.CONNECTED
        return self.connection

    def _create_session_factory(
        self,
    ) -> sessionmaker | scoped_session:
        """Helper method to create a session or connection."""
        if self.connection_type == "session":
            return sessionmaker(bind=self.engine)
        if self.connection_type == "scoped":
            return scoped_session(sessionmaker(bind=self.engine))
        raise ValueError(errors["invalid_session_type"])

    @override
    def close(self) -> None:
        """Close the connection to the database."""
        if self.connection and self.vars.state not in [
            ConnectionState.DISCONNECTED,
            ConnectionState.ERROR,
        ]:
            if isinstance(self._session_factory, scoped_session):
                self.connection.remove()
            else:
                self.connection.close()

            self.connection = None
            self.vars.state = ConnectionState.DISCONNECTED
