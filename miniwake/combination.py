import math
from .rotor_integration import VelocityDeficitIntegrator
from .rotor_integration import AddedTurbulenceIntegrator


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


class WakeAtRotorCenter:

    def __init__(
                self,
                cross_section,
                lateral_distance,
                vertical_distance
                ):

        self.cross_section = cross_section
        self.lateral_distance = lateral_distance
        self.vertical_distance = vertical_distance

        self.upwind_diameter = cross_section.upwind_diameter
        self.normalised_distance_downwind = cross_section.normalised_distance_downwind

    def velocity_deficit(self, lateral_offset, vertical_offset):

        return self.cross_section.velocity_deficit(
                self.lateral_distance + lateral_offset,
                self.vertical_distance + vertical_offset)

    def added_turbulence(self, lateral_offset, vertical_offset):

        return self.cross_section.added_turbulence(
                self.lateral_distance + lateral_offset,
                self.vertical_distance + vertical_offset)

    def normalised_lateral_distance(self, lateral_offset):

        return (self.lateral_distance + lateral_offset) / self.upwind_diameter

class CombinedWake:

    def __init__(
                self,
                downwind_turbine,
                ambient_turbulence,
                velocoity_deficit_integrator=VelocityDeficitIntegrator(),
                added_turbulence_integrator=AddedTurbulenceIntegrator()
                ):

        self.ambient_turbulence = ambient_turbulence
        self.downwind_turbine = downwind_turbine

        self.velocity_deficit_integrator = velocoity_deficit_integrator
        self.added_turbulence_integrator = added_turbulence_integrator

        self.wakes = []

    def add_wake(self, wake):

        # code currently assumes co-ordinates have been rotated
        # so that positive x is along wind direction
        # and that upwind onyl turbines are added in order

        if len(self.wakes) > 0:
            if wake.upwind_turbine.x < self.wakes[-1].cross_section.upwind_turbine.x:
                raise Exception('Added wake is not downwind of previous')

        if wake.upwind_turbine.x > self.downwind_turbine.x:
            raise Exception('Added wake is not upwind of downwind turbine')

        downwind_separation = self.downwind_turbine.x - wake.upwind_turbine.x
        lateral_separation = self.downwind_turbine.y - wake.upwind_turbine.y
        vertical_separation = self.downwind_turbine.hub_height - wake.upwind_turbine.hub_height

        self.wakes.append(
            WakeAtRotorCenter(
                wake.calculate(downwind_separation),
                lateral_separation,
                vertical_separation))

    def velocity_deficit_at_offset(self, lateral_offset, vertical_offset):

        combined = VelocityDeficitCombiner()

        for wake in self.wakes:

            velocity_deficit = wake.velocity_deficit(
                lateral_offset,
                vertical_offset)

            combined.add(
                velocity_deficit,
                wake.normalised_distance_downwind,
                wake.normalised_lateral_distance(lateral_offset))

        return combined.combined_value

    def added_turbulence_at_offset(self, lateral_offset, vertical_offset):

        combined = AddedTurbulenceCombiner()

        for wake in self.wakes:

            combined.add(
                wake.added_turbulence(
                        lateral_offset,
                        vertical_offset)
            )

        return combined.combined_value

    def combined_velocity_deficit(self):

        return self.velocity_deficit_integrator.calculate(
            self.downwind_turbine.diameter,
            self.velocity_deficit_at_offset)

    def combined_local_turbulence(self):

        added_turbulence = self.added_turbulence_integrator.calculate(
                            self.downwind_turbine.diameter,
                            self.added_turbulence_at_offset)

        return math.sqrt(added_turbulence * added_turbulence
                         + self.ambient_turbulence * self.ambient_turbulence)
