import uuid

from quik_db.model.enums import Dialect
from tests.utils import assert_case_result


def test_select(connection, test_user, test_table):
    """
    Test executing a simple SELECT statement to retrieve a user.

    Args:
        connection: A database connection object.

    Asserts:
        - The result contains the expected user with id = 1.
    """
    select_sql = f"SELECT name FROM {test_table} WHERE id = {test_user['id']}"
    result = connection.execute(select_sql)
    assert_case_result(result, expected_value=test_user["name"])


def test_select_with_params(connection, test_user, test_table):
    """
    Test executing a SELECT statement with parameters to retrieve a user.

    Args:
        connection: A database connection object.

    Asserts:
        - The result contains the expected user with the specified name.
    """
    select_sql = f"SELECT name FROM {test_table} WHERE id = :id"
    params = {"id": test_user["id"]}
    name = test_user["name"]
    result = connection.execute(select_sql, params)
    assert_case_result(result, expected_value=name)


def test_stored_procedures(connection, test_user, test_table):
    """
    Test executing stored procedures and verifying their results.

    - For MySQL and SQL Server, the 'GetUser' procedure is executed to
        retrieve a user.
    - For Oracle and PostgreSQL, the 'UpdateUserUUID' procedure updates
        a user's uuid.

    Args:
        connection: A database connection object.

    Asserts:
        - For 'GetUser', the result contains the expected user named
            'Emma Thompson'.
        - For 'UpdateUserUUID', the user's uuid is successfully updated.
    """

    dialect = connection.config.dialect

    if dialect not in (Dialect.ORACLE, Dialect.POSTGRESQL):
        procedure_name = "GetUserName"
        params = {"id": test_user["id"]}
        name = test_user["name"]

        result = connection.execute_sp(procedure_name, params)
        assert_case_result(result, expected_value=name)
    else:
        procedure_name = "UpdateUserUUID"

        # Assuming `connection` is a valid SQLAlchemy connection object
        new_uuid = uuid.uuid4()
        uuid_str = str(new_uuid)
        params = {"id": test_user["id"], "uuid": uuid_str}
        select_sql = f"SELECT uuid FROM {test_table} WHERE id = :id"

        # Execute the change
        connection.execute_sp(procedure_name, params)
        # Retrieve the result
        result = connection.execute(select_sql, {"id": test_user["id"]})

        # Oracle returns the UUID as a string
        if dialect == Dialect.ORACLE:
            assert_case_result(result, expected_value=uuid_str)
        else:
            assert_case_result(result, expected_value=new_uuid)
