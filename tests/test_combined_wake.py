import pytest

from miniwake.combination import VelocityDeficitCombiner
from miniwake.single_wake import SingleWake
from miniwake.turbine import Turbine
from miniwake.turbine import FixedThrustCurve
from miniwake.combination import CombinedWake


class RotorCenterIntegrator:

    def calculate(self,
                  downwind_rotor_diameter,
                  wake_integral):

        return wake_integral(0, 0)


def test_velicity_deficit_combination():

    combiner = VelocityDeficitCombiner()

    combiner.add(value=0.1, normalised_distance_upwind=3.0, normalised_lateral_distance=0.0)

    assert combiner.combined_value == 0.1

    combiner.add(value=0.05, normalised_distance_upwind=7.0, normalised_lateral_distance=0.0)

    assert combiner.closest_normalised_distance_upwind == 3.0

    assert combiner.combined_value == 0.1


def test_combined_wake_diameter():

    ambient_velocity = 9.5
    ambient_turbulence_intensity = 0.1
    
    upwind_turbine = Turbine(
        x=0.0,
        y=0.0,
        hub_height=80.0,
        diameter=76.0,
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    # use really small diameter so get same result as single wake
    downwind_turbine = Turbine(
        x=upwind_turbine.diameter * 4.0,
        y=0.0,
        hub_height=80.0,
        diameter=upwind_turbine.diameter,  
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    upwind_local_turbulence_intensity = ambient_turbulence_intensity

    upwind_wake = SingleWake(
        ambient_turbulence_intensity=ambient_turbulence_intensity,
        upwind_turbine=upwind_turbine,
        upwind_velocity=ambient_velocity,
        upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
        apply_meander=False)

    combined_wake = CombinedWake(
        downwind_turbine,
        ambient_velocity,
        ambient_turbulence_intensity,
        velocity_deficit_integrator=RotorCenterIntegrator(),
        added_turbulence_integrator=RotorCenterIntegrator())

    combined_wake.add_wake(upwind_wake)

    wake_result = combined_wake.combine_and_integrate()

    assert wake_result.waked_velocity == pytest.approx(ambient_velocity * (1.0 - 0.229031), abs=0.005)
    assert wake_result.waked_turbulence == pytest.approx(0.128515208500)


def test_combined_wake_one_diameter_downwind():

    ambient_velocity = 9.5
    ambient_turbulence_intensity = 0.1

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
        hub_height=upwind_turbine.hub_height,
        diameter=upwind_turbine.diameter,
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    upwind_local_turbulence_intensity = ambient_turbulence_intensity

    upwind_wake = SingleWake(
        ambient_turbulence_intensity=ambient_turbulence_intensity,
        upwind_turbine=upwind_turbine,
        upwind_velocity=ambient_velocity,
        upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
        apply_meander=False)

    assert upwind_wake.near_wake_length == pytest.approx(149.4116199, abs=0.0005)

    combined_wake = CombinedWake(
        downwind_turbine,
        ambient_velocity,
        ambient_turbulence_intensity,
        velocity_deficit_integrator=RotorCenterIntegrator(),
        added_turbulence_integrator=RotorCenterIntegrator())

    combined_wake.add_wake(upwind_wake)

    wake_result = combined_wake.combine_and_integrate()

    assert wake_result.waked_velocity == pytest.approx(ambient_velocity * (1 - 0.2910), abs=0.005)
    assert wake_result.waked_turbulence == pytest.approx(0.204077306)

