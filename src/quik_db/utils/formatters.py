from __future__ import annotations

import re
import string


def clean_data(
    data: str | dict | list, lowercase: bool = False
) -> str | dict | list:
    """
    Cleans data based on type. Removes whitespaces and can convert to lowercase
    if specified.

    :param data: data to be cleaned and lowered if True
    :type data: dict, list, str
    :param lowercase: Lowercases nested structure, defaults to False
    :type lowercase: bool, optional
    :return: data
    :rtype: dict, list, str
    """
    if isinstance(data, dict):
        return {
            clean_data(k, lowercase): clean_data(v, lowercase)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [clean_data(item, lowercase) for item in data]
    elif isinstance(data, str):
        return re.sub(r"\s+", "", data.lower() if lowercase else data)
    else:
        return data


def capitalize(str: str) -> str:
    "Capitalizes the first character within a group"
    return re.sub(
        r"(^|[/!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), str
    )


def lowercase_nested_data(data: str | dict | list) -> str | dict | list:
    """
    Lowercases all keys in nested dictionaries and lists.

    :param data: data to be lowercased
    :type data: str, dict, list
    :return: data
    :rtype: str, dict, list
    """
    if isinstance(data, dict):
        return {k.lower(): lowercase_nested_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_nested_data(item) for item in data]
    elif isinstance(data, str):
        return data.lower()
    else:
        return data


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def safe_format(format_string: str, **kwargs) -> str:
    """Format the string with available keys in the dictionary."""
    formatter = string.Formatter()
    safe_dict = SafeDict(**kwargs)
    return formatter.vformat(format_string, (), safe_dict)


def clean_dict(dictionary: dict) -> dict:
    """Removes None values from the dictionary."""

    # if a list, clean each item in the list
    if isinstance(dictionary, list):
        return [clean_dict(item) for item in dictionary]

    # if not a dictionary or a tuple, just return it
    if not isinstance(dictionary, dict):
        return dictionary

    return {
        key: clean_dict(val)
        for key, val in dictionary.items()
        if val is not None
    }


def flatten_str(message: str) -> str:
    """Removes line breaks and excess spaces from the string"""
    return " ".join(message.split())


def flatten_dict(message: dict) -> dict:
    """Flattens strings in a dictionary"""
    for key, value in message.items():
        if isinstance(value, dict):
            message[key] = flatten_dict(value)
        elif isinstance(value, list):
            message[key] = [
                (
                    flatten_dict(item)
                    if isinstance(item, dict)
                    else flatten_str(item)
                )
                for item in value
            ]
        elif isinstance(value, str):
            message[key] = flatten_str(value)
    return message


def fix_format_args(query: str) -> None:
    """
    Checks if the SQL query string contains incorrectly formatted
    arguments, such as {arg}, %s, %d, f-strings, or string
    concatenation.

    Args:
        query (str): The SQL query string.

    Returns:
        str: Fixed query string compatible with the text() construct
    """
    # Define patterns for incorrect formatting
    incorrect_patterns = [
        r"\{.*?\}",  # Curly braces for format() or f-strings
        r"%s",
        r"%d",
        r"%\w",  # Old-style % formatting
        r'f".*?"',  # f-strings (Python 3.6+)
        r"f\'.*?\'",  # f-strings with single quotes
    ]

    # Check for each incorrect pattern
    for pattern in incorrect_patterns:
        if re.search(pattern, query):
            return True  # Return True if any incorrect format is found

    # If none of the incorrect formats are found, return False
    return False
