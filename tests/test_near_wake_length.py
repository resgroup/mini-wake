import pytest

from near_wake_length import ambient_turbulence_wake_erosion_rate

def test_ambient_turbulence_wake_erosion_rate():
	ambientTurbuluence = 0.1
	assert ambient_turbulence_wake_erosion_rate(ambientTurbuluence) == (2.5 * ambientTurbuluence + 0.05)

#to run this write 'py.test test.py' in the command line