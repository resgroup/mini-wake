import math


def distance(delta_x, delta_y):
    return math.sqrt(distance_sq(delta_x, delta_y))


def distance_sq(delta_x, delta_y):
    return delta_x * delta_x + delta_y * delta_y
