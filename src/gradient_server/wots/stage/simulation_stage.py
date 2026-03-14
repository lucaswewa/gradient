"""Functionality for mimicking a stage during simulation and testing."""

from __future__ import annotations

import queue
import threading
import time
from collections.abc import Sequence
from types import TracebackType
from typing import Any, Mapping, Optional
from anyio.from_thread import BlockingPortal
import asyncio
import copy

import labthings_fastapi as lt

import logging

LOGGER = logging.getLogger(__name__)

from . import BaseStage, BaseHardwareStage, JogCommand


class Cmd:
    def __init__(self, cmd: str, val: Mapping[str, float], evt: threading.Event):
        self.cmd: str = cmd
        self.val: Mapping[str, float] = val
        self.res: int = 0
        self.evt: threading.Event = evt

    def __repr__(self) -> str:
        """Represent the command as a string."""
        class_name = type(self).__name__
        return f"<{class_name}> cmd: {self.cmd}, val: {self.val}, res: {self.res}"
    
class SimuatedHardwareStage(BaseHardwareStage):
    def __init__(self):
        super().__init__()
        self._queue = asyncio.Queue(maxsize=10)
        self._tick_interval = 0.005
        self._speed = 1
        self._movement_enabled = False
        self._movement_ongoing = False

    async def task_coro(self):
        cmd = None
        target: Mapping[str, int] = {"x": 0, "y": 0, "z": 0}
        step_sizes: Mapping[str, float] = {"x": 0, "y": 0, "z": 0}
        item: Cmd = None
        move = 100
        while True:
            await asyncio.sleep(self._tick_interval)
            try:
                item = self._queue.get_nowait()
                LOGGER.info(f"[SimulatedStage::task_coro] received cmd={item.cmd}")
                target = copy.deepcopy(self._position)
                if item.cmd == "get_pos":
                    item.res = self._position["x"]
                elif item.cmd == "jp":
                    cmd = "jp"
                    target = self._position["x"] + 100
                    item.res = 1
                elif item.cmd == "jn":
                    cmd = "jn"
                    target = self._position["x"] - 100
                    item.res = 0
                elif item.cmd == "move_relative":
                    cmd = "move_relative"
                    displacement = {"x": 0, "y": 0, "z": 0}
                    for key in ["x", "y", "z"]:
                        if key in item.val:
                            displacement[key] = item.val[key]
                            target[key] += item.val[key]
                    max_displacement = max(abs(displacement["x"]), abs(displacement["y"]), abs(displacement["z"]))
                    move =int(max_displacement/self._speed) if max_displacement > 0 else 0
                    step_sizes = {key: self._speed * displacement[key] / max_displacement for key in ["x", "y", "z"]} if max_displacement > 0 else {"x": 0, "y": 0, "z": 0}
                    item.res = 0
                elif item.cmd == "move_absolute":
                    cmd = "move_absolute"
                    displacement = {"x": 0, "y": 0, "z": 0}
                    for key in ["x", "y", "z"]:
                        if key in item.val:
                            displacement[key] = item.val[key] - self._position[key]
                            target[key] = item.val[key]
                    max_displacement = max(abs(displacement["x"]), abs(displacement["y"]), abs(displacement["z"]))
                    move =int(max_displacement/self._speed) if max_displacement > 0 else 0
                    step_sizes = {key: self._speed * displacement[key] / max_displacement for key in ["x", "y", "z"]} if max_displacement > 0 else {"x": 0, "y": 0, "z": 0}
                    item.res = 0
                elif item.cmd == "stop":
                    cmd = "stop"
                    item.res = 0
                elif item.cmd is None:  # TODO: shutdown the motor controller if shutdown is finished
                    item.evt.set()
                    queue.task_done()
                    break
            except asyncio.QueueEmpty:
                pass
            except Exception as e:
                print(f">>>>>>>> fixme: {e}")

            # TODO:
            #   1. check current status: speed, position, etc
            #   2. run speed controller, torque controller, position controller with item as input
    
            # simple state machine controller
            if cmd == "jp":
                self._position["x"] += self._speed 
                if target - self._position["x"] < 0:
                    cmd = None
                    self._position["x"] = target
            elif cmd == "jn":
                self._position["x"] -= self._speed 
                if target - self._position["x"] > 0:
                    cmd = None
                    self._position["x"] = target
            elif cmd == "move_relative":
                if move == 0:
                    item.evt.set()
                    self._position = target
                    cmd = None
                elif move > 0:
                    self._position["z"] += step_sizes["z"]
                    self._position["y"] += step_sizes["y"]
                    self._position["x"] += step_sizes["x"]
                    move -= 1
            elif cmd == "move_absolute":
                if move == 0:
                    item.evt.set()
                    self._position = target
                    cmd = None
                elif move > 0:
                    self._position["z"] += step_sizes["z"]
                    self._position["y"] += step_sizes["y"]
                    self._position["x"] += step_sizes["x"]
                    move -= 1
            elif cmd == "stop":
                # TODO: stop the movement immediately, which means setting the position to the current position and clearing the queue
                cmd = None


    def open(self):
        pass

    def close(self):
        pass

    def loop(self):
        pass

    def move_relative(
        self, portal: BlockingPortal, block_cancellation: bool = False, **kwargs: int
    ) -> None:
        """Make a relative move in the coordinate system used by the physical hardware.

        Make sure to use and update ``self._hardware_position`` not ``self.position``.
        """
        c = Cmd(cmd="move_relative", val=kwargs, evt=threading.Event())
        portal.call(self._queue.put, c)
        c.evt.wait()
    
    def move_absolute(
        self,
        portal: BlockingPortal,
        block_cancellation: bool = False,
        **kwargs: int,
    ) -> None:
        """Make a absolute move in the coordinate system used by the physical hardware.

        Make sure to use and update ``self._hardware_position`` not ``self.position``.
        """
        # self._position = {"x": 0, "y": 0, "z": 0}
        c = Cmd(cmd="move_absolute", val=kwargs, evt=threading.Event())
        portal.call(self._queue.put, c)
        c.evt.wait()

    def stop(self) -> None:
        raise NotImplementedError(
            "StageThings must define their own _hardware_stop method"
        )

    def poll_moving(self) -> bool:
        """Determine if the stage is still moving."""
        raise NotImplementedError(
            "StageThings must define their own _poll_moving method"
        )
    
    def jog(self, portal: BlockingPortal, command: JogCommand) -> None:
        """Send a jog command to the background jog thread.

        This function will start the background thread if it is not running.
        This function acquires ``_jog_lock`` and uses the ``_jog_send`` event to signal
        the thread to read the next command. As commands interrupt each other, this
        function should never block for a long time.

        :param command: the jog command to send.
        """
        self.move_relative(portal, x=100)

    def set_zero_position(self) -> None:
        """Make the current position zero in all axes.

        This action does not move the stage, but resets the position to zero.
        It is intended for use after manually or automatically recentring the
        stage.
        """
        self._position = {"x": 0, "y": 0, "z": 0}
            
    def get_speed(self) -> float:
        """Get the current speed of the stage in units per second."""
        return self._speed
    
    def set_speed(self, speed: float) -> None:
        """Set the speed of the stage in units per second."""
        self._speed = speed

