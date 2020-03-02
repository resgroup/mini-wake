import pytest

from near_wake_length import calculate_near_wake_length
from single_wake import SingleWake


def test_single_wake():

    upwind_diameter = 76.0
    upwind_thrust_coefficient = 0.4
    upwind_rpm = 17.0
    upwind_number_of_blades = 3
    upwind_velocity = 9.5
    amient_turbulence_intensity = 0.1
    upwind_local_turbulence_intensity = amient_turbulence_intensity

    upwind_near_wake_length = calculate_near_wake_length(diameter=upwind_diameter,
                                                         thrust_coefficient=upwind_thrust_coefficient,
                                                         rpm=upwind_rpm,
                                                         number_of_blades=upwind_number_of_blades,
                                                         velocity=upwind_velocity,
                                                         turbulence_intensity=amient_turbulence_intensity)

    assert upwind_near_wake_length == pytest.approx(149.4116199)

    single_wake = SingleWake(ambient_turbulence_intensity = amient_turbulence_intensity,
                             upwind_diameter = upwind_diameter,
                             upwind_thrust_coefficient = upwind_thrust_coefficient,
                             upwind_local_turbulence_intensity = upwind_local_turbulence_intensity,
                             upwind_near_wake_length = upwind_near_wake_length,
                             apply_meander=False)

    wake = single_wake.calculate(upwind_diameter * 4.0)

    assert wake.width == pytest.approx(71.20098095, abs=0.05)

    assert wake.velocity_deficit(0.0) == pytest.approx(0.229031, abs=0.0005)
    assert wake.velocity_deficit(28.5) == pytest.approx(0.129473057, abs=0.0005)

    assert wake.added_turbulence(0.0) == pytest.approx(0.080722728)
    assert wake.added_turbulence(28.5) == pytest.approx(0.080722728)

