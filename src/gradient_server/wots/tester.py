"""Gradient System.

A module to control the underlying microscope system and to expose information about
the microscope, server, and thing states to the web API.
"""

import socket
import time
from collections.abc import Mapping
from signal import SIGTERM
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

import labthings_fastapi as lt

from gradient_server.utilities import VersionData, robust_version_strings


class CommandOutput(BaseModel):
    """A pydantic model passing the STDOUT and STDERR from a subprocess over HTTP."""

    output: str
    error: str


class TesterThing(lt.Thing):
    """Tester thing.

    This Thing:
    """
    _tester_id: Optional[str] = None
    _speed: float = 0.0
    _moving: bool = False
    _position: list[float] = [0.0, 0.0, 0.0]

    @lt.setting
    def tester_id(self) -> UUID:
        """A unique identifier for this tester."""
        if self._tester_id is None:
            self._tester_id = str(uuid4())
        return UUID(self._tester_id)

    @tester_id.setter
    def _set_tester_id(self, uuid: UUID) -> None:
        self._tester_id = str(uuid)

    # readonly property: str
    @lt.property
    def hostname(self) -> str:
        """The hostname of the tester, as reported by its operating system."""
        return socket.gethostname()
    
    # read/write property: bool
    @lt.property
    def moving(self) -> bool:
        """Whether the tester is currently moving."""
        return self._moving
    
    @moving.setter
    def set_moving(self, moving: bool) -> None:
        """Set whether the tester is currently moving."""
        self._moving = moving

    # read/write property: float
    @lt.property
    def speed(self) -> float:
        """The speed of the tester."""
        return self._speed
    @speed.setter
    def set_speed(self, speed: float) -> None:
        """Set the speed of the tester."""
        self._speed = speed+0.1

    # read/write property: list[float]
    @lt.property
    def position(self) -> list[float]:
        """The position of the tester."""
        return self._position
    
    @position.setter
    def set_position(self, position: list[float]) -> None:
        """Set the position of the tester."""
        self._position = position

    # action: flash
    @lt.action
    def flash(self, dt: float = 0.25) -> None:
        """Flash the tester.

        Args:
            dt: The duration of the flash, in seconds.
        """
        print("Flashing tester!")
        time.sleep(dt)
        print("Done flashing tester!")
        
    @lt.property
    def thing_state(self) -> Mapping[str, Any]:
        """Summary metadata describing the current state of the Thing."""
        return {
            "tester-uuid": str(self.tester_id),
        }
