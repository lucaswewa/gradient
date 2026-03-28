"""VimbaX Camera Thing.

This module defines a Thing that is responsible for using the stage and
camera together to perform an autofocus routine.

See repository root for licensing information.
"""

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
from ...camera.vmbx import VmbX

LOGGER = logging.getLogger(__name__)

class VimbaCamera(BaseCamera):
    """Thing representing a camera that can be used for autofocus and imaging."""

    _stage: BaseStage = lt.thing_slot()

    def __init__(
        self,
        thing_server_interface: lt.ThingServerInterface,
        frame_interval: float = 0.1,
        device_id: str = None,
        **kwargs) -> None:
        super().__init__(thing_server_interface)
        self._capture_enabled = False
        self.frame_interval = frame_interval
        self._vmbx_lock = threading.RLock()
        self._vmbx = VmbX(device_id=device_id, frame_handler=self.frame_handler)
        self._vmb_frame = None
        self.shutter_on = True
        self.c = 1

    def __enter__(self):
        super().__enter__()
        self._vmbx.enter_camera()
        self.start_streaming()
        return self
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._vmbx.exit_camera()
        super().__exit__(exc_type, exc_value, traceback)

    def frame_handler(self, frame: NDArray) -> None:
        """Handle a new frame from the VmbX camera."""
        with self._vmbx_lock:
            data = frame.copy()
            image = Image.fromarray(data.astype("uint8"))
            self.mjpeg_stream.add_frame(_frame2bytes(image))
            ds_frame = image.resize((640, 480), resample=Image.Resampling.NEAREST)
            self.lores_mjpeg_stream.add_frame(_frame2bytes(ds_frame))

    def capture_image(
        self,
        stream_name: Literal["main", "lores", "full"],
        wait: Optional[float] = None,
    ) -> Image.Image:
        """Capture to a PIL image. This is not exposed as a ThingAction.

        It is used for capture to memory.

        :param stream_name: Currently ignored, this argument exists to ensure consistent API across camera Things.
        :param wait: Currently ignored, this argument exists to ensure consistent API across camera Things.
        """
        image = Image.fromarray(self._vmbx.grab_one().astype("uint8"))
        return image

    @lt.action
    def start_streaming(self) -> None:
        """Start streaming frames from the camera."""
        self._vmbx.start_streaming()

    @lt.action
    def stop_streaming(self) -> None:
        """Stop streaming frames from the camera."""
        self._vmbx.stop_streaming()

    @lt.property
    def is_streaming(self) -> bool:
        return self._vmbx.is_streaming()
    
    @is_streaming.setter
    def _set_is_streaming(self, val: bool) -> None:
        pass

    @lt.action
    def arm(self) -> None:
        """Set the simulated LED to on or off."""
        self._vmbx.arm()

    @lt.action
    def disarm(self) -> None:
        """Set the simulated LED to on or off."""
        self._vmbx.disarm()

    @lt.action
    def software_trigger(self) -> None:
        """Set the simulated LED to on or off."""
        self._vmbx.software_trigger()

    @lt.property
    def exposure_time(self) -> float:
        return self._vmbx.get_exposure_time_in_us()
    
    @exposure_time.setter
    def _set_exposure_time(self, exp_time: float) -> None:
        self._vmbx.set_exposure_time_in_us(exp_time)

    @lt.property
    def gain(self) -> float:
        return self._vmbx.get_gain()
    
    @gain.setter
    def _set_gain(self, val: float) -> None:
        self._vmbx.set_gain(val)