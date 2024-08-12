from pydantic import BaseModel
from .rxcompensation_protocol import RxCompensationProtocol
from .rxcompensation_protocol import RxCompensationState, RxCompensationProperties


class RxCompensationSettings(BaseModel):
    sphPower: float = 0.0
    cylPower: float = 0.0
    cylAxis: float = 0.0


class VirtualRxCompensation(RxCompensationProtocol):
    def __init__(self, name):
        self._name = name
        self._status: RxCompensationState = RxCompensationState.CLOSED
        self._position = RxCompensationSettings()
        self._properties: RxCompensationProperties = None

    def thread_run(self): ...

    def open(self):
        self._status = RxCompensationState.OPENED

    def close(self):
        self._status = RxCompensationState.CLOSED

    def get_state(self): ...

    def get_properties(self): ...

    def get_spherical_rx(self) -> float:
        return self._position.sphPower

    def get_cylindrical_rx_power(self) -> str:
        return self._position.cylPower

    def get_cylindrical_rx_axis(self) -> float:
        return self._position.cylAxis

    def move_spherical_rx(self, diopter: float):
        self._position.sphPower = diopter

    def move_cylindrical_rx_power(self, diopter: float):
        self._position.cylPower = diopter

    def move_cylindrical_rx_axis(self, angle: float):
        self._position.cylAxis = angle
