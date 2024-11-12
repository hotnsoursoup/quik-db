"In development. Class for tracking changes to the connection object"

from __future__ import annotations

from datetime import datetime
from typing import (
    Any,
    List,
    Optional,
    Tuple,
    Type,
)

import wrapt
from pydantic import BaseModel


ChangeRecord = Tuple[
    str, str, str, Optional[dict[str, Any]], Optional[Any], datetime
]


class ChangeTrackingProxy(wrapt.ObjectProxy):
    """
    A proxy to track changes in attributes and methods, including
    nested ones.

    Args:
        wrapped: The object to be wrapped and monitored for changes.
    """

    def __init__(self, wrapped: Any) -> None:
        super().__init__(wrapped)
        self._changes: List[ChangeRecord] = []
        self._self_debug = getattr(wrapped, "debug", False)

    def record_change(
        self,
        parent: str,
        path: str,
        change_type: str,
        params: Optional[dict[str, Any]] = None,
        new_value: Optional[Any] = None,
    ) -> None:
        """
        Record a change with specified details.

        Args:
            parent: The name of the parent object.
            path: The path to the changed attribute or method.
            change_type: The type of change, e.g., 'attribute_change'.
            params: Optional; any parameters involved in the change.
            new_value: Optional; the new value after the change.
        """
        timestamp = datetime.now()
        self._changes.append((
            parent,
            path,
            change_type,
            params,
            new_value,
            timestamp,
        ))

    def __setattr__(self, name: str, value: Any) -> None:
        if self._self_debug and not name.startswith("_"):
            old_value = getattr(self, name, None)
            if old_value != value:
                full_path = f"{self.__wrapped__.__class__.__name__}.{name}"
                self.record_change(
                    parent=self.__wrapped__.__class__.__name__,
                    path=full_path,
                    change_type="attribute_change",
                    new_value=value,
                )
        super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        attr = super().__getattr__(name)
        if isinstance(attr, (BaseModel, dict, list)) and not isinstance(
            attr, ChangeTrackingProxy
        ):
            return ChangeTrackingProxy(attr)
        elif callable(attr) and not name.startswith("_"):

            @wrapt.decorator
            def track_call(wrapped, instance, args, kwargs):
                if self._self_debug:
                    full_path = f"{self.__wrapped__.__class__.__name__}.{name}"
                    self.record_change(
                        parent=self.__wrapped__.__class__.__name__,
                        path=full_path,
                        change_type="method_call",
                        params={"args": args, "kwargs": kwargs},
                    )
                return wrapped(*args, **kwargs)

            return track_call(attr)
        return attr


def with_tracking(cls: Type[BaseModel]) -> Type[BaseModel]:
    """
    Class factory to apply ChangeTrackingProxy subclassing if
    `debug` is True.

    Args:
        cls: The target class to apply tracking to if its debug
            attribute is True.

    Returns:
        The tracked class if `debug` is True, else the original class.
    """
    if getattr(cls, "debug", False):

        class TrackedDatabaseConnection(ChangeTrackingProxy, cls):
            """
            TrackedDatabaseConnection is a class that extends
            ChangeTrackingProxy.
            """

            def __init__(self, *args, **kwargs):
                super().__init__(cls(*args, **kwargs))

        return TrackedDatabaseConnection
    return cls
