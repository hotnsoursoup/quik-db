"""
This module is for handlers you can use in the DatabaseConnection objects.
"""

# ruff: noqa: E501
# flake8: noqa: E501
from __future__ import annotations

import re
from typing import Any, Callable

from dateutil import parser
from sqlalchemy.engine.row import Row


def handler(
    handlers: Callable | list[Callable],
    data: Any,
) -> Any:
    """
    Process the data with the given handler(s).

    Args:
        data: The data to process.
        handler: A single handler or a list of handlers.
        out: Provide the default output for the handler(s) if there is no
            expected return value.

    Returns:
        The processed data.
    """
    if isinstance(handlers, list):
        for h in handlers:
            data = h(data)
    else:
        data = handlers(data)
    return data


class DateFormatter:
    """
    Class to recursively format date strings in a data structure.

    Attributes:
        date_format (str): The format to convert date strings into.
        date_patterns (list[str]): list of regex patterns to identify
            date strings.
        compiled_patterns (list[Pattern]): Compiled regex patterns.
    """

    def __init__(self, date_format: str = "%Y-%m-%d") -> None:
        """
        Initializes the DateFormatter with a specific date format.

        Args:
            date_format (str): The desired date format for output
                strings.
        """
        self.date_format = date_format
        # Define regex patterns for date/datetime strings
        self.date_patterns = [
            r"\b\d{4}-\d{1,2}-\d{1,2}\b",  # YYYY-M-D or YYYY-MM-DD
            r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",  # M/D/YYYY or MM/DD/YY
            r"\b\d{1,2}-\d{1,2}-\d{2,4}\b",  # D-M-YYYY or DD-MM-YY
            r"\b\d{4}/\d{1,2}/\d{1,2}\b",  # YYYY/M/D or YYYY/MM/DD
            r"\b\d{4}-\d{1,2}-\d{1,2} \d{2}:\d{2}:\d{2}\b",  # YYYY-M-D HH:MM:SS
            r"\b\d{4}/\d{1,2}/\d{1,2} \d{2}:\d{2}:\d{2}\b",  # YYYY/M/D HH:MM:SS
            r"\b\d{1,2} \w{3} \d{4}\b",  # D Mon YYYY
            r"\b\w{3} \d{1,2}, \d{4}\b",  # Mon D, YYYY
        ]

        self.compiled_patterns = [re.compile(p) for p in self.date_patterns]

    def is_date_string(self, s: str) -> bool:
        """
        Checks if a string matches any of the date regex patterns.

        Args:
            s (str): The string to check.

        Returns:
            bool: True if the string is a date, False otherwise.
        """
        return any(pattern.fullmatch(s) for pattern in self.compiled_patterns)

    def process_data(self, data: Any) -> Any:
        """
        Recursively processes the data to format date strings.

        Args:
            data (Any): The data to process (dict, list, str, or other).

        Returns:
            Any: The processed data with formatted date strings.
        """
        if isinstance(data, dict):
            return {k: self.process_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.process_data(item) for item in data]
        elif isinstance(data, str):
            if self.is_date_string(data):
                try:
                    dt = parser.parse(data)
                    return dt.strftime(self.date_format)
                except (ValueError, OverflowError):
                    return data
            else:
                return data
        else:
            return data

    def __call__(self, data: Any) -> Any:
        """
        Allow the instance to be called like a function.

        Args:
            data (Any): The data to process.

        Returns:
            Any: The processed data.

        """
        return self.process_data(data)


def single_row_to_dict(data: list[dict]) -> dict:
    """Manage the conversion of a single row of data to a dictionary."""
    if len(data) == 1 and isinstance(data, list):
        return data[0]
    return data


def result_to_dict(
    result: Row | list[Row],
) -> dict[str, Any] | list[dict[str, Any]]:
    """
    Converts SQLAlchemy result to a dictionary or list of dictionaries.

    Args:
        result: A single SQLAlchemy Row or a list of Rows.

    Returns:
        A dictionary or a list of dictionaries.
    """
    if isinstance(result, Row):
        return dict(result)
    return [dict(row) for row in result]
