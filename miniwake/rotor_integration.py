import math


class EffectiveRadiusIntegrator:

    def __init__(self, number_of_sections=12):
        self.number_of_sections = number_of_sections
        self.theta_step = 2.0 * math.pi / float(self.number_of_sections)

    def calculate(self,
                  lateral_distance_from_wake_center,
                  vertical_distance_from_wake_center,
                  downwind_rotor_diameter,
                  wake_function):

        effective_radius = 0.75 * 0.5 * downwind_rotor_diameter

        combined_value = 0.0

        for i in range(self.number_of_sections):

            theta = i * self.theta_step

            lateral_distance = math.sin(theta) * effective_radius + lateral_distance_from_wake_center
            vertical_distance = math.sin(theta) * effective_radius + vertical_distance_from_wake_center

            combined_value = self.add_value(combined_value, wake_function(lateral_distance, vertical_distance))

        return self.finalise(combined_value)

    def add_value(self, combined_value, value):
        return combined_value + value

    def finalise(self, combined_value):
        return combined_value / float(self.number_of_sections)


class MaxEffectiveRadiusIntegrator:
            
    def add_value(self, combined_value, value):
        return max([combined_value, value])

    def finalise(self, combined_value):
        return combined_value