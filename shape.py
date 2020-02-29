import math


def calculate_shape(normalized_position):
    if abs(normalized_position) > 1.0:
        return 0.0
    else:
        return math.exp(-3.56 * (normalized_position ** 2.0))
