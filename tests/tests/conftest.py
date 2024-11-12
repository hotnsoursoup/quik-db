"Configure connection fixture for connection tests"

import uuid
from datetime import datetime

import pytest

from quik_db.core.database import SqlAlchemyConnection as Connection
from quik_db.model.enums import ConnectionState
from tests.definitions import databases


@pytest.fixture(params=databases.values(), ids=databases.keys())
def connection(request) -> Connection:
    """
    Create and yield a database connection instance, parameterized by
    the provided configurations. Closes the connection after tests.

    Args:
        request: Pytest request object to access indirect parameters.

    Yields:
        Connection: Instance of SqlAlchemyConnection.
    """
    conn = Connection(request.param)
    return conn


@pytest.fixture(scope="session")
def test_user() -> dict:
    """
    Fixture to return test user details.

    Returns test data that is populated into each database for testing

    Returns:
        dict: A dictionary containing test user details.
    """

    return {
        "id": 1,
        "name": "Emma Thompson",
        "dob": datetime.strptime("1985-07-23", "%Y-%m-%d").date(),
        "uuid": uuid.UUID("8a6f1d9e-53a9-4f8c-bb07-1d18a3e4b9b9"),
    }


@pytest.fixture
def test_table() -> str:
    """Return the test table. Can return direct string or a lookup"""
    return "test_data"


@pytest.fixture(autouse=True)
def check_connection(connection):
    """
    Check if connection is valid still
    """
    if connection.vars.state == ConnectionState.ERROR:
        pytest.skip("Connection in an Error State, skipping tests")
