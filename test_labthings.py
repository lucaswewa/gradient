from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
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
from typing_extensions import Self
from copy import copy
from contextlib import asynccontextmanager
import threading
import anyio
import logging

import labthings_fastapi as lt
from labthings_fastapi import Thing, ThingServerInterface

import fastapi
import anyio
import time
from contextlib import asynccontextmanager
from anyio import create_memory_object_stream
from anyio import Event
import numpy as np
# from _025_task_streams import service

import labthings_fastapi as lt
# import pyee.asyncio as eea
from PIL import Image
import io


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
            media_type=self.media_type,
            status_code=status_code
        )
        
    async def mjpeg_stream_generator(self):
        async for frame in self.frame_async_generator:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
            # yield b"--frame\r\nContent-Type: image/png\r\n\r\n"
            yield frame
            yield b"\r\n"

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

def _frame2bytes(frame: Image.Image) -> bytes:
    """Convert frame to bytes."""
    with io.BytesIO() as buf:
        # Save in low quality for speed.
        frame.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

class Camera(lt.Thing):

    mjpeg_stream = MJPEGStreamAsyncDescriptor()

    def __init__(self, thing_server_interface: lt.ThingServerInterface):
        super().__init__(thing_server_interface)
        self.thing_server_interface = thing_server_interface
        self.gen = None
        self.streaming = True

    async def __aenter__(self):
        self.gen = self.thing_life_span()
        await anext(self.gen)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await anext(self.gen)
        except StopAsyncIteration:
            pass

    async def stream_service(self):
        t0 = time.time()
        counter = 0

        print("Stream service started")
        while self.streaming:
            img = np.random.randint(0, 255, (768, 1024, 3), dtype=np.uint8)
            frame = Image.fromarray(img)
            b = _frame2bytes(frame)
            await self.mjpeg_stream.add_frame(b)

            await anyio.sleep(0.03)

            td = time.time() - t0
            if td >= 5:
                print(f"Streamed {counter} frames in {td:.2f} seconds ({counter/td:.2f} FPS)")
                t0 = time.time()
                counter = 0
            counter += 1
        print("stream_service stopped")

    async def service(self) -> None:
        async for item in self.receive_stream:
            print("consuming", item)

    async def thing_life_span(self):
        """A simple service that prints the light's status every second."""
        try:
            async with anyio.create_task_group() as self.tg:
                self.tg.start_soon(self.stream_service)
                self.send_stream, self.receive_stream = create_memory_object_stream()
                async with self.send_stream, self.receive_stream:
                    self.tg.start_soon(self.service)
                    print("before yield:")
                    yield
                    print("after yield:")
                    await anyio.sleep(1)
        except anyio.get_cancelled_exc_class():
            print("thing_life_span cancelled")
            raise
        except Exception as e:
            print("thing_life_span exception", e)
            raise
    
    @lt.action
    def start_service(self) -> str:
        self.streaming = True
        self._thing_server_interface.start_async_task_soon(self.stream_service)
        return "service started"

    @lt.action
    def stop_service(self) -> str:
        self.streaming = False  
        return "service stopped"

server = lt.ThingServer({"camera": Camera})

app = server.app
