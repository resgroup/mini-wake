import pytest
import math

from velocity_deficit import calculate_velocity_deficit
from velocity_deficit import calculate_shape
from velocity_deficit import calculate_width


def test_calculate_velocity_deficit():
	assert calculate_velocity_deficit(1.5, 100, 0.25) == pytest.approx(0.007609, abs=0.00005)


def test_calculate_shape():
    assert calculate_shape(math.sqrt(1.0 / 3.56)) == pytest.approx(math.exp(-1.0))


def test_calculate_wake_width():
	assert calculate_width(0.4, 0.229031) == pytest.approx(71.20098095 / 76.0)
