"""
Validation Module for database models.

This module provides a validator function for validating any db_models
against a given database configuration. It uses Pydantic for validation and

"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from quik_db.model.exceptions import ModelValidationError
from quik_db.model.models import DatabaseModel, MultiDatabaseModel


db_models = {
    "databasemodel": DatabaseModel,
    "multidatabasemodel": MultiDatabaseModel,
}


def model_validator(
    db_config: dict[str, Any],
    models: dict[str, Any] | None = None,
    model_name: str = "",
) -> DatabaseModel | MultiDatabaseModel:
    """
    Validates the given database configuration against the provided models.
    Args:
        db_config (dict[str, Any]): The database configuration to validate.
        models (dict[str, type[BaseModel]]): A dictionary of model names to
            model classes.
        model_name (str | None, optional): The name of a specific model to
            validate against. If None, all models will be validated.
    Returns:
        BaseModel: The validated model instance.
    Raises:
        ModelValidationError: If validation fails for all models or the
        specified model.
    """

    model_errors = {}
    models = models if models else db_models
    model_name = model_name.lower() if model_name else ""

    # Validation function. Tracks errors for each model.
    def validate_model(
        model_class: type[DatabaseModel | MultiDatabaseModel],
    ) -> MultiDatabaseModel | DatabaseModel | None:
        try:
            return model_class(**db_config)
        except ValidationError as e:
            model_errors[model_class.__name__] = e.errors()
            return None

    # Validate the specified model or all models
    if model_name:
        validated_model = validate_model(models[model_name])
        if validated_model:
            return validated_model
    else:
        for model_class in models.values():
            validated_model = validate_model(model_class)
            if validated_model:
                return validated_model

    raise ModelValidationError(model_errors)
