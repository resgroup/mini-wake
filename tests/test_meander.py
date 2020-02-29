import pytest

from meander import calculate_meander

def test_quarton_added_turbulence():
    result = calculate_meander(0.0, 4.0, 1.0, 1.0)
    assert result.width_meander == 1.0
    assert result.amplitude_meander == 1.0
