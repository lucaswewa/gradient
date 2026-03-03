"""Gradient Simulated Camera.

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
from types import TracebackType
from typing import Literal, Mapping, Optional, Self, overload

import numpy as np
from PIL import Image, ImageFilter

import labthings_fastapi as lt
from labthings_fastapi.types.numpy import NDArray

from ..projector import SimulatedProjector
from ..stage import SimulatedStage
from .base_camera import BaseCamera

LOGGER = logging.getLogger(__name__)

# The ratio between "motor" steps and pixels in (x, y, z)
# higher related to a faster movement
RATIO = (2, 2, 0.07)

# Random Number Generator
RNG = np.random.default_rng()


DOWNSAMPLE = 2
LOW_MAG_DOWNSAMPLE = 8

@overload
def _downsample_shape(
    shape: tuple[int, int], factor: float | int
) -> tuple[int, int]: ...


@overload
def _downsample_shape(
    shape: tuple[int, int, int], factor: float | int
) -> tuple[int, int, int]: ...


def _downsample_shape(
    shape: tuple[int, int] | tuple[int, int, int], factor: float | int
) -> tuple[int, int] | tuple[int, int, int]:
    if len(shape) == 2:
        return (int(shape[0] // factor), int(shape[1] // factor))
    if len(shape) == 3:
        return (int(shape[0] // factor), int(shape[1] // factor), shape[2])
    raise ValueError("Shape should be a 2 or 3 element tuple.")


class SimulatedCamera(BaseCamera):
    """A Thing that simulates a camera for testing."""

    _stage: SimulatedStage = lt.thing_slot()
    _projectors: Mapping[str, SimulatedProjector] = lt.thing_slot() # ["projector_r", "projector_g", "projector_b"])
    _show_sample: bool = True

    _objective: int = 40  # default 40x, our standard build

    @lt.property
    def objective(self) -> int:
        """Objective magnification (e.g. 4, 10, 20, 40, 60, 100)."""
        return self._objective

    @objective.setter
    def _set_objective(self, value: int) -> None:
        if value not in (4, 10, 20, 40, 60, 100):
            raise ValueError("Objective must be one of 4, 10, 20, 40, 60, 100.")
        self._objective = value

    def __init__(
        self,
        thing_server_interface: lt.ThingServerInterface,
        shape: tuple[int, int, int] = (616, 820, 3),
        canvas_shape: tuple[int, int, int] = (1500, 2000, 3),
        frame_interval: float = 0.1,
    ) -> None:
        """Initialise the simulated with settings for how images are generated.

        :param shape: The shape (size) of the generated image.
        :param canvas_shape: The shape (size) of the canvas generated on initialisation
            that images are cropped from. If this is too large the it uses resources,
            but its size limits the range of motion of the simulation.
        :param frame_interval: Nominally the time between frames on the MJPEG stream,
            however the rate may be slower due to calculation time for focus.
        """
        super().__init__(thing_server_interface)
        self.shape = shape
        self.glyph_size = 105 // DOWNSAMPLE
        self.canvas_shape = _downsample_shape(canvas_shape, DOWNSAMPLE)
        self.low_mag_canvas_shape = _downsample_shape(canvas_shape, LOW_MAG_DOWNSAMPLE)
        self.frame_interval = frame_interval
        self._capture_thread: Optional[Thread] = None
        self._capture_enabled = False
        # Whether the LED is on
        self.shutter_on = True
        self._exposure_gain = 1.5
        self._exposure_time = 1000.0  # us
        self._gain = 0.0  # dB

    _blob_density: int = 400

    @lt.property
    def exposure(self) -> float:
        return self._exposure_time
    
    @exposure.setter
    def _set_exposure(self, val: float) -> None:
        self._exposure_time = val

    @lt.property
    def gain(self) -> float:
        return self._gain
    
    @exposure.setter
    def _set_gain(self, val: float) -> None:
        self._gain = val

    @lt.property
    def exposure_gain(self) -> float:
        """The exposure and gain of the camera.
        """
        return self._exposure_gain

    @exposure_gain.setter
    def _set_exposure_gain(self, exposure_gain_value: float) -> None:
        self._exposure_gain = exposure_gain_value

    @lt.property
    def calibration_required(self) -> bool:
        """Whether the camera needs calibrating."""
        if self.background_detector is None:
            return True
        return not self.background_detector.ready

    def generate_image(self, pos: tuple[int, int, int]) -> Image.Image:
        """Generate an image with blobs based on supplied coordinates.

        :param pos: a 3-item tuple containing the x,y,z coordinates of the 'stage'
        """
        canvas_width, canvas_height, _ = self.low_mag_canvas_shape
        # Base image size

        objective_downsample = self.objective / 40
        if objective_downsample >= 0.4:
            canvas = self._projectors["projector_r"].get_output_canvas() + self._projectors["projector_g"].get_output_canvas() + self._projectors["projector_b"].get_output_canvas()
            canvas = canvas * self._exposure_gain / 3
            canvas = canvas.astype(np.int32)
            canvas = canvas.clip(0, 255)
            canvas_width, canvas_height, _ = self.canvas_shape
            canvas_ds = DOWNSAMPLE
            img_downsample = DOWNSAMPLE * objective_downsample
        else:
            canvas = self._projectors["projector_r"].get_output_canvas_low_mag() + self._projectors["projector_g"].get_output_canvas_low_mag() + self._projectors["projector_b"].get_output_canvas_low_mag()
            canvas = canvas * self._exposure_gain / 3
            canvas = canvas.astype(np.int32)
            canvas = canvas.clip(0, 255)
            canvas_width, canvas_height, _ = self.low_mag_canvas_shape
            canvas_ds = LOW_MAG_DOWNSAMPLE
            img_downsample = LOW_MAG_DOWNSAMPLE * objective_downsample
        image_width, image_height, _ = _downsample_shape(self.shape, img_downsample)

        im_pos = (
            pos[0] * RATIO[0] / canvas_ds,
            pos[1] * RATIO[1] / canvas_ds,
            pos[2] * RATIO[2],
        )

        top_left = (
            int(im_pos[0]) - image_width // 2 + canvas_width // 2,
            int(im_pos[1]) - image_height // 2 + canvas_height // 2,
        )

        x_indices = np.arange(top_left[0], top_left[0] + image_width)
        y_indices = np.arange(top_left[1], top_left[1] + image_height)

        x_indices = np.clip(x_indices, 0, canvas_width - 1)
        y_indices = np.clip(y_indices, 0, canvas_height - 1)

        z_indices = np.arange(self.shape[2])

        # Use npx to make each 1d index list 3D
        focused_np_img = canvas[np.ix_(x_indices, y_indices, z_indices)]
        np_img = fast_resize_and_blur(
            focused_np_img, sigma=np.abs(im_pos[2]) / 5, shape=self.shape
        )
        # Generate random noise by repeating 500 noise points, as the speed rather
        # than randomness is important for simulation.
        noise = RNG.normal(scale=self.noise_level, size=500).astype("int16")
        np_img += np.resize(noise, np_img.shape)
        # Clip then convert to uint8
        np.clip(np_img, 0, 255, out=np_img)
        return Image.fromarray(np_img.astype("uint8"))

    @lt.action
    def set_shutter(self, shutter_on: bool = True) -> None:
        """Set the simulated LED to on or off."""
        self.shutter_on = shutter_on

    @lt.action
    def set_led(self, led_on: bool = True) -> None:
        """Set the simulated LED to on or off."""
        # self.set_shutter(led_on)
        self._projectors["projector_r"].set_led(led_on)
        self._projectors["projector_g"].set_led(led_on)
        # self._projectors["projector_b"].set_led(led_on)

    def generate_frame(self) -> Image.Image:
        """Generate a frame with blobs based on the stage coordinates."""
        # Simulate LED turning off by setting all channels to 0
        if not self.shutter_on:
            return Image.new(mode="RGB", size=(self.shape[1], self.shape[0]), color=0)
        # Otherwise, generate a frame from current position
        try:
            pos = self._stage.instantaneous_position
            return self.generate_image((pos["y"], pos["x"], pos["z"]))
        except Exception:
            return Image.new(mode="RGB", size=(self.shape[1], self.shape[0]), color=0)

    def __enter__(self) -> Self:
        """Start the capture thread when the Thing context manager is opened."""
        super().__enter__()
        self.start_streaming()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Close the capture thread when the Thing context manager is closed."""
        if self._capture_thread is not None and self._capture_thread.is_alive():
            self._capture_enabled = False
            self._capture_thread.join()
        super().__exit__(exc_type, exc_value, traceback)

    @lt.action
    def start_streaming(
        self, main_resolution: tuple[int, int] = (820, 616), buffer_count: int = 1
    ) -> None:
        """Start the live stream.

        The start_streaming method is used a camera ``Thing`` to begin streaming
        images or to adjust the stream resolution if streaming is already active.

        The simulation camera does not currently support the resolution argument.
        It will always issue a warning that the resolution is not respected.
        If called while already streaming, the warning will be emitted and no other
        action will be taken.

        :param main_resolution: Currently ignored, this argument exists to ensure consistent API across camera Things.
        :param buffer_count: Currently ignored, this argument exists to ensure consistent API across camera Things.
        """
        LOGGER.warning(
            f"Simulation camera doesn't respect {main_resolution=} or {buffer_count=} "
            "arguments."
        )
        if not self.stream_active:
            self._capture_enabled = True
            self._capture_thread = Thread(target=self._capture_frames)
            self._capture_thread.start()

    @lt.property
    def stream_active(self) -> bool:
        """Whether the MJPEG stream is active."""
        if self._capture_enabled and self._capture_thread:
            return self._capture_thread.is_alive()
        return False

    noise_level: float = lt.property(default=2.0)

    def _capture_frames(self) -> None:
        last_frame_t = time.time()
        while self._capture_enabled:
            wait_time = self.frame_interval - (time.time() - last_frame_t)
            if wait_time > 0:
                time.sleep(wait_time)
            last_frame_t = time.time()

            frame = self.generate_frame()
            self.mjpeg_stream.add_frame(_frame2bytes(frame))
            ds_frame = frame.resize((320, 240), resample=Image.Resampling.NEAREST)
            self.lores_mjpeg_stream.add_frame(_frame2bytes(ds_frame))

    @lt.action
    def discard_frames(self) -> None:
        """Discard frames so that the next frame captured is fresh.

        There is nothing to do as this is a simulation!
        """

    @lt.action
    def capture_array(
        self,
        stream_name: Literal["main", "lores", "raw", "full"] = "full",
        wait: Optional[float] = None,
    ) -> NDArray:
        """Acquire one image from the camera and return as an array.

        This function will produce a nested list containing an uncompressed RGB image.
        It's likely to be highly inefficient - raw and/or uncompressed captures using
        binary image formats will be added in due course.

        :param stream_name: Currently ignored, this argument exists to ensure consistent API across camera Things.
        :param wait: Currently ignored, this argument exists to ensure consistent API across camera Things.
        """
        if wait is not None:
            LOGGER.warning("Simulation camera has no wait option. Use None.")
        LOGGER.warning(f"Simulation camera camera doesn't respect {stream_name=}")
        return np.array(self.generate_frame())

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
        if wait is not None:
            LOGGER.warning("Simulation camera has no wait option. Use None.")
        LOGGER.warning(f"Simulation camera camera doesn't respect {stream_name=}")
        return self.generate_frame()

    @lt.action
    def full_auto_calibrate(self) -> None:
        """Perform a full auto-calibration.

        For the simulation microscope the process is:

        * ``remove_sample``
        * ``set_background``
        * ``load_sample``
        """
        self.remove_sample()
        time.sleep(0.2)
        if self.background_detector is not None:
            self.set_background()
        time.sleep(0.2)
        self.load_sample()

    @lt.action
    def remove_sample(self) -> None:
        """Show the simulated background with no sample."""
        if not self._show_sample:
            raise RuntimeError("Sample is already removed.")
        self._show_sample = False

    @lt.action
    def load_sample(self) -> None:
        """Show the simulated sample."""
        if self._show_sample:
            raise RuntimeError("Sample is already in place.")
        self._show_sample = True


def _frame2bytes(frame: Image.Image) -> bytes:
    """Convert frame to bytes."""
    with io.BytesIO() as buf:
        # Save in low quality for speed.
        frame.save(buf, format="JPEG", quality=85)
        return buf.getvalue()


def fast_resize_and_blur(
    array: np.ndarray, sigma: float, shape: tuple[int, ...]
) -> np.ndarray:
    """Apply Gaussian blur using PIL (faster than scipy)."""
    img_pil = Image.fromarray(array.astype(np.uint8))
    img_pil = img_pil.resize((shape[1], shape[0]), Image.Resampling.BILINEAR)
    if sigma > 0.5:
        img_pil = img_pil.filter(ImageFilter.GaussianBlur(radius=sigma))

    # Convert back to NumPy array
    return np.array(img_pil, dtype=array.dtype)
