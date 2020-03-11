import math

from .velocity_deficit import calculate_shape
from .velocity_deficit import calculate_width
from .velocity_deficit import calculate_velocity_deficit
from .added_turbulence import quarton_added_turbulence
from .meander import calculate_meander
from .near_wake_length import calculate_near_wake_length


def distance(delta_x, delta_y):
    return math.sqrt(delta_x * delta_x + delta_y * delta_y)


class NoWake:

    def velocity_deficit(self,
                         lateral_distance,
                         vertical_distance):
        return 0.0

    def added_turbulence(self,
                         lateral_distance,
                         vertical_distance):
        return 0.0


class Wake:

     def __init__(
            self,
            velocity_deficit,
            added_turbulence,
            wake_width):

        self.velocity_deficit = VelocityDeficitWakeProfile(velocity_deficit, wake_width)
        self.added_turbulence = AddedTurbulenceWakeProfile(added_turbulence, wake_width)
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

            self.ambient_turbulence_intensity = ambient_turbulence_intensity
            self.upwind_diameter = upwind_turbine.diameter
            self.upwind_thrust_coefficient = upwind_turbine.thrust_curve(upwind_velocity)
            self.upwind_local_turbulence_intensity = upwind_local_turbulence_intensity

            self.upwind_near_wake_length = calculate_near_wake_length(
                diameter=self.upwind_diameter,
                thrust_coefficient=self.upwind_thrust_coefficient,
                rpm=upwind_turbine.rotational_speed_rpm,
                number_of_blades=upwind_turbine.number_of_blades,
                velocity=upwind_velocity,
                turbulence_intensity=ambient_turbulence_intensity)

            self.apply_meander = apply_meander

        def calculate(self, distance_downwind):

            if self.is_negligible(self.upwind_thrust_coefficient) or self.is_negligible(self.upwind_diameter):
                return NoWake()

            normalized_distance_downwind = distance_downwind / self.upwind_diameter

            velocity_deficit = calculate_velocity_deficit(
                self.upwind_thrust_coefficient,
                normalized_distance_downwind,
                self.upwind_local_turbulence_intensity)
            normalized_wake_width = calculate_width(self.upwind_thrust_coefficient, velocity_deficit)
            wake_width = normalized_wake_width * self.upwind_diameter

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
                self.upwind_diameter,
                self.upwind_near_wake_length,
                self.ambient_turbulence_intensity)

            return Wake(velocity_deficit, added_turbulence, wake_width)

        def is_negligible(self, value):
            return value < SingleWake.NEAR_ZERO

