import math


def calculate_wake_width(thrust_coefficient, velocity_deficit):

    return math.sqrt(3.56 * thrust_coefficient / (8.0 * velocity_deficit * (1.0 - 0.5 * velocity_deficit)))
