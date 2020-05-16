from scipy import interpolate


def rect_grid_linear(cts, turbulences, distances, deficits):

    return interpolate.RegularGridInterpolator(
        points=(cts, turbulences, distances),
        values=deficits,
        method="linear",
        bounds_error=True)


def rect_grid_nearest(cts, turbulences, distances, deficits):

    return interpolate.RegularGridInterpolator(
        points=(cts, turbulences, distances),
        values=deficits,
        method="nearest",
        bounds_error=True)