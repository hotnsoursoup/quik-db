from __future__ import annotations

from typing import NamedTuple


class TestSchema(NamedTuple):
    """
    A NamedTuple representing the schema for a test case.

    """

    root_category: str  # e.g., 'schema'
    sub_category: str  # e.g., 'db'
    test_type: str  # e.g., 'valid' or 'invalid'
    db_dialect: str  # e.g., 'postgresql', 'mysql'


class TestModelSchema(TestSchema):
    """
    Test models
    """

    connection_type: str  # e.g., 'url' or 'params'
    root_key: str | None = None  # e.g., 'query_settings'
    sub_key: str | None = None  # e.g., 'prefix_schema'


class TestConnectionMethodSchema(TestSchema):
    something: str