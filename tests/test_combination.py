import pytest

from miniwake.combination import VelocityDeficitCombiner
from miniwake.single_wake import SingleWake
from miniwake.turbine import Turbine
from miniwake.turbine import FixedThrustCurve
from miniwake.combination import CombinedWake

def test_velicity_deficit_combination():

    combiner = VelocityDeficitCombiner()

    combiner.add(value=0.1, normalised_distance_upwind=3.0, normalised_lateral_distance=0.0)

    assert combiner.combined_value == 0.1

    combiner.add(value=0.05, normalised_distance_upwind=7.0, normalised_lateral_distance=0.0)

    assert combiner.closest_normalised_distance_upwind == 3.0

    assert combiner.combined_value == 0.1


def test_combined_wake():

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
        diameter=0.00001,  
        rotational_speed_rpm=17.0,
        thrust_curve=FixedThrustCurve(0.4))

    upwind_velocity = 9.5
    amient_turbulence_intensity = 0.1
    upwind_local_turbulence_intensity = amient_turbulence_intensity

    upwind_wake = SingleWake(
        ambient_turbulence_intensity=amient_turbulence_intensity,
        upwind_turbine=upwind_turbine,
        upwind_velocity=upwind_velocity,
        upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
        apply_meander=False)

    combined_wake = CombinedWake(downwind_turbine)

    combined_wake.add_wake(upwind_wake)

    assert combined_wake.velocity_deficit == pytest.approx(0.229031, abs=0.0005)
    assert combined_wake.added_turbulence == pytest.approx(0.080722728)