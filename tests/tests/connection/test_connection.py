from __future__ import annotations

import pytest
from sqlalchemy import Connection
from sqlalchemy.exc import InterfaceError, OperationalError

from quik_db.model.enums import ConnectionState
from tests.utils import assert_case_result


def test_if_connected(connection):
    """
    Check if a Connection is returned upon connection
    """

    connection.connect()
    assert isinstance(connection.connection, Connection)


def test_connection_to_db(connection):
    """
    Test the connectivity to the database using the defined
    configurations.

    The test will test the connection using 2 methods:
    - url:The connection is established using the url .
    - PARAMS: The connection is established using the connection
        parameters.

    The test will execute a simple query to check the connection and
    iterate through each dialect to ensure that the connection is
    successful.
    """

    try:
        result = connection.execute("SELECT 1")

        assert_case_result(result, expected_value=1)

    except (OperationalError, InterfaceError):
        dialect = connection.config.dialect
        connection.vars.state = ConnectionState.ERROR

        pytest.fail(
            f"Connect could not be established for {dialect}."
            "Skipping the remaining tests for dialect."
        )
