"""Gradient Simulated Projector.

See repository root for licensing information.
"""

from __future__ import annotations

import io
import logging
import re
import time
from threading import Thread
from types import TracebackType
from typing import Literal, Optional, overload

import numpy as np
from PIL import Image, ImageFilter

import labthings_fastapi as lt
from labthings_fastapi.types.numpy import NDArray
import anyio

from .base_projector import BaseProjector
from .. import GradientThing

LOGGER = logging.getLogger(__name__)

# Some colour variation, for bg detect.
BG_COLOR = [0, 0, 0]

# Random Number Generator
RNG = np.random.default_rng()


DOWNSAMPLE = 2
LOW_MAG_DOWNSAMPLE = 8
# Upsample for sprites and then downsample to create sharp edges for each sprite
# as these are small and calculated once there is almost no performance penalty
# for a nice gain in quality.
SPRITE_UPSAMPLE = 4

# A list of 6 digit hex colour codes separated by ;. Allow a trailing ;
# For example, Gradient pink would be #C5247F;
COLOUR_LIST_REGEX = re.compile(
    r"^\s*(#[0-9a-fA-F]{6})\s*(?:;\s*(#[0-9a-fA-F]{6})\s*)*;?\s*$"
)
# regex to separate R, G and B from a 6 digit hex code with preceding #
COLOUR_REGEX = re.compile(r"^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$")


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


def colour_str_to_colour(colour_str: str) -> tuple[int, int, int]:
    """Convert a colour string into RGB colour values.

    :param colour_str: Should be a hex colour such as #33aa33 or a list of hex
        colours separated by semicolons (with optional spaces).
    :return: The colour as a tuple of 3 integers from 0 to 255 in value
    :raises ValueError: If the hex string is not valid. This should never happen if the
        user enters a bad colour string as the colour property setter checks the
        whole string regex.
    """
    if ";" in colour_str:
        colours = colour_str.split(";")
        if len(colours) > 1 and colours[-1].strip() == "":
            colours.pop(-1)
        single_colour_str = colours[RNG.integers(0, len(colours))]
    else:
        single_colour_str = colour_str
    single_colour_str = single_colour_str.lower().strip()
    colour_match = COLOUR_REGEX.match(single_colour_str)
    if colour_match is None:
        raise ValueError(
            f"{colour_str} is not a valid colour. Please use HTML hex notation."
        )

    r = int("0x" + colour_match.group(1), 16)
    g = int("0x" + colour_match.group(2), 16)
    b = int("0x" + colour_match.group(3), 16)
    return r, g, b


