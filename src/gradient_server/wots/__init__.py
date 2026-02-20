"""A package containing all thhe WoT(s)."""

import logging

import labthings_fastapi as lt

LOGGER = logging.getLogger(__name__)


class MyThing(lt.Thing):
    """A test WoT thing."""

    @lt.property
    def ai(self) -> str:
        """Get AI."""
        LOGGER.info("get ai")
        return "ai"
