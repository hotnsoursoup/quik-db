"Test configuration models and validators."
# ruff: noqa: E501

import pytest
from pydantic import ValidationError

from quik_db.dictionaries import db_model_errors
from quik_db.model.exceptions import get_error_msg
from quik_db.model.models import DatabaseModel, MultiDatabaseModel
from quik_db.model.validator import model_validator
from tests.definitions import (
    invalid_multidb_tests,
    invalid_test_ids,
    invalid_tests,
    valid_multidb_tests,
    valid_test_ids,
    valid_tests,
)


pytestmark = pytest.mark.model


@pytest.mark.parametrize("test_config", valid_tests, ids=valid_test_ids)
def dbmodel_validate(test_config):
    """
    Test the successful validation of single database configurations.
    This ensures that the `DatabaseModel` can be instantiated with
    various valid configurations.
    """

    config = test_config["config"] if "config" in test_config else {}

    if not test_config:
        pytest.skip("No configuration provided.")

    model = DatabaseModel(**config)
    assert model.dialect == config.get("dialect")
    assert isinstance(model, DatabaseModel)


@pytest.mark.parametrize("test_config", invalid_tests, ids=invalid_test_ids)
def test_dbmodel_validate_fail(test_config):
    """
    Test that invalid configurations raise validation errors.
    Ensures specific errors are raised when the configuration is
    invalid by viewing the test config and checking the error in the
    test config against the error that is raised.
    """

    config = test_config["config"] if "config" in test_config else {}

    if not test_config:
        pytest.skip("No configuration provided.")

    with pytest.raises(ValidationError) as e:
        DatabaseModel(**config)

    if "error" in test_config:
        error_msg = db_model_errors[test_config["error"]]

        errors = e.value.errors()
        msg = [get_error_msg(error) for error in errors]

        assert error_msg in msg


@pytest.mark.parametrize("test_config", valid_multidb_tests)
def test_multidb_model_validate(test_config):
    """
    Test the successful validation of multi-database configurations.
    This ensures that the `MultiDatabaseModel` can handle nesting of
    multiple database configurations and that the nested `DatabaseModel`
    instances are valid.

    Args:
        test_config: A dictionary containing a configuration that
            matches the MultiDatabaseModel model.

    Asserts:
        - The model is an instance of `MultiDatabaseModel`.
        - The model contains nested `DatabaseModel` instances.
    """
    config = test_config["config"] if "config" in test_config else {}

    model = MultiDatabaseModel(**config)

    assert type(model).__name__ == "MultiDatabaseModel"

    for value in config.values():
        value_model = DatabaseModel(**value)
        assert type(value_model).__name__ == "DatabaseModel"


@pytest.mark.parametrize("test_config", invalid_multidb_tests)
def test_multi_db_model_invalid(test_config):
    """
    Test for a few invalid configurations for the MultiDatabaseModel.

    Args:
        test_config: A dictionary containing an invalid multi-database
        configuration.

    Asserts:
        - The model is an instance of `MultiDatabaseModel`.
        - The model contains nested `DatabaseModel` instances.
    """
    config = test_config["config"] if "config" in test_config else {}

    with pytest.raises(ValidationError):
        MultiDatabaseModel(**config)


# Model Validator #################################
# The model validator function differs from the standard model_validate()
# functionality of a Pydantic model. The model_validator function can take
# in either a single database configuration or a multi-database configuration
# and reutrn the specific model that it matches. This may be useful when
# more models are added to the library.


@pytest.mark.parametrize("test_config", valid_tests, ids=valid_test_ids)
def test_model_validator(test_config):
    """
    Test the model_validator function to ensure it returns an instance
    of the DatabaseModel when provided with a configuration that matches.

    Args:
        test_config (dict): A dictionary containing configuration
            settings for the test.
    Asserts:
        The function asserts that the type of the returned model
        is "DatabaseModel".
    """

    config = test_config["config"] if "config" in test_config else {}

    model = model_validator(config)
    assert type(model).__name__ == "DatabaseModel"


@pytest.mark.parametrize("test_config", valid_multidb_tests)
def test_model_valitor_multidb(test_config):
    """
    Test the model_validator function to ensure it returns an instance
    of MultiDatabaseModel when provided with a configuration that matches
    the MultiDatabaseModel schema.
    Args:
        test_config (dict): A dictionary containing the test configuration.
            It should have a key "config" which holds the configuration
            for the model_validator function.
    Asserts:
        Asserts that the type of the model returned by model_validator
        is "MultiDatabaseModel".
    """

    config = test_config["config"] if "config" in test_config else {}

    model = model_validator(config)
    assert type(model).__name__ == "MultiDatabaseModel"
