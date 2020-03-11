import pytest

from miniwake.rotor_integration import EffectiveRadiusIntegrator


def one(lateral_distance, vertical_distance):
    return 1.0


def test_rotor_integration():
    integrator = EffectiveRadiusIntegrator(12)
    assert integrator.calculate(5.0, 10.0, 90.0, one) == 1.0