class SimulatedStage(BaseStage):
    """A simulated stage for testing purposes.

    This stage should work similarly to a Sangaboard stage, but without any
    hardware attached.
    """

    def __init__(
        self,
        thing_server_interface: lt.ThingServerInterface,
        step_time: float = 0.001,
        **kwargs: Any,
    ) -> None:
        """Initialize the simulated stage, setting the step_time to adjust the speed.

        :param step_time: The time in seconds per "motor" step. The default of 0.001
            works well for the live simulation. For unit testing it is very slow
            so the speed can be increased. Increasing it too far is problematic if
            also doing computationally heavy tasks like simulated image blurring.
        """
        super().__init__(thing_server_interface, **kwargs)
        self._hardware_stage = SimuatedHardwareStage()

    @property
    def instantaneous_position(self) -> Mapping[str, int]:
        return self._hardware_stage.position
    
    @lt.property
    def speed(self) -> float:
        """The speed of the stage in units per second."""
        return self._hardware_stage.get_speed()
    
    @speed.setter
    def _set_speed(self, speed: float) -> None:
        self._hardware_stage.set_speed(speed)

    def __enter__(self):
        """Register the stage position and start move thread running.
        
        This method runs in an anyio worker thread.
        """
        LOGGER.debug("[SimulatedStage::__enter__] starting the move thread")
        # self._move_thread.start()
        self.hw_task = self._thing_server_interface.start_async_task_soon(self._hardware_stage.task_coro)
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException],
        _exc_value: Optional[BaseException],
        _traceback: Optional[TracebackType],
    ) -> None:
        """Stop the hardware controller task."""
        # TODO: stop the hardware task
        pass

    axis_inverted: dict[str, bool] = lt.setting(
        default={"x": True, "y": False, "z": False}, readonly=True
    )
    """Used to convert coordinates between the program frame and the hardware frame."""
