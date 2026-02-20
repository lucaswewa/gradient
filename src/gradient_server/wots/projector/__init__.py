"""A package for cameras."""
from .base_projector import BaseProjector
from .simulation_projector import SimulatedProjector

__all__ = [
    "BaseProjector",
    "SimulatedProjector"
]
