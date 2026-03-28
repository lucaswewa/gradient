
from __future__ import annotations

import io
import logging
import re
import time
from threading import Thread
import threading
from types import TracebackType
from typing import Literal, Mapping, Optional, overload

import numpy as np
from PIL import Image, ImageFilter

import labthings_fastapi as lt
from labthings_fastapi.types.numpy import NDArray
import cv2

from gradient_server.wots.camera.simulation_camera import _frame2bytes
from gradient_server.wots.stage import BaseStage

from ..projector import SimulatedProjector
from ..stage import SimulatedStage
from .base_camera import BaseCamera
from ...camera.spinnaker import SpinnakerCamera

import labthings_fastapi as lt
from typing import Literal, Mapping, Optional, overload
from types import TracebackType
from PIL import Image
import io
import threading
from ...camera import Camera

LOGGER = logging.getLogger(__name__)

def _frame2bytes(frame: Image.Image) -> bytes:
    """Convert frame to bytes."""
    with io.BytesIO() as buf:
        # Save in low quality for speed.
        frame.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    
class FlirCamera(BaseCamera):
    # mjpeg_stream = lt.outputs.MJPEGStreamDescriptor()
    _stage: BaseStage = lt.thing_slot()

    def __init__(self, thing_server_interface):
        super().__init__(thing_server_interface)

        self.cam: Camera = SpinnakerCamera()

    def __enter__(self):
        super().__enter__()
        self.cam.enter()
        self.start_streaming()
        return self
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.cam.exit()
        super().__exit__(exc_type, exc_value, traceback)

    def cb(self, data):
        image = Image.fromarray(data.astype("uint8"))
        self.mjpeg_stream.add_frame(_frame2bytes(image))
        ds_frame = image.resize((1280, 960), resample=Image.Resampling.NEAREST)
        self.lores_mjpeg_stream.add_frame(_frame2bytes(ds_frame))

    @lt.action
    def acquire(self):
        data = self.cam.acquire(self.cb, 1000)


    @lt.action
    def start_streaming(self):
        self.cam.start_streaming(self.cb)

    @lt.action
    def stop_streaming(self):
        self.cam.stop_streaming()

    @lt.action
    def software_trigger(self):
        self.cam.trigger_and_capture()

    @lt.property
    def is_streaming(self) -> bool:
        return self.cam.is_streaming()
    
    @is_streaming.setter
    def _set_is_streaming(self, val: bool) -> None:
        pass
    
    @lt.property
    def exposure_time(self) -> float:
        return self.cam.get_exposure_time()
    
    @exposure_time.setter
    def _set_exposure_time(self, exp_time: float):
        self.cam.set_exposure_time(exp_time)

    @lt.property
    def gain(self) -> float:
        return self.cam.get_gain()
    
    @gain.setter
    def _set_gain(self, gain):
        self.cam.set_gain(gain)

    @lt.action
    def arm(self) -> None:
        """Set the simulated LED to on or off."""
        self.cam.arm()

    @lt.action
    def disarm(self) -> None:
        """Set the simulated LED to on or off."""
        self.cam.disarm()

    @lt.action
    def software_trigger(self) -> None:
        """Set the simulated LED to on or off."""
        image_data = self.cam.trigger_and_capture()
