import math
from .rotor_integration import VelocityDeficitIntegrator
from .rotor_integration import AddedTurbulenceIntegrator
from .single_wake import SingleWake

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


class TurbineWake:

    def __init__(
                self,
                downwind_turbine,
                ambient_velocity,
                ambient_turbulence,
                velocity_deficit_integrator=VelocityDeficitIntegrator(),
                added_turbulence_integrator=AddedTurbulenceIntegrator(),
                apply_meander=True
                ):

        self.ambient_velocity = ambient_velocity
        self.ambient_turbulence = ambient_turbulence
        self.downwind_turbine = downwind_turbine

        self.velocity_deficit_integrator = velocity_deficit_integrator
        self.added_turbulence_integrator = added_turbulence_integrator

        self.apply_meander = apply_meander
        
        self.wakes = []

        self._combined = False
        self._waked_velocity = None
        self._waked_turbulence = None
        self._next_wake = None

    def add_wake(self, turbine_wake):

        # code assumes co-ordinates have been rotated
        # so that positive x is along wind direction
        # and that upwind only turbines are added in order

        if not turbine_wake.combined:
            raise Exception(
                    "Wake cannot be added as it "
                    "hasn't been combined yet. "
                    "Call combine() method first.")

        if len(self.wakes) > 0:
            if turbine_wake.x < self.wakes[-1].x:
                raise Exception('Added wake is not downwind of previous')

        downwind_separation = self.x - turbine_wake.x

        if downwind_separation < 0:
            raise Exception('Added wake is not upwind of downwind turbine')

        lateral_separation = self.y - turbine_wake.y
        vertical_separation = self.hub_height - turbine_wake.hub_height

        self.wakes.append(
            WakeAtRotorCenter(
                turbine_wake.calculate_cross_section(downwind_separation),
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

    def combine(self):

        velocity_deficit = self.velocity_deficit_integrator.calculate(
                                self.downwind_turbine.diameter,
                                self.velocity_deficit_at_offset)
        
        self._waked_velocity = (1.0 - velocity_deficit) * self.ambient_velocity

        added_turbulence = self.added_turbulence_integrator.calculate(
                            self.downwind_turbine.diameter,
                            self.added_turbulence_at_offset)

        self._waked_turbulence = math.sqrt(added_turbulence * added_turbulence
                                           + self.ambient_turbulence * self.ambient_turbulence)

        self._next_wake = SingleWake(
                            ambient_turbulence_intensity=self.ambient_turbulence,
                            upwind_turbine=self.downwind_turbine,
                            upwind_velocity=self._waked_velocity,
                            upwind_local_turbulence_intensity=self._waked_turbulence,
                            apply_meander=self.apply_meander)

        self._combined = True

    @property
    def x(self):
        return self.downwind_turbine.x

    @property
    def y(self):
        return self.downwind_turbine.y

    @property
    def hub_height(self):
        return self.downwind_turbine.hub_height

    @property
    def combined(self):
        return self._combined

    def validate_has_been_combined(self):

        if not self.combined:
            raise Exception(
                "Property cannot be called until combine()"
                "method has been called")

    @property
    def waked_velocity(self):

        self.validate_has_been_combined()

        return self._waked_velocity

    @property
    def waked_turbulence(self):

        self.validate_has_been_combined()

        return self._waked_turbulence

    @property
    def near_wake_length(self):

        self.validate_has_been_combined()

        return self._next_wake.near_wake_length

    def calculate_cross_section(self, distance_downwind):

        self.validate_has_been_combined()

        return self._next_wake.calculate(distance_downwind)