import pytest

from miniwake.near_wake_length import calculate_ambient_turbulence_wake_erosion_rate
from miniwake.near_wake_length import calculate_angular_velocity
from miniwake.near_wake_length import calculate_flow_field_ratio
from miniwake.near_wake_length import calculate_mechanical_turbulence_wake_erosion_rate
from miniwake.near_wake_length import calculate_n
from miniwake.near_wake_length import calculate_radius_of_inviscid_expanded_rotor_disk
from miniwake.near_wake_length import calculate_near_wake_length

def test_calculate_ambient_turbulence_wake_erosion_rate():
	ambientTurbuluence = 0.1
	assert calculate_ambient_turbulence_wake_erosion_rate(ambientTurbuluence) == (2.5 * ambientTurbuluence + 0.05)

def test_calculate_angular_velocity():
	assert calculate_angular_velocity(0.0) == 0.0

def test_calculate_flow_field_ratio():
	assert calculate_flow_field_ratio(1.0) == 3.0

def test_calculate_mechanical_turbulence_wake_erosion_rate():
	assert calculate_mechanical_turbulence_wake_erosion_rate(3, 0.0) == 0.0

def test_calculate_n():
	pass #todo

def test_calculate_radius_of_inviscid_expanded_rotor_disk():
	pass #todo

def test_calculate_shear_generated_turbulence_wake_erosion_rate():
	pass #todo

def test_calculate_tip_speed_ratio():
	pass #todo

def test_calculate_total_wake_erosion_rate():
	pass #todo

def testcalculate__near_wake_length():
	assert calculate_near_wake_length(76, 0.7, 15, 3, 10, 0.15) == pytest.approx(140.0160145)
