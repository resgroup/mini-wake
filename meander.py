import math


class MeanderResult:

    def __init__(self, width_meander, amplitude_meander): 
        self.width_meander = width_meander
        self.amplitude_meander = amplitude_meander


def calculate_standard_deviation_of_direction(ambient_turbulence):
    return 0.7 * ambient_turbulence


def calculate_meander_factor(scaled_distance_downwind, velocity_deficit, wake_width, ambient_turbulence):

    sigth = calculate_standard_deviation_of_direction(ambient_turbulence)
    sigth = max([0.0, sigth])
    return 1.0 / math.sqrt(1.0 + 7.12 * (sigth * scaled_distance_downwind / wake_width) ** 2.0)


def calculate_meander(scaled_distance_downwind, velocity_deficit, wake_width, ambient_turbulence):

    meander_factor = calculate_meander_factor(scaled_distance_downwind, velocity_deficit, wake_width, ambient_turbulence)
    return MeanderResult(1.0 / meander_factor, meander_factor)
