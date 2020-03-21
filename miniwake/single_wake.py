import math

from .velocity_deficit import calculate_shape
from .velocity_deficit import calculate_width
from .velocity_deficit import calculate_velocity_deficit
from .added_turbulence import quarton_added_turbulence
from .meander import calculate_meander
from .near_wake_length import calculate_near_wake_length


def distance(delta_x, delta_y):
    return math.sqrt(delta_x * delta_x + delta_y * delta_y)


class NoWakeCrossSection:

    def __init__(self, distance_downwind):
        self.distance_downwind = distance_downwind

    def velocity_deficit(self,
                         lateral_distance,
                         vertical_distance):
        return 0.0

    def added_turbulence(self,
                         lateral_distance,
                         vertical_distance):
        return 0.0


class WakeCrossSection:

    def __init__(
            self,
            distance_downwind,
            velocity_deficit,
            added_turbulence,
            wake_width,
            upwind_diameter):

        self.distance_downwind = distance_downwind
        self.upwind_diameter = upwind_diameter
        self.normalised_distance_downwind = distance_downwind / upwind_diameter

        self.velocity_deficit = VelocityDeficitWakeProfile(
                                    velocity_deficit,
                                    wake_width)

        self.added_turbulence = AddedTurbulenceWakeProfile(
                                    added_turbulence,
                                    wake_width)

        self.width = wake_width


class AddedTurbulenceWakeProfile:

    def __init__(self, added_turbulence, wake_width):
        self.added_turbulence = added_turbulence
        self.wake_width = wake_width

    def __call__(self,
                 lateral_distance,
                 vertical_distance=0.0):

        distance_from_wake_center = distance(lateral_distance,
                                             vertical_distance)

        if abs(distance_from_wake_center) < self.wake_width:
            return self.added_turbulence
        else:
            return 0.0


class VelocityDeficitWakeProfile:

    def __init__(self, velocity_deficit, wake_width):
        self.velocity_deficit = velocity_deficit
        self.wake_width = wake_width

    def __call__(self,
                lateral_distance,
                vertical_distance=0.0):
        
        distance_from_wake_center = distance(lateral_distance,
                                             vertical_distance)

        return calculate_shape(distance_from_wake_center / self.wake_width) * self.velocity_deficit


class SingleWake:

        NEAR_ZERO = 0.000001

        def __init__(
                self,
                ambient_turbulence_intensity,
                upwind_turbine,
                upwind_velocity,
                upwind_local_turbulence_intensity,
                apply_meander=True):

            self.upwind_turbine = upwind_turbine
            self.ambient_turbulence_intensity = ambient_turbulence_intensity
            self.upwind_thrust_coefficient = upwind_turbine.thrust_curve(upwind_velocity)

            if self.upwind_thrust_coefficient < 0.0:
                raise Exception("Thrust coefficient cannot be less than 0")

            if self.upwind_thrust_coefficient > 1.0:
                raise Exception("Thrust coefficient cannot be greater than 1")

            self.upwind_local_turbulence_intensity = upwind_local_turbulence_intensity

            self.near_wake_length = calculate_near_wake_length(
                diameter=upwind_turbine.diameter,
                thrust_coefficient=self.upwind_thrust_coefficient,
                rpm=upwind_turbine.rotational_speed_rpm,
                number_of_blades=upwind_turbine.number_of_blades,
                velocity=upwind_velocity,
                turbulence_intensity=ambient_turbulence_intensity)

            self.apply_meander = apply_meander

        def calculate(self, distance_downwind):

            if distance_downwind < 0.0 or \
               self.is_negligible(self.upwind_thrust_coefficient) or \
               self.is_negligible(self.upwind_turbine.diameter):
                return NoWakeCrossSection(distance_downwind)

            if distance_downwind <= 0:
                raise Exception("Distance downwind must be a positive number")

            normalized_distance_downwind = distance_downwind / self.upwind_turbine.diameter

            velocity_deficit = calculate_velocity_deficit(
                self.upwind_thrust_coefficient,
                normalized_distance_downwind,
                self.upwind_local_turbulence_intensity)

            normalized_wake_width = calculate_width(
                                        self.upwind_thrust_coefficient,
                                        velocity_deficit)

            wake_width = normalized_wake_width * self.upwind_turbine.diameter

            if self.apply_meander:
                meander = calculate_meander(
                    normalized_distance_downwind,
                    velocity_deficit,
                    normalized_wake_width,
                    self.ambient_turbulence_intensity)
                velocity_deficit *= meander.amplitude_meander
                wake_width *= meander.width_meander

            added_turbulence = quarton_added_turbulence(
                distance_downwind,
                self.upwind_thrust_coefficient,
                self.upwind_turbine.diameter,
                self.near_wake_length,
                self.ambient_turbulence_intensity)

            return WakeCrossSection(
                    distance_downwind,
                    velocity_deficit,
                    added_turbulence,
                    wake_width,
                    self.upwind_turbine.diameter)

        def is_negligible(self, value):
            return value < SingleWake.NEAR_ZERO

