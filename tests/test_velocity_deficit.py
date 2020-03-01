import pytest

from velocity_deficit import calculate_velocity_deficit


def test_calculate_velocity_deficit():
	assert calculate_velocity_deficit(1.5, 100, 0.25) == pytest.approx(0.007609, abs=0.00005)
