"Model Validation Errors"

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from quik_db.dictionaries import db_validation_errors


if TYPE_CHECKING:
    from pydantic_core import ErrorDetails


class ModelValidationError(Exception):
    """
    Exception for model validation errors.

    This exception is raised when all models fail to validate the
    configuration.
    """

    def __init__(self, model_errors: dict[str, list[dict]]) -> None:
        """
        Initialize with a dictionary of errors.

        :param model_errors: Dictionary of error messages values from
        ValidationError.errors().

        """
        self.errors = model_errors
        self.models = list(model_errors.keys())
        super().__init__(self._generate_message())

    def _generate_message(self) -> str:
        """
        Generate a comprehensive error message combining all
        model errors.
        """
        messages = []
        model_count = len(self.errors)
        plural = "s" if model_count != 1 else ""
        messages.append(f"{model_count} model{plural} tested for validation.")

        for model, errors in self.errors.items():
            error_count = len(errors)
            messages.append(
                f"\nModel '{model}' encountered {error_count} error(s):",
            )
            for error in errors:
                loc = ".".join(map(str, error.get("loc", [])))
                msg = get_error_msg(error)
                type_ = error.get("type", "")
                # Initialize error message
                error_msg = (
                    f"  - Location: {loc}\n    "
                    f"Message: {msg}\n    "
                    f"Type: {type_}"
                )
                # Add context details
                for k, v in error.get("ctx", {}).items():
                    error_msg += f"\n    {k}: {v}"

                messages.append(error_msg)

        # Summary information
        total_errors = sum(len(errs) for errs in self.errors.values())
        messages.append(f"\nTotal Errors: {total_errors}")
        return "\n".join(messages)


def get_error_msg(error: dict | ErrorDetails) -> str:
    """
    Extract and return an error message from a given error dictionary.

    Args:
        error (dict): A dictionary containing error information.

    Returns:
        str: The extracted error message. If the "ctx" dictionary
            contains an "error" key, its value is returned. Otherwise,
            the value of the "msg" key in the error dictionary is
            returned. If neither is present, an empty string is returned.

    """
    ctx = error.get("ctx", {})
    if ctx and ctx.get("error"):
        return ctx.pop("error")
    return error.get("msg", "")


class SettingValidationError(Exception):
    """Exception to hold a list of validation errors."""

    def __init__(self, errors: list):
        super().__init__("Validation errors occurred.")
        self.errors = errors  # Store the list of errors as-is


def create_error_msg(key: str, ctx: dict | str | None = None) -> dict:
    """
    Retrieve and update an error dictionary for the given key.

    Retrieves the error dictionary from `db_validation_errors` and, if
    `ctx` is provided, updates the "ctx" section in the error dictionary
    with values from `ctx`.

    Args:
        key (str): The key to retrieve the error dictionary.
        ctx (dict, optional): Dictionary with keys to update the "ctx"
            field within the error dictionary.

    Returns:
        dict: Updated error dictionary with None values removed.
    """
    error = deepcopy(db_validation_errors[key])

    # Update the context if provided
    if ctx:
        if isinstance(ctx, str):
            ctx = {"value": ctx}
        if "ctx" not in error:
            error["ctx"] = {}
        error["ctx"].update(ctx)

    # Return only set values
    return {k: v for k, v in error.items() if v is not None}
