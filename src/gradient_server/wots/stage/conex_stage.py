from __future__ import annotations

import queue
import threading
import time
from collections.abc import Sequence
from types import TracebackType
from typing import Any, Mapping, Optional
from anyio.from_thread import BlockingPortal
import asyncio
import copy

import labthings_fastapi as lt

import logging

from ...stage.conex import Conex

LOGGER = logging.getLogger(__name__)

from . import BaseStage, BaseHardwareStage, JogCommand

class ConexStage(BaseStage):
    def __init__(self, thing_server_interface: lt.ThingServerInterface, port: str, **kwargs: Any) -> None:
        super().__init__(thing_server_interface, **kwargs)
        self._stage = Conex(port)

    def __enter__(self):
        self._stage.enter_stage()

    def __exit__(
        self,
        _exc_type: type[BaseException],
        _exc_value: Optional[BaseException],
        _traceback: Optional[TracebackType],
    ) -> None:
        self._stage.exit_stage()

    @lt.property
    def velocity(self) -> float:
        return self._stage.get_velocity()
    
    @velocity.setter
    def set_velocity(self, v: float):
        self._stage.set_velocity(v)

    @lt.action
    def move_abs(self, position: float) -> None:
        """Make a absolute move. Keyword arguments should be axis names."""
        self._stage.move_absolute(position)    

    @lt.action
    def move_rel(self, delta: float) -> None:
        """Make a relative move. Keyword arguments should be axis names."""
        self._stage.move_relative(delta)    

    @lt.property
    def position(self) -> float:
        """Current position of the stage."""
        return self._stage.get_position()