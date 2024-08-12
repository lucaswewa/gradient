import threading
import time

from .filterwheel_protocol import FilterwheelProtocol
from .filterwheel_protocol import FilterwheelState, FilterwheelProperties
from typing import Dict


class VirtualFilterwheel(FilterwheelProtocol):
    def __init__(self, name):
        self._name = name
        self._status = None
        self._position = 0
        self._mapping: Dict[int, str] = None
        self._properties: FilterwheelProperties = FilterwheelProperties()

    def thread_run(self): ...

    def open(self):
        self._status = FilterwheelState.OPENED

    def close(self):
        self._status = FilterwheelState.CLOSED

    def set_position_mapping(self, mapping: Dict[int, str]):
        self._mapping = mapping

    def get_position_mapping(self) -> Dict[int, str]:
        return self._mapping

    def get_properties(self):
        return self._properties

    def get_state(self):
        return self._status

    def get_position(self) -> int:
        return self._position

    def set_position(self, pos: int):
        self._position = pos

    def get_position_by_name(self) -> str:
        return self._mapping[self._position]

    def set_position_by_name(self, position_name: str):
        for key, val in self._mapping.items():
            if val == position_name:
                self._position = key
                return
