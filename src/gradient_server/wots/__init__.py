"""A package containing all thhe WoT(s)."""

import logging

import labthings_fastapi as lt
import anyio
import time
from anyio.from_thread import BlockingPortal
import random

LOGGER = logging.getLogger(__name__)

async def async_method(t):
    print("async method start")
    await anyio.sleep(t)
    print("async method done!")

def sync_method(t, r, portal: BlockingPortal):
    print(f"Sync method: start {r}")
    time.sleep(t)
    portal.start_task_soon(async_method, t)
    print(f"sync method: done! {r}")

class MyThing(lt.Thing):
    """A test WoT thing."""

    @lt.property
    def ai(self) -> str:
        """Get AI."""
        LOGGER.info("get ai")
        return "ai"

    @lt.action
    def ac(self, t: float, portal: lt.deps.BlockingPortal) -> None:
        sync_method(t, random.random(), portal)
