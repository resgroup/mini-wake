import math


class NumberOfImpactiveWakesCalculator:

    def __init__(self, threshold=0.02):
        self.count = 0
        self.threshold = threshold

    def add(self, velocity_deficit):
        if velocity_deficit > self.threshold:
            self.count += 1


class VelocityDeficitCombiner:

    # RSS and Maximum Auto WC method - based on unpublished work of Mike Anderson

    def __init__(self):
        self.far_combination_total = 0.0
        self.near_combination_maximum = 0.0
        self.closest_normalised_distance_upwind = float('inf')
        self.impactive_wakes = NumberOfImpactiveWakesCalculator()

    def add(self, value, normalised_distance_upwind, normalised_lateral_distance):

        if value <= 0.0:
            return

        self.impactive_wakes.add(value)

        self.far_combination_total += value * value
        self.near_combination_maximum = max([value, self.near_combination_maximum])

        if abs(normalised_lateral_distance) <= 1.5:

            self.closest_normalised_distance_upwind = min([normalised_distance_upwind,
                                                           self.closest_normalised_distance_upwind])

    @property
    def combined_value(self):
        if self.closest_normalised_distance_upwind <= 6.0:
            return self.near_combination_maximum
        else:
            return math.sqrt(self.far_combination_total)

    @property
    def number_of_impactive_wakes(self):
        self.impactive_wakes.count


class AddedTurbulenceCombiner:

    # RSS method
    # todo check if right logic

    def __init__(self):
        self.total = 0.0

    def add(self, value):

        if value <= 0.0:
            return

        self.total += value * value

    @property
    def combined_value(self):
        return math.sqrt(self.total)