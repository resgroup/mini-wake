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

            lateral_distance = wake.lateral_distance + lateral_offset
            vertical_distance = wake.vertical_distance + vertical_offset

            velocity_deficit = wake.cross_section.velocity_deficit(
                lateral_distance,
                vertical_distance)

            normalised_lateral_distance = lateral_distance / wake.cross_section.upwind_diameter

            # check here
            combined.add(
                velocity_deficit,
                wake.cross_section.normalised_distance_downwind,
                normalised_lateral_distance)

        return combined.combined_value

    def added_turbulence_at_offset(self, lateral_offset, vertical_offset):

        combined = AddedTurbulenceCombiner()

        for wake in self.wakes:

            lateral_distance = wake.lateral_distance + lateral_offset
            vertical_distance = wake.vertical_distance + vertical_offset

            combined.add(
                wake.cross_section.added_turbulence(
                        lateral_distance,
                        vertical_distance)
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
