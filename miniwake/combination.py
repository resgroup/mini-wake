import math
from .rotor_integration import VelocityDeficitIntegrator
from .rotor_integration import AddedTurbulenceIntegrator


class VelocityDeficitCombiner:

    # RSS and Maximum Auto WC method - based on unpublished work of Mike Anderson

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
    def combined_value(self):
        if self.closest_normalised_distance_upwind <= 6.0:
            return self.near_combination_maximum
        else:
            return math.sqrt(self.far_combination_total)


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


class CombinedWake:

    def __init__(self, downwind_turbine, ambient_turbulence):

        self.ambient_turbulence = ambient_turbulence
        self.downwind_turbine = downwind_turbine

        self.combined_velocity_deficit = VelocityDeficitCombiner()
        self.combined_added_turbulence = AddedTurbulenceCombiner()

    def add_wake(self, upwind_wake):

        # code current assumes co-ordinates have been rotated
        # so that positive x is along wind direction

        downwind_separation = self.downwind_turbine.x - upwind_wake.upwind_turbine.x
        lateral_separation = self.downwind_turbine.y - upwind_wake.upwind_turbine.y
        vertical_separation = self.downwind_turbine.hub_height - upwind_wake.upwind_turbine.hub_height

        normalised_distance_upwind = downwind_separation / upwind_wake.upwind_turbine.diameter
        normalised_lateral_distance = lateral_separation / upwind_wake.upwind_turbine.diameter

        cross_section = upwind_wake.calculate(downwind_separation)

        velocity_deficit = VelocityDeficitIntegrator().calculate(
            lateral_separation,
            vertical_separation,
            self.downwind_turbine.diameter,
            cross_section.velocity_deficit)

        added_turbulence = AddedTurbulenceIntegrator().calculate(
            lateral_separation,
            vertical_separation,
            self.downwind_turbine.diameter,
            cross_section.added_turbulence)

        self.combined_velocity_deficit.add(velocity_deficit,
                                           normalised_distance_upwind,
                                           normalised_lateral_distance)
     
        self.combined_added_turbulence.add(added_turbulence)

    @property
    def velocity_deficit(self):
        return self.combined_velocity_deficit.combined_value

    @property
    def added_turbulence(self):
        return self.combined_added_turbulence.combined_value

    @property
    def local_turbulence(self):

        added_turbulence = self.added_turbulence

        return math.sqrt(added_turbulence * added_turbulence
                         + self.ambient_turbulence * self.ambient_turbulence)
