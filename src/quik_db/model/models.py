"""
Database Validation Models used for validating configurations
"""

# flake8: noqa: E501
# pyright: reportArgumentType=false
# pylint: disable=C0115
# ruff: noqa: E712
from __future__ import annotations

from typing import Any, ClassVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    ValidationError,
    model_validator,
)
from pydantic_core import InitErrorDetails

from quik_db.dictionaries import drivers
from quik_db.dictionaries.model_fields import (
    connection_params_fields,
    db_model_fields,
    query_settings_fields,
)
from quik_db.model.enums import ConnectionState, Dialect
from quik_db.model.exceptions import create_error_msg
from quik_db.model.metadata import update_model_metadata
from quik_db.utils.db_utils import get_default_db_count


class ModelConfig(BaseModel):
    """
    Set the default configuration for the BaseModel
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


class StateVars(BaseModel):
    """
    State variables for the database connection. This model is not
    designed  to be instantiated directly but rather serves as a
    container for state information related to the database execution.
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    state: ConnectionState = ConnectionState.DISCONNECTED
    connection_type: str = ""
    schema_applied: bool = False
    fetch_size: int | None = None
    columns: str | list = []
    page: int = 0
    offset: int = 0
    row_count: int = 0
    query: list = Field(default_factory=list)
    params: list = Field(default_factory=list)
    results: list = Field(default_factory=list)

    def update(
        self, key: str | None = None, value: Any = None, **kwargs: Any
    ) -> None:
        """
        Update state variables with validation.

        Args:
            key (str, optional): A single attribute name to set.
            value (Any, optional): The value for the single attribute.
            kwargs (Any): Multiple attribute-value pairs to set at once.
        """
        if key and value is not None:
            # Single key-value update
            setattr(self, key, value)
        else:
            # Multiple updates via kwargs
            for k, v in kwargs.items():
                if hasattr(self, k) and isinstance(getattr(self, k), list):
                    getattr(self, k).append(v)
                else:
                    setattr(self, k, v)


@update_model_metadata(connection_params_fields)
class ConnectionParams(ModelConfig):
    """
    Connection parameters for the database.

    This model is used to store the necessary information to connect to
    a database.The driver is optional only if odbc is not utilized. If
    url is present in the model, it will override connection parameters.
    Review the model_validator in DatabaseModel for more information.

    """

    model_config = ConfigDict(extra="forbid")

    drivername: str = ""
    host: str = ""
    port: str | int = ""
    username: str = ""
    password: str = ""
    database: str = ""
    query: dict = Field(default_factory=dict)


@update_model_metadata(query_settings_fields)
class QuerySettings(ModelConfig):
    """
    Query model for database operations.

    """

    enable_fetch: bool = True
    prefix_schema: str = ""
    prefix_queries: bool = False
    prefix_procedures: bool = False
    limit: int = 0

    def __init__(self, **data):
        """Sets the default values when enabling prefix_schema."""

        super().__init__(**data)

        p_queries = data.get("prefix_queries", None)
        p_procedures = data.get("prefix_procedures", None)

        # Set the defaults to be True if not defined
        if self.prefix_schema and (p_queries is None and p_procedures is None):
            self.prefix_queries = True
            self.prefix_procedures = True


