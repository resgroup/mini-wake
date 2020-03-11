import math


class RSSAndMaximumAutoWC:

    def __init__(self):
        self.far_combination_total = 0.0
        self.near_combination_maximum = 0.0
        self.closest_normalised_distance_upwind = float('inf')

    def add(self, value, normalised_distance_upwind, normalised_lateral_distance):

        if value <= 0.0:
            return

        self.far_combination_total += value * value
        self.near_combination_maximum = max([value, self.near_combination_maximum])

        if abs(normalised_lateral_distance) <= 1.5:

            self.closest_normalised_distance_upwind = min([normalised_distance_upwind,
                                                           self.closest_normalised_distance_upwind])

    @property
    def value(self):
        if self.closest_normalised_distance_upwind <= 6.0:
            return self.near_combination_maximum
        else:
            return math.sqrt(self.far_combination_total)

