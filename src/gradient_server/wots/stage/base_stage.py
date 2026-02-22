
from __future__ import annotations

import queue
import threading
from collections.abc import Mapping, Sequence
from typing import Any, Literal, Optional, overload
from anyio.from_thread import BlockingPortal

import labthings_fastapi as lt

import logging

LOGGER = logging.getLogger(__name__)

class RedefinedBaseMovementError(RuntimeError):
    """The subclass of BaseStage has overridden ``move_relative`` or ``move_absolute``.

    Overriding ``move_relative`` or ``move_absolute`` can be problematic as these use the
    external position not the hardware position. It is recommended to override
    ``_hardware_move_relative`` and ``_hardware_move_absolute`` instead.

    The BaseStage will raise this on ``__init__``, it is the last thing ``__init__``
    does. As such, this exception can be captured by ``try`` if a stage needs to
    override these for a specific reason.
    """


class JogCommand:
    """A base class for jog operations."""

    def __init__(self, displacement: Optional[Sequence[int]]) -> None:
        """Initialise a JogCommand.

        :param displacement: The distances as a sequence of moves for each axis.
            None for stop motion.
        """
        super().__init__()
        self.displacement = None if displacement is None else tuple(displacement)

    def __repr__(self) -> str:
        """Represent the command as a string."""
        class_name = type(self).__name__
        if self.displacement is None:
            return f"<{class_name}>STOP"
        return f"<{class_name}>{self.displacement}"

class BaseHardwareStage:
    def __init__(self):
        self._position = {"x": 0, "y": 0, "z": 0}

    @property
    def position(self) -> Mapping[str, int]:
        return self._position

    def move_relative(
        self, portal: BlockingPortal, block_cancellation: bool = False, **kwargs: int
    ) -> None:
        """Make a relative move in the coordinate system used by the physical hardware.

        Make sure to use and update ``self._hardware_position`` not ``self.position``.
        """
        raise NotImplementedError(
            "StageThings must define their own _hardware_move_relative method"
        )

    def move_absolute(
        self,
        portal: BlockingPortal,
        block_cancellation: bool = False,
        **kwargs: int,
    ) -> None:
        """Make a absolute move in the coordinate system used by the physical hardware.

        Make sure to use and update ``self._hardware_position`` not ``self.position``.
        """
        raise NotImplementedError(
            "StageThings must define their own _hardware_move_absolute method"
        )

    def stop(self, portal: BlockingPortal) -> None:
        raise NotImplementedError(
            "StageThings must define their own _hardware_stop method"
        )

    def poll_moving(self, portal: BlockingPortal) -> bool:
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
        raise NotImplementedError(
            "StageThings must define their own jog method"
        )
   
    def set_zero_position(self, portal: BlockingPortal) -> None:
        """Make the current position zero in all axes.

        This action does not move the stage, but resets the position to zero.
        It is intended for use after manually or automatically recentring the
        stage.
        """
        raise NotImplementedError(
            "StageThings must define their own set_zero_position method"
        )
        
