"""A package for cameras."""

from typing import Protocol, TypeAlias

import numpy as np
import numpy.typing as npt

Uint8Array2D: TypeAlias = npt.NDArray[np.uint8]
Uint16Array2D: TypeAlias = npt.NDArray[np.uint16]


class Camera(Protocol):
    """Camera Protocol."""

    async def open(self) -> None:
        """Open the camera connection."""
        ...

    async def close(self) -> None:
        """Close the camera connection."""
        ...

    async def set_exposure(self, exposure_in_us: float) -> None:
        """Set the exposure time in us."""
        ...

    async def get_exposure(self) -> float:
        """Return the exposure time in us."""
        ...

    async def set_gain(self, gain: float) -> None:
        """Set the gain."""
        ...

    async def get_gain(self) -> float:
        """Return the gain."""
        ...

    async def start_stream(self) -> None:
        """Start the stream."""
        ...

    async def stop_stream(self) -> None:
        """Stop the streaming."""
        ...

    async def capture(self) -> Uint8Array2D | Uint16Array2D:
        """Capture a image from the camera.

        If the camera is in streaming mode, then the followiwng flow is executed:
        - Stop the streaming
        - Capture the image
        - Start the streaming again

        :Returns a 2D array image.
        """
        ...
