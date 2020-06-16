import pytest

from miniwake.rotor_integration import VelocityDeficitIntegrator


def one(lateral_offset, vertical_offset):
    return 1.0, 2


def test_rotor_integration():
    integrator = VelocityDeficitIntegrator()
    integrated, impactive = integrator.calculate(90.0, one)
    assert integrated == 1.0
    assert impactive == 2