class BaseStage(lt.Thing):
    """A base stage class for OpenFlexure translation stages.

    This can't be used directly but should reduce boilerplate code when
    implementing new stages.

    Note that the coordinate system used for the microscope may need to have different
    axis direction as those used by the underlying stage controller.

    A minimal working stage must implement ``_hardware_move_relative``
    and ``_hardware_move_absolute`` actions, which update the ``_hardware_position``
    attribute on completion, and also should implement ``set_zero_position``.
    """

    _axis_names = ("x", "y", "z")

    def __init__(self, thing_server_interface: lt.ThingServerInterface) -> None:
        """Initialise the stage.

        :raises RedefinedBaseMovementError: if ``move_relative`` and/or
            ``move_absolute`` are overridden. It is recommended to override
            ``_hardware_move_relative`` and/or ``_hardware_move_absolute`` instead so
            that all code in the child class uses the hardware reference frame.
        """
        super().__init__(thing_server_interface)
        self._hardware_stage: BaseHardwareStage = BaseHardwareStage()
        # self._hardware_position: Mapping[str, int] = dict.fromkeys(self._axis_names, 0)

        # This must be the last thing the function does in case it is caught in a try.
        if (
            self.__class__.move_relative.func is not BaseStage.move_relative.func
            or self.__class__.move_absolute.func is not BaseStage.move_absolute.func
        ):
            raise RedefinedBaseMovementError(
                "move_relative and/or move_absolute has been overridden. This may "
                "cause issues as the base methods implement converting from program "
                "coordinates to hardware coordinates. Consider overriding "
                "_hardware_move_relative and/or _hardware_move_absolute instead."
            )

    @lt.property
    def axis_names(self) -> Sequence[str]:
        """The names of the stage's axes, in order."""
        return self._axis_names

    @lt.property
    def position(self) -> Mapping[str, int]:
        """Current position of the stage."""
        return self._apply_axis_direction(self._hardware_stage.position)

    moving: bool = lt.property(default=False, readonly=True)
    """Whether the stage is in motion."""

    axis_inverted: dict[str, bool] = lt.setting(
        default={"x": False, "y": False, "z": False}, readonly=True
    )
    """Used to convert coordinates between the program frame and the hardware frame."""

    @overload
    def _apply_axis_direction(self, position: list[int] | tuple[int]) -> list[int]: ...

    @overload
    def _apply_axis_direction(
        self, position: Mapping[str, int]
    ) -> Mapping[str, int]: ...

    def _apply_axis_direction(
        self, position: list[int] | tuple[int] | Mapping[str, int]
    ) -> list[int] | Mapping[str, int]:
        if isinstance(position, (list, tuple)):
            return [
                -int(pos) if inverted else int(pos)
                for pos, inverted in zip(
                    position, self.axis_inverted.values(), strict=True
                )
            ]
        if isinstance(position, Mapping):
            try:
                return {
                    ax: -int(position[ax])
                    if self.axis_inverted[ax]
                    else int(position[ax])
                    for ax in position
                }
            except KeyError as e:
                raise KeyError(
                    f"One or more axis in {position.keys()} is not defined."
                ) from e
        raise TypeError(
            "Position must be a sequence of positions or a mapping from axis to position."
        )

    @lt.property
    def thing_state(self) -> Mapping[str, Any]:
        """Summary metadata describing the current state of the stage."""
        return {"position": self._hardware_stage.position}

    @lt.action
    def invert_axis_direction(self, axis: Literal["x", "y", "z"]) -> None:
        """Invert the direction setting of the given axis.

        :param axis: The axis name (x, y or z) to invert.
        """
        # Not mutating in place so that setting is saved on change.
        direction = self.axis_inverted
        try:
            direction[axis] = not direction[axis]
        except KeyError as e:
            raise KeyError(f"The axis {axis} is not defined.") from e
        self.axis_inverted = direction

    @lt.action
    def move_relative(self, portal: lt.deps.BlockingPortal, block_cancellation: bool = False, **kwargs: int) -> None:
        """Make a relative move. Keyword arguments should be axis names."""
        self._hardware_stage.move_relative(
            portal,
            block_cancellation=block_cancellation,
            **self._apply_axis_direction(kwargs),
        )

    @lt.action
    def move_absolute(self, portal: lt.deps.BlockingPortal, block_cancellation: bool = False, **kwargs: int) -> None:
        """Make an absolute move. Keyword arguments should be axis names."""
        LOGGER.info("[BaseStage::move_absolute]")
        self._hardware_stage.move_absolute(
            portal,
            block_cancellation=block_cancellation,
            **self._apply_axis_direction(kwargs),
        )

    @lt.action
    def jog(self, portal: lt.deps.BlockingPortal, stop: bool = False, **kwargs: int) -> None:
        """Make a relative move that may be interrupted by a future ``jog``.

        This action makes a relative move. If another ``jog`` action is called while
        a ``jog`` is already in progress, the first will be stopped and the second
        will start immediately. This allows for responsive manual control of the
        stage, for example with a joystick.

        :param stop: if this is set to ``True`` the jog will be terminated.
        :param kwargs: Keyword arguments should be axis names.
        """
        if stop:
            LOGGER.info(f"[BaseStage::jog] stop the jog action")
            self._hardware_stage.jog(portal, JogCommand(None))
            return

        hardware_moves = self._apply_axis_direction(kwargs)
        move = [hardware_moves.get(axis, 0) for axis in self.axis_names]
        if all(ax == 0 for ax in move):
            self.logger.warning(
                "Requested jog movement is is empty. Sending STOP instead."
            )
            LOGGER.info(f"[BaseStage::jog] stop the jog action")
            self._hardware_stage.jog(portal, JogCommand(None))
        else:
            move_cmd = JogCommand(move)
            LOGGER.info(f"[BaseStage::jog] start the jog action, move={move_cmd}")
            self._hardware_stage.jog(portal, move_cmd)

    @lt.action
    def set_zero_position(self) -> None:
        """Make the current position zero in all axes.

        This action does not move the stage, but resets the position to zero.
        It is intended for use after manually or automatically recentring the
        stage.
        """
        self._hardware_stage.set_zero_position()

    @lt.action
    def get_xyz_position(self) -> tuple[int, int, int]:
        """Return a tuple containing (x, y, z) position.

        :raises KeyError: if this stage does not have axes named "x", "y", and "z".

        This method provides the interface expected by the camera_stage_mapping.
        """
        position_dict = self._hardware_stage.position
        return (position_dict["x"], position_dict["y"], position_dict["z"])

    @lt.action
    def move_to_xyz_position(self, portal: lt.deps.BlockingPortal, xyz_pos: tuple[int, int, int]) -> None:
        """Move to the location specified by an (x, y, z) tuple.

        :param xyz_pos: The (x, y, z) position to move to.

        :raises KeyError: if this stage does not have axes named "x", "y", and "z".

        This method provides the interface expected by the camera_stage_mapping.
        """
        self.move_absolute(portal, x=xyz_pos[0], y=xyz_pos[1], z=xyz_pos[2])
