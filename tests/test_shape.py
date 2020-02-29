import pytest
import math

from shape import calculate_shape

def test_calculate_shape():
    assert calculate_shape(math.sqrt(1.0 / 3.56)) == pytest.approx(math.exp(-1.0))
