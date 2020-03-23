import pytest

from miniwake.turbine import Turbine
from miniwake.turbine import FixedThrustCurve
from miniwake.turbine_wake import TurbineWake


class RotorCenterIntegrator:

    def calculate(self,
                  downwind_rotor_diameter,
                  wake_integral):

        return wake_integral(0, 0)


def test_combined_wake_diameter():

    apply_meander = False

    ambient_velocity = 9.5
    ambient_turbulence = 0.1
    
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
        x=upwind_turbine.diameter * 4.0,
        y=0.0,
        hub_height=80.0,
        diameter=upwind_turbine.diameter,
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    upwind_wake = TurbineWake(
        upwind_turbine,
        ambient_velocity=ambient_velocity,
        ambient_turbulence=ambient_turbulence,
        apply_meander=apply_meander)

    upwind_wake.calculate()

    downwind_wake = TurbineWake(
        downwind_turbine,
        ambient_velocity,
        ambient_turbulence,
        apply_meander=apply_meander,
        velocity_deficit_integrator=RotorCenterIntegrator(),
        added_turbulence_integrator=RotorCenterIntegrator())

    downwind_wake.add_wake(upwind_wake)

    downwind_wake.calculate()

    assert downwind_wake.waked_velocity == pytest.approx(ambient_velocity * (1.0 - 0.229031), abs=0.005)
    assert downwind_wake.waked_turbulence == pytest.approx(0.128515208500)


def test_combined_wake_one_diameter_downwind():

    ambient_velocity = 9.5
    ambient_turbulence_intensity = 0.1

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
        hub_height=upwind_turbine.hub_height,
        diameter=upwind_turbine.diameter,
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    upwind_local_turbulence_intensity = ambient_turbulence_intensity

    upwind_wake = TurbineWake(
                    upwind_turbine,
                    ambient_velocity=ambient_velocity,
                    ambient_turbulence=ambient_turbulence_intensity,
                    apply_meander=False
                )

    upwind_wake.calculate()

    assert upwind_wake.near_wake_length == pytest.approx(149.4116199, abs=0.0005)

    downwind_wake = TurbineWake(
        downwind_turbine,
        ambient_velocity,
        ambient_turbulence_intensity,
        velocity_deficit_integrator=RotorCenterIntegrator(),
        added_turbulence_integrator=RotorCenterIntegrator())

    downwind_wake.add_wake(upwind_wake)

    downwind_wake.calculate()

    assert downwind_wake.waked_velocity == pytest.approx(ambient_velocity * (1 - 0.2910), abs=0.005)
    assert downwind_wake.waked_turbulence == pytest.approx(0.204077306)

