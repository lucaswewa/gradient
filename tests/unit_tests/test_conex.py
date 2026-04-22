"""Unit tests for the CONEX stage serial wrapper."""

import pytest

from gradient_server.stage.conex import Conex


@pytest.mark.parametrize(
    ("acceleration", "expected_command"),
    [
        (1.5, "AC1.500"),
        (1500, "AC1500.000"),
    ],
)
def test_set_acceleration_accepts_values_in_range(
    monkeypatch, acceleration, expected_command
):
    """Check that valid acceleration values are sent to the controller."""
    commands = []

    def fake_send_command(_ser, cmd):
        commands.append(cmd)

    monkeypatch.setattr("gradient_server.stage.conex.send_command", fake_send_command)

    stage = Conex("COM_TEST")
    stage.set_acceleration(acceleration)

    assert commands == [expected_command]


@pytest.mark.parametrize("acceleration", [1.499, 1500.001])
def test_set_acceleration_rejects_values_out_of_range(monkeypatch, acceleration):
    """Check that out-of-range acceleration values raise an error."""
    commands = []

    def fake_send_command(_ser, cmd):
        commands.append(cmd)

    monkeypatch.setattr("gradient_server.stage.conex.send_command", fake_send_command)

    stage = Conex("COM_TEST")

    with pytest.raises(ValueError, match="Acceleration must be between 1.5 and 1500."):
        stage.set_acceleration(acceleration)

    assert commands == []