class SimulatedProjector(BaseProjector, GradientThing):
    """A simulated projector for testing."""

    def __init__(
        self,
        thing_server_interface: lt.ThingServerInterface,
        color: str = "#b937b9",
        shape: tuple[int, int, int] = (616, 820, 3),
        canvas_shape: tuple[int, int, int] = (1500, 2000, 3),
        frame_interval: float = 0.1,
    ) -> None:
        """Initialise the simulated projector with settings for how images are generated.

        :param shape: The shape (size) of the generated image.
        :param canvas_shape: The shape (size) of the canvas generated on initialisation
            that images are cropped from. If this is too large the it uses resources,
            but its size limits the range of motion of the simulation.
        :param frame_interval: Nominally the time between frames on the MJPEG stream,
            however the rate may be slower due to calculation time for focus.
        """
        super().__init__(thing_server_interface)
        self._color = color
        self.shape = shape
        self.glyph_size = 105 // DOWNSAMPLE
        self.canvas_shape = _downsample_shape(canvas_shape, DOWNSAMPLE)
        self.low_mag_canvas_shape = _downsample_shape(canvas_shape, LOW_MAG_DOWNSAMPLE)
        self.frame_interval = frame_interval
        self._capture_thread: Optional[Thread] = None
        self._capture_enabled = False
        self.generate_sprites()
        self.output_canvas = None
        self.output_canvas_low_mag = None
        self.output_blank_canvas = None
        self._dark_canvas = np.zeros(self.canvas_shape, dtype=np.int16)
        self._brightness = 1.0
        # Whether the LED is on
        self.led_on = True

    _blob_density: int = 400

    async def life_span(self):
        print("before yield")
        yield
        print("after yield")
        await anyio.sleep(1)

    @lt.property
    def blob_density(self) -> int:
        """The number of blobs per million pixels."""
        return self._blob_density

    @blob_density.setter
    def _set_blob_density(self, value: int) -> None:
        self._blob_density = value
        if self._capture_enabled:
            self.generate_canvas()
            self.generate_output_canvas()

    @lt.property
    def blob_brightness(self) -> float:
        """The brightness of blobs."""
        return self._brightness

    @blob_brightness.setter
    def _set_blob_brightness(self, value: float) -> None:
        self._brightness = value
        self.generate_output_canvas()

    # _colour: str = "#b937b9"

    @lt.property
    def colour(self) -> str:
        """The colour of the blobs as a HTML hex string.

        The string can either be a single colour (e.g. "#c5247f") or a list of
        colours separated by semicolons (e.g. "#c5247f; #b937b9"). Additional
        spaces are allowed between colours.
        """
        return self._color

    @colour.setter
    def _set_colour(self, colour_value: str) -> None:
        if COLOUR_LIST_REGEX.match(colour_value) is None:
            self.logger.warning(f"{colour_value} is not a valid colour string.")
            return

        self._color = colour_value
        if self._capture_enabled:
            self.generate_canvas()

    def generate_sprites(self) -> None:
        """Generate sprites to populate the image."""
        sprite_sizes = [10, 21, 36, 40, 50]
        sprite_sizes = [s * SPRITE_UPSAMPLE for s in sprite_sizes]
        self.sprites = []

        block_size = self.glyph_size * DOWNSAMPLE * SPRITE_UPSAMPLE
        channel_block = np.zeros((block_size, block_size))
        x = np.arange(channel_block.shape[0])
        y = np.arange(channel_block.shape[1])
        # 2D grid of radii
        r_coord = np.sqrt(
            (x[:, None] - np.mean(x)) ** 2 + (y[None, :] - np.mean(y)) ** 2
        )

        for sprite_size in sprite_sizes:
            # Mask of where this sprite is
            sprite_mask = r_coord < sprite_size
            # Calculate a sharp edged circle with value varying from 0 in centre to 255
            # at the edge
            sprite_px = r_coord[sprite_mask]
            sprite_px -= np.min(sprite_px)
            sprite_px /= np.max(sprite_px)
            sprite = channel_block.copy()
            sprite[sprite_mask] = 255 * sprite_px

            # Convert to uint8
            sprite = sprite.astype(np.uint8)
            # Convert to PIL (and back) to resize then append to list of sprites
            sprite_pil = Image.fromarray(sprite)
            sprite_pil = sprite_pil.resize(
                (self.glyph_size, self.glyph_size), Image.Resampling.BILINEAR
            )
            # Convert back and ensure all edges are zero as these are repeated at sample
            # edge
            sprite = np.array(sprite_pil)
            sprite[0, :] = 0
            sprite[-1, :] = 0
            sprite[:, 0] = 0
            sprite[:, -1] = 0
            self.sprites.append(sprite)

    def generate_output_canvas(self):
        self.output_canvas = self.canvas*self._brightness
        self.output_canvas = self.output_canvas.astype(np.int16)
        self.output_canvas_low_mag = self.canvas_low_mag*self._brightness
        self.output_canvas_low_mag = self.output_canvas_low_mag.astype(np.int16)
        
    def generate_blobs(self, n_blobs: int = 1000) -> None:
        """Generate coordinates of blobs and their sizes, centered around (0,0).

        Note that blob density is determined by sample size and n_blobs, and for larger
        samples n_blobs will need increasing to keep a high level of sample coverage per
        field of view.

        :param n_blobs: The number of blobs to generate.
        """
        self.blobs = np.zeros((n_blobs, 3))
        w = self.glyph_size

        self.blobs[:, 0] = RNG.uniform(w // 2, self.canvas_shape[1] - w // 2, n_blobs)
        self.blobs[:, 1] = RNG.uniform(w // 2, self.canvas_shape[0] - w // 2, n_blobs)
        self.blobs[:, 2] = RNG.choice(len(self.sprites), n_blobs)

    def get_output_canvas(self):
        if self.led_on:
            return self.output_canvas
        else:
            return self._dark_canvas
        
    def get_output_canvas_low_mag(self):
        if self.led_on:
            return self.output_canvas_low_mag
        else:
            return self._dark_canvas

    def generate_canvas(self) -> None:
        """Generate a canvas with generated blobs centered at the middle.

        Canvas is int16 so that random noise can be added to simulation image before
        changing to unit8 to stop wrapping.
        """
        n_pixels = self.canvas_shape[0] * self.canvas_shape[1] * DOWNSAMPLE**2
        self.generate_blobs(int(self.blob_density * 1e-6 * n_pixels))
        self.blank_canvas = np.ones(self.canvas_shape, dtype=np.int16)
        self.blank_canvas[:, :, 0] *= BG_COLOR[0]
        self.blank_canvas[:, :, 1] *= BG_COLOR[1]
        self.blank_canvas[:, :, 2] *= BG_COLOR[2]
        self.blank_canvas_low_mag = np.ones(self.low_mag_canvas_shape, dtype=np.int16)
        self.blank_canvas_low_mag[:, :, 0] *= BG_COLOR[0]
        self.blank_canvas_low_mag[:, :, 1] *= BG_COLOR[1]
        self.blank_canvas_low_mag[:, :, 2] *= BG_COLOR[2]
        new_canvas = self.blank_canvas.copy()

        for blob_x, blob_y, sprite_index in self.blobs:
            self.draw_sprite_on_canvas(
                new_canvas, self.sprites[int(sprite_index)], int(blob_y), int(blob_x)
            )
        self.canvas = np.clip(new_canvas, 0, 255)
        # Create a further downsized canvas for low mag. This has a minimal memory
        # footprint but speeds up indexing the canvas when simulation uses low magnification
        # objectives
        self.canvas_low_mag = fast_resize_and_blur(
            self.canvas, sigma=0, shape=self.low_mag_canvas_shape
        )
        # Check edge pixels are blank as these are repeated for finite samples.
        self.canvas_low_mag[0, :, :] = self.blank_canvas_low_mag[0, :, :]
        self.canvas_low_mag[-1, :, :] = self.blank_canvas_low_mag[-1, :, :]
        self.canvas_low_mag[:, 0, :] = self.blank_canvas_low_mag[:, 0, :]
        self.canvas_low_mag[:, -1, :] = self.blank_canvas_low_mag[:, -1, :]

    def draw_sprite_on_canvas(
        self, canvas: np.ndarray, sprite: np.ndarray, centre_y: int, centre_x: int
    ) -> None:
        """Place one sprite on canvas at given centre coordinates.

        Note that self.canvas is modified in place.

        :param sprite: The sprite array to place on the canvas.
        :param centre_y: The y coordinate to place the centre of the sprite.
        :param centre_x: The x coordinate to place the centre of the sprite.
        """
        canvas_h, canvas_w, _ = canvas.shape
        sprite_h, sprite_w = sprite.shape

        sprite_f = sprite.astype(float) / 255
        r, g, b = colour_str_to_colour(self.colour)
        sprite_r = r * sprite_f
        sprite_g = g * sprite_f
        sprite_b = b * sprite_f
        sprite_rgb = np.stack([sprite_r, sprite_g, sprite_b], axis=2)

        # Canvas region containing the sprite
        top = max(centre_y - sprite_h // 2, 0)
        left = max(centre_x - sprite_w // 2, 0)
        bottom = min(centre_y + (sprite_h - sprite_h // 2), canvas_h)
        right = min(centre_x + (sprite_w - sprite_w // 2), canvas_w)

        canvas[top:bottom, left:right] += sprite_rgb.astype("int16")

    @lt.property
    def led(self) -> bool:
        """Whether the simulated LED is on."""
        return self.led_on
    
    @led.setter
    def _set_led(self, led_on: bool) -> None:
        self.led_on = led_on
    
    @lt.action
    def set_led(self, led_on: bool = True) -> None:
        """Set the simulated LED to on or off."""
        self.led_on = led_on

    def __enter__(self):
        """Start the capture thread when the Thing context manager is opened."""
        super().__enter__()
        self.generate_canvas()
        self.generate_output_canvas()

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
