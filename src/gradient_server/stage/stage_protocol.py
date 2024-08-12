from typing import Protocol, Dict
from enum import Enum
from pydantic import BaseModel


class StageState(str, Enum):
    OPENED = "opened"
    CLOSED = "closed"
    MOVING = "moving"


class StageProperties(BaseModel): ...


class StageProtocol(Protocol):
    def open(self): ...

    def close(self): ...

    def get_position(self) -> float: ...

    def move_position_abs(self, pos: float): ...

    def move_position_rel(self, step: float): ...

    def get_state(self) -> StageState: ...

    def get_properties(self) -> StageProperties: ...
