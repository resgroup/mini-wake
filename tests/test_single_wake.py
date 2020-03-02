import pytest

from single_wake import SingleWake


def test_single_wake():

    upwind_diameter = 76.0
    upwind_thrust_coefficient = 0.4
    upwind_rpm = 17.0
    upwind_velocity = 9.5
    amient_turbulence_intensity = 0.1
    upwind_local_turbulence_intensity = amient_turbulence_intensity

    single_wake = SingleWake(ambient_turbulence_intensity=amient_turbulence_intensity,
                             upwind_diameter=upwind_diameter,
                             upwind_thrust_coefficient=upwind_thrust_coefficient,
                             upwind_velocity=upwind_velocity,
                             upwind_local_turbulence_intensity=upwind_local_turbulence_intensity,
                             upwind_rpm=upwind_rpm,
                             apply_meander=False)

    assert single_wake.upwind_near_wake_length == pytest.approx(149.4116199)

    wake = single_wake.calculate(upwind_diameter * 4.0)

    assert wake.width == pytest.approx(71.20098095, abs=0.05)

    assert wake.velocity_deficit(0.0) == pytest.approx(0.229031, abs=0.0005)
    assert wake.velocity_deficit(28.5) == pytest.approx(0.129473057, abs=0.0005)

    assert wake.added_turbulence(0.0) == pytest.approx(0.080722728)
    assert wake.added_turbulence(28.5) == pytest.approx(0.080722728)

