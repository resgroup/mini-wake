import pytest

from miniwake.added_turbulence import quarton_added_turbulence

def test_quarton_added_turbulence():
	 assert quarton_added_turbulence(1.0, 1.0, 1.0, 1.0, 1.0) == pytest.approx(1.1)
