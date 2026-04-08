"""Async version MJPEGStream."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
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
import anyio

import labthings_fastapi as lt
from labthings_fastapi.types.numpy import NDArray
from labthings_fastapi import Thing, ThingServerInterface
from fastapi import FastAPI
import cv2
from fastapi.responses import StreamingResponse, HTMLResponse
from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Literal,
    Optional,
    TYPE_CHECKING,
    Union,
    overload,
)

from gradient_server.wots.camera.simulation_camera import _frame2bytes
from gradient_server.wots.stage import BaseStage

from ..projector import SimulatedProjector
from ..stage import SimulatedStage
from .base_camera import BaseCamera
from ...camera.vmbx import VmbX

LOGGER = logging.getLogger(__name__)


@dataclass
class RingbufferEntry:
    frame: bytes
    timestamp: datetime
    index: int

class MJPEGStreamResponse(StreamingResponse):
    media_type = "multipart/x-mixed-replace; boundary=frame"
    def __init__(self, gen, status_code=200):
        self.frame_async_generator = gen
        StreamingResponse.__init__(
            self,
            self.mjpeg_stream_generator(),
            headers={"Cache-Control": "no-cache", "Pragma": "no-cache", "age": "0"},
            media_type=self.media_type,
            status_code=status_code
        )
        
    async def mjpeg_stream_generator(self):
        async for frame in self.frame_async_generator:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            await anyio.sleep(0)

class MJPEGStreamAsync:
    def __init__(self, thing_server_interface, ringbuffer_size=10):
        self._lock = anyio.Lock()
        self.condition = anyio.Condition()
        self._streaming = False
        self._ringbuffer: list[RingbufferEntry] = []
        self._thing_server_interface = thing_server_interface
        self.reset_buffer(ringbuffer_size=10)

    def reset_buffer(self, ringbuffer_size=10):
        self._streaming = True
        n = ringbuffer_size or len(self._ringbuffer)
        self._ringbuffer = [
            RingbufferEntry(
                frame=b"",
                index=-1,
                timestamp=datetime.min,
            )
            for i in range(n)
        ]
        self.last_frame_i = -1

    async def reset(self, ringbuffer_size=10):
        async with self._lock:
            self.reset_buffer(ringbuffer_size=ringbuffer_size)

    async def stop(self) -> None:
        async with self._lock:
            self._streaming = False
            await self.notify_stream_stopped()

    async def ringbuffer_entry(self, i: int) -> RingbufferEntry:
        entry = self._ringbuffer[i % len(self._ringbuffer)]
        return entry

    @asynccontextmanager
    async def buffer_for_reading(self, i) -> AsyncIterator[bytes]:
        entry = await self.ringbuffer_entry(i)
        yield entry.frame

    async def next_frame(self) -> int:
        async with self.condition:
            await self.condition.wait()
            if not self._streaming:
                raise StopAsyncIteration()
            return self.last_frame_i

    async def grab_frame(self) -> bytes:
        pass

    async def next_frame_size(self) -> int:
        i = await self.next_frame()
        async with self.buffer_for_reading(i) as frame:
            return len(frame)

    async def frame_async_generator(self) -> AsyncGenerator[bytes, None]:
        while self._streaming:
            try:
                i = await self.next_frame()
                async with self.buffer_for_reading(i) as frame:
                    yield frame
            except StopAsyncIteration:
                break
            except Exception as e:
                return

    async def mjpeg_stream_response(self) -> MJPEGStreamResponse:
        return MJPEGStreamResponse(self.frame_async_generator())
    
    async def add_frame(self, frame: bytes) -> None:
        if not (
            frame[0] == 0xFF
            and frame[1] == 0xD8
            and frame[-2] == 0xFF
            and frame[-1] == 0xD9
        ):
            # raise ValueError("Invalid JPEG")
            pass
        # loop = anyio.get_running_loop()
        async with self._lock:
            entry = self._ringbuffer[(self.last_frame_i + 1) % len(self._ringbuffer)]
            entry.timestamp = datetime.now()
            entry.frame = frame
            entry.index = self.last_frame_i + 1
            await self.notify_new_frame(entry.index)

    async def notify_new_frame(self, i: int) -> None:
        async with self.condition:
            self.last_frame_i = i
            self.condition.notify_all()

    async def notify_stream_stopped(self) -> None:
        async with self.condition:
            self.condition.notify_all()

class MJPEGStreamAsyncDescriptor:

    def __init__(self, **kwargs: Any) -> None:
        self._kwargs: Any = kwargs

    def __set_name__(self, _owner: Thing, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, obj: Literal[None], type: type | None = None) -> Self: ...  # noqa: D105

    @overload
    def __get__(self, obj: Thing, type: type | None = None) -> MJPEGStreamAsync: ...  # noqa: D105

    def __get__(
        self, obj: Optional[Thing], type: type[Thing] | None = None
    ) -> Union[MJPEGStreamAsync, Self]:
        if obj is None:
            return self
        try:
            return obj.__dict__[self.name]
        except KeyError:
            obj.__dict__[self.name] = MJPEGStreamAsync(
                **self._kwargs,
                thing_server_interface=obj._thing_server_interface,
            )
            return obj.__dict__[self.name]

    async def viewer_page(self, url: str) -> HTMLResponse:
        return HTMLResponse(f"<html><body><img src='{url}'></body></html>")

    def add_to_fastapi(self, app: FastAPI, thing: Thing) -> None:
        app.get(
            f"{thing.path}{self.name}",
            response_class=MJPEGStreamResponse,
        )(self.__get__(thing).mjpeg_stream_response)

        @app.get(
            f"{thing.path}{self.name}/viewer",
            response_class=HTMLResponse,
        )
        async def viewer_page() -> HTMLResponse:
            return await self.viewer_page(f"{thing.path}{self.name}")

