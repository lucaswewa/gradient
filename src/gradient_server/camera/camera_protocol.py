from typing import Protocol
from enum import Enum
from pydantic import BaseModel


class PixelFormat(str, Enum):
    MONO8 = "MONO8"
    MONO10 = "MONO10"
    MONO12 = "MONO12"


class CameraState(str, Enum):
    OPENED = "opened"
    CLOSED = "closed"
    STREAMING = "streaming"
    CAPTURING1 = "capturing1"
    CAPTURING2 = "capturing2"
    CAPTURING3 = "capturing3"
    CAPTURING4 = "capturing4"
    IDLE1 = "idle1"
    IDLE2 = "idle2"
    IDLE3 = "idle3"
    IDLE4 = "idle4"


class CameraProperties(BaseModel): ...


class CameraProtocol(Protocol):
    def open(self): ...

    def close(self): ...

    def get_properties(self) -> CameraProperties: ...

    def get_state(self) -> CameraState: ...

    def set_exposure(self, exposure: float): ...

    def get_exposure(self) -> float: ...

    def set_gain(self, gain: float): ...

    def get_gain(self) -> float: ...

    def set_pixel_format(self, format: PixelFormat): ...

    def get_pixel_format(self) -> PixelFormat: ...

    def set_binning(self, binning_hori: int, binning_vert: int): ...

    def get_binning(self) -> tuple[int, int]: ...

    def start_stream(self): ...

    def stop_stream(self): ...

    def capture(self): ...

    def register_frame_callback(self, cb): ...
