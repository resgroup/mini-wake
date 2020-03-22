import pytest

from miniwake.rotation import rotate_and_sort_turbines


class TurbineStub:

    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def clone_at_new_location(self, x, y):
        return TurbineStub(self.name, x, y)


def test_rotate_and_sort_turbines():

    turbines = [TurbineStub("T1", 400, 200),
                TurbineStub("T2", 800, 200),
                TurbineStub("T3", 300, 200)]

    transformed_turbines = rotate_and_sort_turbines(270.0, turbines)

    assert transformed_turbines[0].name == "T3"
    assert transformed_turbines[0].x == 0.0
    assert transformed_turbines[0].y == 0.0

    assert transformed_turbines[1].name == "T1"
    assert transformed_turbines[1].x == 100.0
    assert transformed_turbines[1].y == 0.0

    assert transformed_turbines[2].name == "T2"
    assert transformed_turbines[2].x == 500.0
    assert transformed_turbines[2].y == 0.0
