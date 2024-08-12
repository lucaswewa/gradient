from .stage_protocol import StageProtocol
from .stage_protocol import StageState, StageProperties


class VirtualStage(StageProtocol):
    def __init__(self, name):
        self._name = name
        self._status = None
        self._position = 0.0
        self._properties: StageProperties

    def thread_run(self): ...

    def open(self):
        self._status = StageState.OPENED

    def close(self):
        self._status = StageState.CLOSED

    def move_position_abs(self, pos_abs: float):
        self._position = pos_abs

    def move_position_rel(self, pos_rel: float):
        self._position += pos_rel

    def get_position(self):
        return self._position

    def get_state(self) -> StageState:
        return self._status

    def get_properties(self) -> StageProperties:
        return self._properties
