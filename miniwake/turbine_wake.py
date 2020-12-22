import math
import numpy as np

from .rotor_integration import VelocityDeficitIntegrator
from .rotor_integration import AddedTurbulenceIntegrator

from .single_wake import SingleWake
from .single_wake import NoWakeCrossSection

from .combination import WeightedAverageRSSLinearVelocityDeficitCombiner
from .combination import AddedTurbulenceCombiner

from .distance import distance_sq


class WakeAtRotorCenter:

    def __init__(
            self,
            x,
            cross_section,
            lateral_distance,
            vertical_distance):

        self.x = x

        self.lateral_distance = lateral_distance
        self.vertical_distance = vertical_distance

        self.set_cross_Section(cross_section)

    def set_cross_Section(self, cross_section):

        self.upwind_diameter = cross_section.upwind_diameter
        self.one_over_upwind_diameter = 1.0 / self.upwind_diameter
        self.normalised_distance_downwind = cross_section.normalised_distance_downwind

        self.cross_section = cross_section

    def velocity_deficit(self, lateral_offset, vertical_offset):

        return self.cross_section.velocity_deficit(
            self.lateral_distance + lateral_offset,
            self.vertical_distance + vertical_offset)

    def added_turbulence(self, lateral_offset, vertical_offset):

        return self.cross_section.added_turbulence(
            self.lateral_distance + lateral_offset,
            self.vertical_distance + vertical_offset)

    def normalised_lateral_distance(self, lateral_offset):

        return (self.lateral_distance + lateral_offset) * self.one_over_upwind_diameter


