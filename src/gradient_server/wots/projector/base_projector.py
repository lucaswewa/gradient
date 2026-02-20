"""Base Camera.

This module defines the BaseCamera. Any compatible lt.Thing
should enable the server to work.

See repository root for licensing information.
"""

from __future__ import annotations

from types import TracebackType
from typing import Optional, Self



import labthings_fastapi as lt


class BaseProjector(lt.Thing):
    """The base class for all projectors. All projectors must directly inherit from this class.

    The connection to the projector hardware should be added to the ``__enter__`` method not
    ``__init__`` method of the subclass.
    """

    def __init__(self, thing_server_interface: lt.ThingServerInterface) -> None:
        """Initialise the base projector.

        This must be run by all child projector classes.
        """
        super().__init__(thing_server_interface)

    def __enter__(self) -> Self:
        """Open hardware connection when the Thing context manager is opened."""
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException],
        _exc_value: Optional[BaseException],
        _traceback: Optional[TracebackType],
    ) -> None:
        """Close hardware connection when the Thing context manager is closed."""
        pass
