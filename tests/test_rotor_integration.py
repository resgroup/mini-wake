import pytest

from miniwake.rotor_integration import VelocityDeficitIntegrator


def one(lateral_offset, vertical_offset):
    return 1.0


def test_rotor_integration():
    integrator = VelocityDeficitIntegrator()
    assert integrator.calculate(90.0, one) == 1.0