class TurbineWake:

    def __init__(
            self,
            downwind_turbine,
            ambient_velocity,
            ambient_turbulence,
            velocity_deficit_integrator=VelocityDeficitIntegrator(),
            velocity_deficit_combiner=WeightedAverageRSSLinearVelocityDeficitCombiner(),
            added_turbulence_integrator=AddedTurbulenceIntegrator(),
            apply_meander=True,
            apply_added_turbulence=True):

        self.set_ambient_conditions(ambient_velocity, ambient_turbulence)

        self.downwind_turbine = downwind_turbine

        self.name = self.downwind_turbine.name
        self.x = self.downwind_turbine.x
        self.y = self.downwind_turbine.y
        self.diameter = self.downwind_turbine.diameter
        self.hub_height = self.downwind_turbine.hub_height

        self.velocity_deficit_integrator = velocity_deficit_integrator
        self.velocity_deficit_combiner = velocity_deficit_combiner
        self.added_turbulence_integrator = added_turbulence_integrator

        self.apply_meander = apply_meander
        self.apply_added_turbulence = apply_added_turbulence

        self.wakes = []

        self._calculated = False
        self._waked_velocity = None
        self._waked_turbulence = None
        self._impacting_wakes = None
        self._next_wake = None

    def set_ambient_conditions(self, ambient_velocity, ambient_turbulence):

        if np.isnan(ambient_turbulence):
            raise Exception("Ambient turbulence intensity is nan")

        if np.isnan(ambient_velocity):
            raise Exception("Ambient velocity intensity is nan")

        self.ambient_velocity = ambient_velocity
        self.ambient_turbulence = ambient_turbulence

    def add_wake(self, turbine_wake):

        # code assumes co-ordinates have been rotated
        # so that positive x is along wind direction
        # and that upwind only turbines are added in order

        if not turbine_wake.is_calculated:
            raise Exception(
                "Wake cannot be added as it "
                "hasn't been calculated yet. "
                "Call calculate() method first.")

        if len(self.wakes) > 0:
            if turbine_wake.x < self.wakes[-1].x:
                raise Exception(f'Added wake (x={turbine_wake.x}) is not downwind of previous (x={self.wakes[-1].x})')

        downwind_separation = self.x - turbine_wake.x

        if downwind_separation < 0:
            raise Exception('Added wake is not upwind of downwind turbine')

        lateral_separation = self.y - turbine_wake.y
        vertical_separation = self.hub_height - turbine_wake.hub_height

        # the '45 degree rule' to avoid expensive calculations where there
        # is clearly no wake overlap

        dual_radius = 0.5 * (self.diameter + turbine_wake.diameter)

        rd_sq = distance_sq(
            max([0, abs(lateral_separation) - dual_radius]),
            max([0, abs(vertical_separation) - dual_radius]))

        cross_section = self.calculate_cross_section_if_in_wake(
            downwind_separation,
            rd_sq,
            turbine_wake)

        self.wakes.append(
            WakeAtRotorCenter(
                turbine_wake.x,
                cross_section,
                lateral_separation,
                vertical_separation))

    def calculate_cross_section_if_in_wake(
            self,
            downwind_separation,
            rd_sq,
            turbine_wake):

        if self.rule_of_thumb_control_surface(
                downwind_separation,
                rd_sq,
                turbine_wake.waked_turbulence,
                turbine_wake.diameter):

            return turbine_wake.calculate_cross_section(downwind_separation)

        else:

            return NoWakeCrossSection(
                downwind_separation,
                turbine_wake.diameter)

    def rule_of_thumb_control_surface(self, downwind_separation, rd_sq, turbulence, diameter):

        a = -0.0232381 * turbulence * turbulence + 0.0001743 * turbulence
        b = 1.84646 * turbulence + 0.00400
        c = 2.0

        normalised_downwind_separation = downwind_separation / diameter
        normalised_downwind_separation_sq = normalised_downwind_separation * normalised_downwind_separation

        normalised_control_surface = a * normalised_downwind_separation_sq + b * normalised_downwind_separation + c
        control_surface = max([0.0, normalised_control_surface * diameter])

        control_surface_sq = control_surface * control_surface

        if (rd_sq < control_surface_sq):
            return True
        else:
            return False

    def rule_of_thumb_45_degree(self, downwind_separation, rd_sq, turbulence, diameter):

        control_surface_sq = downwind_separation * downwind_separation

        if (rd_sq < control_surface_sq):
            return True
        else:
            return False

    def velocity_deficit_at_offset(self, lateral_offset, vertical_offset):

        combined = self.velocity_deficit_combiner()

        for wake in self.wakes:
            velocity_deficit = wake.velocity_deficit(
                lateral_offset,
                vertical_offset)

            combined.add(
                velocity_deficit,
                wake.normalised_distance_downwind,
                wake.normalised_lateral_distance(lateral_offset))

        return combined.combined_value(), combined.impacting_wakes()

    def added_turbulence_at_offset(self, lateral_offset, vertical_offset):

        combined = AddedTurbulenceCombiner()

        for wake in self.wakes:

            combined.add(
                wake.added_turbulence(
                    lateral_offset,
                    vertical_offset)
            )

        return combined.combined_value(), 0

    def recalculate(self, ambient_velocity, ambient_turbulence):

        self._is_calculated = False

        self.set_ambient_conditions(ambient_velocity, ambient_turbulence)

        for wake in self.wakes: #WakeAtRotorCenter
            # need to update cross_section
            wake.set_cross_Section()

        self.calculate()

    def calculate(self):

        self._velocity_deficit, self._impacting_wakes = self.velocity_deficit_integrator.calculate(
            self.downwind_turbine.diameter,
            self.velocity_deficit_at_offset)

        self._waked_velocity = (1.0 - self._velocity_deficit) * self.ambient_velocity

        added_turbulence, _ = self.added_turbulence_integrator.calculate(
            self.downwind_turbine.diameter,
            self.added_turbulence_at_offset)

        self._waked_turbulence = math.sqrt(
            added_turbulence * added_turbulence +
            self.ambient_turbulence * self.ambient_turbulence)

        self._next_wake = SingleWake(
            ambient_turbulence_intensity=self.ambient_turbulence,
            upwind_turbine=self.downwind_turbine,
            upwind_velocity=self._waked_velocity,
            upwind_local_turbulence_intensity=self._waked_turbulence,
            apply_meander=self.apply_meander,
            apply_added_turbulence=self.apply_added_turbulence)

        self._is_calculated = True

    @property
    def is_calculated(self):
        return self._is_calculated

    def validate_has_been_calculated(self):

        if not self.is_calculated:
            raise Exception(
                "Property/mehtod cannot be called until calculate()"
                "method has been called.")

    @property
    def velocity_deficit(self):

        self.validate_has_been_calculated()

        return self._velocity_deficit

    @property
    def waked_velocity(self):

        self.validate_has_been_calculated()

        return self._waked_velocity

    @property
    def waked_turbulence(self):

        self.validate_has_been_calculated()

        return self._waked_turbulence

    @property
    def impacting_wakes(self):

        self.validate_has_been_calculated()

        return self._impacting_wakes

    @property
    def near_wake_length(self):

        self.validate_has_been_calculated()

        return self._next_wake.near_wake_length

    def calculate_cross_section(self, distance_downwind):

        self.validate_has_been_calculated()

        return self._next_wake.calculate(distance_downwind)
