import pytest

from rotor_integration import EffectiveRadiusIntegrator

def one(radius, theta):
    return 1.0

def test_rotor_integration():
    integrator = EffectiveRadiusIntegrator(12)
    assert integrator.calculate(1.0, one) == 1.0