@update_model_metadata(db_model_fields)
class DatabaseModel(BaseModel):
    """
    Single database configuration model.

    The model forces a configuration to align with the expected schema
    to ensure that the database connection has the necessary parameters
    to create a connection.

    """

    model_config = ConfigDict(extra="ignore", use_enum_values=True)
    # Do not use. Tracks execution state.
    # Class attributes
    default_config: ClassVar[str] = ""
    default_config_name: ClassVar[str] = ""
    reserved_attrs: ClassVar[list] = Field(default_factory=list)

    dialect: Dialect
    description: str = ""
    default: bool = False
    url: str = ""
    connection_params: ConnectionParams = Field(
        default_factory=ConnectionParams
    )
    schema_name: str = ""
    options: dict[str, Any] = Field(default_factory=dict)
    result_as_mappings: bool = False
    query_settings: QuerySettings = Field(default_factory=QuerySettings)

    @model_validator(mode="before")
    @classmethod
    def field_validation(cls, values: dict) -> dict:
        """
        Validates the fields of a database configuration dictionary.
        Args:
            cls: The class that calls this method.
            values (dict): The dictionary containing database configuration.
        Returns:
            dict: The validated and possibly modified configuration dictionary.
        Raises:
            TypeError: If the input `values` is not a dictionary.
            ValidationError: If any validation checks fail.
        Validation Checks:
            - Ensures `values` is a dictionary.
            - Checks for the presence and validity of the `dialect` key.
            - Validates connection parameters (`username`, `password`,
            `host`, `driver`).
            - Validates query settings related to schema prefix.
            - For SQLite, ensures the presence of the `path` key.
            - For other dialects, ensures either `url` or connection
            parameters are provided.
            - Sets a default driver if not provided.
        Note:
            - Raises `ValidationError` with detailed error messages if
                any validation fails.
        """

        errors = []
        if not isinstance(values, dict):
            errors.append(create_error_msg("invalid_value_type"))
        else:
            dialect = values.get("dialect")
            url = values.get("url")
            use_params = values.get("use_params")
            # Check for missing dialect
            if not dialect:
                errors.append(create_error_msg("missing_dialect"))
            if dialect not in Dialect:
                errors.append(create_error_msg("invalid_dialect"))

            # Connection Parameters
            params = values.get("connection_params") or {}
            username = params.get("username")
            password = params.get("password", "")
            host = params.get("host")
            drivername = params.get("driver") if params else None

            # Query Settings
            qs = values.get("query_settings", {})
            schema_prefix = qs.get("prefix_schema")
            prefix_queries = qs.get("prefix_queries", None)
            prefix_procedures = qs.get("prefix_procedures", None)

            if schema_prefix:
                if prefix_queries is False and prefix_procedures is False:
                    errors.append(create_error_msg("invalid_prefix_settings"))

            if not schema_prefix and (prefix_queries or prefix_procedures):
                errors.append(create_error_msg("invalid_prefix_settings"))

            # Sqlite only requires the url (path to .db file)
            if dialect == "sqlite":
                if not url or ".db" not in url:
                    errors.append(create_error_msg("missing_sqlite_url"))
                if params:
                    errors.append(create_error_msg("invalid_sqlite_params"))
                if use_params:
                    errors.append(create_error_msg("invalid_sqlite_params"))
            else:
                if url and params:
                    errors.append(create_error_msg("invalid_url_and_params"))
                if not (url or params):
                    errors.append(create_error_msg("missing_url_or_params"))
                if params:
                    if not host:
                        errors.append(create_error_msg("invalid_params"))
                    if username and not password:
                        errors.append(create_error_msg("missing_password"))
                if not url and params and not drivername:
                    values["connection_params"]["drivername"] = drivers[
                        dialect
                    ]

        if errors:
            _errors = [InitErrorDetails(err) for err in errors]
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=_errors,
            )

        # Set the default driver

        return values


class MultiDatabaseModel(RootModel[str | dict[str, DatabaseModel]]):
    """
    Model for Multidatabase configurations.

    Conifigurations that are defined
    with a root key (database name) and only have 1 value (DatabaseModel)
    will pass validation.

    e.g.

    mydatabase1:
      dialect: mysql
      url:mysql://user:pass
    mydatabase2:
        dialect: sqlite
        url:sqlite:///path/to/db.sqlite
    """

    @model_validator(mode="before")
    @classmethod
    def validate_schema(cls, values: dict) -> dict:
        """
        Validate the schema of the provided dictionary.

        This method checks if the input is a dictionary and validates
        the structure of its nested dictionaries. It also ensures that
        there is at most one default database specified.

        Args:
            values (dict): The dictionary to validate.

        Returns:
            dict: The validated dictionary.

        Raises:
            TypeError: If the root element is not a dictionary.
            ValidationError: If there are any validation errors, such as
                invalid nesting or multiple default databases.

        """
        errors = []

        for v in values.values():
            if v is None or not isinstance(v, dict):
                error = create_error_msg("invalid_nesting")
                if error not in errors:
                    errors.append(error)
        # Checking for multiple defaults=
        if get_default_db_count(values) > 1:
            errors.append(create_error_msg("multiple_default_db"))

        if errors:
            _errors = [InitErrorDetails(err) for err in errors]
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=_errors,
            )

        # Return with meta
        return values
