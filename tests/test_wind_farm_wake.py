import pytest

from miniwake.turbine import Turbine
from miniwake.turbine import FixedThrustCurve
from miniwake.wind_farm_wake import WindFarmWake


class RotorCenterIntegrator:

    def calculate(self,
                  downwind_rotor_diameter,
                  wake_integral):

        return wake_integral(0, 0)


def test_two_turbines_second_turbine_one_diameter_downwind():

    apply_meander = False

    ambient_velocity = 9.5
    ambient_turbulence = 0.1

    direction = 270.0

    upwind_turbine = Turbine(
        x=0.0,
        y=0.0,
        hub_height=80.0,
        diameter=76.0,
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    downwind_turbine = Turbine(
        x=upwind_turbine.diameter,
        y=0.0,
        hub_height=80.0,
        diameter=upwind_turbine.diameter,
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))
    
    turbines = [upwind_turbine, downwind_turbine]

    wind_farm_wake = WindFarmWake(
        turbines=turbines,
        ambient_velocity=ambient_velocity,
        ambient_turbulence=ambient_turbulence,
        velocity_deficit_integrator=RotorCenterIntegrator(),
        added_turbulence_integrator=RotorCenterIntegrator(),
        apply_meander=apply_meander)
    
    downwind_wake = wind_farm_wake.turbine_wakes[1]

    assert downwind_wake.waked_velocity == pytest.approx(ambient_velocity * (1.0 - 0.2910), abs=0.005)
    assert downwind_wake.waked_turbulence == pytest.approx(0.204077306)

