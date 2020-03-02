from velocity_deficit import calculate_shape
from velocity_deficit import calculate_width
from velocity_deficit import calculate_velocity_deficit
from added_turbulence import quarton_added_turbulence
from meander import calculate_meander


class NoWake:

    def velocity_deficit(self, distance_from_wake_center):
        return 0.0

    def added_turbulence(self, distance_from_wake_center):
        return 0.0


class Wake:

     def __init__(self, velocity_deficit, added_turbulence, wake_width):
        self.velocity_deficit = VelocityDeficitWakeProfile(velocity_deficit, wake_width)
        self.added_turbulence = AddedTurbulenceWakeProfile(added_turbulence, wake_width)
        self.width = wake_width


class AddedTurbulenceWakeProfile:

    def __init__(self, added_turbulence, wake_width):
        self.added_turbulence = added_turbulence
        self.wake_width = wake_width

    def __call__(self, distance_from_wake_center):

        if abs(distance_from_wake_center) < self.wake_width:
            return self.added_turbulence
        else:
            return 0.0


class VelocityDeficitWakeProfile:

    def __init__(self, velocity_deficit, wake_width):
        self.velocity_deficit = velocity_deficit
        self.wake_width = wake_width

    def __call__(self, distance_from_wake_center):
        return calculate_shape(distance_from_wake_center / self.wake_width) * self.velocity_deficit


class SingleWake:

        NEAR_ZERO = 0.000001

        def __init__(self,
                     ambient_turbulence_intensity,
                     upwind_diameter,
                     upwind_thrust_coefficient,
                     upwind_local_turbulence_intensity,
                     upwind_near_wake_length,
                     apply_meander):

            self.ambient_turbulence_intensity = ambient_turbulence_intensity
            self.upwind_diameter = upwind_diameter
            self.upwind_thrust_coefficient = upwind_thrust_coefficient
            self.upwind_local_turbulence_intensity = upwind_local_turbulence_intensity
            self.upwind_near_wake_length = upwind_near_wake_length

            self.apply_meander = apply_meander

        def calculate(self, distance_downwind):

            if self.is_negligible(self.upwind_thrust_coefficient) or self.is_negligible(self.upwind_diameter):
                return NoWake()

            normalized_distance_downwind = distance_downwind / self.upwind_diameter

            velocity_deficit = calculate_velocity_deficit(self.upwind_thrust_coefficient, normalized_distance_downwind, self.upwind_local_turbulence_intensity)
            normalized_wake_width = calculate_width(self.upwind_thrust_coefficient, velocity_deficit)
            wake_width = normalized_wake_width * self.upwind_diameter

            if self.apply_meander:
                meander = calculate_meander(normalized_distance_downwind, velocity_deficit, normalized_wake_width, self.ambient_turbulence)
                velocity_deficit *= meander.amplitude_meander
                wake_width *= meander.width_meander

            added_turbulence = quarton_added_turbulence(distance_downwind, self.upwind_thrust_coefficient, self.upwind_diameter, self.upwind_near_wake_length, self.ambient_turbulence_intensity)

            return Wake(velocity_deficit, added_turbulence, wake_width)

        def is_negligible(self, value):
            return value < SingleWake.NEAR_ZERO

