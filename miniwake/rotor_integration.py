import math


class EffectiveRadiusIntegrator:

    def __init__(self, number_of_sections=12):
        self.number_of_sections = number_of_sections
        self.theta_step = 2.0 * math.pi / float(self.number_of_sections)

    def calculate(self, rotor_radius, polar_function):

        effective_radius = 0.75 * rotor_radius

        combined_value = 0.0

        for i in range(self.number_of_sections):
            theta = i * self.theta_step
            combined_value = self.add_value(combined_value, polar_function(theta, effective_radius))

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