import math
from .turbine import Turbine

PI_OVER_180_DEGRESS = math.pi / 180.0


def rotate_and_sort_turbines(direction, turbines):

    delr = PI_OVER_180_DEGRESS * (direction - 270)

    cd = math.cos(delr)
    sd = math.sin(delr)

    rotated = []

    min_x = None
    y_at_min_x = None

    for turbine in turbines:

        x = turbine.x * cd - turbine.y * sd
        y = turbine.x * sd + turbine.y * cd

        rotated.append(turbine.clone_at_new_location(x, y))

        if min_x is None or x < min_x:
            min_x = x
            y_at_min_x = y

    shifted = []

    for turbine in turbines:

        shifted.append(
            turbine.clone_at_new_location(
                    x=turbine.x - min_x,
                    y=turbine.y - y_at_min_x)
                )

    shifted.sort(key=lambda t: t.x, reverse=False)

    return shifted
