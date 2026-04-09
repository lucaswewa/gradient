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

import numpy as np
import vmbpy
import time

from typing import Callable
import threading
from abc import ABC, abstractmethod

class GradientThing(ABC, lt.Thing):
    def __init__(self, thing_server_interface: lt.ThingServerInterface):
        super().__init__(thing_server_interface=thing_server_interface)

    async def __aenter__(self):
        self.gen = self.life_span()
        await anext(self.gen)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await anext(self.gen)
        except StopAsyncIteration:
            pass

    @abstractmethod
    async def life_span(self):
        pass

class Camera(GradientThing):

    def __init__(self, thing_server_interface: lt.ThingServerInterface):
        super().__init__(thing_server_interface)
        self.thing_server_interface = thing_server_interface
        self.gen = None

    # async def __aenter__(self):
    #     self.gen = self.thing_life_span()
    #     await anext(self.gen)
    #     return self
    
    # async def __aexit__(self, exc_type, exc_val, exc_tb):
    #     try:
    #         await anext(self.gen)
    #     except StopAsyncIteration:
    #         pass

    async def queue_service(self) -> None:
        async for item in self.receive_stream:
            pass

    async def life_span(self):
        try:
            async with anyio.create_task_group() as self.tg:
                self.send_stream, self.receive_stream = create_memory_object_stream()
                async with self.send_stream, self.receive_stream:
                    self.tg.start_soon(self.queue_service)
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
    def start(self):
        print("Camera streaming started")

    @lt.action
    def stop(self):
        print("Camera streaming stopped")

    @lt.action
    def capture(self):
        return

    @lt.property
    def exposure_time(self) -> float:
        return 1
    
    @exposure_time.setter
    def _set_exposure_time(self, exposure_time: float):
        print(self.exposure_time)


server = lt.ThingServer({"camera": Camera})

app = server.app
