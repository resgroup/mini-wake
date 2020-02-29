import pytest

from width import calculate_wake_width


def test_calculate_wake_width():
	assert calculate_wake_width(0.4, 0.229031) == pytest.approx(71.20098095 / 76.0)
