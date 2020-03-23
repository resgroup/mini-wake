import pytest

from miniwake.turbine import Turbine
from miniwake.turbine import FixedThrustCurve
from miniwake.wind_farm import WindFarm


class RotorCenterIntegrator:

    def calculate(self,
                  downwind_rotor_diameter,
                  wake_integral):

        return wake_integral(0, 0)


class FixedAmbientValue:

    def __init__(self, value):
        self.value = value

    def get_bin(self, direction, reference_ambient_velocity):
        return self

    def get_turbine(self, turbine):
        return self.value


def test_two_turbines_second_turbine_one_diameter_downwind():

    apply_meander = False

    ambient_velocity = 9.5
    ambient_turbulence = 0.1

    direction = 270.0

    upwind_turbine = Turbine(
        name="T1",
        x=0.0,
        y=0.0,
        hub_height=80.0,
        diameter=76.0,
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    downwind_turbine = Turbine(
        name="T2",
        x=upwind_turbine.diameter,
        y=0.0,
        hub_height=80.0,
        diameter=upwind_turbine.diameter,
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    turbines = [upwind_turbine, downwind_turbine]

    wind_farm = WindFarm(
        turbines=turbines,
        ambient_velocity=FixedAmbientValue(ambient_velocity),
        ambient_turbulence=FixedAmbientValue(ambient_turbulence),
        velocity_integrator=RotorCenterIntegrator(),
        turbulence_integrator=RotorCenterIntegrator(),
        apply_meander=apply_meander)

    wakes = wind_farm.calculate(direction, ambient_velocity)

    assert wakes[0].name == "T1"
    assert wakes[1].name == "T2"

    assert wakes[0].waked_velocity == ambient_velocity
    assert wakes[0].waked_turbulence == ambient_turbulence

    assert wakes[1].waked_velocity == pytest.approx(ambient_velocity * (1.0 - 0.2910), abs=0.005)
    assert wakes[1].waked_turbulence == pytest.approx(0.204077306)
